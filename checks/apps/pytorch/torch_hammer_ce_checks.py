# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))
from container_engine import ContainerEngineMixin  # noqa: E402


class TorchHammerBase(rfm.RunOnlyRegressionTest):
    descr = 'Base class for all Torch Hammer benchmarks'
    sourcesdir = None
    script = variable(str, value='torch-hammer.py')
    repo = variable(
        str,
        value='https://raw.githubusercontent.com/HPE/torch-hammer')
    device_index = variable(int, value=0)
    warmup = variable(int, value=10)
    duration = variable(int, value=60)  # seconds

    @run_after('setup')
    def setup_code(self):
        self.prerun_cmds = [
            f'wget --quiet {self.repo}/refs/heads/main/{self.script}',
            f'chmod +x {self.script}'
        ]

    @run_before('run')
    def set_executable(self):
        self.executable = self.script
        self.executable_opts = [
            f'--device-index={self.device_index}',
            f'--warmup={self.warmup}',
        ]
        if self.duration > 0:
            self.executable_opts.append(f'--duration={self.duration}')
            self.time_limit = int(self.duration * 2.5)


@rfm.simple_test
class TorchHammerCEMultiGPU(TorchHammerBase, ContainerEngineMixin):
    descr = 'Torch Hammer CE Multi-GPU Benchmark'
    valid_systems = ['+ce +nvgpu']
    valid_prog_environs = ['builtin']
    tags = {'gpu', 'multi-gpu', 'parallel', 'production'}
    maintainers = ['VCUE']
    pytorch_version = variable(str, value='26.05-py3')

    @run_after('init')
    def set_container_image(self):
        self.container_image = f'nvcr.io#nvidia/pytorch:{self.pytorch_version}'
        self.container_env_table = {
            'annotations.com.hooks': {
                    'aws_ofi_nccl.enabled': 'true',
                    'aws_ofi_nccl.variant': 'cuda13',
            },
        }

    @run_before('run')
    def set_multigpu_test(self):
        # Remove single --device-index
        self.executable_opts = [
            opt for opt in self.executable_opts
            if not opt.startswith('--device-index')
        ]

        # Add multi-GPU options
        self.num_gpus = \
            self.current_partition.select_devices('gpu')[0].num_devices
        gpu_list = ','.join(str(i) for i in range(self.num_gpus))
        self.executable_opts.extend([
            f'--gpu-list={gpu_list}', '--batched-gemm', '--cpu-affinity',
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
