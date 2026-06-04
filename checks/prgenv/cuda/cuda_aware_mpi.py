# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os

import reframe as rfm
import reframe.utility.sanity as sn

# keeping as reference:
# import reframe.utility as rfm_util
# sys.path.append(os.path.abspath(os.path.join(__file__, '../../..')))
# import microbenchmarks.gpu.hooks as hooks


@rfm.simple_test
class cuda_aware_mpi_build(rfm.CompileOnlyRegressionTest):
    descr = 'Cuda-aware MPI test from NVIDIA code-samples.git'
    sourcesdir = ('https://github.com/NVIDIA-developer-blog/'
                  'code-samples.git')
    # TODO: parse clone
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['+uenv +prgenv +cuda']
    time_limit = '2m'
    prebuild_cmds = [
        'rm -fr MATLAB_deeplearning MATLAB_arrayfun c++11_cuda series',
        'cd posts/cuda-aware-mpi-example/src'
    ]
    build_system = 'Make'
    postbuild_cmds = ['ls ../bin']
    build_locally = False
    maintainers = ['@ekouts', '@jgphpc']
    tags = {'production'}

    # keeping for future generations:
    # gpu_arch = variable(str, type(None))
    # run_after('setup')(bind(hooks.set_gpu_arch))
    # run_after('setup')(bind(hooks.set_num_gpus_per_node))

    @run_before('compile')
    def set_compilers(self):
        self.env_vars = {
            'CUDA_INSTALL_PATH': '$CUDA_HOME',
            'MPI_HOME': '$CUDA_HOME'
        }
        self.build_system.options = [
            f'GENCODE_FLAGS=-arch={self.current_partition.devices[0].arch}'
        ]

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found(r'jacobi_cuda_aware_mpi',
                                               self.stdout)


class cuda_aware_mpi_run(rfm.RunOnlyRegressionTest):
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['+uenv +prgenv +cuda']
    time_limit = '2m'
    sourcesdir = 'src/cuda_aware_mpi'
    env_vars = {
        'MPICH_GPU_SUPPORT_ENABLED': '1',
        'MPICH_RDMA_ENABLED_CUDA': '1',
        'MPICH_OFI_NIC_POLICY': 'GPU',
        'MPICH_VERSION_DISPLAY': '1'
    }

    @run_after('init')
    def add_deps(self):
        self.depends_on('cuda_aware_mpi_build')

    @require_deps
    def set_executable(self, cuda_aware_mpi_build):
        self.executable = \
            os.path.join(cuda_aware_mpi_build().stagedir, 'posts',
                         'cuda-aware-mpi-example', 'bin',
                         'jacobi_cuda_aware_mpi')

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found(r'Stopped after 1000 iterations'
                                               r' with residue 0.00024',
                                               self.stdout)


@rfm.simple_test
class cuda_aware_mpi_one_node_check(cuda_aware_mpi_run):
    descr = 'Run cuda_aware_mpi test on 1 node using CUDA_MPS'

    @run_before('run')
    def set_num_tasks(self):
        self.executable = './mps-wrapper.sh ' + self.executable
        self.num_tasks = 2 * self.current_partition.devices[0].num_devices
        self.num_tasks_per_node = self.num_tasks
        self.num_cpus_per_task = 1
        self.executable_opts = [f'-t {int(self.num_tasks/2)} 2']


@rfm.simple_test
class cuda_aware_mpi_two_nodes_check(cuda_aware_mpi_run):
    descr = 'Run cuda_aware_mpi test on 2 nodes'

    @run_before('run')
    def set_num_tasks(self):
        self.num_tasks = self.current_partition.devices[0].num_devices
        self.num_tasks_per_node = self.num_tasks
        self.num_cpus_per_task = 1
        self.executable_opts = [f'-t {self.num_tasks} 1']
