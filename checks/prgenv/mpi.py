# Copyright 2016-2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os

import reframe as rfm
import reframe.utility.sanity as sn
# import uenv  # <-----------------


@rfm.simple_test
class MpiInitTest(rfm.RegressionTest):
    '''
    This test checks the value returned by calling MPI_Init_thread.
    '''
    required_threads = ['funneled', 'serialized', 'multiple']
    valid_systems = ['+uenv +remote', '+cpe_ce +remote']
    valid_prog_environs = ['+mpi']
    build_system = 'Make'
    sourcesdir = 'src/mpi_thread'
    executable = '$SLURM_SUBMIT_DIR/mpi_init_thread_single.exe'
    maintainers = ['VCUE']
    time_limit = '2m'
    build_locally = False
    tags = {'production', 'craype', 'uenv'}

#     @run_before('run')
#     def set_job_parameters(self):
#         # To avoid: "MPIR_pmi_init(83)....: PMI2_Job_GetId returned 14"
#         self.job.launcher.options += (
#             self.current_environ.extras.get('launcher_options', [])
#         )

    @run_before('run')
    def pre_run(self):
        cmd = self.job.launcher.run_command(self.job)
        self.prerun_cmds = [
            f'{cmd} $SLURM_SUBMIT_DIR/mpi_init_thread_{ii}.exe &> {ii}.rpt'
            for ii in self.required_threads
        ]
        self.postrun_cmds = ['ln -s rfm_job.out single.rpt']

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
        # {{{ regexes:
        regex = (r'^mpi_thread_required=(\w+)\s+mpi_thread_supported=\w+'
                 r'\s+mpi_thread_queried=\w+\s+(\d)')
        # single:
        req_thread_si = sn.extractsingle(regex, stdout, 1)
        runtime_mpithread_si = sn.extractsingle(
            regex, stdout, 2, int)
        # funneled:
        req_thread_f = sn.extractsingle(
            regex, f'{self.stagedir}/funneled.rpt', 1)
        runtime_mpithread_f = sn.extractsingle(
            regex, f'{self.stagedir}/funneled.rpt', 2, int)
        # serialized:
        req_thread_s = sn.extractsingle(
            regex, f'{self.stagedir}/serialized.rpt', 1)
        runtime_mpithread_s = sn.extractsingle(
            regex, f'{self.stagedir}/serialized.rpt', 2, int)
        # multiple:
        req_thread_m = sn.extractsingle(
            regex, f'{self.stagedir}/multiple.rpt', 1)
        runtime_mpithread_m = sn.extractsingle(
            regex, f"{self.stagedir}/multiple.rpt", 2, int)
        # }}}
        self.sanity_patterns = sn.all([
            sn.assert_found(r'tid=0 out of 1 from rank 0 out of 1',
                            stdout, msg='sanity: not found'),
            sn.assert_eq(runtime_mpithread_si,
                         self.mpithread_version[sn.evaluate(mpich_version)]
                                               [sn.evaluate(req_thread_si)],
                         msg='sanity_eq: {0} != {1}'),
            sn.assert_eq(runtime_mpithread_f,
                         self.mpithread_version[sn.evaluate(mpich_version)]
                                               [sn.evaluate(req_thread_f)],
                         msg='sanity_eq: {0} != {1}'),
            sn.assert_eq(runtime_mpithread_s,
                         self.mpithread_version[sn.evaluate(mpich_version)]
                                               [sn.evaluate(req_thread_s)],
                         msg='sanity_eq: {0} != {1}'),
            sn.assert_eq(runtime_mpithread_m,
                         self.mpithread_version[sn.evaluate(mpich_version)]
                                               [sn.evaluate(req_thread_m)],
                         msg='sanity_eq: {0} != {1}'),
        ])
