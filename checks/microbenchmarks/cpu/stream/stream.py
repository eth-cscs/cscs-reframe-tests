# Copyright 2016-2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib
import sys
import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent / 'mixins'))
from container_engine import ContainerEngineCPEMixin


@rfm.simple_test
class StreamTest(rfm.RegressionTest, ContainerEngineCPEMixin):
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
    num_tasks_per_socket = 1
    env_vars = {
        'OMP_PLACES': 'cores',
        'OMP_PROC_BIND': 'spread'
    }
    stream_bw_reference = {
        'zen3': (122000., -0.05, 0.05, 'MB/s'),
        'neoverse_v2': (430000., -0.05, 0.15, 'MB/s')
    }

    @sanity_function
    def assert_validation(self):
        return sn.assert_found(
            r'Solution Validates: avg error less than', self.stdout
        )

    @performance_function('MB/s')
    def triad(self):
        return sn.min(sn.extractall(
            r'Triad:\s+(?P<triad>\S+)\s+\S+', self.stdout, 'triad', float
        ))

    @run_after('setup')
    def prepare_test(self):
        self.skip_if_no_procinfo()

        # Sort the caches by type alphabetically (L1 < L2 < L3 ...) and get
        # the total cache size of the last-level cache, for example:
        # last_level_cache = {'type': 'L3', 'size': 33554432, ...}
        caches = self.current_partition.processor.topology['caches']
        num_sockets = int(self.current_partition.processor.num_sockets)
        last_level_cache = max(caches, key=lambda c: c['type'])
        cache_size_bytes = (int(last_level_cache['size']) *
                            len(last_level_cache['cpusets'])) // num_sockets
        # Sizes of each array must be at least 4x the size of the sum of all
        # the last-level caches, (double precision floating points are 8 bytes)
        array_size = 4 * cache_size_bytes // 8
        self.build_system.cppflags = [f'-DSTREAM_ARRAY_SIZE={array_size}']

        self.num_tasks = self.num_tasks_per_node = num_sockets
        self.num_cpus_per_task = int(
            self.current_partition.processor.num_cores_per_socket
        )
        self.env_vars['OMP_NUM_THREADS'] = self.num_cpus_per_task
        self.build_system.cflags += (
            self.current_environ.extras.get('c_openmp_flags', ['-fopenmp'])
        )
        self.build_system.cflags.append('-O3')

        # This is typically needed for large array sizes
        mcmodel = 'medium'
        proc = self.current_partition.processor

        # -mcmodel=medium is not available for AARCH64 on gcc
        if proc.arch == 'neoverse_v2':
            mcmodel = 'large'

        self.build_system.cflags += [f'-mcmodel={mcmodel}']

    @run_before('performance')
    def set_reference(self):
        proc = self.current_partition.processor
        try:
            ref = self.stream_bw_reference[proc.arch]
        except KeyError:
            return
        else:
            self.reference = {'*': {'triad': ref}}
