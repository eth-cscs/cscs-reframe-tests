import os

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class run_only(rfm.RunOnlyRegressionTest):
    valid_systems = ['+uenv']
    valid_prog_environs = ['+uenv +prgenv']
    executable = 'date'
    time_limit = '1m'

    @sanity_function
    def set_sanity(self):
        return sn.assert_found(r'2026', self.stdout)
