# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps
from uenv import uarch


@rfm.simple_test
class FFTBenchBuild(rfm.CompileOnlyRegressionTest):
    descr = 'Build FFT benchmark'
    maintainers = ['AdhocMan', 'SSA']
    sourcesdir = None
    valid_systems = ['+uenv +amdgpu', '+uenv +nvgpu']
    valid_prog_environs = ['+uenv +prgenv +rocm', '+uenv +prgenv +cuda']
    build_system = 'CMake'
    prebuild_cmds = [
        'git clone --depth 1 -b reframe-ci '
        'https://github.com/eth-cscs/gpu-benchmarks.git'
    ]
    time_limit = '4m'
    build_locally = False
    tags = {'production', 'uenv'}

    @run_before('compile')
    def prepare_build(self):
        srcdir = f'gpu-benchmarks/fft'
        self.build_system.srcdir = srcdir
        self.build_system.builddir = f'build'
        self.prebuild_cmds += [f'cd {self.build_system.srcdir}']
        self.build_system.max_concurrency = 8
        self.executable = os.path.join(
            self.stagedir, srcdir, self.build_system.builddir, 'fft_bench'
        )

        if 'rocm' in self.current_environ.features:
            self.build_system.config_opts = [
                '-DFFT_BENCH_GPU_BACKEND=ROCM',
            ]
        else:
            self.build_system.config_opts = [
                '-DFFT_BENCH_GPU_BACKEND=CUDA',
            ]

    @sanity_function
    def validate_test(self):
        return os.path.isfile(self.executable)


@rfm.simple_test
class FFTCheck(rfm.RunOnlyRegressionTest):
    maintainers = ['AdhocMan', 'SSA']
    valid_systems = ['+uenv +amdgpu', '+uenv +nvgpu']
    valid_prog_environs = ['+uenv +prgenv +rocm', '+uenv +prgenv +cuda']
    time_limit = '4m'
    tags = {'production', 'uenv', 'bencher'}

    fft_dim = parameter(['1D', '2D', '3D'])
    fft_size = parameter([128, 256, 512, 1024])

    # runtime values in ms
    reference_timings = {
        '1D': {
            'mi200': {'128': 0.179489, '256':  0.333746, '512': 0.667365, '1024': 1.33991},  # noqa: E501
            'mi300': {'128': 0.0726874, '256': 0.210958, '512': 0.32853, '1024': 0.601683},  # noqa: E501
            'gh200': {'128': 0.0606304, '256': 0.117171, '512': 0.228963, '1024': 0.459949},  # noqa: E501
        },
        '2D': {
            'mi200': {'128': 0.432062, '256': 1.86332, '512': 8.9016, '1024': 54.3387},  # noqa: E501
            'mi300': {'128': 0.180459, '256': 0.879223, '512': 3.80603, '1024': 23.7081},  # noqa: E501
            'gh200': {'128': 0.155469, '256': 0.58984, '512': 2.32393, '1024': 10.7417},  # noqa: E501
        },
        '3D': {
            'mi200': {'128': 0.23045, '256': 1.7439, '512': 16.0939, '1024': 161.762},  # noqa: E501
            'mi300': {'128': 0.0794162, '256': 0.673843, '512': 5.85871, '1024': 75.8344},  # noqa: E501
            'gh200': {'128': 0.0550848, '256': 0.472509, '512': 3.68538, '1024': 36.0022},  # noqa: E501
        }
    }

    # Batch size to use in each dimension
    batch_sizes = {
        '1D': 50000,
        '2D': 500,
        '3D': 1,
    }

    # convert time in ms to bandwith in TB/s
    def runtime_to_bandwidth(self, time):
        # estimate total size with 16 bytes per element and
        # 1 / 2 / 3 reads per element depending on dimension
        read_bytes = self.fft_size * 16.0
        if self.fft_dim == '2D':
            read_bytes *= self.fft_size * 2.0

        if self.fft_dim == '3D':
            read_bytes *= self.fft_size * self.fft_size * 3.0

        read_bytes *= self.batch_sizes[self.fft_dim]

        return read_bytes / (time * 1e-3) / 1e12

    @run_after('init')
    def setup_dependency(self):
        self.depends_on('FFTBenchBuild', udeps.fully)

    @run_before('run')
    def set_executable(self):
        parent = self.getdep('FFTBenchBuild')
        self.executable = parent.executable
        size_arg = f'{self.fft_size}'
        if self.fft_dim == '2D':
            size_arg += f' {self.fft_size}'
        if self.fft_dim == '3D':
            size_arg += f' {self.fft_size} {self.fft_size}'
        self.executable_opts = [
            f'-b {self.batch_sizes[self.fft_dim]}',
            '-p double',
            '-s 10',
            f'-n {size_arg}'
        ]

    @sanity_function
    def assert_reference(self):
        return sn.assert_found(r'Mean time', self.stdout)

    @run_before('performance')
    def set_perf_vars(self):
        make_perf = sn.make_performance_function
        runtime = sn.extractsingle(
            r'Mean time \[ms\]: (?P<time>\S+)', self.stdout, 'time', float)
        bandwidth = self.runtime_to_bandwidth(runtime)

        self.perf_variables = {
            'bandwidth': make_perf(bandwidth, 'TB/s'),
        }

    @run_before('performance')
    def set_references(self):
        self.uarch = uarch(self.current_partition)

        runtime = self.reference_timings.get(self.fft_dim, {}).get(self.uarch, {}).get(str(self.fft_size))  # noqa: E501

        if runtime is not None:
            bandwidth = self.runtime_to_bandwidth(runtime)
            self.reference = {
                self.current_partition.fullname:
                {
                    'bandwidth': (bandwidth, -0.2, None, 'TB/s'),
                }
            }
