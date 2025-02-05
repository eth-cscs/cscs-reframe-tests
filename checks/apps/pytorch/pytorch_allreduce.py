# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib
import sys
import subprocess

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))

from container_engine import ContainerEngineMixin  # noqa: E402

@rfm.simple_test
class PyTorchNCCLAllReduce(rfm.RunOnlyRegressionTest, ContainerEngineMixin):
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['builtin']
    sourcesdir = None
    num_nodes = parameter([8], loggable=True) # 32 ranks
    sourcesdir = 'src'
    # sizes = list(range(15,32))
    sizes = [32] # Message size is 16GB
    size = parameter(sizes, loggable=True)
    aws_ofi_nccl = parameter([True])
    image = parameter([
        'nvcr.io#nvidia/pytorch:24.01-py3',
    ])

    env_vars = {
        'NCCL_DEBUG': 'Info',
    }
    tags = {'ml'}
    all_ref = {
        'sm_80':
            {'*':
                {'GB/s': (91.04, -0.05, None, 'GB/s')}
            }, # Taken from NCCLTest
        'sm_90':
            {'*':
                {'GB/s': (91.04, -0.05, None, 'GB/s')}
            }, # Taken from NCCLTest
    }

    @run_after('init')
    def set_image(self):
        self.container_image = self.image
        if self.aws_ofi_nccl:
            cuda_major = 'cuda12' if self.image > 'nvcr.io#nvidia/pytorch:23' else 'cuda11'
            self.container_env_table = {
                'annotations.com.hooks': {
                    'cxi.enabled': 'true',
                    'aws_ofi_nccl.enabled': 'true',
                    'aws_ofi_nccl.variant': cuda_major,
                },
            }

    @run_after('setup')
    def setup_test(self):
        curr_part = self.current_partition
        self.num_gpus_per_node = curr_part.select_devices('gpu')[0].num_devices
        self.num_tasks_per_node = 1
        self.num_tasks = self.num_nodes
        self.job.options = ['--gpus-per-task=4']
        self.executable = 'python -u -m torch.distributed.run ' + \
                          f'--nproc_per_node={self.num_gpus_per_node} ' + \
                          f'--nnodes={self.num_nodes} ' + \
                          '--rdzv_endpoint $(scontrol show hostnames $SLURM_JOB_NODELIST | head -n 1):6000 ' + \
                          '--rdzv_backend c10d ' + \
                          'all_reduce.py'

    @run_after('setup')
    def set_executable_opts(self):
        self.executable_opts = [
            f'{self.size}'
        ]

    @sanity_function
    def assert_sanity(self):
        return sn.assert_found(r'The average bandwidth of all_reduce', self.stdout)

    @run_before('performance')
    def set_perf(self):
        self.perf_patterns = {
            'GB/s': sn.extractsingle(
                r'busbw:\s+(\d+.\d+)GBps',
                self.stdout, tag=1, conv=float)
        }
        partition = self.current_partition
        gpu_arch = partition.select_devices('gpu')[0].arch
        self.reference = self.all_ref[gpu_arch]
