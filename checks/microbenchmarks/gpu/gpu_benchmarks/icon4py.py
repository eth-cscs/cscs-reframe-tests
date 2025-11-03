# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
from uenv import uarch


@rfm.simple_test
class ICON4PyBenchmarks(rfm.RegressionTest):
    descr = 'ICON4Py GPU benchmarks'
    maintainers = ['SSA']
    valid_systems = ['+uenv +amdgpu', '+uenv +nvgpu']
    valid_prog_environs = ['+uenv +prgenv +rocm', '+uenv +prgenv +cuda']
    sourcesdir = None
    prebuild_cmds = [
        'git clone --depth 1 -b main https://github.com/C2SM/icon4py.git',
        'cd icon4py',
        'curl -LsSf https://astral.sh/uv/install.sh | sh ',
    ]
    time_limit = '2m'
    build_locally = False
    tags = {'production', 'uenv'}
    executable = 'nox'

    @run_before('compile')
    def activate_venv(self):
        self.prebuild_cmds += [
            'uv sync --extra all',
            'source ./venv/bin/activate'
        ]

    @run_before('run')
    def activate_venv(self):
        self.prerun_cmds += [
            'nox -s __bencher_baseline_CI-3.10 -- --backend=$BACKEND --grid=$GRID',
            # TODO
        ]
