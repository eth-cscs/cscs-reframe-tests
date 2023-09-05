# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn

qe_tests = {
    'Au-surf' : {
        'hohgant:cpu' : {
            'energy_reference' : -11427.09017218,
            'performance_reference' : [
                {'R' : 32,  # total number of ranks
                 'T' : 4    # threads per rank
                 'P' : 55.4 # performance. here is time to solution
                }
            ]
        },
        'hohgant-uenv:cpu' : { # TODO: only hohgant:cpu should remain in the future
            'energy_reference' : -11427.09017218,
            'performance_reference' : [
                {'R' : 32,  # total number of ranks
                 'T' : 4    # threads per rank
                 'P' : 55.4 # performance. here is time to solution
                }
            ]
        },
        'hohgant:nvgpu' : {
            'energy_reference' : -11427.09017218,
            'performance_reference' : [
                {'R' : 4,  # total number of ranks
                 'T' : 16    # threads per rank
                 'P' : 55.4 # performance. here is time to solution
                }
            ]
        }
    }
}

class QuantumESPRESSOCheckBase(rfm.RunOnlyRegressionTest):
    valid_systems = ['hohgant:cpu', 'hohgant:nvgpu', 'hohgant-uenv:cpu']
    valid_prog_environs = ['builtin','+quantum-espresso']
    container_image = variable(str, value='NULL')
    executable = 'pw.x'
    # TODO: tests should all have pw.in as input file
    executable_opts = ['-in', 'ausurf.in']
    strict_check = False
    maintainers = ['antonk']
    # todo: which tags it should have?
    tags = {'scs'}

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
class QuantumESPRESSOCheck(QuantumESPRESSOCheckBase):
    energy_tolerance = 1.0e-6
    test_name = 'Au-surf'

    @run_after('init')
    def setup_test(self):
        self.descr = (f'QuantumESPRESSO ground state SCF check')
        self.env_vars = {
            #'MPICH_OFI_STARTUP_CONNECT': 1,
            'OMP_NUM_THREADS': '$SLURM_CPUS_PER_TASK'
            #'OMP_PLACES': 'cores',
            #'OMP_PROC_BIND': 'close'
        }

    @run_after('setup')
    def setup_reference_dict(self)
        self.ref_dict = qe_tests[test_name][self.current_partition.fullname]

    @run_after('setup')
    def setup_container_platform(self):
        # in case container_image was provided, initialize a container execution
        if self.container_image != 'NULL':
            self.container_platform = 'Sarus'
            self.container_platform.image = self.container_image
            self.container_platform.with_mpi = False
            self.container_platform.pull_image = False
            self.container_platform.command = f'{self.executable} {" ".join(self.executable_opts)}'

    @run_after('setup')
    def setup_uenv_modules(self):
        # for uenv we need modules, for containers no
        if self.container_image == 'NULL':
            # is self.modules needed here?
            modules = ['quantum-espresso']

    @run_after('setup')
    def setup_mpi_layout(self):
        self.energy_reference = ref_dict['energy_reference']
        self.num_tasks = ref_dict['performance_reference']['R']
        self.num_cpus_per_task = ref_dict['performance_reference']['T']
        # TODO: this is a derived quantity from the threads_per_core and cores_per_node
        #self.num_tasks_per_node

    @run_before('performance')
    def set_reference(self):
        self.reference = {
            '*': {'time': (ref_dict['performance_reference']['P'], None, 0.10, 's')}
        }

    @run_before('run')
    def set_task_distribution(self):
        #self.job.options = ['--distribution=block:block']
        return

    @run_before('run')
    def set_cpu_binding(self):
        #self.job.launcher.options = ['--cpu-bind=cores', ' --hint=nomultithread']
        #
        self.job.launcher.options = [' --hint=nomultithread']
        # Sarus binds to nvhpc compilerd mpich which requires --mpi=pmi2 flag
        if self.current_system.name in {'hohgant'} and self.container_image != 'NULL':
            self.job.launcher.options += ['--mpi=pmi2']
