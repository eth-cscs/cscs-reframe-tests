# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class linaro_ddt(rfm.RunOnlyRegressionTest):
    valid_systems = ['*']
    valid_prog_environs = ['+ddt +map']
    sourcesdir = 'src/linaro'
    executable = 'exe'
    rpt = variable(str, value='rpt.txt')

    @run_before('run')
    def setup_ddt_flags(self):
        self.prerun_cmds = [f'g++ -g -O3 -o {self.executable} hello.cpp']
        self.postrun_cmds = [
            'echo "# --- DDT:" ;echo "# --- DDT:" >&2',
            f'ddt --nompi --offline --output=rpt.txt {self.executable}',
            'echo "# --- MAP:" ;echo "# --- MAP:" >&2',
            f'map --nompi --profile {self.executable}',
        ]

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
            sn.assert_found(
                f'Offline log written to:.*{self.rpt}', self.stderr),
            sn.assert_found('Startup complete', self.rpt),
            sn.assert_found(
                'Every process in your program has terminated', self.rpt),
            sn.assert_found('MAP generated', self.stderr),
        ])
