# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class TinyEGLTest(rfm.RegressionTest):
    descr = 'Test OpenGL without X server'
    valid_systems = ['daint:gpu', 'dom:gpu']
    valid_prog_environs = ['PrgEnv-gnu']
    prerun_cmds = ['unset DISPLAY']
    executable = 'tinyegl'
    nvidia_path = '/usr/lib64'
    build_system = 'Make'
    tags = {'production'}

    @run_before('compile')
    def set_build_system_opts(self):
        self.build_system.options = [f'PATH_TO_LIB={self.nvidia_path}']
        self.env_vars = {
            'LD_LIBRARY_PATH': f'{self.nvidia_path}:$LD_LIBRARY_PATH'}

    @sanity_function
    def assert_found_pattern(self):
        return sn.assert_found(
            '0  0  0  0  0  0 76 51 25 76 51 25 76 '
            '51 25 76 51 25 76 51 25  0  0  0  0  0  0', self.stdout)
