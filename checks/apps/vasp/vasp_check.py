# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class VASPCheck(rfm.RunOnlyRegressionTest):
    valid_prog_environs = ['cpeIntel']
    modules = ['VASP']
    executable = 'vasp_std'
    extra_resources = {
        'switches': {
            'num_switches': 1
        }
    }
    keep_files = ['OUTCAR']
    strict_check = False
    use_multithreading = False
    tags = {'maintenance', 'production'}
    maintainers = ['LM']

    num_nodes = parameter([6, 16], loggable=True)
    allref = {
        6: {
            'zen2': {
                'eiger:mc': {'elapsed_time': (112.347, None, 0.10, 's')},
                'pilatus:mc': {'elapsed_time': (89.083, None, 0.10, 's')},
            },
        },
        16: {
            'zen2': {
                'eiger:mc': {'elapsed_time': (69.459, None, 0.10, 's')},
                'pilatus:mc': {'elapsed_time': (100.0, None, 0.10, 's')}
            }
        }
    }

    @performance_function('s')
    def elapsed_time(self):
        return sn.extractsingle(r'Elapsed time \(sec\):'
                                r'\s+(?P<time>\S+)', 'OUTCAR',
                                'time', float)

    @sanity_function
    def assert_reference(self):
        force = sn.extractsingle(r'1 F=\s+(?P<result>\S+)',
                                 self.stdout, 'result', float)
        return sn.assert_reference(force, -.85026214E+03, -1e-5, 1e-5)

    @run_after('init')
    def setup_system_filtering(self):
        self.descr = f'VASP check ({self.num_nodes} node(s))'

        # setup system filter
        valid_systems = {
            6: ['eiger:mc', 'pilatus:mc'],
            16: ['eiger:mc']
        }

        self.skip_if(self.num_nodes not in valid_systems,
                     f'No valid systems found for {self.num_nodes}(s)')
        self.valid_systems = valid_systems[self.num_nodes]

        # setup programming environment filter

    @run_before('run')
    def setup_run(self):
        # set auto-detected architecture
        self.skip_if_no_procinfo()
        proc = self.current_partition.processor
        arch = proc.arch

        try:
            found = self.allref[self.num_nodes][arch]
        except KeyError:
            self.skip(f'Configuration with {self.num_nodes} node(s) '
                      f'is not supported on {arch!r}')

        # common setup for every architecture
        self.job.launcher.options = ['--cpu-bind=cores']
        self.job.options = ['--distribution=block:block']
        self.num_tasks_per_node = proc.num_sockets
        self.num_cpus_per_task = proc.num_cores // self.num_tasks_per_node
        self.num_tasks = self.num_nodes * self.num_tasks_per_node
        self.env_vars = {
            'OMP_NUM_THREADS': self.num_cpus_per_task,
            'OMP_PLACES': 'cores',
            'OMP_PROC_BIND': 'close'
        }

        # custom settings for selected architectures
        if arch == 'zen2':
            self.env_vars.update({
                'MPICH_OFI_STARTUP_CONNECT': 1
            })

        # setup performance references
        self.reference = self.allref[self.num_nodes][arch]
