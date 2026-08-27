# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# The Containerfiles for the images used in these checks can be found here:
# - OMB MPICH: https://github.com/sarus-suite/containerfiles-ci/tree/main/hpc/benchmarks/omb-mpich/  # noqa: E501
# - OMB OMPI: https://github.com/sarus-suite/containerfiles-ci/tree/main/hpc/benchmarks/omb-openmpi/  # noqa: E501

import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))

from container_engine import ContainerEngineMixin  # noqa: E402
from slurm_mpi_pmi2 import SlurmMpiPmi2Mixin       # noqa: E402
from slurm_mpi_pmix import SlurmMpiPmixMixin       # noqa: E402


class OMB_Base_CE(rfm.RunOnlyRegressionTest, ContainerEngineMixin):
    valid_prog_environs = ['builtin']
    valid_systems = ['+ce']
    maintainers = ['amadonna', 'VCUE']
    sourcesdir = None
    test_name = parameter(['pt2pt/osu_bw', 'collective/osu_alltoall'])
    num_nodes = variable(int, value=2)
    container_env_table = {
        'annotations.com.hooks': {
            'cxi.enabled': 'true',
        }
    }
    tags = {'production', 'ce', 'ce_dev', 'maintenance'}

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
        return sn.assert_found(self.sanity_per_test[self.test_name],
                               self.stdout)

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
                'latency_1M': sn.extractsingle(
                    r'1048576\s+(?P<latency_1M>\S+)', self.stdout,
                    'latency_1M', float)
            }
        }
        self.perf_patterns = self.patterns_per_test[self.test_name]


@rfm.simple_test
class OMB_MPICH_CE(OMB_Base_CE, SlurmMpiPmi2Mixin):
    descr = 'OSU Micro-benchmarks for MPICH/CE (Point2Point and All2All)'
    container_image = (
        'jfrog.svc.cscs.ch/ghcr/sarus-suite/containerfiles-ci/'
        'omb:7.5.2-mpich4.3.2-ofi1.22-cuda12.8.1'
    )
    valid_systems = ['+ce +nvgpu']
    reference_per_test = {
        'pt2pt/osu_bw': {
            '*': {
                'bw_4M': (24000., -0.15, None, 'MB/s')
            }
        },
        'collective/osu_alltoall': {
            'zinal': {
                'latency_1M': (2400., None, 0.15, 'us')
            },
            '*': {
                'latency_1M': (1800., None, 0.15, 'us')
            }
        }
    }

    @run_after('init')
    def skip_xfail_test(self):
        self.skip_if(self.test_name == 'collective/osu_alltoall',
                     'skipping Known performance regression')


@rfm.simple_test
class OMB_OMPI_CE(OMB_Base_CE, SlurmMpiPmixMixin):
    descr = 'OSU Micro-benchmarks for OpenMPI/CE (Point2Point and All2All)'
    container_image = (
        'jfrog.svc.cscs.ch/ghcr/sarus-suite/containerfiles-ci/'
        'omb:7.5.2-ompi5.0.9-ofi1.22-cuda12.8.1'
    )
    valid_systems = ['+ce +nvgpu']
    reference_per_test = {
        'pt2pt/osu_bw': {
            '*': {
                'bw_4M': (24000., -0.15, None, 'MB/s')
            }
        },
        'collective/osu_alltoall': {
            'zinal': {
                'latency_1M': (1400., None, 0.15, 'us')
            },
            '*': {
                'latency_1M': (500., None, 0.15, 'us')
            }
        }
    }

    @run_after('init')
    def skip_xfail_test(self):
        self.skip_if(self.test_name == 'collective/osu_alltoall',
                     'skipping Known performance regression')


@rfm.simple_test
class OMB_MPICH_CE_Host(OMB_MPICH_CE):
    descr = '''
    OSU Micro-benchmarks for MPICH/CE with host netstack
    (Point2Point and All2All)
    '''

    @run_after('init')
    def setup_netstack_source(self):
        self.container_env_table['annotations.com.hooks'].update({
            'netstack.source': 'host'
        })


@rfm.simple_test
class OMB_OMPI_CE_Host(OMB_OMPI_CE):
    descr = '''
    OSU Micro-benchmarks for OpenMPI/CE with host netstack
    (Point2Point and All2All)
    '''

    @run_after('init')
    def setup_netstack_source(self):
        self.container_env_table['annotations.com.hooks'].update({
            'netstack.source': 'host'
        })


@rfm.simple_test
class OMB_MPICH_Skybox(OMB_MPICH_CE):
    descr = '''
    OSU Micro-benchmarks for MPICH/CE/Skybox (Point-to-Point & All-to-All)
    '''
    tags = {'ce_dev', 'skybox'}
    spank_option = 'edf'


@rfm.simple_test
class OMB_OMPI_Skybox(OMB_OMPI_CE):
    descr = '''
    OSU Micro-benchmarks for OpenMPI/CE/Skybox (Point-to-Point & All-to-All)
    '''
    tags = {'ce_dev', 'skybox'}
    spank_option = 'edf'
