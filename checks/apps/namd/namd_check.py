# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class NamdCheck(rfm.RunOnlyRegressionTest):
    scale = parameter(['small', 'large'])
    arch = parameter(['cpu'])
    valid_systems = ['eiger:mc', 'pilatus:mc']
    valid_prog_environs = ['cpeGNU']
    modules = ['NAMD']
    executable = 'namd2'
    use_multithreading = True
    num_tasks_per_core = 2
    maintainers = ['CB', 'LM']
    tags = {'scs', 'external-resources'}
    extra_resources = {
        'switches': {
            'num_switches': 1
        }
    }

    @run_after('init')
    def adapt_description(self):
        self.descr = f'NAMD check ({self.arch})'
        self.tags |= {'maintenance', 'production'}

    @run_after('init')
    def setup_parallel_run(self):
        # On Eiger a no-smp NAMD version is the default
        self.executable_opts = ['+idlepoll', 'stmv.namd']
        self.num_cpus_per_task = 2

        if self.scale == 'small':
            self.num_tasks = 768
            self.num_tasks_per_node = 128
        else:
            self.num_tasks = 2048
            self.num_tasks_per_node = 128

    @run_before('compile')
    def prepare_build(self):
        # Reset sources dir relative to the SCS apps prefix
        self.sourcesdir = os.path.join(self.current_system.resourcesdir,
                                       'NAMD', 'prod')

    @sanity_function
    def validate_energy(self):
        energy = sn.avg(sn.extractall(
            r'ENERGY:([ \t]+\S+){10}[ \t]+(?P<energy>\S+)',
            self.stdout, 'energy', float)
        )
        energy_reference = -2451359.5
        energy_diff = sn.abs(energy - energy_reference)
        return sn.all([
            sn.assert_eq(sn.count(sn.extractall(
                         r'TIMING: (?P<step_num>\S+)  CPU:',
                         self.stdout, 'step_num')), 50),
            sn.assert_lt(energy_diff, 2720)
        ])

    @run_before('performance')
    def set_reference(self):
        if self.scale == 'small':
            self.reference = {
                'eiger:mc': {'days_ns': (0.126, None, 0.05, 'days/ns')},
                'pilatus:mc': {'days_ns': (0.128, None, 0.05, 'days/ns')},
            }
        else:
            self.reference = {
                'eiger:mc': {'days_ns': (0.057, None, 0.05, 'days/ns')},
                'pilatus:mc': {'days_ns': (0.054, None, 0.10, 'days/ns')}
            }

    @performance_function('days/ns')
    def days_ns(self):
        return sn.avg(sn.extractall(
            r'Info: Benchmark time: \S+ CPUs \S+ '
            r's/step (?P<days_ns>\S+) days/ns \S+ MB memory',
            self.stdout, 'days_ns', float))
