# Copyright ETHZ/CSCS
# See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn

from reframe.core.builtins import xfail


@rfm.simple_test
class MPIIntranodePinned(rfm.RegressionTest):
    descr = 'Reproducer for slow intranode performance with pinned memory'
    valid_systems = ['+remote +nvgpu']
    valid_prog_environs = ['+uenv +prgenv -ce']
    sourcesdir = 'https://github.com/eth-cscs/alps-gh200-reproducers.git'
    prebuild_cmds = ['cd intranode-pinned-host-comm']
    prerun_cmds = ['cd intranode-pinned-host-comm']
    build_system = 'CMake'
    build_locally = False
    time_limit = '2m'
    tags = {'maintenance', 'uenv'}
    maintainers = ['SSA', 'VCUE', 'msimberg', 'perettig']
    executable = 'intranode_pinned_host_comm'
    mem = parameter(['host', 'pinned_host'])

    @run_after('setup')
    def setup_job(self):
        self.num_tasks = 2
        self.num_tasks_per_node = 2
        self.job.launcher.options += ['--cpu-bind=sockets']

    @run_before('run')
    def set_exe_opts(self):
        self.executable_opts = ['2', '5', self.mem, str(1 << 27)]

    @sanity_function
    def validate(self):
        return sn.assert_found(r'rank 0 to rank 1', self.stdout)

    @performance_function('s')
    def time_value(self):
        regex = r'\[1:4]\s*time:\s*(?P<sec>\S+)'
        return sn.extractsingle(regex, self.stdout, 'sec', float)

    @run_after('init')
    def set_reference(self):
        if self.mem == 'pinned_host':
            self.reference = {
            '*': {
                # Reference value as suggested by @msimberg
                # based on the non-pinned test case performance
                'time_value': xfail('Known issue for pinned memory', 
                                    (0.003, None, 0.15, 's'))
            }
        }
        else:
            self.reference = {
            '*': {
                'time_value': (0.003, None, 0.15, 's')
            }
        }   
