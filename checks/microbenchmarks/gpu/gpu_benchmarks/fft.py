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
    '''
    Build FFT benchmark
    '''
    maintainers = ['SSA']
    sourcesdir = None
    valid_prog_environs = ['+uenv +prgenv +rocm', '+uenv +prgenv +cuda']
    valid_systems = ['+uenv']
    build_system = 'CMake'
    prebuild_cmds = [
        'git clone --depth 1 -b rocfft https://github.com/AdhocMan/gpu-benchmarks.git'
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
    maintainers = ['SSA']
    valid_prog_environs = ['+uenv +prgenv +rocm', '+uenv +prgenv +cuda']
    valid_systems = ['+uenv']
    time_limit = '4m'
    tags = {'production', 'uenv'}

    fft_dim = parameter(['1D', '2D', '3D'])
    fft_size = parameter([128, 256, 512, 1024])

    # runtime values in ms
    reference_timings = {
        '1D': {
            'mi200': {'128': 0.0413282, '256':  0.0816478, '512': 0.137825, '1024': 0.275295},
            'mi300': {'128': 0.016324, '256': 0.0484761, '512': 0.0618052, '1024': 0.158051 },
            'gh200': {'128': 0.0112, '256': 0.02696, '512': 0.050016, '1024': 0.0973504},
        },
        '2D': {
            'mi200': {'128': 0.0989124, '256': 0.403151, '512': 1.79282, '1024': 10.8999},
            'mi300': {'128': 0.0419043, '256': 0.195893, '512': 0.817081, '1024': 5.01644},
            'gh200': {'128': 0.0314304, '256': 0.127504, '512': 0.476746, '1024': 2.10344},
        },
        '3D': {
            'mi200': {'128': 0.23045, '256': 1.7439, '512': 16.0939, '1024': 161.762},
            'mi300': {'128': 0.0794162, '256': 0.673843, '512': 5.85871, '1024': 75.8344},
            'gh200': {'128': 0.0550848, '256': 0.472509, '512': 3.68538, '1024': 36.0022},
        }
    }

    # Batch size to use in each dimension. 
    batch_sizes = {
        '1D': 10000,
        '2D': 100,
        '3D': 1,
    }

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
        self.executable_opts = [f'-b {self.batch_sizes[self.fft_dim]}', '-p double', '-s 10', f'-n {size_arg}']

    @sanity_function
    def assert_reference(self):
        return sn.assert_found(r'Mean time', self.stdout)

    @run_before('performance')
    def set_perf_vars(self):
        make_perf = sn.make_performance_function
        runtime = sn.extractsingle('Mean time \[ms\]: (?P<time>\S+)', self.stdout, 'time', float)

        self.perf_variables = {
            'runtime': make_perf(runtime, 'ms'),
        }

    @run_before('performance')
    def set_references(self):
        self.uarch = uarch(self.current_partition)

        self.reference = {
            self.current_partition.fullname:
            {
                'runtime': (self.reference_timings[self.fft_dim][self.uarch][str(self.fft_size)], None, 0.1, 'ms'),
            }
        }

