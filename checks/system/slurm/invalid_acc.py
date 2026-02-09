# Copyright 2026 ETHZ/CSCS
# See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class InvalidAccount(rfm.RunOnlyRegressionTest):
    valid_systems = ['-remote']
    valid_prog_environs = ['builtin']
    local = True
    executable = 'srun -N1 -A abcd1234 echo FAILED'
    tags = {'production', 'maintenance'}
    maintainers = ['VCUE', 'perettig']

    @sanity_function
    def validate(self):
        return sn.assert_found(r'nvalid account', self.stderr) 
