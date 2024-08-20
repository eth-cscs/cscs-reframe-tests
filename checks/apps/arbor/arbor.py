# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn

@rfm.simple_test
class linaro_ddt(rfm.RunOnlyRegressionTest):
    valid_systems = ['*']
    valid_prog_environs = ['+arbor']
    sourcesdir = None
    executable = 'python3'
    env_vars = { }

    @run_before('run')
    def setup_ddt_flags(self):
        executable_opts = ['-c', 'import arbor; print(arbor.__version__)']

    @sanity_function
    def validate_solution(self):
        """
        Sanity checks:
         - "Error communicating with Licence Server velan.cscs.ch: The proxy
         type is invalid for this operation"
         - Offline log written to: 'rpt.txt'
         - message (0): Startup complete.
         - message (n/a): Every process in your program has terminated.
        """
        return sn.all([
            sn.assert_not_found('Error communicating with Licence Server',
                                self.stdout),
        ])
