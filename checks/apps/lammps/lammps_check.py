# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os

import reframe as rfm
import reframe.utility.sanity as sn


class LAMMPSCheck(rfm.RunOnlyRegressionTest):
    scale = parameter(['small', 'large'])
    modules = ['cray-python', 'LAMMPS']
    tags = {'external-resources', 'maintenance', 'production'}
    maintainers = ['LM']
    strict_check = False
    extra_resources = {
        'switches': {
            'num_switches': 1
        }
    }

    @run_after('init')
    def setup_by_system(self):
        # Reset sources dir relative to the SCS apps prefix
        self.sourcesdir = os.path.join(self.current_system.resourcesdir,
                                       'LAMMPS')
        if self.current_system.name in ['eiger', 'pilatus']:
            self.valid_prog_environs = ['cpeGNU']
        else:
            self.valid_prog_environs = ['builtin']

    @performance_function('timesteps/s')
    def perf(self):
        return sn.extractsingle(r'\s+(?P<perf>\S+) timesteps/s',
                                self.stdout, 'perf', float)

    @sanity_function
    def assert_energy_diff(self):
        energy_reference = -4.6195
        energy = sn.extractsingle(
            r'\s+500000(\s+\S+){3}\s+(?P<energy>\S+)\s+\S+\s\n',
            self.stdout, 'energy', float)
        energy_diff = sn.abs(energy - energy_reference)
        return sn.all([
            sn.assert_found(r'Total wall time:', self.stdout),
            sn.assert_lt(energy_diff, 6e-4)
        ])


@rfm.simple_test
class LAMMPSGPUCheck(LAMMPSCheck):
    valid_systems = []
    executable = 'lmp_mpi'
    executable_opts = ['-sf gpu', '-pk gpu 1', '-in in.lj.gpu']
    env_vars = {'CRAY_CUDA_MPS': 1}
    num_gpus_per_node = 1
    refs_by_scale = {
        'small': {
            'dom:gpu': {'perf': (3456.792, -0.10, None, 'timesteps/s')},
            'daint:gpu': {'perf': (1566.979, -0.10, None, 'timesteps/s')}
        },
        'large': {
            'daint:gpu': {'perf': (2108.561, -0.10, None, 'timesteps/s')}
        }
    }

    @run_after('init')
    def setup_by_scale(self):
        self.descr = f'LAMMPS GPU check (version: {self.scale})'
        if self.scale == 'small':
            self.valid_systems += []
            self.num_tasks = 12
            self.num_tasks_per_node = 2
        else:
            self.num_tasks = 32
            self.num_tasks_per_node = 2

        self.reference = self.refs_by_scale[self.scale]


@rfm.simple_test
class LAMMPSCPUCheck(LAMMPSCheck):
    valid_systems = ['eiger:mc', 'pilatus:mc']
    refs_by_scale = {
        'small': {
            'eiger:mc': {'perf': (3807.095, -0.10, None, 'timesteps/s')},
            'pilatus:mc': {'perf': (4828.986, -0.10, None, 'timesteps/s')}
        },
        'large': {
            'eiger:mc': {'perf': (4922.81, -0.10, None, 'timesteps/s')},
            'pilatus:mc': {'perf': (7247.484, -0.10, None, 'timesteps/s')}
        }
    }

    @run_after('init')
    def setup_by_scale(self):
        self.descr = f'LAMMPS CPU check (version: {self.scale})'
        if self.current_system.name in ['eiger', 'pilatus']:
            self.executable = 'lmp_mpi'
            self.executable_opts = ['-in in.lj.cpu']
        else:
            self.executable = 'lmp_omp'
            self.executable_opts = ['-sf omp', '-pk omp 1', '-in in.lj.cpu']

        if self.scale == 'small':
            self.valid_systems += []
            self.num_tasks = 216
            self.num_tasks_per_node = 36
        else:
            self.num_tasks_per_node = 36
            self.num_tasks = 576

        if self.current_system.name == 'eiger':
            self.num_tasks_per_node = 128
            self.num_tasks = 256 if self.scale == 'small' else 512

        self.reference = self.refs_by_scale[self.scale]
