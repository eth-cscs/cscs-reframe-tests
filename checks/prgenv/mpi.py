# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class MpiInitTest(rfm.RegressionTest):
    '''
    This test checks the value returned by calling MPI_Init_thread.
    '''
    required_thread = parameter(['single', 'funneled', 'serialized',
                                 'multiple'])
    valid_prog_environs = ['*']
    valid_systems = ['*']
    build_system = 'SingleSource'
    sourcesdir = 'src/mpi_thread'
    sourcepath = 'mpi_init_thread.cpp'
    cppflags = variable(
        dict, value={
            'single': ['-D_MPI_THREAD_SINGLE'],
            'funneled': ['-D_MPI_THREAD_FUNNELED'],
            'serialized': ['-D_MPI_THREAD_SERIALIZED'],
            'multiple': ['-D_MPI_THREAD_MULTIPLE']
        }
    )
    prebuild_cmds += ['module list']
    time_limit = '2m'
    maintainers = ['@jgphpc']
    tags = {'production', 'craype'}

    @run_after('init')
    def set_cpp_flags(self):
        self.build_system.cppflags = self.cppflags[self.required_thread]

    @run_after('setup')
    def skip_if_no_mpi(self):
        self.skip_if(self.current_partition.name.startswith('login'),
                     'skip login partition')
        self.skip_if(self.current_environ.name.startswith('builtin'),
                     'skip builtin pe')

    @run_before('run')
    def set_job_parameters(self):
        # To avoid: "MPIR_pmi_init(83)....: PMI2_Job_GetId returned 14"
        self.job.launcher.options += (
            [self.current_environ.extras['launcher_options']]
            if 'launcher_options' in self.current_environ.extras
            else ''
        )

    @run_before('sanity')
    def set_sanity(self):
        # {{{ CRAY MPICH version:
        # - 7.7.15 (ANL base 3.2)
        # - 8.0.16.17 (ANL base 3.3)
        # - 8.1.4.31,8.1.5.32,8.1.18.4,8.1.21.11,8.1.25.17 (ANL base 3.4a2)
        regex = r'= MPI VERSION\s+: CRAY MPICH version \S+ \(ANL base (\S+)\)'
        stdout = os.path.join(self.stagedir, sn.evaluate(self.stdout))
        mpich_version = sn.extractsingle(regex, stdout, 1)
        self.mpithread_version = {
            '3.2': {
                'MPI_THREAD_SINGLE': 0,
                'MPI_THREAD_FUNNELED': 1,
                'MPI_THREAD_SERIALIZED': 2,
                'MPI_THREAD_MULTIPLE': 2
                # req=MPI_THREAD_MULTIPLE -> supported=MPI_THREAD_SERIALIZED
            },
            '3.3': {
                'MPI_THREAD_SINGLE': 0,
                'MPI_THREAD_FUNNELED': 1,
                'MPI_THREAD_SERIALIZED': 2,
                'MPI_THREAD_MULTIPLE': 3
            },
            '3.4a2': {
                'MPI_THREAD_SINGLE': 0,
                'MPI_THREAD_FUNNELED': 1,
                'MPI_THREAD_SERIALIZED': 2,
                'MPI_THREAD_MULTIPLE': 3
            },
        }
        # }}}
        regex = (r'^mpi_thread_required=(\w+)\s+mpi_thread_supported=\w+'
                 r'\s+mpi_thread_queried=\w+\s+(\d)')
        required_thread = sn.extractsingle(regex, stdout, 1)
        found_mpithread = sn.extractsingle(regex, stdout, 2, int)
        self.sanity_patterns = sn.all([
            sn.assert_found(r'tid=0 out of 1 from rank 0 out of 1',
                            stdout, msg='sanity: not found'),
            sn.assert_eq(found_mpithread,
                         self.mpithread_version[sn.evaluate(mpich_version)]
                                               [sn.evaluate(required_thread)],
                         msg='sanity_eq: {0} != {1}')
        ])
