# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class CoralGemm(rfm.RunOnlyRegressionTest):
    valid_systems = ['+amdgpu']
    valid_prog_environs = ['+rocm']
    build_system = 'CMake'

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
    batch_count = variable(int, value=10)

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

    sourcesdir = 'https://github.com/AMD-HPC/CoralGemm.git'
    num_tasks_per_node = 1
    # num_gpus = 4

    @run_after('setup')
    def set_num_gpus(self):
        curr_part = self.current_partition
        self.num_gpus = curr_part.select_devices('gpu')[0].num_devices

    @run_before('run')
    def set_executable(self):
        # Set mandatory arguments of the benchmark
        self.executable = (
            './gemm '
            f'{self.precision_A} '
            f'{self.precision_B} '
            f'{self.precision_C} '
            f'{self.compute_precision} '
            f'{self.op_A} '
            f'{self.op_B} '
            f'{self.M} '
            f'{self.N} '
            f'{self.K} '
            f'{self.lda} '
            f'{self.ldb} '
            f'{self.ldc} '
            f'{self.batch_count} '
            f'{self.duration}'
        )

        # Set optional arguments of the benchmark
        if self.batched:
            self.executable += ' batched'

        if self.strided:
            self.executable += ' strided'

        if self.ex_api:
            self.executable += ' ex'

        if self.hipBLASLt_api:
            self.executable += ' lt'

        if self.host_A:
            self.executable += ' hostA'

        if self.host_B:
            self.executable += ' hostB'

        if self.host_C:
            self.executable += ' hostC'

        if self.coherent_A:
            self.executable += ' coherentA'

        if self.coherent_B:
            self.executable += ' coherentB'

        if self.coherent_C:
            self.executable += ' coherentC'

        if self.shared_A:
            self.executable += ' sharedA'

        if self.shared_B:
            self.executable += ' sharedB'

        if self.zero_beta:
            self.executable += ' zeroBeta'

        # Set the time limit with a padding of 2 minutes
        self.time_limit = self.duration + 120

    @sanity_function
    def assert_results(self):
        # The binary automatically launches on all available GPUs
        # simultaneously, so we check that the output contains performance
        # results for all GPUs.
        s1 = sn.all([
            sn.assert_found(rf'device_{i}_\[GFLOPS\]', self.stdout) for i in range(self.num_gpus)
        ])

        # We also check that the output does not contain more GPUs than
        # the expected number. In case of misconfiguration, the node can
        # appear to have more GPUs than it actually has, with lower
        # performance.
        s2 = sn.assert_not_found(rf'device_{self.num_gpus+1}', self.stdout)

        return sn.all([s1, s2])

    @performance_function('GFlops')
    def min_gflops(self):
        regex = r'^'
        # We get one column per GPU and one for the timestamp
        regex += ''.join(r'\s*(\d+.\d+)' for i in range(self.num_gpus + 1))
        regex += r'\s*$'
        return sn.min(
            sn.min(
                sn.extractall(regex, self.stdout, i+1, float)
            ) for i in range(self.num_gpus)
        )
