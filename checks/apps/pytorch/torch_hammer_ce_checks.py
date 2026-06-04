# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os  # del
import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))
from container_engine import ContainerEngineMixin  # noqa: E402


class TorchHammerBase(rfm.RunOnlyRegressionTest):
    descr = 'Base class for all Torch Hammer benchmarks'
    sourcesdir = None
    # valid_systems = ['*']
    # valid_prog_environs = ['*']
    # num_gpus_per_node = 1
    # time_limit = '30m'
    torch_hammer_script = variable(str, value='torch-hammer.py')

    repo = variable(
        str,
        value='https://raw.githubusercontent.com/HPE/torch-hammer')
    device_index = variable(int, value=0)
    warmup = variable(int, value=10)
    duration = variable(int, value=60)  # seconds

    @run_after('setup')
    def setup_code(self):
        self.prerun_cmds = [
            f'wget --quiet {self.repo}/refs/heads/main/torch-hammer.py',
            f'chmod +x torch-hammer.py'
        ]

    @run_before('run')
    def set_executable(self):
        # script_dir = os.path.dirname(os.path.abspath(__file__))
        self.executable = self.torch_hammer_script
        self.executable_opts = [
            f'--device-index={self.device_index}',
            f'--warmup={self.warmup}',
        ]
        if self.duration > 0:
            self.executable_opts.append(f'--duration={self.duration}')
            self.time_limit = self.duration

#todo     @sanity_function
#todo     def validate_run(self):
#todo         return sn.assert_found(r'\[OK\] Benchmark run finished', self.stdout)


@rfm.simple_test
class TorchHammerCEMultiGPU(TorchHammerBase, ContainerEngineMixin):
    descr = 'Torch Hammer CE Multi-GPU Benchmark'
    valid_systems = ['+ce +nvgpu']
    valid_prog_environs = ['builtin']
    tags = {'gpu', 'multi-gpu', 'parallel', 'production'}
    maintainers = ['VCUE']
    num_gpus = variable(int, value=4)
    time_limit = '4m'

    @run_after('init')
    def set_container_image(self):
        self.container_image = 'nvcr.io#nvidia/pytorch:25.06-py3'
        self.container_env_table = {
            'annotations.com.hooks': {
                    'aws_ofi_nccl.enabled': 'true',
                    'aws_ofi_nccl.variant': 'cuda12',
            },
        }

    @run_before('run')
    def set_multigpu_test(self):
        # self.executable = f'python3 {self.torch_hammer_script}'

        # Remove single device index
        self.executable_opts = [
            opt for opt in self.executable_opts
            if not opt.startswith('--device-index')
        ]

        # Add multi-GPU options
        gpu_list = ','.join(str(i) for i in range(self.num_gpus))
        self.executable_opts.extend([
            f'--gpu-list={gpu_list}',
            '--batched-gemm',
            '--cpu-affinity',
        ])

    @sanity_function
    def validate_test(self):
        sanity_checks = [
            sn.assert_found(rf'\[OK] Benchmark run finished on GPU{ii}',
                            self.stdout)
            for ii in range(self.num_gpus)
        ]

        return sn.all(sanity_checks)

    @performance_function('GFLOP/s')
    def torch_hammer_ce_gflops(self):
        regex = r'^.*\s+Aggregate: (?P<flops>\S+) GFLOP\/s across \d+ GPUs'
        return sn.extractsingle(regex, self.stdout, 'flops', float)
