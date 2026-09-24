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
# 100 GB/s. Cray MPICH on daint is compiled without scalable endpoints
# (MPIDI_OFI_ENABLE_SCALABLE_ENDPOINTS=0), so a single MPI process uses
# exactly 1 NIC - multi-NIC striping per process is not possible regardless
# of MPIR_CVAR_CH4_OFI_MAX_NICS or MPIR_CVAR_CH4_OFI_ENABLE_MULTI_NIC_STRIPING
# settings. This is consistent with observations on Frontier (OLCF) and
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
    all_partition_nodes,
    get_l0_switches,
    get_partition_nodes,
    get_switch_group_names,
    get_switch_groups,
)


def _extract_reservation(options):
    """Return the reservation name from Slurm job options, or None.

    Handles both ``--reservation=name`` and ``--reservation name``
    (space-separated) forms.  An empty value (``--reservation=``) is
    skipped rather than treated as "no reservation."
    """
    if not options:
        return None

    for i, opt in enumerate(options):
        if opt in ('--reservation', 'reservation'):
            if i + 1 < len(options):
                return options[i + 1]

        if opt.startswith('--reservation=') or opt.startswith('reservation='):
            value = opt.split('=', 1)[1]
            if value:
                return value

    return None


class OMB_MBW_MR_Base(rfm.RunOnlyRegressionTest,
                      ContainerEngineMixin,
                      SlurmMpiPmi2Mixin):
    """Base class for OSU Multiple Bandwidth / Message Rate checks.

    Set the MPICH Container Engine image with the CXI hook for
    Slingshot, PMI-2 launcher flags, and `set_perf` which extracts
    aggregate bandwidth and message rate at a single message size.
    Concrete subclasses select node placement (intra-switch or
    cross-switch).

    Each rank is bound to one CPU LDOM (--cpu-bind=ldoms) so that Cray
    MPICH selects the nearest Slingshot NIC.  With num_tasks_per_node=4
    on GH200 (4 NICs per node), all NICs are exercised and the aggregate
    bandwidth reflects the full node injection capability. See the file
    header for theoretical limits and expected results.
    """

    valid_prog_environs = ['builtin']
    valid_systems = []  # set in the other classes
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
    # Note: osu_mbw_mr is O(n^2) in rank pairs - 16 ranks = 120 pairs
    # (~30s), 32 ranks = 496 pairs (~5min), 256 ranks = 32,640 pairs
    # (>10min). Keep num_tasks_per_node and num_nodes small.
    num_nodes = 2
    num_tasks_per_node = 4
    num_tasks = required

    # OSU options.  By default measure at 4 MiB with a short run.
    message_size = variable(int, value=4194304)
    warmup_iters = variable(int, value=10)
    num_iters = variable(int, value=50)
    # When True, pass -c to osu_mbw_mr for internal correctness checking.
    # This is independent of ReFrame's reference comparison.
    osu_correctness_check = variable(bool, value=True)

    # Set to True in subclasses that should record num_switch_groups
    # as a performance metric (e.g. FullTopology, where the count
    # changes with the live topology).
    _record_num_switch_groups = False

    # Initialized at class level so that set_perf can use .update()
    # without clobbering subclass additions.
    perf_patterns = {}

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
        if self.osu_correctness_check:
            opts.append('-c')

        self.executable_opts = opts

    @run_before('run')
    def set_num_tasks(self):
        self.num_tasks = self.num_nodes * self.num_tasks_per_node

    @run_before('run')
    def set_binding(self):
        self.job.launcher.options += [
            '--cpu-bind=ldoms', '--distribution=block:block'
        ]

    @sanity_function
    def assert_sanity(self):
        return sn.assert_found(
            r'^# OSU MPI Multiple Bandwidth / Message Rate Test', self.stdout
        )

    @run_before('performance')
    def set_perf(self):
        # Extract aggregate bandwidth and message rate from the single line
        # that corresponds to the configured message size.
        self.perf_patterns.update({
            'agg_bw_mb_s': sn.extractsingle(
                rf'^{self.message_size}\s+(?P<bw>\S+)\s+(?P<mr>\S+)',
                self.stdout, 'bw', float
            ),
            'agg_mr': sn.extractsingle(
                rf'^{self.message_size}\s+(?P<bw>\S+)\s+(?P<mr>\S+)',
                self.stdout, 'mr', float
            )
        })
        if self._record_num_switch_groups:
            # Use the count of groups actually selected for this partition;
            # fall back to the raw topology count if not set.
            if hasattr(self, '_used_switch_groups'):
                self.perf_patterns['num_switch_groups'] = sn.len(
                    self._used_switch_groups
                )
            else:
                self.perf_patterns['num_switch_groups'] = sn.count(
                    get_switch_group_names(0)
                )


@rfm.simple_test
class OMB_MBW_MR_PerSwitch(OMB_MBW_MR_Base):
    '''Intra-switch bandwidth reference, one variant per L0 switch group.

    Each variant constrains `--nodelist` to all nodes in a specific
    Level-0 switch group and lets Slurm pick any 4. This gives
    per-switch bandwidth data - a consistently slow switch indicates a
    hardware issue (degraded cable, failing transceiver, etc...).

    Groups with fewer than `num_nodes` nodes total are skipped
    (physically impossible). Groups with 0 idle nodes are NOT skipped
    - the job waits for 4 nodes to become available, which is
    reasonable in production given the large group sizes (26-111
    nodes per group on daint).

    The container image (~9.6 GB) is cached in the shared
    `${SCRATCH}/.edf_imagestore`. The first run per account pulls
    the image (~20-30 min); subsequent runs complete in < 1 minute.
    '''
    descr = 'OSU mbw_mr per-switch (4 nodes, 16 ranks)'
    valid_systems = ['daint:normal', 'starlex:normal']
    tags = {'production'}
    switch_group = parameter(get_l0_switches(), loggable=True)
    num_nodes = 4
    num_tasks_per_node = 4
    warmup_iters = 10
    num_iters = 50
    # Allow extra time for container image pull on first run (per
    # account); the benchmark itself completes in < 1 minute once
    # cached. The 1h limit gives Slurm enough time to find 4 idle
    # nodes within the --nodelist constraint during production.
    time_limit = '1h'
    # Disable OSU's internal -c correctness check for the reference run;
    # this is unrelated to ReFrame's reference comparison below.
    osu_correctness_check = False

    # Reference values collected on daint (Sep 2026) from 10 L0 switch
    # groups with 0.8% spread (49,229-49,632 MB/s).  The ±10% tolerance
    # accommodates normal fabric variance across switches and load
    # conditions; a consistently slow group (outside tolerance) flags a
    # hardware issue requiring investigation.
    reference = {
        'daint:normal':   {'agg_bw_mb_s': (48251.31, -0.1, 0.1, 'MB/s'),
                           'agg_mr':      (11504.01, -0.1, 0.1, 'Messages/s')},
        'starlex:normal': {'agg_bw_mb_s': (49705.12, -0.1, 0.1, 'MB/s'),
                           'agg_mr':      (11851.62, -0.1, 0.1, 'Messages/s')},
    }

    @run_after('init')
    def set_descr(self):
        self.descr = (
            f'OSU mbw_mr per-switch={self.switch_group} '
            f'({self.num_nodes} nodes)'
        )

    @run_after('setup')
    def set_nodelist(self):
        # Constrain to all nodes in this switch group; Slurm picks any
        # num_nodes from the list. All nodes in a single L0 group are
        # on the same switch by definition, so --switches=1 is not
        # needed. --nodes is required because --nodelist makes Slurm
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


@rfm.simple_test
class OMB_MBW_MR_FullTopology(OMB_MBW_MR_Base):
    '''Cross-switch stress test spanning available Level-0 switch groups.

    One node is selected from each live Level-0 group that belongs to
    the current partition and currently has at least one usable node.
    The number of nodes is therefore dynamic and reflects the live load;
    the test only skips if fewer than ``min_switch_groups`` groups are
    available.  The idle-node check is a scheduling hint, not a guarantee
    that Slurm will immediately allocate the selected nodes.

    The ``num_switch_groups`` performance metric records the actual number
    of groups used in the run, so historical results can be filtered by
    topology size.

    Tagged ``maintenance`` because it may require many idle nodes across
    all switch groups; daily production runs are covered by the
    ``PerSwitch`` variant.

    Per-switch-count reference values are set for the baselines collected
    on daint (Sep 2026) for ``N = 2..8`` groups.  Larger topologies still
    record performance without comparison until additional maintenance
    windows provide stable baselines.
    '''
    descr = 'OSU mbw_mr full topology (available Level-0 switch groups)'
    valid_systems = ['daint:normal', 'starlex:normal', 'clariden:normal']
    tags = {'maintenance'}
    num_tasks_per_node = 4
    _record_num_switch_groups = True
    reservation = variable(str, value='')
    # Minimum number of switch groups required for a meaningful cross-switch
    # run.  The test will use every available group as long as at least this
    # many have usable nodes.
    min_switch_groups = variable(int, value=2)
    # Maximum number of switch groups to use.  Zero means "use every
    # available group" (default production behaviour).  Set to a positive
    # value to run controlled scaling benchmarks.
    max_switch_groups = variable(int, value=0)

    # Baseline performance values per number of switch groups actually used.
    # These are shared across the Alps vclusters (daint/starlex/clariden)
    # because they use the same Slingshot 11 fabric.  The ±10% tolerance
    # accounts for fabric variance across switch groups and load
    # conditions; measured spread was <2% for most N, up to 5% for N=5
    # and N=7 due to group composition differences.  Topologies with no
    # entry in this table still record performance without comparison.
    _baselines = {
        # Baselines collected on daint (Sep 2026).  Shared across Alps
        # vclusters (daint/starlex/clariden) with ±10% tolerance.
        # N: {'agg_bw_mb_s': MB/s, 'agg_mr': Messages/s}
        2: {'agg_bw_mb_s': 23215.04, 'agg_mr': 5534.90},
        3: {'agg_bw_mb_s': 39788.99, 'agg_mr': 9486.43},
        4: {'agg_bw_mb_s': 46437.60, 'agg_mr': 11071.59},
        5: {'agg_bw_mb_s': 57577.84, 'agg_mr': 13727.63},
        6: {'agg_bw_mb_s': 71766.80, 'agg_mr': 17110.54},
        7: {'agg_bw_mb_s': 81816.81, 'agg_mr': 19506.65},
        8: {'agg_bw_mb_s': 94085.66, 'agg_mr': 22431.77},
    }

    @run_after('setup')
    def set_num_nodes(self):
        partition = self.current_partition.name
        groups = get_switch_groups(level=0)
        all_nodes = all_partition_nodes(partition)
        partition_groups = [
            name for name, nodes in groups.items() if set(nodes) & all_nodes
        ]

        usable = get_partition_nodes(partition)
        available_groups = [
            name for name in partition_groups
            if set(groups[name]) & usable
        ]

        target = len(available_groups)
        if self.max_switch_groups > 0:
            target = min(target, self.max_switch_groups)

        if target < self.min_switch_groups:
            self.skip(
                f'only {len(available_groups)} switch group(s) usable, '
                f'need at least {self.min_switch_groups}'
            )

        self._used_switch_groups = available_groups[:target]
        self.num_nodes = target
        self._num_switch_groups = target
        self.logger.info(
            f'OMB_MBW_MR_FullTopology: running on '
            f'{target}/{len(partition_groups)} switch groups'
        )

    @run_before('run')
    def pick_nodes(self):
        partition = self.current_partition.name
        reservation = self.reservation or _extract_reservation(self.job.options)
        if reservation and not any(
            opt.startswith('--reservation=') for opt in self.job.options
        ):
            self.job.options += [f'--reservation={reservation}']

        groups = get_switch_groups(level=0)
        usable = get_partition_nodes(partition, reservation=reservation)

        nodes = []
        for group in self._used_switch_groups:
            candidates = list(set(groups[group]) & usable)
            if candidates:
                nodes.append(candidates[0])

        if len(nodes) < self.min_switch_groups:
            self.skip(
                f'could not find {self.min_switch_groups} usable nodes in '
                f'distinct switch groups (found {len(nodes)})'
            )

        self.job.options += [
            f'--nodes={len(nodes)}',
            f'--nodelist={",".join(nodes)}',
        ]

    @run_before('performance')
    def set_reference(self):
        # Set per-switch-count reference values shared across the Alps
        # vclusters.  If no baseline exists for the actual number of groups
        # used in this run, leave reference empty and record only.
        n = self._num_switch_groups
        baseline = self._baselines.get(n)
        if baseline is None:
            return

        ref_entry = {
            'agg_bw_mb_s': (baseline['agg_bw_mb_s'], -0.1, 0.1, 'MB/s'),
            'agg_mr':      (baseline['agg_mr'],      -0.1, 0.1, 'Messages/s'),
        }
        self.reference = {
            'daint:normal':    ref_entry,
            'starlex:normal':  ref_entry,
            'clariden:normal': ref_entry,
        }
