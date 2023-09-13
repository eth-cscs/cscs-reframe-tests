# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class StreamTest(rfm.RegressionTest):
    '''This test checks the stream test:
       Function    Best Rate MB/s  Avg time     Min time     Max time
       Triad:          13991.7     0.017174     0.017153     0.017192

       Code taken from https://www.cs.virginia.edu/stream/FTP/Code/.
    '''

    descr = 'STREAM Benchmark'
    exclusive_access = True
    valid_systems = ['+remote']
    valid_prog_environs = ['+openmp']
    use_multithreading = False
    sourcepath = 'stream.c'
    build_system = 'SingleSource'
    build_locally = False
    num_tasks = 1
    num_tasks_per_node = 1
    env_vars = {
        'OMP_PLACES': 'threads',
        'OMP_PROC_BIND': 'spread'
    }
    tags = {'production', 'craype'}
    stream_bw_reference = {
        'PrgEnv-cray': {
            'hohgant:nvgpu': {'triad': (488656, -0.05, None, 'MB/s')},
            'hohgant:amdgpu': {'triad': (427082, -0.05, None, 'MB/s')},
            'hohgant:cpu': {'triad': (2001258, -0.05, None, 'MB/s')}
        },
        'PrgEnv-gnu': {
            'hohgant:nvgpu': {'triad': (541783, -0.10, None, 'MB/s')},
            'hohgant:amdgpu': {'triad': (461546, -0.10, None, 'MB/s')},
            'hohgant:cpu': {'triad': (1548666, -0.10, None, 'MB/s')}
        },
        'PrgEnv-nvhpc': {
            'hohgant:nvgpu': {'triad': (511500, -0.05, None, 'MB/s')},
            'hohgant:cpu': {'triad': (1791161, -0.05, None, 'MB/s')}
        },
        'PrgEnv-nvidia': {
            'hohgant:nvgpu': {'triad': (477077, -0.05, None, 'MB/s')},
            'hohgant:cpu': {'triad': (1804001, -0.05, None, 'MB/s')}
        }
    }

    @sanity_function
    def assert_validation(self):
        return sn.assert_found(
            r'Solution Validates: avg error less than', self.stdout
        )

    @performance_function('MB/s')
    def triad(self):
        return sn.extractsingle(
            r'Triad:\s+(?P<triad>\S+)\s+\S+', self.stdout, 'triad', float
        )

    @run_after('setup')
    def prepare_test(self):
        self.skip_if_no_procinfo()
        self.num_cpus_per_task = int(self.current_partition.processor.num_cores)
        self.env_vars['OMP_NUM_THREADS'] = self.num_cpus_per_task

        self.build_system.cflags += (
            self.current_environ.extras.get('c_openmp_flags', ['-fopenmp'])
        )
        self.build_system.cflags.append('-O3')
        envname = self.current_environ.name

        try:
            self.reference = self.stream_bw_reference[envname]
        except KeyError:
            self.reference = self.stream_bw_reference['PrgEnv-gnu']
