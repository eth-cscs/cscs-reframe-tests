# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
from hpctestlib.sciapps.gromacs.benchmarks import gromacs_check


@rfm.simple_test
class cscs_gromacs_check(gromacs_check):
    valid_systems = ['*']
    valid_prog_environs = ['+gromacs']
    modules = ['gromacs']
    maintainers = ['TM']
    use_multithreading = False
    executable_opts += ['-dlb yes', '-ntomp 1', '-npme -1']

    # CSCS-specific parameterization
    num_nodes = parameter([1, 2], loggable=True)
    allref = {
        1: {
            'zen2': {
                'HECBioSim/Crambin': (320.0, None, None, 'ns/day'),
                'HECBioSim/Glutamine-Binding-Protein': (120.0, None, None, 'ns/day'),  # noqa: E501
                'HECBioSim/hEGFRDimer': (16.0, None, None, 'ns/day'),
                'HECBioSim/hEGFRDimerSmallerPL': (31.0, None, None, 'ns/day'),
                'HECBioSim/hEGFRDimerPair': (7.0, None, None, 'ns/day'),
            },
        },
        2: {
            'zen2': {
                'HECBioSim/Crambin': (355.0, None, None, 'ns/day'),
                'HECBioSim/Glutamine-Binding-Protein': (210.0, None, None, 'ns/day'),  # noqa: E501
                'HECBioSim/hEGFRDimer': (31.0, None, None, 'ns/day'),
                'HECBioSim/hEGFRDimerSmallerPL': (53.0, None, None, 'ns/day'),
                'HECBioSim/hEGFRDimerPair': (13.0, None, None, 'ns/day'),
            },
        },
        4: {
            'zen2': {
                'HECBioSim/Crambin': (340.0, None, None, 'ns/day'),
                'HECBioSim/Glutamine-Binding-Protein': (230.0, None, None, 'ns/day'),  # noqa: E501
                'HECBioSim/hEGFRDimer': (56.0, None, None, 'ns/day'),
                'HECBioSim/hEGFRDimerSmallerPL': (80.0, None, None, 'ns/day'),
                'HECBioSim/hEGFRDimerPair': (25.0, None, None, 'ns/day'),
                'HECBioSim/hEGFRtetramerPair': (11.0, None, None, 'ns/day'),
            },
        },
        6: {
            'zen2': {
                'HECBioSim/Glutamine-Binding-Protein': (240.0, None, None, 'ns/day'),  # noqa: E501
                'HECBioSim/hEGFRDimer': (75.0, None, None, 'ns/day'),
                'HECBioSim/hEGFRDimerSmallerPL': (110.0, None, None, 'ns/day'),
                'HECBioSim/hEGFRDimerPair': (33.0, None, None, 'ns/day'),
                'HECBioSim/hEGFRtetramerPair': (13.0, None, None, 'ns/day'),
            },
        },
        8: {
            'zen2': {
                'HECBioSim/Glutamine-Binding-Protein': (250.0, None, None, 'ns/day'),   # noqa: E501
                'HECBioSim/hEGFRDimer': (80.0, None, None, 'ns/day'),
                'HECBioSim/hEGFRDimerSmallerPL': (104.0, None, None, 'ns/day'),
                'HECBioSim/hEGFRDimerPair': (43.0, None, None, 'ns/day'),
                'HECBioSim/hEGFRtetramerPair': (20.0, None, None, 'ns/day'),
            },
        },
        16: {
            'zen2': {
                'HECBioSim/hEGFRDimer': (82.0, None, None, 'ns/day'),
                'HECBioSim/hEGFRDimerSmallerPL': (70.0, None, None, 'ns/day'),
                'HECBioSim/hEGFRDimerPair': (49.0, None, None, 'ns/day'),
                'HECBioSim/hEGFRtetramerPair': (25.0, None, None, 'ns/day'),
            },
        }
    }

    @run_after('init')
    def filter_checks(self):
        # Update test's description
        self.descr += f' ({self.num_nodes} node(s))'
        if self.nb_impl == 'gpu':
            self.valid_systems = ['+nvgpu']


    @run_before('run')
    def setup_run(self):
        self.skip_if_no_procinfo()
        proc = self.current_partition.processor
        arch = proc.arch

        try:
            found = self.allref[self.num_nodes][arch][self.bench_name]
        except KeyError:
            self.skip(f'Configuration with {self.num_nodes} node(s) of '
                      f'{self.bench_name!r} is not supported on {arch!r}')

        # Setup performance references
        self.reference = {
            '*': {
                'perf': self.allref[self.num_nodes][arch][self.bench_name]
            }
        }

        # Setup parallel run
        self.num_tasks_per_node = proc.num_cores
        self.num_tasks = self.num_nodes * self.num_tasks_per_node
