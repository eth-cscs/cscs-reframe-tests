# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
from datetime import datetime

import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.backends import getlauncher


def to_seconds(str):
    return (datetime.strptime(str, '%H:%M:%S') -
            datetime.strptime('00:00:00', '%H:%M:%S')).total_seconds()


@rfm.simple_test
class GREASYCheck(rfm.RegressionTest):
    configuration = parameter([('serial', 'gpu', 24, 12, 1, 1),
                               ('serial', 'mc',  72, 36, 1, 1),
                               ('openmp', 'gpu', 24,  3, 1, 4),
                               ('openmp', 'mc',  72,  9, 1, 4),
                               ('mpi', 'gpu', 24,  4, 3, 1),
                               ('mpi', 'mc',  72, 12, 3, 1),
                               ('mpi+openmp', 'gpu', 24,  3, 2, 2),
                               ('mpi+openmp', 'mc',  72,  6, 3, 2)])
    variant = variable(str)
    partition = variable(str)
    num_greasy_tasks = variable(int)
    workers_per_node = variable(int)
    ranks_per_worker = variable(int)
    cpus_per_worker = variable(int)
    valid_prog_environs = ['PrgEnv-gnu']
    sourcepath = 'tasks_mpi_openmp.c'
    build_system = 'SingleSource'
    executable = 'tasks_mpi_openmp.x'
    tasks_file = variable(str, value='tasks.txt')
    greasy_logfile = variable(str, value='greasy.log')
    nnodes = variable(int, value=2)

    # sleep enough time to distinguish if the files are running in parallel
    # or not
    sleep_time = variable(int, value=60)
    use_multithreading = False
    modules = ['GREASY']
    maintainers = ['VH', 'SK']
    tags = {'production'}

    @run_after('init')
    def unpack_configuration_parameter(self):
        self.variant, self.partition = self.configuration[0:2]
        self.num_greasy_tasks, self.workers_per_node = self.configuration[2:4]
        self.ranks_per_worker, self.cpus_per_worker = self.configuration[4:6]

    @run_after('init')
    def set_valid_systems(self):
        self.valid_systems = []

    @run_before('compile')
    def setup_build_system(self):
        self.build_system.cflags = [f'-DSLEEP_TIME={self.sleep_time:d}']
        if self.variant == 'openmp':
            self.build_system.cflags += ['-fopenmp']
        elif self.variant == 'mpi':
            self.build_system.cflags += ['-D_MPI']
        elif self.variant == 'mpi+openmp':
            self.build_system.cflags += ['-fopenmp', '-D_MPI']

    @run_before('run')
    def setup_greasy_run(self):
        self.executable_opts = [self.tasks_file]
        self.keep_files = [self.tasks_file, self.greasy_logfile]
        self.num_tasks_per_node = self.ranks_per_worker * self.workers_per_node
        self.num_tasks = self.num_tasks_per_node * self.nnodes
        self.num_cpus_per_task = self.cpus_per_worker

    @run_before('run')
    def set_environment_variables(self):
        # On SLURM there is no need to set OMP_NUM_THREADS if one defines
        # num_cpus_per_task, but adding for completeness and portability
        self.env_vars = {
            'OMP_NUM_THREADS': self.num_cpus_per_task,
            'GREASY_NWORKERS_PER_NODE': self.workers_per_node,
            'GREASY_LOGFILE': self.greasy_logfile
        }

    @run_before('run')
    def generate_tasks_file(self):
        with open(os.path.join(self.stagedir, self.tasks_file), 'w') as fp:
            for i in range(self.num_greasy_tasks):
                fp.write(f'./{self.executable} output-{i}\n')

    @run_before('run')
    def daint_dom_gpu_specific_workaround(self):
        if self.current_partition.fullname in ['daint:gpu', 'dom:gpu']:
            self.env_vars['CRAY_CUDA_MPS'] = 1
            self.env_vars['CUDA_VISIBLE_DEVICES'] = 0
            self.env_vars['GPU_DEVICE_ORDINAL'] = 0
            self.extra_resources = {
                'gres': {
                    'gres': 'gpu:0,craynetwork:4'
                }
            }
        elif self.current_partition.fullname in ['dom:mc']:
            self.extra_resources = {
                'gres': {
                    'gres': 'craynetwork:72'
                }
            }
        elif self.current_partition.fullname in ['daint:mc']:
            if 'serial' not in self.variant:
                self.extra_resources = {
                    'gres': {
                        'gres': 'craynetwork:72'
                    }
                }

    @run_before('run')
    def change_executable_name(self):
        # After compiling the code we can change the executable to be
        # the greasy one
        self.executable = 'greasy'

    @run_before('run')
    def set_launcher(self):
        # The job launcher has to be changed to local since greasy
        # make calls to srun
        self.job.launcher = getlauncher('local')()

    @sanity_function
    def assert_success(self):
        output_files = []
        output_files = [file for file in os.listdir(self.stagedir)
                        if file.startswith('output-')]
        num_greasy_tasks = len(output_files)
        failure_msg = (f'Requested {self.num_greasy_tasks} task(s), but '
                       f'executed only {num_greasy_tasks} tasks(s)')
        sn.evaluate(
            sn.assert_eq(num_greasy_tasks, self.num_greasy_tasks,
                         msg=failure_msg)
        )
        num_tasks = sn.getattr(self, 'ranks_per_worker')
        num_cpus_per_task = sn.getattr(self, 'num_cpus_per_task')

        def tid(match):
            return int(match.group(1))

        def num_threads(match):
            return int(match.group(2))

        def rank(match):
            return int(match.group(3))

        def num_ranks(match):
            return int(match.group(4))

        for output_file in output_files:
            result = sn.findall(r'Hello, World from thread \s*(\d+) out '
                                r'of \s*(\d+) from process \s*(\d+) out of '
                                r'\s*(\d+)', output_file)

            failure_msg = (f'Found {sn.count(result)} Hello, World... '
                           f'pattern(s) but expected '
                           f'{num_tasks * num_cpus_per_task} pattern(s) '
                           f'inside the output file {output_file}')
            sn.evaluate(sn.assert_eq(sn.count(result),
                                     num_tasks * num_cpus_per_task,
                                     msg=failure_msg))

            sn.evaluate(sn.all(
                sn.chain(
                    sn.map(
                        lambda x: sn.assert_lt(
                            tid(x), num_threads(x),
                            msg=(f'Found {tid(x)} threads rather than '
                                 f'{num_threads(x)}')
                        ), result
                    ),
                    sn.map(
                        lambda x: sn.assert_lt(
                            rank(x), num_ranks(x),
                            msg=(f'Rank id {rank(x)} is not lower than the '
                                 f'number of ranks {self.ranks_per_worker} '
                                 f'in output file')
                        ), result
                    ),
                    sn.map(
                        lambda x: sn.assert_lt(
                            tid(x), self.num_cpus_per_task,
                            msg=(f'Rank id {tid(x)} is not lower than the '
                                 f'number of cpus per task '
                                 f'{self.num_cpus_per_task} in output '
                                 f'file {output_file}')
                        ), result
                    ),
                    sn.map(
                        lambda x: sn.assert_eq(
                            num_threads(x), num_cpus_per_task,
                            msg=(f'Found {num_threads(x)} threads rather than '
                                 f'{self.num_cpus_per_task} in output file '
                                 f'{output_file}')
                        ), result
                    ),
                    sn.map(
                        lambda x: sn.assert_lt(
                            rank(x), num_tasks,
                            msg=(f'Found {rank(x)} threads rather than '
                                 f'{self.num_cpus_per_task} in output file '
                                 f'{output_file}')
                        ), result
                    ),
                    sn.map(
                        lambda x: sn.assert_eq(
                            num_ranks(x), num_tasks,
                            msg=(f'Number of ranks {num_ranks(x)} is not '
                                 f'equal to {self.ranks_per_worker} in '
                                 f'output file {output_file}')
                        ), result
                    )
                )
            ))
        sn.evaluate(sn.assert_found(r'Finished greasing', self.greasy_logfile))
        sn.evaluate(sn.assert_found(
            (f'INFO: Summary of {self.num_greasy_tasks} '
             f'tasks: '
             f'{self.num_greasy_tasks} OK, '
             f'0 FAILED, '
             f'0 CANCELLED, '
             fr'0 INVALID\.'), self.greasy_logfile
        ))

        return True

    @run_before('performance')
    def set_reference(self):
        # Reference value is system agnostic
        # Adding 10 secs of slowdown per greasy tasks
        # this is to compensate for whenever the systems are full and srun gets
        # slightly slower
        refperf = (
            (self.sleep_time + 10) * self.num_greasy_tasks /
            self.workers_per_node / self.nnodes
        )
        self.reference = {
            '*': {
                'time': (refperf, None, 0.5, 's')
            }
        }

    @performance_function('s')
    def time(self):
        return sn.extractsingle(r'Total time: (?P<perf>\S+)',
                                self.greasy_logfile, 'perf', to_seconds)
