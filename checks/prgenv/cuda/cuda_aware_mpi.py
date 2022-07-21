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
    descr = 'Cuda-aware MPI test from the NVIDIA repo.'
    sourcesdir = ('https://github.com/NVIDIA-developer-blog/'
                  'code-samples.git')
    valid_systems = [
        'daint:gpu', 'dom:gpu', 'arolla:cn', 'tsa:cn',
        'ault:amdv100', 'ault:intelv100'
    ]
    prebuild_cmds = ['cd posts/cuda-aware-mpi-example/src']
    build_system = 'Make'
    postbuild_cmds = ['ls ../bin']
    maintainers = ['JO']
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
            self.variables = {
                'CUDA_HOME': '$CRAY_NVIDIA_PREFIX/cuda'
            }

        gcd_flgs = (
            '-gencode arch=compute_{0},code=sm_{0}'.format(self.gpu_arch)
        )
        self.build_system.options = [
            'CUDA_INSTALL_PATH=$CUDA_HOME',
            'MPI_HOME=$CRAY_MPICH_PREFIX',
            'GENCODE_FLAGS="%s"' % (gcd_flgs),
            'MPICC="%s"' % self.current_environ.cc,
            'MPILD="%s"' % self.current_environ.cxx
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
        self.executable_opts = ['-t %d 1' % self.num_tasks]


@rfm.simple_test
class gpu_direct(rfm.RegressionTest):
    descr = 'gpuDirect MPI test'
    sourcepath = 'gpudirect.cpp'
    valid_systems = ['daint:gpu', 'dom:gpu']
    valid_prog_environs = ['PrgEnv-cray']
    build_system = 'SingleSource'
    maintainers = ['JG']
    tags = {'production', 'scs'}
    valid_prog_environs = ['PrgEnv-cray']

    module_info = parameter(rfm_util.find_modules('cdt/'))
    gpu_arch = variable(str, type(None))
    run_after('setup')(bind(hooks.set_num_gpus_per_node))

    @run_after('init')
    def apply_module_info(self):
        s, e, m = self.module_info
        self.modules = ['cudatoolkit', m]

    @run_before('compile')
    def set_compilers(self):
        self.build_system.options = [
            '-I/usr/local/cuda/targets/x86_64-linux/include',
            '-L/usr/local/cuda/targets/x86_64-linux/lib',
            '-lcudart',
        ]

    @run_before('run')
    def set_env(self):
        self.variables = {
            'MPICH_RDMA_ENABLED_CUDA': '1',
            'MPICH_VERSION_DISPLAY': '1',
            # 'CRAY_CUDA_MPS': '1',
        }
        self.prerun_cmds = [
            'export LD_LIBRARY_PATH=$CRAY_LD_LIBRARY_PATH:$LD_LIBRARY_PATH',
            # test will fail when built with cdt<=21.09 (cray-mpich<=7.7.18):
            # PASS:rk=1     // 1st call
            # FAIL:rk=1:-1  //  2d call
        ]

    @run_before('run')
    def set_num_tasks(self):
        self.num_tasks = 2
        self.num_tasks_per_node = 1

    @run_before('sanity')
    def set_sanity_patterns(self):
        result = sn.count(sn.extractall(r'^(PASS):', self.stdout, 1))
        self.sanity_patterns = sn.assert_reference(result, 2, 0, 0)

    @performance_function('')
    def mpi_version(self):
        regex = r'MPI VERSION\s+: CRAY MPICH version (\S+) '
        version = sn.extractsingle(regex, self.stdout, 1,
                                   conv=lambda x: int(x.replace('.', '')))
        return version

    @performance_function('')
    def num_pass(self):
        return sn.count(sn.extractall(r'^(PASS):', self.stdout, 1))
