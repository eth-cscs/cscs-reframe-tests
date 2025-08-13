# Copyright 2025 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


class AmdGPUBenchmarks(rfm.RegressionTest):
    '''
    Base class for amd-gpu-benchmarks
    '''
    sourcesdir = 'https://github.com/eth-cscs/amd-gpu-benchmarks.git'
    valid_prog_environs = ['+rocm', '+cuda']
    valid_systems = ['+remote']
    build_system = 'CMake'
    time_limit = '2m'
    build_locally = False
    tags = {'production', 'uenv'}


@rfm.simple_test
class rocPRISM(AmdGPUBenchmarks):
    benchmark = 'rocPRISM'
    # _executable_opts = parameter(['6', '12', '27'])
    _executable_opts = parameter(['6'])

    @run_before('compile')
    def prepare_build(self):
        self.build_system.builddir = 'build'
        self.prebuild_cmds = [f'ln -fs {self.benchmark}/* .', 'pwd']
        gpu_arch = self.current_partition.select_devices('gpu')[0].arch
        if 'rocm' in self.current_environ.features:
            self.build_system.config_opts = [
                '-DWITH_CUDA=OFF',
                '-DWITH_HIP=ON',
                f'-DCMAKE_HIP_ARCHITECTURES="{gpu_arch}"'
            ]
        else:
            gpu_arch = (
                gpu_arch[len("sm_"):]
                if gpu_arch.startswith("sm_")
                else gpu_arch
            )
            self.build_system.config_opts = [
                '-DWITH_CUDA=ON',
                '-DWITH_HIP=OFF',
                f'-DCMAKE_CUDA_ARCHITECTURES="{gpu_arch}"'
            ]

    @run_before('run')
    def set_executable(self):
        self.executable = f'{self.build_system.builddir}/radix-sort'
        self.executable_opts = [self._executable_opts]

    @run_before('sanity')
    def set_sanity(self):
        regex = r'radix sort time for.*key-value pairs:.*s, bandwidth:.*MiB/s'
        self.sanity_patterns = sn.all([sn.assert_found(regex, self.stdout)])

    @run_before('performance')
    def set_perf_vars(self):
        make_perf = sn.make_performance_function

        regex = (
            r'radix sort time for (?P<keys>\S+) '
            r'key-value pairs: (?P<latency>\S+) s, '
            r'bandwidth: (?P<bandwidth>\S+) MiB/s'
        )
        keys = sn.extractsingle(regex, self.stdout, 'keys', int)
        latency = sn.extractsingle(regex, self.stdout, 'latency', float)
        bandwidth = sn.extractsingle(regex, self.stdout, 'bandwidth', float)

        self.perf_variables = {
            'latency': make_perf(latency, 's'),
            'bandwidth': make_perf(bandwidth, 'MiB/s'),
            'keys/second': make_perf((keys/latency)/1e9, 'Gkeys/s'),
        }
