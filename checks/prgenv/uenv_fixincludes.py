# Copyright 2016-2025 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class UenvFixincludes(rfm.RunOnlyRegressionTest):
    descr = '''
    Check that GCC is not "fixing" the pthread.h header. See
    https://github.com/spack/spack-packages/pull/2596 for an overview and links
    to further details.
    '''

    valid_systems = ['+uenv +remote +scontrol']
    valid_prog_environs = ['+uenv']
    maintainers = ['msimberg', 'SSA']

    time_limit = '1m'
    num_tasks_per_node = 1
    sourcesdir = None
    executable = 'find'
    executable_opts = ["/user-environment", "/user-tools", "-type", "f", "-name", "pthread.h"]
    tags = {'production', 'maintenance', 'uenv'}

    @sanity_function
    def validate(self):
        return sn.assert_not_found(r'include-fixed', self.stdout)
