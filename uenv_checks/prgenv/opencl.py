# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class OpenCLCheck(rfm.RegressionTest):
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['+cuda']
    build_locally = False
    build_system = 'SingleSource'
    sourcepath = 'vecAdd.c'
    sourcesdir = 'src/opencl'
    num_gpus_per_node = 1
    executable = 'vecAdd'
    tags = {'production', 'craype'}

    @run_before('compile')
    def setflags(self):
        self.build_system.cflags = ['-I$CUDA_HOME/include']
        self.build_system.ldflags = ['-L$CUDA_HOME/lib64', '-lOpenCL']

    @run_before('sanity')
    def set_sanity(self):
        self.sanity_patterns = sn.assert_found('SUCCESS', self.stdout)
