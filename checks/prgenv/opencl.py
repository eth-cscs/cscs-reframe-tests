# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


class OpenCLBase(rfm.RegressionTest):
    build_locally = False
    build_system = 'SingleSource'
    sourcepath = 'vecAdd.c'
    sourcesdir = 'src/opencl'
    num_gpus_per_node = 1
    executable = 'vecAdd'

    @run_before('sanity')
    def set_sanity(self):
        self.sanity_patterns = sn.assert_found('SUCCESS', self.stdout)


@rfm.simple_test
class CPE_OpenCLCheck(OpenCLBase):
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['+cuda +opencl -uenv']
    tags = {'production', 'craype'}

    @run_after('setup')
    def setup_modules(self):
        sm = self.current_partition.select_devices('gpu')[0].arch[-2:]
        self.modules = ['cudatoolkit', f'craype-accel-nvidia{sm}']

    @run_before('compile')
    def setflags(self):
        self.build_system.cflags = ['$CRAY_CUDATOOLKIT_INCLUDE_OPTS']
        self.build_system.ldflags = ['$CRAY_CUDATOOLKIT_POST_LINK_OPTS',
                                     '-lOpenCL']


@rfm.simple_test
class UENV_OpenCLCheck(OpenCLBase):
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['+cuda +opencl +uenv']
    tags = {'production', 'uenv'}

    @run_before('compile')
    def setflags(self):
        self.build_system.cflags = ['-I$CUDA_HOME/include']
        self.build_system.ldflags = ['-L$CUDA_HOME/lib64', '-lOpenCL']
