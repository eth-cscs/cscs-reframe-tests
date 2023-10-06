# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class build_device_count(rfm.CompileOnlyRegressionTest):
    '''Fixture for building the device counter binary'''
    valid_systems = ['*']
    valid_prog_environs = ['+cuda']
    sourcepath = 'deviceCounter.cu'
    num_tasks_per_node = 1

    @run_before('compile')
    def setup_compilers(self):
        self.build_system.ldflags = ['-lnvidia-ml']

    @sanity_function
    def validate_build(self):
        # If build fails, the test will fail before reaching this point.
        return True
