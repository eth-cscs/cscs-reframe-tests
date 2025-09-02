# Copyright 2016 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(
    str(pathlib.Path(__file__).parent.parent.parent / 'mixins')
)
from container_engine import ContainerEngineCPEMixin  # noqa: E402


class CudaSamplesBase(rfm.RegressionTest):
    sourcesdir = 'https://github.com/NVIDIA/cuda-samples.git'
    build_system = 'CMake'
    build_locally = False
    time_limit = '2m'
    maintainers = ['PA', 'SSA']
    sample = parameter([
        'deviceQuery', 'simpleCUBLAS', 'conjugateGradient'
    ])
    sample_dir = {
        'deviceQuery': '1_Utilities',
        'simpleCUBLAS': '4_CUDA_Libraries',
        'conjugateGradient': '4_CUDA_Libraries'
    }
    # concurrentKernels is osbsolete since cuda/12.8
    # bandwidthTest is osbsolete since cuda/12.9
    # https://github.com/NVIDIA/cuda-samples/releases/tag/v12.8
    tags = {'production'}

    @run_after('init')
    def set_descr(self):
        self.descr = f'CUDA {self.sample} test'

    @run_before('compile')
    def set_branch(self):
        self.prebuild_cmds += [
            # Retrieve the CUDA version from nvcc and checkout tag
            rf"export CUDA_VER=v$(nvcc -V | "
            rf"sed -n 's/^.*release \([[:digit:]]*\.[[[:digit:]]\).*$/\1/p')",
            #
            # The tags v12.[6-7] do not exist, checkout v12.8 instead
            rf"[[ $CUDA_VER = 'v12.6' || $CUDA_VER = 'v12.7' ]] && "
            rf"export CUDA_VER='v12.8'",
            #
            rf"echo CUDA_VER=$CUDA_VER",
            rf"git checkout ${{CUDA_VER}}",
        ]

    @run_before('compile')
    def set_gpu_arch(self):
        gpu_arch = self.current_partition.select_devices('gpu')[0].arch[3:]
        self.build_system.config_opts += [
            f'-S Samples',
            f'-DCMAKE_CUDA_ARCHITECTURES={gpu_arch}',
        ]
        self.build_system.make_opts = [self.sample]

    @run_before('run')
    def set_executable(self):
        self.executable = (f'./Samples/{self.sample_dir[self.sample]}/'
                           f'{self.sample}/{self.sample}')

    @run_before('sanity')
    def set_sanity_patterns(self):
        output_patterns = {
            'deviceQuery': r'Result = PASS',
            'simpleCUBLAS': r'test passed',
            'conjugateGradient':
                r'Test Summary:  Error amount = 0.00000'
        }
        self.sanity_patterns = sn.assert_found(
            output_patterns[self.sample], self.stdout
        )


@rfm.simple_test
class UENV_CudaSamples(CudaSamplesBase):
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['+uenv +prgenv +cuda -cpe']
    # env_vars = {'LD_LIBRARY_PATH': '$CUDA_HOME/lib64:$LD_LIBRARY_PATH'}

    @run_before('compile')
    def set_build_flags(self):
        self.prebuild_cmds += ['echo CUDA_HOME=$CUDA_HOME']
        # self.build_system.options += [f'CUDA_PATH=$CUDA_HOME']
