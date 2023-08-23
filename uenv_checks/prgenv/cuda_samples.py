# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class CudaSamplesTest(rfm.RegressionTest):
    sample = parameter([
        'concurrentKernels', 'deviceQuery', 'bandwidthTest', 'simpleCUBLAS',
        'conjugateGradientCudaGraphs'
    ])
    sample_dir = {
        'concurrentKernels': '0_Introduction',
        'deviceQuery': '1_Utilities',
        'bandwidthTest': '1_Utilities',
        'simpleCUBLAS': '4_CUDA_Libraries',
        'conjugateGradientCudaGraphs': '4_CUDA_Libraries'
    }
    env_vars = {
        'LD_LIBRARY_PATH': '$CUDA_HOME/lib64:$LD_LIBRARY_PATH'
    }
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['+cuda']
    sourcesdir = 'https://github.com/NVIDIA/cuda-samples.git'
    build_system = 'Make'
    build_locally = False

    @run_after('init')
    def set_descr(self):
        self.descr = f'CUDA {self.sample} test'

    @run_before('compile')
    def set_build_options(self):
        # Remove the `sm_` prefix from the cuda arch
        gpu_arch = self.current_partition.select_devices('gpu')[0].arch[3:]
        self.build_system.options = [
            f'SMS="{gpu_arch}"', f'CUDA_PATH=$CUDA_HOME'
        ]

        self.prebuild_cmds = [
            # Retrieve the Cuda version from the nvcc compiler
            rf"export CUDA_VER=v$(nvcc -V | "
            rf"sed -n 's/^.*release \([[:digit:]]*\.[[[:digit:]]\).*$/\1/p')",
            rf"git checkout ${{CUDA_VER}}",
            rf"cd Samples/{self.sample_dir[self.sample]}/{self.sample}"
        ]

    @run_before('run')
    def set_executable(self):
        self.executable = (f'Samples/{self.sample_dir[self.sample]}/'
                           f'{self.sample}/{self.sample}')

    @run_before('sanity')
    def set_sanity_patterns(self):
        output_patterns = {
            'concurrentKernels': r'Test passed',
            'deviceQuery': r'Result = PASS',
            'bandwidthTest': r'Result = PASS',
            'simpleCUBLAS': r'test passed',
            'conjugateGradientCudaGraphs':
                r'Test Summary:  Error amount = 0.00000'
        }
        self.sanity_patterns = sn.assert_found(
            output_patterns[self.sample], self.stdout
        )
