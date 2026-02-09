# Copyright ETHZ/CSCS
# See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class InvalidAccount(rfm.RunOnlyRegressionTest):
    valid_systems = ['-remote']
    valid_prog_environs = ['+builtin']
    local = True
    sourcesdir = None
    executable = 'srun'
    executable_opts = [
        '--account=abcd1234', 'echo', 'this job should never start']
    tags = {'production', 'maintenance'}
    maintainers = ['VCUE', 'perettig']

    @run_before('setup')
    def skip_on_uenv(self):
        self.skip_if('UENV' in os.environ, 'Skipping when UENV is set')

    @sanity_function
    def validate(self):
        return sn.assert_found(r'nvalid account', self.stderr)
