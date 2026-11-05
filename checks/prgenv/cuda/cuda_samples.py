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
    # simpleCUBLAS was removed in cuda-samples v13.4 (moved to
    # NVIDIA/CUDALibrarySamples); conjugateGradientCudaGraphs uses cuBLAS
    # and cuSPARSE and exists in every supported tag
    sample = parameter(['deviceQuery', 'conjugateGradientCudaGraphs'])
    tags = {'production'}

    @run_after('init')
    def set_descr(self):
        self.descr = f'CUDA {self.sample} test'

    @run_before('compile')
    def set_gpu_arch(self):
        gpu_arch = self.current_partition.select_devices('gpu')[0].arch[3:]
        self.build_system.srcdir = 'cuda-samples'
        # set by set_branch, e.g. cuda-samples/cpp/1_Utilities/deviceQuery:
        # the samples moved from Samples/ to cpp/ in cuda-samples v13.2update
        self.build_system.configuredir = '$CUDA_SAMPLE_DIR'
        self.build_system.builddir = f'_build'
        self.build_system.config_opts += [
            f'-DCMAKE_CUDA_ARCHITECTURES={gpu_arch}',
        ]
        self.build_system.build_opts = [self.sample]

    @run_before('compile')
    def set_branch(self):
        # every job has a separate directory, cloning inside each dir is fine
        srcdir = self.build_system.srcdir
        self.prebuild_cmds += [
            rf'git clone --quiet {self.repo}',
            rf'./_git_checkout.sh {srcdir} || exit 1',
            rf'export CUDA_SAMPLE_DIR=$(find {srcdir}/cpp {srcdir}/Samples '
            rf'-mindepth 2 -maxdepth 2 -type d -name {self.sample} '
            rf'2>/dev/null | head -1)',
            rf'[ -n "$CUDA_SAMPLE_DIR" ] || '
            rf'{{ echo "{self.sample} not found in {srcdir}"; exit 1; }}',
            # trying to save disk space for daily runs:
            r'./_clean.sh $CUDA_SAMPLE_DIR || exit 1'
        ]

    @run_before('run')
    def set_executable(self):
        self.executable = f'$(find . -type f -name {self.sample} -executable)'

    @run_before('sanity')
    def set_sanity_patterns(self):
        if self.sample == 'conjugateGradientCudaGraphs':
            err = sn.extractsingle(r'Test Summary:\s+Error amount = (\S+)',
                                   self.stdout, 1, float)
            self.sanity_patterns = sn.assert_lt(err, 1e-5)
        else:
            self.sanity_patterns = sn.assert_found(r'Result = PASS',
                                                   self.stdout)


@rfm.simple_test
class UENV_CudaSamples(CudaSamplesBase):
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['+uenv +prgenv +cuda -cpe']

    @run_before('compile')
    def set_build_flags(self):
        self.prebuild_cmds += ['echo CUDA_HOME=$CUDA_HOME']
