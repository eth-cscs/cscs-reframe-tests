# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
from uenv import uarch


@rfm.simple_test
class CoralGemm(rfm.RegressionTest):
    descr = 'AMD CoralGemm test'
    valid_systems = ['+amdgpu +uenv']
    valid_prog_environs = ['+uenv +prgenv +rocm']
    maintainers = ['SSA']
    sourcesdir = None
    build_system = 'CMake'
    prebuild_cmds = [
        'git clone --depth 1 --branch 2025.11 '
        'https://github.com/AMD-HPC/CoralGemm.git'
    ]
    time_limit = '3m'
    build_locally = False
    num_tasks_per_node = 1
    tags = {'production', 'uenv', 'benchmark', 'bencher'}

    # Sweep matrix sizes and precisions
    # dimensions are in bytes for one dimension of a square matrix
    _size_bytes = parameter([12800, 25600, 51200, 128000])
    _precisions = parameter(['R_16B', 'R_32F', 'R_64F'])

    # Data precision for matrix A, B, C and computation
    precision_A = variable(str, value='R_64F')
    precision_B = variable(str, value='R_64F')
    precision_C = variable(str, value='R_64F')
    compute_precision = variable(str, value='R_64F')

    # Operation applied to matrix A and B, eg. OP_N, OP_T, OP_C
    op_A = variable(str, value='OP_N')
    op_B = variable(str, value='OP_T')

    # Matrix dimensions
    M = variable(int, value=9728)
    N = variable(int, value=6144)
    K = variable(int, value=8192)

    # Leading dimensions of matrix A, B, C
    lda = variable(int, value=9728)
    ldb = variable(int, value=6144)
    ldc = variable(int, value=9728)

    # Number of batched matrices
    batch_count = variable(int, value=1)

    # Duration to run the GEMM operation in seconds
    duration = variable(int, value=45)

    # Optional argument to run the extended version of the benchmark
    batched = variable(bool, value=False)
    strided = variable(bool, value=False)
    ex_api = variable(bool, value=False)
    hipBLASLt_api = variable(bool, value=False)

    # A, B, C matrices are stored in host memory
    host_A = variable(bool, value=False)
    host_B = variable(bool, value=False)
    host_C = variable(bool, value=False)

    # if in host memory, A/B/C is coherent (not cached)
    coherent_A = variable(bool, value=False)
    coherent_B = variable(bool, value=False)
    coherent_C = variable(bool, value=False)

    shared_A = variable(bool, value=False)
    shared_B = variable(bool, value=False)

    # set beta to zero
    zero_beta = variable(bool, value=False)

    @run_before('compile')
    def set_build_options(self):
        self.build_system.configuredir = 'CoralGemm'
        self.build_system.builddir = 'build'

        gpu_arch = self.current_partition.select_devices('gpu')[0].arch
        if 'rocm' in self.current_environ.features:
            self.build_system.config_opts = [
                '-DCMAKE_BUILD_TYPE=Release',
                '-DUSE_CUDA=OFF',
                '-DUSE_HIP=ON',
                f'-DCMAKE_HIP_ARCHITECTURES="{gpu_arch}"'
            ]
        else:  # cuda
            gpu_arch = (
                gpu_arch[len("sm_"):]
                if gpu_arch.startswith("sm_")
                else gpu_arch
            )
            self.build_system.config_opts = [
                '-DCMAKE_BUILD_TYPE=Release',
                '-DUSE_CUDA=ON',
                '-DUSE_HIP=OFF',
                f'-DCMAKE_CUDA_ARCHITECTURES="{gpu_arch}"'
            ]

    @run_after('setup')
    def set_num_gpus(self):
        curr_part = self.current_partition
        self.num_gpus = curr_part.select_devices('gpu')[0].num_devices

    @run_before('run')
    def set_executable(self):
        # Set mandatory arguments of the benchmark
        self.executable = os.path.join(self.build_system.builddir, 'gemm')

        # Data precision for matrix A, B, C and computation
        self.precision_A = self._precisions
        self.precision_B = self._precisions
        self.precision_C = self._precisions
        self.compute_precision = self._precisions

        if self.precision_A == 'R_16B':
            self.precision_C = 'R_32F'
            self.compute_precision = 'R_32F'

        # Adjust matrix sizes based on the current parameters
        if self.precision_C == 'R_32F':
            self.M = self._size_bytes // 4
            self.N = self._size_bytes // 4
            self.K = self._size_bytes // 4
        else:  # R_64F
            self.M = self._size_bytes // 8
            self.N = self._size_bytes // 8
            self.K = self._size_bytes // 8

        # Leading dimensions of matrix A, B, C
        self.lda = self.M
        self.ldb = self.N
        self.ldc = self.M

        self.executable_opts = [
            f'{self.precision_A} ',
            f'{self.precision_B} ',
            f'{self.precision_C} ',
            f'{self.compute_precision} ',
            f'{self.op_A} ',
            f'{self.op_B} ',
            f'{self.M} ',
            f'{self.N} ',
            f'{self.K} ',
            f'{self.lda} ',
            f'{self.ldb} ',
            f'{self.ldc} ',
            f'{self.batch_count} ',
            f'{self.duration}'
        ]

        # Fix option for BF16 precision
        if self._precisions == 'R_16B':
            self.executable_opts.append('ex')

        # Set optional arguments of the benchmark
        if self.batched:
            self.executable_opts.append('batched')

        if self.strided:
            self.executable_opts.append('strided')

        if self.ex_api:
            self.executable_opts.append('ex')

        if self.hipBLASLt_api:
            self.executable_opts.append('lt')

        if self.host_A:
            self.executable_opts.append('hostA')

        if self.host_B:
            self.executable_opts.append('hostB')

        if self.host_C:
            self.executable_opts.append('hostC')

        if self.coherent_A:
            self.executable_opts.append('coherentA')

        if self.coherent_B:
            self.executable_opts.append('coherentB')

        if self.coherent_C:
            self.executable_opts.append('coherentC')

        if self.shared_A:
            self.executable_opts.append('sharedA')

        if self.shared_B:
            self.executable_opts.append('sharedB')

        if self.zero_beta:
            self.executable_opts.append('zeroBeta')

        # Set the time limit with a padding of 2 minutes
        self.time_limit = self.duration + 120

    @sanity_function
    def assert_results(self):
        # The binary automatically launches on all available GPUs
        # simultaneously, so we check that the output contains performance
        # results for all GPUs.
        s1 = sn.all([
            sn.assert_found(rf'device_{i}_\[GFLOPS\]', self.stdout)
            for i in range(self.num_gpus)
        ])

        # We also check that the output does not contain more GPUs than
        # the expected number. In case of misconfiguration, the node can
        # appear to have more GPUs than it actually has, with lower
        # performance.
        s2 = sn.assert_not_found(rf'device_{self.num_gpus+1}', self.stdout)

        return sn.all([s1, s2])

    @sn.deferrable
    def extract_gflops(self, func=sn.min):
        regex = r'^'
        # We get one column per GPU and one for the timestamp
        regex += ''.join(r'\s*(\d+.\d+)' for i in range(self.num_gpus + 1))
        regex += r'\s*\S+$'
        gflops = func(
            func(
                sn.extractall(regex, self.stdout, i+1, float)
            ) for i in range(self.num_gpus)
        )
        return gflops

    @run_before('performance')
    def set_perf_vars(self):
        make_perf = sn.make_performance_function

        self.perf_variables = {
            'min_gflops': make_perf(self.extract_gflops(sn.min), 'GFlops'),
            'max_gflops': make_perf(self.extract_gflops(sn.max), 'GFlops'),
            'avg_gflops': make_perf(self.extract_gflops(sn.avg), 'GFlops')
        }

    @run_before('performance')
    def set_references(self):
        self.uarch = uarch(self.current_partition)
        ref_flops = (
            self._ref_flops.get(self.uarch, {})
            .get(self._precisions, {})
            .get(self._size_bytes, None)
        )
        if ref_flops is not None:
            self.reference = {
                self.current_partition.fullname: {
                    'avg_gflops': (ref_flops, -0.1, 0.1, 'GFlops')
                }
            }

    _ref_flops = {
        # These are the average GFLOPS observed on the respective systems,
        # sizes are in bytes.
        'mi200': {
            'R_16B': {12800: 92955, 25600: 108550, 51200: 119803, 128000: 87451},
            'R_32F': {12800: 31598, 25600: 30690, 51200: 32907, 128000: 28638},
            'R_64F': {12800: 19102, 25600: 23178, 51200: 26740, 128000: 23870}
        },
        'mi300': {
            'R_16B': {12800: 230008, 25600: 428416, 51200: 389497, 128000: 273200},
            'R_32F': {12800: 64777, 25600: 74340, 51200: 80478, 128000: 67092},
            'R_64F': {12800: 25702, 25600: 52668, 51200: 60874, 128000: 53913}
        },
        'gh200': {
            'R_16B': {12800: 548292, 25600: 570109, 51200: 574525, 128000: 599912},
            'R_32F': {12800: 47849, 25600: 50990, 51200: 52200, 128000: 51011},
            'R_64F': {12800: 42362, 25600: 40700, 51200: 39845, 128000: 51717}
        },
    }
