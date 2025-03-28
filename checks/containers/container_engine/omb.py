# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))

from container_engine import ContainerEngineMixin  # noqa: E402


class OMB_Base_CE(rfm.RunOnlyRegressionTest, ContainerEngineMixin):
    valid_prog_environs = ['builtin']
    valid_systems = ['+ce']
    sourcesdir = None
    test_name = parameter(['pt2pt/osu_bw','collective/osu_alltoall'])
    num_nodes = variable(int, value=2)
    container_env_table = {
        'annotations.com.hooks': {
            'cxi.enabled': 'true',
        }
    }
    tags = {'production', 'ce'}

    mpi_tests_dir = '/usr/local/libexec/osu-micro-benchmarks/mpi'

    local_ranks_per_test = {
        'pt2pt/osu_bw': 1,
        'collective/osu_alltoall': 4
    }

    sanity_per_test = {
        'pt2pt/osu_bw': r'4194304',
        'collective/osu_alltoall': r'1048576'
    }

    @run_after('setup')
    def set_executable(self):
        self.executable = f'{self.mpi_tests_dir}/{self.test_name}'

    @run_after('setup')
    def set_num_gpus_per_node(self):
        curr_part = self.current_partition
        self.num_gpus_per_node = curr_part.select_devices('gpu')[0].num_devices
        self.num_tasks_per_node = self.local_ranks_per_test[self.test_name]
        self.num_tasks = self.num_nodes * self.num_tasks_per_node

    @sanity_function
    def assert_sanity(self):
        return sn.assert_found(self.sanity_per_test[self.test_name], self.stdout)

    @run_before('performance')
    def set_reference(self):
        self.reference = self.reference_per_test[self.test_name]

    @run_before('performance')
    def set_perf(self):
        self.patterns_per_test = {
            'pt2pt/osu_bw': {
                'bw_4M': sn.extractsingle(r'4194304\s+(?P<bw_4M>\S+)',
                                          self.stdout, 'bw_4M', float)
            },
            'collective/osu_alltoall': {
                'latency_1M': sn.extractsingle(r'1048576\s+(?P<latency_1M>\S+)',
                                     self.stdout, 'latency_1M', float)
            }
        }
        self.perf_patterns = self.patterns_per_test[self.test_name]


@rfm.simple_test
class OMB_MPICH_CE(OMB_Base_CE):
    valid_systems = ['+ce +nvgpu']
    reference_per_test = {
        'pt2pt/osu_bw': {
            '*': {
                'bw_4M': (24000., -0.15, None, 'MB/s')
            }
        },
        'collective/osu_alltoall': {
            '*': {
                'latency_1M': (1800., None, 0.15, 'us')
            }
        }
    }

    @run_before('run')
    def set_pmi2(self):
        self.job.launcher.options += ['--mpi=pmi2']

    @run_after('init')
    def setup_ce(self):
        self.container_image = (f'jfrog.svc.cscs.ch#reframe-oci/osu-mb:7.5-mpich4.3.0-ofi1.15-cuda12.8')


@rfm.simple_test
class OMB_OMPI_CE(OMB_Base_CE):
    valid_systems = ['+ce +nvgpu']
    reference_per_test = {
        'pt2pt/osu_bw': {
            '*': {
                'bw_4M': (24000., -0.15, None, 'MB/s')
            }
        },
        'collective/osu_alltoall': {
            '*': {
                'latency_1M': (500., None, 0.15, 'us')
            }
        }
    }

    @run_before('run')
    def set_pmix(self):
        self.job.launcher.options += ['--mpi=pmix']

    @run_after('init')
    def setup_ce(self):
        self.container_image = (f'jfrog.svc.cscs.ch#reframe-oci/osu-mb:7.5-ompi5.0.7-ofi1.15-cuda12.8')

