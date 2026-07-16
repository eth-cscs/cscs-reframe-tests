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

import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))

from container_engine import ContainerEngineMixin  # noqa: E402
from slurm_mpi_pmi2 import SlurmMpiPmi2Mixin       # noqa: E402
from switch_topology import select_nodes_across_groups  # noqa: E402


class OMB_MBW_MR_Base(rfm.RunOnlyRegressionTest,
                      ContainerEngineMixin,
                      SlurmMpiPmi2Mixin):
    valid_prog_environs = ['builtin']
    valid_systems = ['+ce +nvgpu']
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
    # num_tasks is computed from those values in set_num_tasks().
    num_nodes = 2
    num_tasks_per_node = 4
    num_tasks = required

    # OSU options.  By default measure at 4 MiB with a short run.
    message_size = variable(str, value='4194304')
    warmup_iters = variable(int, value=10)
    num_iters = variable(int, value=50)
    validate = variable(bool, value=True)

    @run_after('setup')
    def set_executable(self):
        self.executable = f'{self.mpi_tests_dir}/{self.test_name}'

    @run_after('setup')
    def set_num_tasks(self):
        self.num_tasks = self.num_nodes * self.num_tasks_per_node

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

    def _reservation_set(self):
        """Return True if the job is submitted with a Slurm reservation."""
        return any(
            opt.startswith('--reservation=') or opt.startswith('reservation=')
            for opt in (self.job.options or [])
        )

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


@rfm.simple_test
class OMB_MBW_MR_SingleSwitch(OMB_MBW_MR_Base):
    '''Intra-switch aggregate bandwidth reference.
    '''
    descr = 'OSU mbw_mr intra-switch reference (10 nodes, 320 ranks)'
    num_nodes = 10
    num_tasks_per_node = 32
    warmup_iters = 100
    num_iters = 1000
    # Validation is disabled for the long reference run; the values are used
    # purely for the intra-switch performance baseline.
    validate = False
    tags = {'maintenance'}
    reference = {
        '*': {
            'agg_bw_mb_s': (121118.51, -0.1, 0.1, 'MB/s'),
            'agg_mr': (28876.90, -0.1, 0.1, 'Messages/s')
        }
    }
    extra_resources = {
        'switches': {
            'num_switches': 1
        }
    }

    @run_before('run')
    def set_binding(self):
        self.job.launcher.options += [
            '--cpu-bind=ldoms', '--distribution=block:block'
        ]


@rfm.simple_test
class OMB_MBW_MR_Canary(OMB_MBW_MR_Base):
    '''Light-weight cross-switch canary for daily trend detection.

    Picks one node from each of two distinct Level-0 switch groups via
    ``--nodelist`` so the traffic crosses a leaf switch.  The reference
    values were collected on starlex.
    '''
    descr = 'OSU mbw_mr cross-switch canary (2 nodes, 8 ranks)'
    num_nodes = 2
    num_tasks_per_node = 4
    tags = {'production'}
    reference = {
        '*': {
            'agg_bw_mb_s': (93463.34, -0.1, 0.1, 'MB/s'),
            'agg_mr': (22283.4, -0.1, 0.1, 'Messages/s')
        }
    }

    @run_before('run')
    def pick_nodes(self):
        partition = self.current_partition.name
        nodes = select_nodes_across_groups(
            self.num_nodes, partition,
            allow_reserved=self._reservation_set()
        )
        if len(nodes) < self.num_nodes:
            self.skip(
                f'could not find {self.num_nodes} usable nodes in distinct '
                f'switch groups (found {len(nodes)})'
            )

        self.job.options += [f'--nodelist={",".join(nodes)}']


@rfm.simple_test
class OMB_MBW_MR_Stress(OMB_MBW_MR_Base):
    '''Large cross-switch stress test intended for an empty system after
    maintenance.'''
    descr = 'OSU mbw_mr cross-switch stress (15 nodes, 60 ranks)'
    num_nodes = 15
    num_tasks_per_node = 4
    tags = {'maintenance'}

    @run_before('run')
    def pick_nodes(self):
        partition = self.current_partition.name
        nodes = select_nodes_across_groups(
            self.num_nodes, partition,
            allow_reserved=self._reservation_set()
        )
        if len(nodes) < self.num_nodes:
            self.skip(
                f'could not find {self.num_nodes} usable nodes in distinct '
                f'switch groups (found {len(nodes)})'
            )

        self.job.options += [f'--nodelist={",".join(nodes)}']
