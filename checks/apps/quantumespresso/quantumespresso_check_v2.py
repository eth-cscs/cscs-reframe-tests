# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


class QuantumESPRESSOCheck(rfm.RunOnlyRegressionTest):
    valid_systems = ['hohgant:cpu', 'hohgant-uenv:cpu']
    valid_prog_environs = ['builtin']
    container_image = variable(str, value='NULL')
    scale = parameter(['small'])
    executable = 'pw.x'
    executable_opts = ['-in', 'ausurf.in']
    #extra_resources = {
    #    'switches': {
    #        'num_switches': 1
    #    }
    #}
    strict_check = False
    maintainers = ['antonk']
    # todo: which tags it should have?
    tags = {'scs'}

    #@run_after('init')
    #def skip_if_null_image(self):
    #    self.skip_if(self.container_image_image == 'NULL', 'no QE container image was given')

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

@rfm.simple_test
class QuantumESPRESSOCpuCheck(QuantumESPRESSOCheck):
    energy_tolerance = 1.0e-6

    @run_after('init')
    def setup_test(self):
        self.descr = (f'QuantumESPRESSO CPU check (version: {self.scale})')
        self.env_vars = {
            'MPICH_OFI_STARTUP_CONNECT': 1,
            'OMP_NUM_THREADS': 4,
            'OMP_PLACES': 'cores',
            'OMP_PROC_BIND': 'close'
        }

        if self.scale == 'small':
            self.energy_reference = -11427.09017218
            self.num_tasks = 32
            self.num_tasks_per_node = 32
            self.num_cpus_per_task = 4
            self.num_tasks_per_core = 1
        else:
            self.energy_reference = -11427.09017152
            self.num_tasks = 256
            self.num_tasks_per_node = 16
            self.num_cpus_per_task = 16
            self.num_tasks_per_core = 1

    @run_after('setup')
    def setup_container_platform(self):
        # in case container_image was provided, initialize a container execution
        if self.container_image != 'NULL':
            self.container_platform = 'Sarus'
            self.container_platform.image = self.container_image
            self.container_platform.with_mpi = False
            self.container_platform.pull_image = False
            self.container_platform.command = f'{self.executable} {" ".join(self.executable_opts)}'

    @run_before('performance')
    def set_reference(self):
        references = {
            'small': {
                '*': {'time': (55.51, None, 0.10, 's')}
            },
            'large': {
                '*': {'time': (43.211, None, 0.10, 's')}
            }
        }
        self.reference = references[self.scale]

    @run_before('run')
    def set_task_distribution(self):
        #self.job.options = ['--distribution=block:block']
        return

    @run_before('run')
    def set_cpu_binding(self):
        #self.job.launcher.options = ['--cpu-bind=cores', ' --hint=nomultithread']
        #
        self.job.launcher.options = [' --hint=nomultithread']
        if self.current_system.name in {'hohgant'}:
            self.job.launcher.options += ['--mpi=pmi2']
