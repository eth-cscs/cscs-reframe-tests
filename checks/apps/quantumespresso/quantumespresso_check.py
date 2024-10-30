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
    # R:total number of MPI ranks, T:threads per rank, P:walltime
    'Au-surf': {
        'zen2': {
            # zen2 cpu nodes: 2sockets, 8 numa, 16c/numa = 128c (no MT)
            'energy_reference': -11427.09017218,
            'performance_reference': [{'R': 32, 'T': 4, 'P': 102.0}]
        },
        'zen3-4x-gpu-sm_80': {
            # A100 nodes: 1socket, 4 numa, 16c/numa = 64c (no MT)
            'energy_reference': -11427.09017218,
            'performance_reference': [{'R': 4, 'T': 16, 'P': 32.0}]
        }
    }
}


class QuantumESPRESSOBase(rfm.RunOnlyRegressionTest):
    energy_tolerance = 1.0e-6
    executable = 'pw.x'
    # TODO: tests should all have pw.in as input file
    executable_opts = ['-in', 'ausurf.in']

    @run_after('init')
    def set_description(self):
        self.descr = f'QuantumESPRESSO {self.test_name} check'

    @run_before('run')
    def set_parallel_resources(self):
        self.skip_if_no_procinfo()
        processor_info = self.current_partition.processor
        self.node_label = processor_info.arch
        if self.current_partition.devices:
            # device label, for example 4x-gpu-sm_80
            dev_label = ''
            for e in self.current_partition.devices:
                dev_label = f"-{dev_label}{e.num_devices}x-{e.type}-{e.arch}"

            self.node_label = self.node_label + dev_label

        # number of physical cores
        num_cores = int(
            processor_info.num_cpus / processor_info.num_cpus_per_core)

        self.ref_dict = (
            qe_tests[self.test_name][self.node_label]
        )
        # total number of ranks
        self.num_tasks = self.ref_dict['performance_reference'][0]['R']
        # threads / rank
        T = self.ref_dict['performance_reference'][0]['T']
        self.num_cpus_per_task = T
        # ranks per node
        self.num_tasks_per_node = int(num_cores / T)
        if not self.env_vars:
            self.env_vars = {}
        self.env_vars['OMP_NUM_THREADS'] = '$SLURM_CPUS_PER_TASK'
        self.env_vars['OMP_PLACES'] = 'cores'
        self.env_vars['OMP_PROC_BIND'] = 'close'

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


@rfm.simple_test
class UENV_QuantumESPRESSOCheck(QuantumESPRESSOBase,
                                ExtraLauncherOptionsMixin,
                                CudaVisibleDevicesAllMixin):
    valid_systems = ['-amdgpu']
    valid_prog_environs = ['+quantum-espresso +mpi +openmp +uenv']
    use_multithreading = False
    test_name = parameter(['Au-surf'])
    tags = {'production', 'uenv'}


@rfm.simple_test
class SARUS_QuantumESPRESSOCheck(QuantumESPRESSOBase,
                                 SarusExtraLauncherOptionsMixin,
                                 CudaVisibleDevicesAllMixin):
    container_image = variable(str, type(None), value=None)
    valid_systems = ['+sarus']
    valid_prog_environs = ['builtin']
    use_multithreading = False
    test_name = parameter(['Au-surf'])
    tags = {'production', 'sarus'}

    @run_after('setup')
    def setup_container_platform(self):
        # if container_image was provided then initialize a container execution
        if self.container_image is not None:
            self.container_platform = 'Sarus'
            self.container_platform.image = self.container_image
            self.container_platform.with_mpi = False
            self.container_platform.pull_image = False
            self.container_platform.command = (
                f'{self.executable} {" ".join(self.executable_opts)}'
            )
        else:
            raise ConfigError('container_image is not set')
