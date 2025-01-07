# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
import os

import reframe as rfm
import reframe.utility.sanity as sn
import uenv


ref_nb_gflops = {
    'a100': {'nb_gflops': (9746*2*0.85, -0.1, None, 'GFlops')},
    # https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/a100/pdf/
    # + nvidia-a100-datasheet-us-nvidia-1758950-r4-web.pdf (FP64 Tensor Core)
    'gh200': {'nb_gflops': (42700, -0.1, None, 'GFlops')},
    # from https://confluence.cscs.ch/display/SCISWDEV/Feeds+and+Speeds
}


@rfm.simple_test
class baremetal_cuda_node_burn(rfm.RegressionTest):
    valid_systems = ['+nvgpu +remote']
    valid_prog_environs = ['builtin']
    num_gpus = variable(int, value=4)
    nb_duration = variable(int, value=10)
    nb_matrix_size = variable(int, value=30000)
    # NOTE: nb_matrix_size = parameter([nn for nn in range(4000, 32000, 2000)])
    executable = 'build/burn'
    jfrog = variable(
        str, value='https://jfrog.svc.cscs.ch/artifactory/cscs-reframe-tests')
    build_system = 'CMake'

    def fullpath(self, files):
        return next((file for file in files if os.path.exists(file)), None)

    @run_before('compile')
    def set_compilation_env(self):
        gcc_l = [f'/usr/bin/gcc-{gnu_version}' for gnu_version in (13, 12, 11)]
        self.build_system.cc = self.fullpath(gcc_l)
        self.build_system.cxx = self.fullpath(gcc_l).replace('gcc', 'g++')

        platform = self.current_partition.processor.platform
        nvcc_l = [f'/opt/nvidia/hpc_sdk/Linux_{platform}/{year}/cuda/bin/nvcc'
                  for year in (2025, 2024, 2023)]
        self.build_system.nvcc = os.path.realpath(self.fullpath(nvcc_l))

        self.prebuild_cmds += [
            'git clone --depth=1 https://github.com/bcumming/node-burn.git',
            'mv node-burn/* .',
            # sles/15 comes with cmake/3.20.4
            f'wget -q {self.jfrog}/cmake/cmake-3.31.0-linux-{platform}.tar.gz',
            f'tar xf cmake-3.31.0-linux-{platform}.tar.gz',
            f'rm -f cmake-3.31.0-linux-{platform}.tar.gz'
        ]
        self.env_vars = {
            'PATH': f'$PWD/cmake-3.31.0-linux-{platform}/bin:$PATH',
        }

    @run_before('compile')
    def set_build_system_attrs(self):
        self.build_system.max_concurrency = 6
        self.build_system.srcdir = 'node-burn.git'
        self.build_system.builddir = 'build'
        c_part = self.current_partition
        self.build_system.config_opts = [
            '-DCMAKE_BUILD_TYPE=Release',
            '-DCMAKE_EXE_LINKER_FLAGS='
            '"/usr/lib64/openblas-pthreads/libopenblas.so.0"'
            # avoids "Looking for sgemm_ - not found"
        ]

    @run_before('run')
    def set_executable(self):
        self.skip_if_no_procinfo()
        self.num_tasks = self.num_gpus
        self.num_tasks_per_node = self.current_partition.devices[0].num_devices
        self.extra_resources = {
            'gres': {'gres': f'gpu:{self.num_tasks_per_node}'}
        }
        self.executable_opts = [
            f'-ggemm,{self.nb_matrix_size}',
            f'-d{self.nb_duration}', '--batch'
        ]

    @sanity_function
    def validate_test(self):
        """
        nid002..:gpu 4 iterations, 16147.33 GFlops, 13.4 seconds, 21.600 Gbytes
        """
        regex = r'nid\d+:gpu.*\s+(\d+\.\d+)\s+GFlops,'
        num_gpus_res = sn.count(sn.extractall(regex, self.stdout, 1, float))
        return sn.assert_eq(self.num_gpus, num_gpus_res)

    @performance_function('GFlops')
    def nb_gflops(self):
        regex = r'nid\d+:gpu.*\s+(\d+\.\d+)\s+GFlops,'
        return sn.min(sn.extractall(regex, self.stdout, 1, float))
        # TODO: report power cap (nodelist is already in json)

    @run_before('performance')
    def validate_perf(self):
        self.uarch = uenv.uarch(self.current_partition)
        if (
            self.uarch is not None and
            self.uarch in ref_nb_gflops
        ):
            self.reference = {
                self.current_partition.fullname: ref_nb_gflops[self.uarch]
            }
