# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys

import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility as rfm_util

sys.path.append(os.path.abspath(os.path.join(__file__, '../../..')))  # '
import microbenchmarks.gpu.hooks as hooks


@rfm.simple_test
class cuda_aware_mpi_check(rfm.CompileOnlyRegressionTest):
    descr = 'Cuda-aware MPI test from NVIDIA code-samples.git'
    sourcesdir = ('https://github.com/NVIDIA-developer-blog/'
                  'code-samples.git')
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['+uenv +prgenv +cuda']
        # 'daint:gpu', 'dom:gpu', 'arolla:cn', 'tsa:cn',
        # 'ault:amdv100', 'ault:intelv100'
    prebuild_cmds = ['cd posts/cuda-aware-mpi-example/src']
    build_system = 'Make'
    postbuild_cmds = ['ls ../bin']
    maintainers = ['@ekouts', '@jgphpc']
    tags = {'production'}

    gpu_arch = variable(str, type(None))

#todo     @run_after('init')
#todo     def set_valid_prog_environs(self):
#todo         if self.current_system.name in ['arolla', 'tsa']:
#todo             self.valid_prog_environs = ['PrgEnv-gnu']
#todo         elif self.current_system.name in ['ault']:
#todo             self.valid_prog_environs = ['PrgEnv-gnu']
#todo         else:
#todo             self.valid_prog_environs = ['PrgEnv-cray', 'PrgEnv-gnu',
#todo                                         'PrgEnv-pgi', 'PrgEnv-nvidia']
#todo 
#todo         if self.current_system.name in ['arolla', 'tsa', 'ault']:
#todo             self.exclusive_access = True

    run_after('setup')(bind(hooks.set_gpu_arch))
    run_after('setup')(bind(hooks.set_num_gpus_per_node))

    @run_before('compile')
    def set_compilers(self):
#todo         if self.current_environ.name == 'PrgEnv-pgi':
#todo             self.build_system.cflags = ['-std=c99', ' -O3']
#todo         elif self.current_environ.name == 'PrgEnv-nvidia':
#todo             self.env_vars = {
#todo                 'CUDA_HOME': '$CRAY_NVIDIA_PREFIX/cuda'
#todo             }

        gcd_flgs = (
            '-gencode arch=compute_{0},code=sm_{0}'.format(self.gpu_arch)
        )

        self.build_system.options = [
            # f'CUDA_INSTALL_PATH=$CUDA_HOME',  # cuda_runtime.h
            # f'MPI_HOME=$CRAY_MPICH_PREFIX',  # mpi.h
            f'GENCODE_FLAGS="{gcd_flgs}"',
            # f'MPICC="{self.current_environ.cc}"',
            # f'MPILD="{self.current_environ.cxx}"'
        ]

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found(r'jacobi_cuda_aware_mpi',
                                               self.stdout)


class CudaAwareMpiRuns(rfm.RunOnlyRegressionTest):
    prerun_cmds = ['export MPICH_RDMA_ENABLED_CUDA=1']
    valid_systems = ['+nvgpu']
        #'daint:gpu', 'dom:gpu', 'arolla:cn', 'tsa:cn',
        #'ault:amdv100', 'ault:intelv100'
    #]

#todo     @run_after('init')
#todo     def set_valid_prog_environs(self):
#todo         if self.current_system.name in ['arolla', 'tsa']:
#todo             self.valid_prog_environs = ['PrgEnv-gnu']
#todo         elif self.current_system.name in ['ault']:
#todo             self.valid_prog_environs = ['PrgEnv-gnu']
#todo         else:
#todo             self.valid_prog_environs = ['PrgEnv-cray', 'PrgEnv-gnu',
#todo                                         'PrgEnv-pgi', 'PrgEnv-nvidia']
#todo 
#todo         if self.current_system.name in ['arolla', 'tsa', 'ault']:
#todo             self.exclusive_access = True

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
    '''Run the case on one node.'''
    prerun_cmds += ['export CRAY_CUDA_MPS=1']

    @run_before('run')
    def set_num_tasks(self):
        self.num_tasks = 2 * self.num_gpus_per_node
        self.num_tasks_per_node = self.num_tasks
        self.executable_opts = [f'-t {self.num_tasks/2} 2']


@rfm.simple_test
class cuda_aware_mpi_two_nodes_check(CudaAwareMpiRuns):
    '''Run the case on two nodes.'''

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


#todo @rfm.simple_test
#todo class cuda_aware_mpi_check_xc(rfm.RegressionTest):
#todo     descr = 'Cuda-aware MPI test from NVIDIA code-samples.git'
#todo     sourcesdir = ('https://github.com/NVIDIA-developer-blog/'
#todo                   'code-samples.git')
#todo     valid_systems = [
#todo         'daint:gpu',
#todo         # TODO: 'dom:gpu', 'hohgant:nvgpu', 'hohgant:nvgpu-sqfs',
#todo     ]
#todo     valid_prog_environs = ['PrgEnv-gnu']  # TODO: PrgEnv-cray
#todo     env_vars = {
#todo         'MPICH_RDMA_ENABLED_CUDA': '1',
#todo         'MPICH_VERSION_DISPLAY': '1',
#todo         'LD_LIBRARY_PATH': '$CRAY_LD_LIBRARY_PATH:$LD_LIBRARY_PATH',
#todo     }
#todo     prebuild_cmds = [
#todo         'rm -fr MATLAB* series c++11_cuda',
#todo         'cd posts/cuda-aware-mpi-example/src'
#todo     ]
#todo     build_system = 'Make'
#todo     maintainers = ['@ekouts', '@jgphpc']
#todo     tags = {'production', 'scs', 'craype'}
#todo     test_data = [
#todo         find_cdts('daint:gpu', 'PrgEnv-gnu', 'cdt/'),
#todo         find_cdts('daint:gpu', 'PrgEnv-gnu', 'nvhpc-nompi/'),
#todo         find_cdts('daint:gpu', 'PrgEnv-gnu', 'gcc/')
#todo     ]
#todo     if [] not in test_data:
#todo         cdt_info = parameter(test_data[0])
#todo         nvhpc_info = parameter(test_data[1])
#todo         gcc_info = parameter(test_data[2])
#todo 
#todo     gpu_arch = variable(str, type(None))
#todo 
#todo     @run_after('init')
#todo     def apply_module_info(self):
#todo         # bad_pe= ['cdt/21.09', 'cdt/20.08']
#todo         # making sure 'gcc version' is compatible with 'cuda version' in nvhpc,
#todo         # nvhpc/22.3 has cuda/11.6 which supports gcc<12:
#todo         nvhpc2gcc = {
#todo             '21.3': {'cuda': '11.2', 'gcc': '10'},
#todo             '21.5': {'cuda': '11.3', 'gcc': '10'},
#todo             '21.9': {'cuda': '11.4', 'gcc': '11'},
#todo             '22.2': {'cuda': '11.6', 'gcc': '11'},
#todo             '22.3': {'cuda': '11.6', 'gcc': '11'},
#todo             # TODO: newer nvhpc
#todo         }
#todo         if [] in self.test_data:
#todo             self.skip('No data found')
#todo 
#todo         gcc_major_version = self.gcc_info.split('/')[1].split('.')[0]
#todo         nvhpc_version = self.nvhpc_info.split('/')[1]
#todo         gcc_max_version = nvhpc2gcc[nvhpc_version]['gcc']
#todo         cuda_max_version = nvhpc2gcc[nvhpc_version]['cuda']
#todo         skip_msg = (
#todo             f'gcc/{gcc_major_version} != nvhpc/{nvhpc_version}:'
#todo             f'cuda/{cuda_max_version}:gcc/{gcc_max_version}'
#todo         )
#todo         self.skip_if(gcc_major_version != gcc_max_version, skip_msg)
#todo         self.modules = [self.cdt_info, self.nvhpc_info, self.gcc_info]
#todo 
#todo     @run_before('compile')
#todo     def set_compilers(self):
#todo         gput = self.current_partition.select_devices('gpu')[0]
#todo         gcd_flgs = f'-arch={gput.arch}'
#todo         nvhpc_version = self.nvhpc_info.split('/')[1]
#todo         cuda_path = f'/opt/nvidia/hpc_sdk/Linux_x86_64/{nvhpc_version}/cuda'
#todo         link_flags = (
#todo             # add -lcuda to avoid segmentation fault
#todo             f'-Wl,-rpath={cuda_path}/lib64/ -lcuda '
#todo             # TODO: add -lmpi_gtl_cuda to avoid hangs (alps)
#todo             # '$PE_MPICH_GTL_DIR_nvidia80 $PE_MPICH_GTL_LIBS_nvidia80'
#todo         )
#todo         self.build_system.options = [
#todo             f'CUDA_INSTALL_PATH={cuda_path}',
#todo             f'MPI_HOME=$CRAY_MPICH_PREFIX',
#todo             f'GENCODE_FLAGS="{gcd_flgs}"',
#todo             f'MPICC="{self.current_environ.cc}"',
#todo             f'MPILD="{self.current_environ.cxx} {link_flags}"',
#todo         ]
#todo 
#todo     @run_before('compile')
#todo     def extract_versions(self):
#todo         cmd1 = 'ldd ../bin/jacobi_cuda_aware_mpi | grep libcudart '
#todo         cmd2 = "awk '{print \"ls -l \",$3}'"
#todo         cmd3 = 'sh'
#todo         cmd4 = "awk '{print $11}'"
#todo         self.rpt = os.path.join(self.stagedir, 'rpt')
#todo         cmd = f'{cmd1} | {cmd2} | {cmd3} | {cmd4} > {self.rpt}'
#todo         self.postbuild_cmds += [cmd]
#todo 
#todo     @run_before('run')
#todo     def set_executable(self):
#todo         self.executable = os.path.join(
#todo             self.stagedir,
#todo             'posts', 'cuda-aware-mpi-example', 'bin', 'jacobi_cuda_aware_mpi'
#todo         )
#todo 
#todo     @run_before('run')
#todo     def set_run(self):
#todo         self.num_tasks = 2
#todo         self.num_tasks_per_node = 1
#todo         self.num_gpus_per_node = 1
#todo         self.executable_opts = [f'-t {self.num_tasks} 1']
#todo 
#todo     @run_before('sanity')
#todo     def set_sanity_patterns(self):
#todo         self.sanity_patterns = sn.assert_found(r'Stopped after 1000 iterations'
#todo                                                r' with residue 0.00024',
#todo                                                self.stdout)
#todo 
#todo     @run_before('performance')
#todo     def report_linked_versions(self):
#todo         regex_mpich = r'MPI VERSION\s+: CRAY MPICH version (\S+) '
#todo         regex_cudart = r'libcudart.so.(\S+)$'
#todo         self.perf_patterns = {
#todo             'mpich': sn.extractsingle(regex_mpich, self.stderr, 1,
#todo                                       conv=lambda x: int(x.replace('.', ''))),
#todo             'cudart': sn.extractsingle(regex_cudart, self.rpt, 1,
#todo                                        conv=lambda x: int(x.replace('.', ''))),
#todo         }
