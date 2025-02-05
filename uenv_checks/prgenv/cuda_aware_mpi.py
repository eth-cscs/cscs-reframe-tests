# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility as rfm_util

sys.path.append(str(pathlib.Path(__file__).parent.parent / 'mixins'))

from cuda_visible_devices_all import CudaVisibleDevicesAllMixin


@rfm.simple_test
class cuda_aware_mpi_compile(rfm.CompileOnlyRegressionTest):
    descr = 'Compilation of Cuda-aware MPI test from NVIDIA code-samples.git'
    sourcesdir = 'https://github.com/NVIDIA-developer-blog/code-samples.git'
    valid_systems = ['+remote +nvgpu']
    valid_prog_environs = ['+cuda-aware-mpi']
    build_locally = False
    prebuild_cmds = [
        'cd posts/cuda-aware-mpi-example/src',
        'rm -rf MATLAB* series c++11_cuda'
    ]
    build_system = 'Make'

    @run_before('compile')
    def set_compilers(self):
        # Remove the `sm_` prefix from the cuda arch
        gpu_arch = self.current_partition.select_devices('gpu')[0].arch[3:]
        gcd_flgs = f'-gencode arch=compute_{gpu_arch},code=sm_{gpu_arch}'
        self.build_system.options = [
            rf'CUDA_INSTALL_PATH=${{CUDA_HOME}}',  # cuda_runtime.h
            # Extract the include paths from the mpic++
            rf'MPICFLAGS=$(mpic++ -compile-info | tr " " "\n" | '
            rf'grep "^-I" | tr "\n" " ")',
            rf'GENCODE_FLAGS="{gcd_flgs}"',
            rf'MPICC="{self.current_environ.cc}"',
            rf'MPILD="{self.current_environ.cxx}"'
        ]

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found(r'jacobi_cuda_aware_mpi',
                                               self.stdout)


class CudaAwareMpiRuns(CudaVisibleDevicesAllMixin, rfm.RunOnlyRegressionTest):
    valid_systems = ['+remote +nvgpu']
    valid_prog_environs = ['+cuda-aware-mpi']
    sourcesdir = None
    env_vars = {
        'MPICH_GPU_SUPPORT_ENABLED': 1,
        'LD_LIBRARY_PATH': '${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}'
    }

    @run_after('init')
    def add_deps(self):
        self.depends_on('cuda_aware_mpi_compile')

    @require_deps
    def set_executable(self, cuda_aware_mpi_compile):
        self.executable = str(
            pathlib.Path(cuda_aware_mpi_compile().stagedir) / 'posts' /
            'cuda-aware-mpi-example' / 'bin' / 'jacobi_cuda_aware_mpi'
        )

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found(
            'Stopped after 1000 iterations with residue 0.00024', self.stdout
        )

@rfm.simple_test
class cuda_aware_mpi_one_node_check(CudaAwareMpiRuns):
    # Enable Cuda MPS to use more tasks than the available gpus
    prerun_cmds += ['nvidia-cuda-mps-control -d ']
    postrun_cmds += ['echo quit | nvidia-cuda-mps-control']

    @run_before('run')
    def set_num_tasks(self):
        self.num_tasks = 2 * self.num_gpus_per_node
        self.num_tasks_per_node = self.num_tasks
        self.executable_opts = [f'-t {self.num_tasks // 2} 2']


@rfm.simple_test
class cuda_aware_mpi_two_nodes_check(CudaAwareMpiRuns):
    @run_before('run')
    def set_num_tasks(self):
        self.num_tasks = 2
        self.num_tasks_per_node = 1
        self.num_gpus_per_node = 1
        self.executable_opts = [f'-t {self.num_tasks} 1']
