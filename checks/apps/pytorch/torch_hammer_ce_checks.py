#!/usr/bin/env python3
"""
ReFrame regression tests for Torch Hammer GPU benchmarks.

This module provides ReFrame-compatible tests wrapping torch-hammer.py
for HPC system validation and performance regression testing.

Usage:
    reframe -c reframe/torch_hammer_checks.py -r

Configuration:
    Set valid_systems and valid_prog_environs in your ReFrame config
    to match your HPC system partitions and programming environments.
"""
import pathlib
import re  # noqa: F401
import sys

import os
import reframe as rfm
from reframe.core.builtins import run_after
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))

from container_engine import ContainerEngineMixin  # noqa: E402

class TorchHammerBase(rfm.RunOnlyRegressionTest):
    """Base class for all Torch Hammer benchmarks."""
    
    # Override these in your site config
    valid_systems = ['*']
    valid_prog_environs = ['*']
    
    # Common settings
    num_gpus_per_node = 1
    time_limit = '30m'
    
    # Torch Hammer script location (relative to test file)
    torch_hammer_script = variable(str, value='torch-hammer.py')
    
    # Common benchmark parameters
    duration = variable(int, value=60)  # seconds
    warmup = variable(int, value=10)
    
    # Device selection
    device_index = variable(int, value=0)
    
    @run_before('run')
    def set_executable(self):
        """Set up the torch-hammer executable and common options."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.executable = f'python3 {os.path.join(script_dir, self.torch_hammer_script)}'

        # Common options
        self.executable_opts = [
            f'--device-index={self.device_index}',
            f'--warmup={self.warmup}',
        ]
        
        # Add duration if specified
        if self.duration > 0:
            self.executable_opts.append(f'--duration={self.duration}')
    
    @sanity_function
    def validate_run(self):
        """Validate that the benchmark completed successfully."""
        return sn.assert_found(r'\[OK\] Benchmark run finished', self.stdout)

# ============================================================================
# CE MULTI-GPU BENCHMARK
# ============================================================================
@rfm.simple_test
class TorchHammerCEMultiGPU(TorchHammerBase, ContainerEngineMixin):
    """Multi-GPU CE parallel benchmark."""
    
    descr = 'Torch Hammer CE Multi-GPU Benchmark'
    tags = {'gpu', 'multi-gpu', 'parallel'}
    
    num_gpus = variable(int, value=4)
    time_limit = '10m'
    valid_prog_environs = ['builtin']
    
    @run_after('init')
    def set_image(self):
        self.container_image = 'nvcr.io#nvidia/pytorch:25.06-py3'
        self.container_env_table = {
            'annotations.com.hooks': {
                    'aws_ofi_nccl.enabled': 'true',
                    'aws_ofi_nccl.variant': 'cuda12',
            },
        }

    @run_after('setup')
    def setup_test(self):
        self.prerun_cmds = ['wget https://raw.githubusercontent.com/HPE/torch-hammer/refs/heads/main/torch-hammer.py ']  

    @run_before('run')
    def set_multi_gpu_options(self):
        """Configure for multi-GPU execution."""
        self.executable = f'python3 {self.torch_hammer_script}'

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
    def validate_multi_gpu(self):
        """Validate all GPUs completed."""
        # Check that we see output from all GPUs
        checks = [
            #sn.assert_found(rf'\[GPU{i}\]', self.stdout) 
            sn.assert_found(rf'\[OK] Benchmark run finished on GPU{i}', self.stdout)
            for i in range(self.num_gpus)
        ]
        return sn.all(checks)
