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
    tags = {'production', 'uenv', 'bencher'}


@rfm.simple_test
class ParallelAlgos(GPUBenchmarks):
    benchmark = 'parallel_algos'
    algo = parameter(['radix-sort', 'scan', 'reduce'])
    _executable_opts = parameter(['6', '12', '27'])

    _algo_specs = {
        'radix-sort': {
            'sanity_regex': r'radix sort (normal|with memory tracking) time for.*key-value pairs:.*s, bandwidth:.*MiB/s',
            'perf_regex_normal': (
                r'radix sort normal time for (?P<items>\S+) '
                r'key-value pairs: (?P<latency>\S+) s, '
                r'bandwidth: (?P<bandwidth>\S+) MiB/s'
            ),
            'perf_regex_tracked': (
                r'radix sort with memory tracking time for (?P<items>\S+) '
                r'key-value pairs: (?P<latency>\S+) s, '
                r'bandwidth: (?P<bandwidth>\S+) MiB/s'
            ),
            'unit_name': 'keys/second',
            'unit': 'Gkeys/s'
        },
        'scan': {
            'sanity_regex': r'exclusive scan (normal|with memory tracking) time for.*values:.*s, bandwidth:.*MiB/s',
            'perf_regex_normal': (
                r'exclusive scan normal time for (?P<items>\S+) '
                r'values: (?P<latency>\S+) s, '
                r'bandwidth: (?P<bandwidth>\S+) MiB/s'
            ),
            'perf_regex_tracked': (
                r'exclusive scan with memory tracking time for (?P<items>\S+) '
                r'values: (?P<latency>\S+) s, '
                r'bandwidth: (?P<bandwidth>\S+) MiB/s'
            ),
            'unit_name': 'values/second',
            'unit': 'Gvalues/s'
        },
        'reduce': {
            'sanity_regex': r'reduction (normal|with memory tracking) time for.*values:.*s, bandwidth:.*MiB/s',
            'perf_regex_normal': (
                r'reduction normal time for (?P<items>\S+) '
                r'values: (?P<latency>\S+) s, '
                r'bandwidth: (?P<bandwidth>\S+) MiB/s'
            ),
            'perf_regex_tracked': (
                r'reduction with memory tracking time for (?P<items>\S+) '
                r'values: (?P<latency>\S+) s, '
                r'bandwidth: (?P<bandwidth>\S+) MiB/s'
            ),
            'unit_name': 'values/second',
            'unit': 'Gvalues/s'
        }
    }

    _memory_regex = (
        r'Memory statistics:\s+'
        r'Total allocated: (?P<total_mem>\S+) MiB\s+'
        r'Peak allocated: (?P<peak_mem>\S+) MiB\s+'
        r'Number of allocations: (?P<num_allocs>\S+)'
    )

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

        items_normal = sn.extractsingle(spec['perf_regex_normal'], self.stdout, 'items', float)
        latency_normal = sn.extractsingle(spec['perf_regex_normal'], self.stdout, 'latency', float)
        bandwidth_normal = sn.extractsingle(spec['perf_regex_normal'], self.stdout, 'bandwidth', float)

        items_tracked_memory = sn.extractsingle(spec['perf_regex_tracked'], self.stdout, 'items', float)
        latency_tracked_memory = sn.extractsingle(spec['perf_regex_tracked'], self.stdout, 'latency', float)
        bandwidth_tracked_memory = sn.extractsingle(spec['perf_regex_tracked'], self.stdout, 'bandwidth', float)

        total_mem = sn.extractsingle(self._memory_regex, self.stdout, 'total_mem', float)
        peak_mem = sn.extractsingle(self._memory_regex, self.stdout, 'peak_mem', float)
        num_allocs = sn.extractsingle(self._memory_regex, self.stdout, 'num_allocs', int)

        self.perf_variables = {
            'latency_normal': make_perf(latency_normal, 's'),
            'bandwidth_normal': make_perf(bandwidth_normal, 'MiB/s'),
            f'{spec["unit_name"]}_normal': make_perf((items_normal/latency_normal)/1e9, spec['unit']),
            'latency_tracked_memory': make_perf(latency_tracked_memory, 's'),
            'bandwidth_tracked_memory': make_perf(bandwidth_tracked_memory, 'MiB/s'),
            f'{spec["unit_name"]}_tracked_memory': make_perf((items_tracked_memory/latency_tracked_memory)/1e9, spec['unit']),
            'memory_total': make_perf(total_mem, 'MiB'),
            'memory_peak': make_perf(peak_mem, 'MiB'),
            'memory_allocations': make_perf(num_allocs, 'count'),
        }

    @run_before('performance')
    def set_references(self):
        self.uarch = uarch(self.current_partition)

        ref_bw = self._reference_bandwidths.get(self.algo, {}).get(self.uarch, {}).get(self._executable_opts)
        if ref_bw is not None:
            self.reference = {
                self.current_partition.fullname: {
                    'bandwidth_normal': (ref_bw, -0.60, None, 'MiB/s'),
                    'bandwidth_tracked_memory': (ref_bw, -0.60, None, 'MiB/s')
                    # will pass when: (60% * ref_bw) < bandwidth < +infinity
                }
            }
