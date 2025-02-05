# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


class Cp2kCheck(rfm.RunOnlyRegressionTest):
    modules = ['CP2K']
    executable = 'cp2k.psmp'
    executable_opts = ['H2O-256.inp']
    maintainers = ['LM']
    tags = {'scs'}
    strict_check = False
    extra_resources = {
        'switches': {
            'num_switches': 1
        }
    }

    @sanity_function
    def assert_energy_diff(self):
        energy = sn.extractsingle(
            r'\s+ENERGY\| Total FORCE_EVAL \( QS \) '
            r'energy [\[\(]a\.u\.[\]\)]:\s+(?P<energy>\S+)',
            self.stdout, 'energy', float, item=-1
        )
        energy_reference = -4404.2323
        energy_diff = sn.abs(energy-energy_reference)
        return sn.all([
            sn.assert_found(r'PROGRAM STOPPED IN', self.stdout),
            sn.assert_eq(sn.count(sn.extractall(
                r'(?i)(?P<step_count>STEP NUMBER)',
                self.stdout, 'step_count')), 10),
            sn.assert_lt(energy_diff, 1e-4)
        ])

    @performance_function('s')
    def time(self):
        return sn.extractsingle(r'^ CP2K(\s+[\d\.]+){4}\s+(?P<perf>\S+)',
                                self.stdout, 'perf', float)


@rfm.simple_test
class Cp2kCpuCheck(Cp2kCheck):
    scale = parameter(['small', 'large'])
    valid_systems = ['eiger:mc', 'pilatus:mc']
    valid_prog_environs = ['cpeGNU']
    refs_by_scale = {
        'small': {
            'eiger:mc': {'time': (76.116, None, 0.08, 's')},
            'pilatus:mc': {'time': (70.568, None, 0.08, 's')}
        },
        'large': {
            'eiger:mc': {'time': (54.381, None, 0.05, 's')},
            'pilatus:mc': {'time': (49.916, None, 0.05, 's')}
        }
    }

    @run_after('init')
    def setup_by__scale(self):
        self.descr = f'CP2K CPU check (version: {self.scale})'
        self.tags |= {'maintenance', 'production'}
        if self.scale == 'small':
            self.num_tasks = 96
            self.num_tasks_per_node = 16
            self.num_cpus_per_task = 16
            self.num_tasks_per_core = 1
            self.use_multithreading = False
            self.env_vars = {
                'MPICH_OFI_STARTUP_CONNECT': 1,
                'OMP_NUM_THREADS': 8,
                'OMP_PLACES': 'cores',
                'OMP_PROC_BIND': 'close'
            }
        else:
            self.num_tasks = 256
            self.num_tasks_per_node = 16
            self.num_cpus_per_task = 16
            self.num_tasks_per_core = 1
            self.use_multithreading = False
            self.env_vars = {
                'MPICH_OFI_STARTUP_CONNECT': 1,
                'OMP_NUM_THREADS': 8,
                'OMP_PLACES': 'cores',
                'OMP_PROC_BIND': 'close'
            }

        self.reference = self.refs_by_scale[self.scale]

    @run_before('run')
    def set_task_distribution(self):
        self.job.options = ['--distribution=block:block']

    @run_before('run')
    def set_cpu_binding(self):
        self.job.launcher.options = ['--cpu-bind=cores']


@rfm.simple_test
class Cp2kGpuCheck(Cp2kCheck):
    scale = parameter(['small', 'large'])
    valid_systems = []
    valid_prog_environs = []
    num_gpus_per_node = 1
    num_tasks_per_node = 6
    num_cpus_per_task = 2
    env_vars = {
        'CRAY_CUDA_MPS': '1',
        'OMP_NUM_THREADS': str(num_cpus_per_task)
    }
    refs_by_scale = {
        'small': {
            'dom:gpu': {'time': (176.153, None, 0.10, 's')},
            'daint:gpu': {'time': (179.683, None, 0.10, 's')}
        },
        'large': {
            'daint:gpu': {'time': (140.498, None, 0.10, 's')}
        }
    }

    @run_after('init')
    def setup_by_scale(self):
        self.descr = f'CP2K GPU check (version: {self.scale})'
        if self.scale == 'small':
            self.valid_systems += []
            self.num_tasks = 36
        else:
            self.num_tasks = 96

        self.reference = self.refs_by_scale[self.scale]
        self.tags |= {'maintenance', 'production'}
