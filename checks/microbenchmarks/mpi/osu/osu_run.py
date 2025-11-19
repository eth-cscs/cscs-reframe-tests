# Copyright 2016 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.parent / 'mixins'))
from uenv_slurm_mpi_options import UenvSlurmMpiOptionsMixin


class BaseCheck(rfm.RunOnlyRegressionTest, UenvSlurmMpiOptionsMixin):
    valid_systems = ['+remote']
    valid_prog_environs = ['+osu-micro-benchmarks +uenv']
    sourcesdir = None
    num_tasks = 2
    num_tasks_per_node = 1
    env_vars = {
        # Disable GPU support for mpich
        'MPIR_CVAR_ENABLE_GPU': 0,

        # Disable GPU support for cray-mpich
        'MPICH_GPU_SUPPORT_ENABLED': 0,

        # Set to one byte more than the last entry of the test (for mpich)
        'MPIR_CVAR_CH4_OFI_MULTI_NIC_STRIPING_THRESHOLD': 4194305
    }
    tags = {'uenv'}

    @run_after('init')
    def set_descr(self):
        self.descr = f'{self.name} on {self.num_tasks} nodes(s)'

    @run_after('setup')
    def prepare_test(self):
        self.skip_if_no_procinfo()

        # Use a single socket per node (num_tasks_per_node == 1)
        processor = self.current_partition.processor
        self.num_cpus_per_task = processor.num_cpus_per_socket

    @sanity_function
    def assert_sanity(self):
        # Only check for the last entry in the latency test,
        # if exists program completed successfully
        return sn.assert_found(r'4194304', self.stdout)


@rfm.simple_test
class OSULatency(BaseCheck):
    reference = {
        '*': {
            'latency_256': (2.3, None, 0.60, 'us'),
            'latency_4M':  (180., None, 0.15, 'us')
        },
    }
    executable = 'osu_latency'

    @run_before('performance')
    def set_perf(self):
        self.perf_patterns = {
            'latency_256': sn.extractsingle(r'256\s+(?P<latency_256>\S+)',
                                            self.stdout, 'latency_256', float),
            'latency_4M': sn.extractsingle(r'4194304\s+(?P<latency_4M>\S+)',
                                           self.stdout, 'latency_4M', float)
        }

@rfm.simple_test
class OSUBandwidth(BaseCheck):
    executable = 'osu_bw'
    reference = {
        '*': {
            'bandwidth_256': (600., -0.50, None, 'MB/s'),
            'bandwidth_4M':  (24000., -0.15, None, 'MB/s')
        },
    }

    @run_before('performance')
    def set_perf(self):
        # For performance we only evaluate two points of output
        self.perf_patterns = {
            'bandwidth_256':
                sn.extractsingle(r'256\s+(?P<bandwidth_256>\S+)', self.stdout,
                                 'bandwidth_256', float),
            'bandwidth_4M':
                sn.extractsingle(r'4194304\s+(?P<bandwidth_4M>\S+)',
                                 self.stdout, 'bandwidth_4M', float)
        }


class OSUCuda(rfm.RegressionMixin):
    @run_after('init')
    def setup_test(self):
        self.valid_systems = ['+remote +nvgpu']
        self.valid_prog_environs = ['+osu-micro-benchmarks +cuda +uenv']
        self.env_vars = {
            # Enable GPU support for mpich
            'MPIR_CVAR_ENABLE_GPU': 1,

            # Enable GPU support for cray-mpich
            'MPICH_GPU_SUPPORT_ENABLED': 1,

            # Use only the first CUDA GPU
            'CUDA_VISIBLE_DEVICES': 0,

            # Set to one byte more than the last entry of the test (for mpich)
            'MPIR_CVAR_CH4_OFI_MULTI_NIC_STRIPING_THRESHOLD': 4194305,

            # This is needed otherwise the test hangs
            'LD_LIBRARY_PATH': '${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}'
        }
        self.executable_opts = ['-d', 'cuda', 'D', 'D']


@rfm.simple_test
class OSUBandwidthCuda(OSUCuda, OSUBandwidth):
    reference = {
        '*': {
            'bandwidth_256': (200., -0.15, None, 'MB/s'),
            'bandwidth_4M':  (24000., -0.15, None, 'MB/s')
        },
    }


@rfm.simple_test
class OSULatencyCuda(OSUCuda, OSULatency):
    reference = {
        '*': {
            'latency_256': (3.75, None, 0.15, 'us'),
            'latency_4M':  (180., None, 0.15, 'us')
        },
    }
