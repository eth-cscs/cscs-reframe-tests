# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys

import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility as rfm_util

sys.path.append(os.path.abspath(os.path.join(__file__, '../../..')))
import microbenchmarks.gpu.hooks as hooks


@rfm.simple_test
class cuda_aware_mpi_check(rfm.CompileOnlyRegressionTest):
    descr = 'Cuda-aware MPI test from NVIDIA code-samples.git'
    sourcesdir = ('https://github.com/NVIDIA-developer-blog/'
                  'code-samples.git')
    valid_systems = [
        'daint:gpu', 'dom:gpu', 'arolla:cn', 'tsa:cn',
        'ault:amdv100', 'ault:intelv100'
    ]
    prebuild_cmds = ['cd posts/cuda-aware-mpi-example/src']
    build_system = 'Make'
    postbuild_cmds = ['ls ../bin']
    maintainers = ['@ekouts', '@teojgo']
    tags = {'production', 'scs'}

    gpu_arch = variable(str, type(None))

    @run_after('init')
    def set_valid_prog_environs(self):
        if self.current_system.name in ['arolla', 'tsa']:
            self.valid_prog_environs = ['PrgEnv-gnu']
        elif self.current_system.name in ['ault']:
            self.valid_prog_environs = ['PrgEnv-gnu']
        else:
            self.valid_prog_environs = ['PrgEnv-cray', 'PrgEnv-gnu',
                                        'PrgEnv-pgi', 'PrgEnv-nvidia']

        if self.current_system.name in ['arolla', 'tsa', 'ault']:
            self.exclusive_access = True

    run_after('setup')(bind(hooks.set_gpu_arch))
    run_after('setup')(bind(hooks.set_num_gpus_per_node))

    @run_before('compile')
    def set_compilers(self):
        if self.current_environ.name == 'PrgEnv-pgi':
            self.build_system.cflags = ['-std=c99', ' -O3']
        elif self.current_environ.name == 'PrgEnv-nvidia':
            self.env_vars = {
                'CUDA_HOME': '$CRAY_NVIDIA_PREFIX/cuda'
            }

        gcd_flgs = (
            '-gencode arch=compute_{0},code=sm_{0}'.format(self.gpu_arch)
        )
        self.build_system.options = [
            f'CUDA_INSTALL_PATH=$CUDA_HOME',  # cuda_runtime.h
            f'MPI_HOME=$CRAY_MPICH_PREFIX',  # mpi.h
            f'GENCODE_FLAGS="{gcd_flgs}"',
            f'MPICC="{self.current_environ.cc}"',
            f'MPILD="{self.current_environ.cxx}"'
        ]

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found(r'jacobi_cuda_aware_mpi',
                                               self.stdout)


class CudaAwareMpiRuns(rfm.RunOnlyRegressionTest):

    prerun_cmds = ['export MPICH_RDMA_ENABLED_CUDA=1']
    valid_systems = [
        'daint:gpu', 'dom:gpu', 'arolla:cn', 'tsa:cn',
        'ault:amdv100', 'ault:intelv100'
    ]

    @run_after('init')
    def set_valid_prog_environs(self):
        if self.current_system.name in ['arolla', 'tsa']:
            self.valid_prog_environs = ['PrgEnv-gnu']
        elif self.current_system.name in ['ault']:
            self.valid_prog_environs = ['PrgEnv-gnu']
        else:
            self.valid_prog_environs = ['PrgEnv-cray', 'PrgEnv-gnu',
                                        'PrgEnv-pgi', 'PrgEnv-nvidia']

        if self.current_system.name in ['arolla', 'tsa', 'ault']:
            self.exclusive_access = True

    @run_after('init')
    def add_deps(self):
        self.depends_on('cuda_aware_mpi_check')

    run_after('setup')(bind(hooks.set_gpu_arch))
    run_after('setup')(bind(hooks.set_num_gpus_per_node))

    @require_deps
    def set_executable(self, cuda_aware_mpi_check):
        self.executable = os.path.join(
            cuda_aware_mpi_check().stagedir,
            'posts', 'cuda-aware-mpi-example',
            'bin', 'jacobi_cuda_aware_mpi'
        )

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found(r'Stopped after 1000 iterations'
                                               r' with residue 0.00024',
                                               self.stdout)


@rfm.simple_test
class cuda_aware_mpi_one_node_check(CudaAwareMpiRuns):
    '''Run the case in one node.'''

    prerun_cmds += ['export CRAY_CUDA_MPS=1']

    @run_before('run')
    def set_num_tasks(self):
        self.num_tasks = 2 * self.num_gpus_per_node
        self.num_tasks_per_node = self.num_tasks
        self.executable_opts = [f'-t {self.num_tasks/2} 2']


@rfm.simple_test
class cuda_aware_mpi_two_nodes_check(CudaAwareMpiRuns):
    '''Run the case across two nodes.'''

    @run_before('run')
    def set_num_tasks(self):
        self.num_tasks = 2
        self.num_tasks_per_node = 1
        self.num_gpus_per_node = 1
        self.executable_opts = [f'-t {self.num_tasks} 1']


def find_cdts(valid_systems, valid_prog_environs, modulename):
    # TODO: use rt.runtime().system.partitions[] ?
    modulefiles = []
    for system, prog_env, modulefile in rfm_util.find_modules(modulename):
        if (system in valid_systems and prog_env in valid_prog_environs):
            modulefiles.append(modulefile)
    return modulefiles


@rfm.simple_test
class cuda_aware_mpi_check_xc(rfm.RegressionTest):
    descr = 'Cuda-aware MPI test from NVIDIA code-samples.git'
    sourcesdir = ('https://github.com/NVIDIA-developer-blog/'
                  'code-samples.git')
    valid_systems = [
        'daint:gpu',
        # TODO: 'dom:gpu', 'hohgant:nvgpu', 'hohgant:nvgpu-sqfs',
    ]
    valid_prog_environs = ['PrgEnv-gnu']  # TODO: PrgEnv-cray
    env_vars = {
        'MPICH_RDMA_ENABLED_CUDA': '1',
        'MPICH_VERSION_DISPLAY': '1',
        'LD_LIBRARY_PATH': '$CRAY_LD_LIBRARY_PATH:$LD_LIBRARY_PATH',
    }
    prebuild_cmds = [
        'rm -fr MATLAB* series c++11_cuda',
        'cd posts/cuda-aware-mpi-example/src'
    ]
    build_system = 'Make'
    maintainers = ['@ekouts', '@jgphpc']
    tags = {'production', 'scs', 'craype'}
    test_data = [
        find_cdts('daint:gpu', 'PrgEnv-gnu', 'cdt/'),
        find_cdts('daint:gpu', 'PrgEnv-gnu', 'nvhpc-nompi/'),
        find_cdts('daint:gpu', 'PrgEnv-gnu', 'gcc/')
    ]
    if [] not in test_data:
        cdt_info = parameter(test_data[0])
        nvhpc_info = parameter(test_data[1])
        gcc_info = parameter(test_data[2])

    gpu_arch = variable(str, type(None))

    @run_after('init')
    def apply_module_info(self):
        # bad_pe= ['cdt/21.09', 'cdt/20.08']
        # making sure 'gcc version' is compatible with 'cuda version' in nvhpc,
        # nvhpc/22.3 has cuda/11.6 which supports gcc<12:
        nvhpc2gcc = {
            '21.3': {'cuda': '11.2', 'gcc': '10'},
            '21.5': {'cuda': '11.3', 'gcc': '10'},
            '21.9': {'cuda': '11.4', 'gcc': '11'},
            '22.2': {'cuda': '11.6', 'gcc': '11'},
            '22.3': {'cuda': '11.6', 'gcc': '11'},
            # TODO: newer nvhpc
        }
        if None in self.test_data:
            self.skip('No data found')

        gcc_major_version = self.gcc_info.split('/')[1].split('.')[0]
        nvhpc_version = self.nvhpc_info.split('/')[1]
        gcc_max_version = nvhpc2gcc[nvhpc_version]['gcc']
        cuda_max_version = nvhpc2gcc[nvhpc_version]['cuda']
        skip_msg = (
            f'gcc/{gcc_major_version} != nvhpc/{nvhpc_version}:'
            f'cuda/{cuda_max_version}:gcc/{gcc_max_version}'
        )
        self.skip_if(gcc_major_version != gcc_max_version, skip_msg)
        self.modules = [self.cdt_info, self.nvhpc_info, self.gcc_info]

    @run_before('compile')
    def set_compilers(self):
        gput = self.current_partition.select_devices('gpu')[0]
        gcd_flgs = f'-arch={gput.arch}'
        nvhpc_version = self.nvhpc_info.split('/')[1]
        cuda_path = f'/opt/nvidia/hpc_sdk/Linux_x86_64/{nvhpc_version}/cuda'
        link_flags = (
            # add -lcuda to avoid segmentation fault
            f'-Wl,-rpath={cuda_path}/lib64/ -lcuda '
            # TODO: add -lmpi_gtl_cuda to avoid hangs (alps)
            # '$PE_MPICH_GTL_DIR_nvidia80 $PE_MPICH_GTL_LIBS_nvidia80'
        )
        self.build_system.options = [
            f'CUDA_INSTALL_PATH={cuda_path}',
            f'MPI_HOME=$CRAY_MPICH_PREFIX',
            f'GENCODE_FLAGS="{gcd_flgs}"',
            f'MPICC="{self.current_environ.cc}"',
            f'MPILD="{self.current_environ.cxx} {link_flags}"',
        ]

    @run_before('compile')
    def extract_versions(self):
        cmd1 = 'ldd ../bin/jacobi_cuda_aware_mpi | grep libcudart '
        cmd2 = "awk '{print \"ls -l \",$3}'"
        cmd3 = 'sh'
        cmd4 = "awk '{print $11}'"
        self.rpt = os.path.join(self.stagedir, 'rpt')
        cmd = f'{cmd1} | {cmd2} | {cmd3} | {cmd4} > {self.rpt}'
        self.postbuild_cmds += [cmd]

    @run_before('run')
    def set_executable(self):
        self.executable = os.path.join(
            self.stagedir,
            'posts', 'cuda-aware-mpi-example', 'bin', 'jacobi_cuda_aware_mpi'
        )

    @run_before('run')
    def set_run(self):
        self.num_tasks = 2
        self.num_tasks_per_node = 1
        self.num_gpus_per_node = 1
        self.executable_opts = [f'-t {self.num_tasks} 1']

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found(r'Stopped after 1000 iterations'
                                               r' with residue 0.00024',
                                               self.stdout)

    @run_before('performance')
    def report_linked_versions(self):
        regex_mpich = r'MPI VERSION\s+: CRAY MPICH version (\S+) '
        regex_cudart = r'libcudart.so.(\S+)$'
        self.perf_patterns = {
            'mpich': sn.extractsingle(regex_mpich, self.stderr, 1,
                                      conv=lambda x: int(x.replace('.', ''))),
            'cudart': sn.extractsingle(regex_cudart, self.rpt, 1,
                                       conv=lambda x: int(x.replace('.', ''))),
        }
