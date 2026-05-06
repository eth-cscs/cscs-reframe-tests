# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class PingLdap(rfm.RunOnlyRegressionTest):
    descr = 'Ping ldap.cscs.ch'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-LDAP'}

    executable = 'ping'
    executable_opts = ['-n', '-q', '-c', '5', 'ldap.cscs.ch']

    @sanity_function
    def validate(self):
        return sn.assert_found(
            r'5 packets transmitted, 5 received, 0% packet loss',
            self.stdout
        )

@rfm.simple_test
class GetentTimeoutCheck(rfm.RunOnlyRegressionTest):
    descr = 'Verify getent hosts works within timeout'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-LDAP'}
    executable = 'timeout'
    executable_opts = ['-v', '-k', '3', '3', 'getent', 'hosts']

    @sanity_function
    def validate(self):
        return sn.all([
            sn.assert_found(r'localhost', self.stdout),
            sn.assert_not_found(r'sending signal', self.stderr)
        ])