# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class OsReleaseCheck(rfm.RunOnlyRegressionTest):
    descr = 'OS installation check - verify SUSE Linux Enterprise Server 15 SP6 is installed'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-OSINSTALL'}
    executable = 'cat'
    executable_opts = ['/etc/os-release']

    @sanity_function
    def assert_correct_os(self):
       expected_map = {
        'daint': r'PRETTY_NAME="SUSE Linux Enterprise Server 15 SP6"',
        'eiger': r'PRETTY_NAME="SUSE Linux Enterprise Server 15 SP5"',
        }

       expected = expected_map[self.current_system.name]
       return sn.assert_found(expected, self.stdout)


@rfm.simple_test
class OsLocaleCheck(rfm.RunOnlyRegressionTest):
    descr = 'OS installation check - verify system locale is set to en_US.UTF-8'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-OSINSTALL'}
    executable = 'cat'
    executable_opts = ['/etc/locale.conf']

    @sanity_function
    def assert_correct_locale(self):
        return sn.assert_found(r'LANG=en_US.UTF-8', self.stdout)


@rfm.simple_test
class OsServiceSshDaemon(rfm.RunOnlyRegressionTest):
    descr = 'OS service check - verify SSH daemon process is running'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-OSSERVICE'}
    
    executable = 'pgrep'
    executable_opts = ['-u', 'root', '-f', '/usr/sbin/sshd']

    @sanity_function
    def assert_sshd_running(self):
        return sn.assert_eq(self.job.exitcode, 0)

@rfm.simple_test
class OsServiceSsh(rfm.RunOnlyRegressionTest):
    descr = 'OS service check - verify SSH service is listening on port 22'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-OSSERVICE'}
    executable = 'bash'
    executable_opts = ['-c', '/usr/bin/ss -ltup | grep :ssh || echo FAILED']

    @sanity_function
    def assert_ssh_listening(self):
        return sn.assert_not_found(r'FAILED', self.stdout)


@rfm.simple_test
class OsServiceHttpNotRunning(rfm.RunOnlyRegressionTest):
    descr = 'OS service check - verify HTTP service is not listening (security check)'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-OSSERVICE'}
    
    executable = 'ss'
    executable_opts = ['-ltup']

    @sanity_function
    def assert_http_not_listening(self):
        return sn.assert_not_found(r':http\b', self.stdout)

