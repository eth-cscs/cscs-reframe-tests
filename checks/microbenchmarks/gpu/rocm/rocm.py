# Copyright 2025 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import pathlib
import sys
import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class AmdGPUBenchmarks(rfm.RegressionTest):
    '''
    This test runs amd-gpu-benchmarks
    '''
    valid_prog_environs = ['+rocm']
    valid_systems = ['+remote']
    benchmark = parameter(['rocPRISM'])
    build_system = 'CMake'
    sourcesdir = 'https://github.com/eth-cscs/amd-gpu-benchmarks.git'
    time_limit = '2m'
    build_locally = False
    # env_vars = {'MPICH_GPU_SUPPORT_ENABLED': 0}
    tags = {'production', 'uenv'}

    @run_before('compile')
    def prepare_build(self):
        self.build_system.builddir = 'build'
        self.prebuild_cmds = [f'ln -fs {self.benchmark}/* .', 'pwd']
        self.build_system.config_opts = [
            f'-DWITH_CUDA=OFF',
            f'-DWITH_HIP=ON',
            f'-DCMAKE_HIP_ARCHITECTURES="gfx90a;gfx942"'
        ]

    @run_before('run')
    def set_executable(self):
        exe = {
            'rocPRISM': 'radix-sort'
        }
        self.executable = f'{self.build_system.builddir}/{exe[self.benchmark]}'

    @run_before('sanity')
    def set_sanity(self):
        self.sanity_patterns = sn.all([
            sn.assert_found(r'radix sort time.*MiB/s', self.stdout)
        ])
