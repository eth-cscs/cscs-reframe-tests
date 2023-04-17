# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os

import reframe as rfm
import reframe.utility.sanity as sn


class LAMMPSCheck(rfm.RunOnlyRegressionTest):
    scale = parameter(['small', 'large'])
    valid_systems = ['*']
    valid_prog_environs = ['+lammps']
    executable = 'lmp'
    modules = ['lammps']
    tags = {'external-resources', 'maintenance', 'production'}
    maintainers = ['TM']
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

    @performance_function('timesteps/s')
    def perf(self):
        return sn.extractsingle(r'\s+(?P<perf>\S+) timesteps/s',
                                self.stdout, 'perf', float)

    @sanity_function
    def assert_energy_diff(self):
        energy_reference = -4.6195
        energy = sn.extractsingle(
            r'^\s+500000(\s+\S+){3}\s+(?P<energy>\S+).*$',
            self.stdout, 'energy', float)
        energy_diff = sn.abs(energy - energy_reference)
        return sn.all([
            sn.assert_found(r'Total wall time:', self.stdout),
            sn.assert_lt(energy_diff, 6e-4)
        ])


@rfm.simple_test
class LAMMPSGPUCheck(LAMMPSCheck):
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['+lammps +cuda']
    executable = 'lmp'
    modules = ['cuda', 'lammps']
    #env_vars = {'CRAY_CUDA_MPS': 1}
    num_gpus_per_node = 1
    refs_by_scale = {
        'small': {
            'hohgant-uenv': {'perf': (1566.979, -0.10, None, 'timesteps/s')}
        },
        'large': {
            'hohgant-uenv': {'perf': (1566.979, -0.10, None, 'timesteps/s')}
        }
    }

    @run_after('setup')
    def set_test_parameters(self):
        self.descr = f'LAMMPS GPU check (version: {self.scale})'
        curr_part = self.current_partition
        gpu_count = curr_part.select_devices('gpu')[0].num_devices
        #self.num_gpus_per_node = gpu_count
        cuda_visible_devices = ','.join(f'{i}' for i in range(gpu_count))
        self.env_vars['CUDA_VISIBLE_DEVICES'] = cuda_visible_devices
        self.executable_opts = [
            '-sf gpu', f'-pk gpu {gpu_count}', '-in in.lj.gpu'
        ]

        if self.scale == 'small':
            self.num_tasks = 12
            self.num_tasks_per_node = gpu_count
        else:
            self.num_tasks = 32
            self.num_tasks_per_node = gpu_count

        self.reference = self.refs_by_scale[self.scale]
        

@rfm.simple_test
class LAMMPSCPUCheck(LAMMPSCheck):
    refs_by_scale = {
        'small': {
            'hohgant-uenv': {'perf': (3807.095, -0.10, None, 'timesteps/s')},
        },
        'large': {
            'hohgant-uenv': {'perf': (7247.484, -0.10, None, 'timesteps/s')}
        }
    }

    @run_after('init')
    def setup_by_scale(self):
        self.descr = f'LAMMPS CPU check (version: {self.scale})'
        self.executable_opts = ['-in in.lj.cpu']
        self.num_tasks_per_node = 128
        self.num_tasks = 256 if self.scale == 'small' else 512
        self.reference = self.refs_by_scale[self.scale]
