# Copyright 2025 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))

from container_engine import ContainerEngineMixin  # noqa: E402


@rfm.simple_test
class PyTorchNCCLAllReduce(rfm.RunOnlyRegressionTest, ContainerEngineMixin):
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['builtin']
    num_nodes = variable(int, value=8)
    sourcesdir = None
    image = parameter(['nvcr.io#nvidia/pytorch:25.01-py3'])
    env_vars = {
        'NCCL_DEBUG': 'Info',
    }
    tags = {'ml'}
    all_ref = {
        'sm_90':
            {'*':
                {'GB/s': (91.04, -0.05, None, 'GB/s')}
            },
    }

    @run_after('init')
    def set_image(self):
        self.container_image = self.image
        self.container_env_table = {
            'annotations.com.hooks': {
                    'aws_ofi_nccl.enabled': 'true',
                    'aws_ofi_nccl.variant': 'cuda12',
            },
       }

    @run_after('setup')
    def setup_test(self):
        curr_part = self.current_partition
        self.num_gpus_per_node = curr_part.select_devices('gpu')[0].num_devices
        self.num_tasks_per_node = 1
        self.num_tasks = self.num_nodes
        self.job.options = [f'--gpus-per-task={self.num_gpus_per_node}']
        self.num_cpus_per_task = curr_part.processor.num_cpus
        self.env_vars['OMP_NUM_THREADS'] = (self.num_cpus_per_task //
                                            self.num_gpus_per_node)
        self.executable = 'python'

    @run_after('setup')
    def set_executable_opts(self):
        self.prerun_cmds = ['wget https://raw.githubusercontent.com/stas00/ml-engineering/179e37865157c526b7f80b258b448caab4953247/network/benchmarks/all_reduce_bench.py'] # noqa: E501
        headnode_cmd = (
            '$(scontrol show hostnames $SLURM_JOB_NODELIST | head -n 1)'
        )
        self.executable_opts = [
            f'-u', f'-m', f'torch.distributed.run',
            f'--nproc_per_node={self.num_gpus_per_node}',
            f'--nnodes={self.num_nodes}',
            f'--rdzv_endpoint {headnode_cmd}:6000',
            f'--rdzv_backend c10d',
            f'all_reduce_bench.py',
        ]

    @sanity_function
    def assert_sanity(self):
        return sn.assert_found(
            r'The average bandwidth of all_reduce', self.stdout
        )

    @run_before('performance')
    def set_perf(self):
        self.perf_patterns = {
            'GB/s': sn.extractsingle(
                r'\|\s*16GiB\s*\|\s*(?P<busbw>\S+)GBps\s*\|',
                self.stdout, tag='busbw', conv=float
            )
        }
        partition = self.current_partition
        gpu_arch = partition.select_devices('gpu')[0].arch
        self.reference = self.all_ref[gpu_arch]
