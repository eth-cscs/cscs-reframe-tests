# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


class CudaSamplesBase(rfm.RegressionTest):
    repo = 'https://github.com/NVIDIA/cuda-samples.git'
    sourcesdir = 'src/cuda_samples'
    build_system = 'CMake'
    build_locally = False
    time_limit = '2m'
    maintainers = ['PA', 'SSA']
    sample = parameter(['deviceQuery', 'simpleCUBLAS'])
    tags = {'production'}

    @run_after('init')
    def set_descr(self):
        self.descr = f'CUDA {self.sample} test'
        self.keep_files = {
            'deviceQuery': 'cuda-samples/Samples/1_Utilities/deviceQuery',
            'simpleCUBLAS':
                'cuda-samples/Samples/4_CUDA_Libraries/simpleCUBLAS'
        }

    @run_before('compile')
    def set_gpu_arch(self):
        gpu_arch = self.current_partition.select_devices('gpu')[0].arch[3:]
        self.build_system.srcdir = 'cuda-samples'
        self.build_system.configuredir = self.keep_files[self.sample]
        self.build_system.builddir = f'_build'
        self.build_system.config_opts += [
            f'-DCMAKE_CUDA_ARCHITECTURES={gpu_arch}',
        ]
        self.build_system.build_opts = [self.sample]

    @run_before('compile')
    def set_branch(self):
        # every job has a separate directory, cloning inside each dir is fine
        self.prebuild_cmds += [
            rf'git clone --quiet {self.repo}',
            rf'./_git_checkout.sh {self.build_system.srcdir}',
            # trying to save disk space for daily runs:
            rf'./_clean.sh {self.keep_files[self.sample]}'
        ]

    @run_before('run')
    def set_executable(self):
        self.executable = f'$(find . -type f -name {self.sample} -executable)'

    @run_before('sanity')
    def set_sanity_patterns(self):
        output_patterns = {
            'deviceQuery': r'Result = PASS',
            'simpleCUBLAS': r'test passed',
        }
        self.sanity_patterns = sn.assert_found(
            output_patterns[self.sample], self.stdout
        )


@rfm.simple_test
class UENV_CudaSamples(CudaSamplesBase):
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['+uenv +prgenv +cuda -cpe']

    @run_before('compile')
    def set_build_flags(self):
        self.prebuild_cmds += ['echo CUDA_HOME=$CUDA_HOME']
