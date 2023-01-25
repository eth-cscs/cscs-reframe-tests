# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.osext as osext
import reframe.utility.sanity as sn


@rfm.simple_test
class OpenCLCheck(rfm.RegressionTest):
    valid_systems = ['daint:gpu', 'dom:gpu', 'hohgant:nvgpu']
    valid_prog_environs = ['PrgEnv-cray', 'PrgEnv-nvidia']
    build_system = 'SingleSource'
    sourcepath = 'vecAdd.c'
    sourcesdir = 'src/opencl'
    num_gpus_per_node = 1
    executable = 'vecAdd'
    maintainers = ['TM', 'SK']
    tags = {'production', 'craype'}

    @run_after('init')
    def restrict_environments_hohgant(self):
        if self.current_system.name not in {'dom', 'daint'}:
            self.valid_prog_environs = ['PrgEnv-nvidia']

    @run_after('setup')
    def setup_modules(self):
        if (self.current_environ.name == 'PrgEnv-cray' and
            self.current_system.name in {'dom', 'daint'}):
            self.modules = ['craype-accel-nvidia60']

    @run_before('compile')
    def setflags(self):
        include_path = '$CRAY_NVIDIA_PREFIX/cuda/include'
        libpath = '$CRAY_NVIDIA_PREFIX/cuda/lib64'
        self.build_system.cflags = [f'-I{include_path}']
        self.build_system.ldflags = [f'-L{libpath}', '-lOpenCL']

    @run_before('sanity')
    def set_sanity(self):
        self.sanity_patterns = sn.assert_found('SUCCESS', self.stdout)
