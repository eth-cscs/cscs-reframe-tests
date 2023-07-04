# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent / 'mixins'))

from cuda_visible_devices_all import CudaVisibleDevicesAllMixin


class LAMMPSCheck(rfm.RunOnlyRegressionTest):
    scale = parameter(['small', 'large'])
    valid_systems = ['*']
    valid_prog_environs = ['+lammps']
    executable = 'lmp'
    modules = ['lammps']
    tags = {'uenv'}
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
class LAMMPSGPUCheck(CudaVisibleDevicesAllMixin, LAMMPSCheck):
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['+lammps +cuda']
    executable = 'lmp'
    modules = ['cuda', 'lammps']
    refs_by_scale = {
        'small': {
            'hohgant': {'perf': (1566.979, -0.10, None, 'timesteps/s')}
        },
        'large': {
            'hohgant': {'perf': (1566.979, -0.10, None, 'timesteps/s')}
        }
    }

    @run_after('setup')
    def set_test_parameters(self):
        self.descr = f'LAMMPS GPU check (version: {self.scale})'
        self.executable_opts = [
            '-sf gpu', f'-pk gpu {gpu_count}', '-in in.lj.gpu'
        ]

        if self.scale == 'small':
            self.num_tasks = 12
            self.num_tasks_per_node = self.num_gpus_per_node
        else:
            self.num_tasks = 32
            self.num_tasks_per_node = self.num_gpus_per_node

        self.reference = self.refs_by_scale[self.scale]


@rfm.simple_test
class LAMMPSCPUCheck(LAMMPSCheck):
    refs_by_scale = {
        'small': {
            'hohgant': {'perf': (3807.095, -0.10, None, 'timesteps/s')},
        },
        'large': {
            'hohgant': {'perf': (7247.484, -0.10, None, 'timesteps/s')}
        }
    }

    @run_after('init')
    def setup_by_scale(self):
        self.descr = f'LAMMPS CPU check (version: {self.scale})'
        self.executable_opts = ['-in in.lj.cpu']
        self.num_tasks_per_node = 128
        self.num_tasks = 256 if self.scale == 'small' else 512
        self.reference = self.refs_by_scale[self.scale]
