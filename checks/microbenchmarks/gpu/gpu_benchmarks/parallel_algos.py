# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
from uenv import uarch


class GPUBenchmarks(rfm.RegressionTest):
    '''
    Base class for GPU microbenchmarks.
    '''
    maintainers = ['SSA']
    sourcesdir = None
    valid_prog_environs = ['+uenv +prgenv +rocm', '+uenv +prgenv +cuda']
    valid_systems = ['+uenv']
    build_system = 'CMake'
    prebuild_cmds = [
        'git clone --depth 1 -b reframe-ci https://github.com/eth-cscs/gpu-benchmarks.git'
    ]
    time_limit = '2m'
    build_locally = False
    tags = {'production', 'uenv'}


@rfm.simple_test
class ParallelAlgos(GPUBenchmarks):
    benchmark = 'parallel_algos'
    algo = parameter(['radix-sort', 'scan', 'reduce'])
    _executable_opts = parameter(['6', '12', '27'])

    _algo_specs = {
        'radix-sort': {
            'sanity_regex': r'radix sort time for.*key-value pairs:.*s, bandwidth:.*MiB/s',
            'perf_regex': (
                r'radix sort time for (?P<items>\S+) '
                r'key-value pairs: (?P<latency>\S+) s, '
                r'bandwidth: (?P<bandwidth>\S+) MiB/s'
            ),
            'unit_name': 'keys/second',
            'unit': 'Gkeys/s'
        },
        'scan': {
            'sanity_regex': r'exclusive scan time for.*values:.*s, bandwidth:.*MiB/s',
            'perf_regex': (
                r'exclusive scan time for (?P<items>\S+) '
                r'values: (?P<latency>\S+) s, '
                r'bandwidth: (?P<bandwidth>\S+) MiB/s'
            ),
            'unit_name': 'values/second',
            'unit': 'Gvalues/s'
        },
        'reduce': {
            'sanity_regex': r'reduction time for.*values:.*s, bandwidth:.*MiB/s',
            'perf_regex': (
                r'reduction time for (?P<items>\S+) '
                r'values: (?P<latency>\S+) s, '
                r'bandwidth: (?P<bandwidth>\S+) MiB/s'
            ),
            'unit_name': 'values/second',
            'unit': 'Gvalues/s'
        }
    }

    # bandwidth values in MiB/s
    _reference_bandwidths = {
        'scan': {
            'mi200': {'6': 9.06516, '12': 600.609, '27': 1266670.0},
            'mi300': {'6': 6.41283, '12': 404.344, '27': 2209560.0},
            'gh200': {'6': 19.0931, '12': 1101.08, '27': 2362160.0},
        },
        'reduce': {
            'mi200': {'6': 9.06516, '12': 600.609, '27': 1266670.0},
            'mi300': {'6': 6.41283, '12': 404.344, '27': 2209560.0},
            'gh200': {'6': 19.0931, '12': 1101.08, '27': 2362160.0},
        },
        'radix-sort': {
            'mi200': {'6': 16.9316, '12': 826.918, '27': 66868.9},
            'mi300': {'6': 17.1352, '12': 911.252, '27': 23908.8},
            'gh200': {'6': 34.8331, '12': 997.079, '27': 217461.0},
        }
    }

    @run_before('compile')
    def prepare_build(self):
        # self.build_system.srcdir is not available in set_executable
        self._srcdir = f'gpu-benchmarks/{self.benchmark}'
        self.build_system.srcdir = self._srcdir
        self.build_system.builddir = f'build_{self.benchmark}'
        self.prebuild_cmds += [f'cd {self.build_system.srcdir}']
        self.build_system.max_concurrency = 8
        gpu_arch = self.current_partition.select_devices('gpu')[0].arch
        if 'rocm' in self.current_environ.features:
            self.build_system.config_opts = [
                '-DWITH_CUDA=OFF',
                '-DWITH_HIP=ON',
                f'-DCMAKE_HIP_ARCHITECTURES="{gpu_arch}"'
            ]
        else:
            gpu_arch = (
                gpu_arch[len("sm_"):]
                if gpu_arch.startswith("sm_")
                else gpu_arch
            )
            self.build_system.config_opts = [
                '-DWITH_CUDA=ON',
                '-DWITH_HIP=OFF',
                f'-DCMAKE_CUDA_ARCHITECTURES="{gpu_arch}"'
            ]

    @run_before('run')
    def set_executable(self):
        self.executable = os.path.join(self._srcdir, self.build_system.builddir, self.algo)
        self.executable_opts = [self._executable_opts]

    @run_before('sanity')
    def set_sanity(self):
        spec = self._algo_specs[self.algo]
        self.sanity_patterns = sn.all([sn.assert_found(spec['sanity_regex'], self.stdout)])

    @run_before('performance')
    def set_perf_vars(self):
        make_perf = sn.make_performance_function
        spec = self._algo_specs[self.algo]

        items = sn.extractsingle(spec['perf_regex'], self.stdout, 'items', float)
        latency = sn.extractsingle(spec['perf_regex'], self.stdout, 'latency', float)
        bandwidth = sn.extractsingle(spec['perf_regex'], self.stdout, 'bandwidth', float)

        self.perf_variables = {
            'latency': make_perf(latency, 's'),
            'bandwidth': make_perf(bandwidth, 'MiB/s'),
            spec['unit_name']: make_perf((items/latency)/1e9, spec['unit']),
        }

    @run_before('performance')
    def set_references(self):
        self.uarch = uarch(self.current_partition)

        ref_bw = self._reference_bandwidths.get(self.algo, {}).get(self.uarch, {}).get(self._executable_opts)
        if ref_bw is not None:
            self.reference = {
                self.current_partition.fullname: {
                    'bandwidth': (ref_bw, -0.6, None, 'MiB/s')
                    # will pass when: (60% * ref_bw) < bandwidth < +infinity
                }
            }
