# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class BasicSanityTimeoutSuccess(rfm.RunOnlyRegressionTest):
    descr = 'Basic sanity check for timeout command - verify successful process exit'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-SLEEP'}
    executable = 'timeout'
    executable_opts = ['-v', '-k', '3', '3', 'sleep', '1']

    @sanity_function
    def assert_exit_ok(self):
        return sn.assert_not_found(r'sending signal', self.stderr)


@rfm.simple_test
class BasicSanityTimeoutSignal(rfm.RunOnlyRegressionTest):
    descr = 'Basic sanity check for timeout command - verify signal delivery (TERM)'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-SLEEP'}
    executable = 'timeout'
    executable_opts = ['-v', '-k', '3', '2', 'sleep', '4']

    @sanity_function
    def assert_signal_sent(self):
        return sn.assert_found(r'sending signal TERM', self.stderr)
