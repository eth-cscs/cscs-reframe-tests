# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
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
    # N:number of nodes, R:ranks per node, T:threads per rank, P:walltime
    'Au-surf': {
        'hohgant:cpu': {
            # hohgant-cpu: 2sockets, 8 numa, 16c/numa = 128c (no MT)
            'energy_reference': -11427.09017218,
            'performance_reference': [{'N': 1, 'R': 32, 'T': 4, 'P': 55.4}]
        },
        'hohgant:nvgpu': {
            # hohgant-nvgpu: 1socket, 4 numa, 16c/numa = 64c (no MT)
            'energy_reference': -11427.09017218,
            'performance_reference': [{'N': 1, 'R': 4, 'T': 16, 'P': 55.4}]
        }
    }
}


# {{{ BASE
class QuantumESPRESSOBase(rfm.RunOnlyRegressionTest):
    energy_tolerance = 1.0e-6
    executable = 'pw.x'
    # TODO: tests should all have pw.in as input file
    executable_opts = ['-in', 'ausurf.in']

    @run_after('init')
    def set_description(self):
        self.descr = f'QuantumESPRESSO {self.test_name} check'

    @run_after('setup')
    def set_runtime_resources(self):
        self.ref_dict = (
            qe_tests[self.test_name][self.current_partition.fullname]
        )
        N = self.ref_dict['performance_reference'][0]['N']
        R = self.ref_dict['performance_reference'][0]['R']
        T = self.ref_dict['performance_reference'][0]['T']
        self.num_tasks = N * R
        self.num_cpus_per_task = T
        self.num_tasks_per_node = R
        self.env_vars = {
            'OMP_NUM_THREADS': '$SLURM_CPUS_PER_TASK',
            'OMP_PLACES': 'cores',
            'OMP_PROC_BIND': 'close',
        }

    @sanity_function
    def assert_simulation_success(self):
        self.energy_reference = self.ref_dict['energy_reference']
        energy = sn.extractsingle(r'!\s+total energy\s+=\s+(?P<energy>\S+) Ry',
                                  self.stdout, 'energy', float)
        energy_diff = sn.abs(energy - self.energy_reference)
        return sn.all([
            sn.assert_found(r'convergence has been achieved', self.stdout),
            sn.assert_lt(energy_diff, self.energy_tolerance)
        ])

    @performance_function('s')
    def time(self):
        return sn.extractsingle(r'electrons.+\s(?P<wtime>\S+)s WALL',
                                self.stdout, 'wtime', float)

    @run_before('performance')
    def set_performance_reference(self):
        self.reference = {
            '*': {'time': (self.ref_dict['performance_reference'][0]['P'],
                           None, 0.10, 's')}
        }
# }}}


# {{{ UENV/GPU
@rfm.simple_test
class UENV_QuantumESPRESSO_GPU_Check(QuantumESPRESSOBase,
                                     ExtraLauncherOptionsMixin,
                                     CudaVisibleDevicesAllMixin):
    valid_systems = ['+nvgpu +uenv']
    valid_prog_environs = ['+quantum-espresso']
    tags = {'production', 'uenv'}
    energy_tolerance = 1.0e-6
    test_name = parameter(['Au-surf'])
# }}}


# {{{ UENV/CPU
# MPI_Abort @rfm.simple_test
# MPI_Abort class UENV_QuantumESPRESSO_CPU_Check(QuantumESPRESSOBase,
# MPI_Abort                                      ExtraLauncherOptionsMixin):
# MPI_Abort     valid_systems = ['+cpu +uenv']
# MPI_Abort     valid_prog_environs = ['+quantum-espresso']
# MPI_Abort     tags = {'production', 'uenv'}
# MPI_Abort     energy_tolerance = 1.0e-6
# MPI_Abort     test_name = parameter(['Au-surf'])
# }}}


# {{{ SARUS
@rfm.simple_test
class SARUS_QuantumESPRESSOCheck(QuantumESPRESSOBase,
                                 SarusExtraLauncherOptionsMixin,
                                 CudaVisibleDevicesAllMixin):
    """
    jfrog=jfrog.svc.cscs.ch/docker-ci-ext/4931289112286619/apps
    sarus pull --login $jfrog/9adaeeabb5e743e3-803e055e8eaa895a:latest
    """
    container_image = variable(str, value='NULL')
    valid_prog_environs = ['builtin']
    valid_systems = ['+nvgpu', '+cpu']
    test_name = parameter(['Au-surf'])
    tags = {'production', 'sarus'}

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
        else:
            raise ConfigError('container_image is not set')
# }}}
