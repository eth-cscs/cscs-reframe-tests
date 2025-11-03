# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
from uenv import uarch


class ICON4PyBenchmarks(rfm.RegressionTest):
    '''
    ICON4Py GPU benchmarks.
    '''
    maintainers = ['SSA']
    valid_prog_environs = ['+uenv +prgenv +rocm', '+uenv +prgenv +cuda']
    valid_systems = ['+uenv']
    sourcesdir = None
    prerun_cmds = [
        'git clone --depth 1 -b main https://github.com/C2SM/icon4py.git',
        'cd icon4py',
        'curl -LsSf https://astral.sh/uv/install.sh | sh ',
    ]
    time_limit = '2m'
    build_locally = False
    tags = {'production', 'uenv'}
    executable = 'nox'

    @run_after('setup')
    def activate_venv(self):
        self.prerun_cmds.append(
            'uv sync --extra all',
            'source ./venv/bin/activate'
        )
