# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(
    str(pathlib.Path(__file__).parent.parent / 'mixins')
)
from container_engine import ContainerEngineCPEMixin


class CudaSamplesBase(rfm.RegressionTest, ContainerEngineCPEMixin):
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
    tags = {'production'}

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
            # The tags v12.[6-7] do not exist, fall back to v12.5
            rf"[[ $CUDA_VER = 'v12.6' || $CUDA_VER = 'v12.7' ]] && "
            rf"export CUDA_VER='v12.5'",
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
        sm = self.current_partition.select_devices('gpu')[0].arch[-2:]

        # FIXME Temporary workaround for cudatoolkit absence in ce image
        if 'containerized_cpe' not in self.current_environ.features:
            self.modules = ['cudatoolkit', f'craype-accel-nvidia{sm}',
                            'cpe-cuda']

    @run_before('compile')
    def set_build_flags(self):
        self.prebuild_cmds += [
            'echo CUDATOOLKIT_HOME=${CUDATOOLKIT_HOME:-$CUDA_HOME}',
            'module list'
        ]
        self.build_system.cflags = [
            '-I ${CUDATOOLKIT_HOME:-$CUDA_HOME}/include'
        ]
        self.build_system.ldflags = [
            '-L ${CUDATOOLKIT_HOME:-$CUDA_HOME}/lib64 -lnvidia-ml'
        ]

        # for simpleCUBLAS and conjugateGradientCudaGraphs:
        if 'containerized_cpe' not in self.current_environ.features:
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
