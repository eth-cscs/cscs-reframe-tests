# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class SarusPullCommandCheck(rfm.RunOnlyRegressionTest):
    sourcesdir = None
    valid_systems = ['+sarus']
    valid_prog_environs = ['builtin']
    num_tasks = 1
    num_tasks_per_node = 1
    executable = 'sarus pull alpine && echo CHECK_SUCCESSFUL'
    prerun_cmds = ['sarus --version', 'unset XDG_RUNTIME_DIR']

    @run_after('setup')
    def set_modules(self):
        if self.current_system.name not in {'eiger', 'pilatus', 'hohgant'}:
            self.modules = ['sarus']

    @sanity_function
    def assert_sanity(self):
        return sn.assert_found(r'CHECK_SUCCESSFUL', self.stdout)
