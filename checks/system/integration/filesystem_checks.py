# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class FilesystemDfCompletion(rfm.RunOnlyRegressionTest):
    descr = 'Filesystem sanity check - verify df command completes successfully'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-FS'}
    executable = 'timeout'
    executable_opts = ['-v', '-k', '5', '3', 'df']

    @sanity_function
    def assert_no_timeout(self):
        return sn.assert_not_found(r'sending signal', self.stderr)


@rfm.simple_test
class FilesystemCapacityCheck(rfm.RunOnlyRegressionTest):
    descr = 'Filesystem sanity check - verify no filesystems at 100% capacity'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-FS'}

    executable = 'timeout'
    executable_opts = ['-v', '-k', '3', '3', 'df']

    @sanity_function
    def assert_no_full_filesystems(self):
        return sn.all([
            sn.assert_not_found(r'100%', self.stdout),
            sn.assert_not_found(r'sending signal', self.stderr)
        ])
