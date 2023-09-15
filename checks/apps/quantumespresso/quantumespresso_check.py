# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib
import re
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))
from extra_launcher_options import ExtraLauncherOptionsMixin
from sarus_extra_launcher_options import SarusExtraLauncherOptionsMixin
from cuda_visible_devices_all import CudaVisibleDevicesAllMixin

qe_tests = {
    'Au-surf': {
        'hohgant:cpu': {
            'energy_reference': -11427.09017218,
            'performance_reference': [{
                'N': 1,    # number of nodes
                'R': 32,   # ranks per node
                'T': 4,    # threads per rank
                'P': 55.4  # performance. here is time to solution
                }
            ]
        },
        'hohgant:nvgpu': {
            'energy_reference': -11427.09017218,
            'performance_reference': [{
                'N': 1,    # number of nodes
                'R': 4,    # ranks per node
                'T': 16,   # threads per rank
                'P': 55.4  # performance. here is time to solution
                }
            ]
        }
    }
}

class QuantumESPRESSOCheck(rfm.RunOnlyRegressionTest):
    energy_tolerance = 1.0e-6
    test_name = 'Au-surf'
    executable = 'pw.x'
    # TODO: tests should all have pw.in as input file
    executable_opts = ['-in', 'ausurf.in']
    maintainers = ['antonk']

    @sanity_function
    def assert_simulation_success(self):
        energy = sn.extractsingle(r'!\s+total energy\s+=\s+(?P<energy>\S+) Ry',
                                  self.stdout, 'energy', float)
        energy_diff = sn.abs(energy-self.energy_reference)
        return sn.all([
            sn.assert_found(r'convergence has been achieved', self.stdout),
            sn.assert_lt(energy_diff, self.energy_tolerance)
        ])

    @performance_function('s')
    def time(self):
        return sn.extractsingle(r'electrons.+\s(?P<wtime>\S+)s WALL',
                                self.stdout, 'wtime', float)

    @run_after('init')
    def setup_test(self):
        self.descr = (f'QuantumESPRESSO ground state SCF check')
        self.env_vars = {
            'OMP_NUM_THREADS': '$SLURM_CPUS_PER_TASK'
        }

    @run_after('setup')
    def setup_reference_dict(self):
        self.ref_dict = (
            qe_tests[self.test_name][self.current_partition.fullname]
        )

    @run_after('setup')
    def setup_resources(self):
        N = self.ref_dict['performance_reference'][0]['N']
        R = self.ref_dict['performance_reference'][0]['R']
        T = self.ref_dict['performance_reference'][0]['T']

        self.num_tasks = N * R
        self.num_cpus_per_task = T
        self.num_tasks_per_node = R

    @run_before('sanity')
    def set_sanity_reference(self):
        self.energy_reference = self.ref_dict['energy_reference']

    @run_before('performance')
    def set_performance_reference(self):
        self.reference = {
            '*': {'time': (self.ref_dict['performance_reference'][0]['P'],
                           None, 0.10, 's')}
        }

@rfm.simple_test
class SARUS_QuantumESPRESSOCheck(QuantumESPRESSOCheck, SarusExtraLauncherOptionsMixin, CudaVisibleDevicesAllMixin):
    tags = {'production', 'sarus'}
    container_image = variable(str, value='NULL')
    valid_prog_environs = ['builtin']
    valid_systems = ['+nvgpu +cpu']

    @run_after('setup')
    def setup_container_platform(self):
        # if container_image was provided then initialize a container execution
        if self.container_image != 'NULL':
            self.container_platform = 'Sarus'
            self.container_platform.image = self.container_image
            self.container_platform.with_mpi = False
            self.container_platform.pull_image = False
            self.container_platform.command = (
                f'{self.executable} {" ".join(self.executable_opts)}'
            )
        #else stop here, container_image can't be empty


@rfm.simple_test
class UENV_QuantumESPRESSOCheck(QuantumESPRESSOCheck, ExtraLauncherOptionsMixin, CudaVisibleDevicesAllMixin):
    tags = {'production', 'uenv'}
    valid_prog_environs = ['+quantum-espresso']
    valid_systems = ['+nvgpu +cpu +uenv']

    @run_after('setup')
    def setup_uenv_modules(self):
        # is self.modules needed here?
        modules = ['quantum-espresso']

