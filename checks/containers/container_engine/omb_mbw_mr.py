# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# OSU Multiple Bandwidth / Message Rate checks across Slurm switch groups.
#
# The tests use the upstream MPICH Container Engine image that already ships
# the OSU Micro-Benchmarks.  The Container Engine CXI hook injects the host's
# optimised libfabric/xpmem libraries, giving native Slingshot performance.
#
# Benchmark purpose
# -----------------
# osu_mbw_mr measures the aggregate uni-directional bandwidth across multiple
# simultaneous rank pairs.  Each rank is bound to a CPU LDOM so that Cray
# MPICH selects the nearest Slingshot NIC (via libfabric hwloc topology).
# With 4 ranks per node on GH200 (4 Slingshot 11 NICs per node), all 4 NICs
# are exercised and the aggregate bandwidth reflects the full node injection
# capability, not just a single-NIC ceiling.
#
# Theoretical limits and expected results
# ----------------------------------------
# Each Slingshot 11 (Cassini) NIC provides 200 Gbps = 25 GB/s unidirectional.
# GH200 nodes have 4 NICs, giving a theoretical node injection bandwidth of
# 100 GB/s.  Cray MPICH on daint is compiled without scalable endpoints
# (MPIDI_OFI_ENABLE_SCALABLE_ENDPOINTS=0), so a single MPI process uses
# exactly one NIC — multi-NIC striping per process is not possible regardless
# of MPIR_CVAR_CH4_OFI_MAX_NICS or MPIR_CVAR_CH4_OFI_ENABLE_MULTI_NIC_STRIPING
# settings.  This is consistent with observations on Frontier (OLCF) and
# Perlmutter (NERSC), which use identical hardware and report comparable
# single-pair bandwidth (see "Bringing HPE Slingshot 11 Support to Open MPI",
# Shehata et al., SC23).
#
# Typical measured values at 4 MiB message size:
#   1 pair  (2 nodes,  1 rank/node):  ~22-25 GB/s  ( 88-100% of 1 NIC)
#   2 pairs (2 nodes,  2 ranks/node): ~45-49 GB/s  ( 90- 98% of 2 NICs)
#   8 pairs (4 nodes,  4 ranks/node): ~49  GB/s    (~49% of 4×100 GB/s;
#                                                    per-pair drops due to
#                                                    switch/fabric contention
#                                                    and shared-node overhead)
#
# The 8-pair baseline (~49 GB/s) is the reference for the PerSwitch variant.
# Per-pair bandwidth decreases as more pairs contend for the same fabric
# paths, which is expected and does not indicate a hardware problem.
# Consistent per-switch results across all L0 groups confirm fabric health;
# a single outlier group (slow switch, degraded cable, failing transceiver)
# would flag a hardware issue requiring investigation.

import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))

from container_engine import ContainerEngineMixin                      # noqa: E402
from slurm_mpi_pmi2 import SlurmMpiPmi2Mixin                          # noqa: E402
from switch_topology import (                                          # noqa: E402
    _get_l0_switches,
    get_switch_group_names,
    get_switch_groups,
    select_nodes_across_groups,
)


def _extract_reservation(options):
    """Return the reservation name from Slurm job options, or None."""
    for opt in (options or []):
        if opt.startswith('--reservation=') or opt.startswith('reservation='):
            return opt.split('=', 1)[1]

    return None


class OMB_MBW_MR_Base(rfm.RunOnlyRegressionTest,
                      ContainerEngineMixin,
                      SlurmMpiPmi2Mixin):
    """Base class for OSU Multiple Bandwidth / Message Rate checks.

    Provides the MPICH Container Engine image with the CXI hook for
    Slingshot, PMI-2 launcher flags, and ``set_perf`` which extracts
    aggregate bandwidth and message rate at a single message size.
    Concrete subclasses select node placement (intra-switch or
    cross-switch).

    Each rank is bound to one CPU LDOM (--cpu-bind=ldoms) so that Cray
    MPICH selects the nearest Slingshot NIC.  With num_tasks_per_node=4
    on GH200 (4 NICs per node), all NICs are exercised and the aggregate
    bandwidth reflects the full node injection capability.  See the file
    header for theoretical limits and expected results.
    """

    valid_prog_environs = ['builtin']
    # Concrete classes set explicit valid_systems so that references are
    # only compared on systems where a baseline has been collected.
    valid_systems = []
    maintainers = ['perettig', 'UE']
    sourcesdir = None
    container_image = (
        'jfrog.svc.cscs.ch/ghcr/sarus-suite/containerfiles-ci/'
        'omb:7.5.2-mpich4.3.2-ofi1.22-cuda12.8.1'
    )
    container_env_table = {
        'annotations.com.hooks': {
            'cxi.enabled': 'true',
        }
    }
    mpi_tests_dir = '/usr/local/libexec/osu-micro-benchmarks/mpi'
    test_name = 'pt2pt/osu_mbw_mr'

    # Concrete tests below override num_nodes and num_tasks_per_node.
    # num_tasks is computed from those values in set_num_tasks(), which
    # runs in run_before('run') so that subclass hooks set_num_nodes()
    # (run_after('setup')) have already executed.
    #
    # Note: osu_mbw_mr is O(n^2) in rank pairs — 16 ranks = 120 pairs
    # (~30s), 32 ranks = 496 pairs (~5min), 256 ranks = 32,640 pairs
    # (>10min).  Keep num_tasks_per_node and num_nodes small.
    num_nodes = 2
    num_tasks_per_node = 4
    num_tasks = required

    # OSU options.  By default measure at 4 MiB with a short run.
    message_size = variable(str, value='4194304')
    warmup_iters = variable(int, value=10)
    num_iters = variable(int, value=50)
    # When True, pass -c to osu_mbw_mr for internal correctness checking.
    # This is independent of ReFrame's reference comparison.
    validate = variable(bool, value=True)

    # Set to True in subclasses that should record num_switch_groups
    # as a performance metric (e.g. FullTopology, where the count
    # changes with the live topology).
    _record_num_switch_groups = False

    @run_after('setup')
    def set_executable(self):
        self.executable = f'{self.mpi_tests_dir}/{self.test_name}'

    @run_after('setup')
    def set_executable_opts(self):
        # osu_mbw_mr expects a message-size range as "min:max".
        opts = [
            '-m', f'{self.message_size}:{self.message_size}',
            '-x', str(self.warmup_iters),
            '-i', str(self.num_iters)
        ]
        if self.validate:
            opts.append('-c')

        self.executable_opts = opts

    @run_before('run')
    def set_num_tasks(self):
        self.num_tasks = self.num_nodes * self.num_tasks_per_node

    @sanity_function
    def assert_sanity(self):
        return sn.assert_found(
            r'^# OSU MPI Multiple Bandwidth / Message Rate Test', self.stdout
        )

    @run_before('performance')
    def set_perf(self):
        # Extract aggregate bandwidth and message rate from the single line
        # that corresponds to the configured message size.
        self.perf_patterns = {
            'agg_bw_mb_s': sn.extractsingle(
                rf'^{self.message_size}\s+(?P<bw>\S+)\s+(?P<mr>\S+)',
                self.stdout, 'bw', float
            ),
            'agg_mr': sn.extractsingle(
                rf'^{self.message_size}\s+(?P<bw>\S+)\s+(?P<mr>\S+)',
                self.stdout, 'mr', float
            )
        }
        if self._record_num_switch_groups:
            self.perf_patterns['num_switch_groups'] = sn.count(
                get_switch_group_names(0)
            )


@rfm.simple_test
class OMB_MBW_MR_PerSwitch(OMB_MBW_MR_Base):
    '''Intra-switch bandwidth reference, one variant per L0 switch group.

    Each variant constrains ``--nodelist`` to all nodes in a specific
    Level-0 switch group and lets Slurm pick any 4.  This gives
    per-switch bandwidth data — a consistently slow switch indicates a
    hardware issue (degraded cable, failing transceiver, etc.).

    Groups with fewer than ``num_nodes`` nodes total are skipped
    (physically impossible).  Groups with 0 idle nodes are NOT skipped
    — the job waits for 4 nodes to become available, which is
    reasonable in production given the large group sizes (26-111
    nodes per group on daint).

    The container image (~9.6 GB) is cached in the shared
    ``${SCRATCH}/.edf_imagestore``.  The first run per account pulls
    the image (~20-30 min); subsequent runs complete in < 1 minute.
    '''
    descr = 'OSU mbw_mr per-switch (4 nodes, 16 ranks)'
    valid_systems = ['daint:normal', 'starlex:normal']
    switch_group = parameter(_get_l0_switches(), loggable=True)
    num_nodes = 4
    num_tasks_per_node = 4
    warmup_iters = 10
    num_iters = 50
    # Allow extra time for container image pull on first run (per
    # account); the benchmark itself completes in < 1 minute once
    # cached.  The 1h limit gives Slurm enough time to find 4 idle
    # nodes within the --nodelist constraint during production.
    time_limit = '1h'
    # Disable OSU's internal -c correctness check for the reference run;
    # this is unrelated to ReFrame's reference comparison below.
    validate = False
    reference = {
        'daint:normal':   {'agg_bw_mb_s': (48251.31, -0.1, 0.1, 'MB/s'),
                           'agg_mr':      (11504.01, -0.1, 0.1, 'Messages/s')},
        'starlex:normal': {'agg_bw_mb_s': (49705.12, -0.1, 0.1, 'MB/s'),
                           'agg_mr':      (11851.62, -0.1, 0.1, 'Messages/s')},
    }

    @run_after('init')
    def set_switch_descr(self):
        self.descr = f'OSU mbw_mr per-switch={self.switch_group} (4 nodes)'

    @run_after('setup')
    def set_nodelist(self):
        # Constrain to all nodes in this switch group; Slurm picks any
        # num_nodes from the list.  All nodes in a single L0 group are
        # on the same switch by definition, so --switches=1 is not
        # needed.  --nodes is required because --nodelist makes Slurm
        # default to one node per task rather than respecting
        # --ntasks-per-node.
        groups = get_switch_groups(level=0)
        nodes = groups.get(self.switch_group, [])
        if len(nodes) < self.num_nodes:
            self.skip(
                f'switch group {self.switch_group!r} has only '
                f'{len(nodes)} node(s), need {self.num_nodes}'
            )

        self.job.options += [
            f'--nodes={self.num_nodes}',
            f'--nodelist={",".join(nodes)}',
        ]

    @run_before('run')
    def set_binding(self):
        self.job.launcher.options += [
            '--cpu-bind=ldoms', '--distribution=block:block'
        ]


@rfm.simple_test
class OMB_MBW_MR_FullTopology(OMB_MBW_MR_Base):
    '''Cross-switch stress test spanning all Level-0 switch groups.

    One node is selected from each live Level-0 group via
    ``select_nodes_across_groups`` so that the traffic crosses every
    leaf switch.  The number of nodes is derived dynamically from the
    live topology (``len(get_switch_group_names(0))``); if fewer groups
    have usable nodes than required, the test is skipped.

    The ``num_switch_groups`` performance metric is recorded so that
    historical runs can be filtered by topology size — a changing switch
    count affects aggregate bandwidth even if per-pair performance is
    unchanged.

    Intended for an empty system after maintenance.  Performance is
    recorded but not yet compared — add per-partition ``reference``
    entries once a stable baseline has been collected.
    '''
    descr = 'OSU mbw_mr full topology (all Level-0 switch groups)'
    valid_systems = ['daint:normal', 'starlex:normal']
    num_tasks_per_node = 4
    _record_num_switch_groups = True

    @run_after('setup')
    def set_num_nodes(self):
        self.num_nodes = len(get_switch_group_names(0))

    @run_before('run')
    def pick_nodes(self):
        partition = self.current_partition.name
        reservation = _extract_reservation(self.job.options)
        nodes = select_nodes_across_groups(
            self.num_nodes, partition, reservation=reservation
        )
        if len(nodes) < self.num_nodes:
            self.skip(
                f'could not find {self.num_nodes} usable nodes in distinct '
                f'switch groups (found {len(nodes)})'
            )

        self.job.options += [f'--nodelist={",".join(nodes)}']
