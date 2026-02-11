# Copyright ETHZ/CSCS
# See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class MPIIntranodePinned(rfm.RegressionTest):
    description = '''Reproducer for slow intranode performance 
    with pinned memory (Known issue on Alps)
    
    Based on the test case provided by @msimberg in
    https://github.com/eth-cscs/alps-gh200-reproducers'''
    valid_systems = ['+remote']
    valid_prog_environs = ['+uenv -ce']
    sourcesdir = 'src'
    build_system = 'CMake'
    build_locally = False
    tags = {'maintenance', 'uenv'}
    maintainers = ['SSA', 'VCUE', 'msimberg', 'perettig']
    executable = 'intranode_pinned_host_comm'
    executable_opts = [
        '1',
        '2',
        'pinned_host',
        str(1 << 27)  
    ]

    @run_after('setup')
    def setup_job(self):
        self.num_tasks = 2
        self.num_tasks_per_node = 2
        self.num_nodes = 1
        self.job.launcher.options += ['--cpu-bind=sockets']

    @sanity_function
    def validate(self):
        return sn.assert_found(r'rank 0 to rank 1', self.stdout)
    
    @performance_function('s')
    def time_value(self):
        regex = r'\[0:1]\s*time:\s*(?P<t>\S+)'
        return sn.extractsingle(regex, self.stdout, 't', float)

    @run_after('init')
    def set_reference(self):
        self.reference = {
            '*': { 
                # Reference value as suggested by @msimberg 
                # based on the non-pinned test case performance.
                'time_value': (0.003, None, 0.10, 's')   
            }
        }
