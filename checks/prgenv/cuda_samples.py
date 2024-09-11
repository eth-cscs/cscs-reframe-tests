# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


class CudaSamplesBase(rfm.RegressionTest):
    sourcesdir = 'https://github.com/NVIDIA/cuda-samples.git'
    build_system = 'Make'
    build_locally = False
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

    @run_after('init')
    def set_descr(self):
        self.descr = f'CUDA {self.sample} test'

    @run_before('compile')
    def set_branch(self):
        self.prebuild_cmds += [
            # Retrieve the Cuda version from the nvcc compiler
            rf"export CUDA_VER=v$(nvcc -V | "
            rf"sed -n 's/^.*release \([[:digit:]]*\.[[[:digit:]]\).*$/\1/p')",
            #
            rf"git checkout ${{CUDA_VER}}",
            rf"cd Samples/{self.sample_dir[self.sample]}/{self.sample}"
        ]

    @run_before('compile')
    def set_gpu_arch(self):
        # Remove the `sm_` prefix from the cuda arch
        gpu_arch = self.current_partition.select_devices('gpu')[0].arch[3:]
        self.build_system.options = [f'SMS="{gpu_arch}"']

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


@rfm.simple_test
class CPE_CudaSamples(CudaSamplesBase):
    env_vars = {
        'LD_LIBRARY_PATH': '$CUDA_HOME/lib64:$LD_LIBRARY_PATH'
    }
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['+cuda -uenv']

    @run_after('setup')
    def set_modules(self):
        if 'PrgEnv-nvhpc' != self.current_environ.name:
            sm = self.current_partition.select_devices('gpu')[0].arch[-2:]
            self.modules = ['cudatoolkit', f'craype-accel-nvidia{sm}',
                            'cpe-cuda']

    @run_before('compile')
    def set_build_flags(self):
        self.prebuild_cmds += [
            'echo CUDATOOLKIT_HOME=$CUDATOOLKIT_HOME',
            'module list'
        ]
        self.build_system.cflags = ['-I $CUDATOOLKIT_HOME/include']
        self.build_system.ldflags = ['-L $CUDATOOLKIT_HOME/lib64 -lnvidia-ml']
        # for simpleCUBLAS and conjugateGradientCudaGraphs:
        self.build_system.options += [
            'EXTRA_NVCCFLAGS="-I $CUDATOOLKIT_HOME/../../math_libs/include"',
            'EXTRA_LDFLAGS="-L $CUDATOOLKIT_HOME/../../math_libs/lib64"'
        ]


@rfm.simple_test
class UENV_CudaSamples(CudaSamplesBase):
    env_vars = {'LD_LIBRARY_PATH': '$CUDA_HOME/lib64:$LD_LIBRARY_PATH'}
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['+cuda +uenv']

    @run_before('compile')
    def set_build_flags(self):
        self.prebuild_cmds += [
            'echo CUDA_HOME=$CUDA_HOME',
        ]
        self.build_system.options += [f'CUDA_PATH=$CUDA_HOME']
