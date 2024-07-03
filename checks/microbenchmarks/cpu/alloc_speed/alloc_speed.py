# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class AllocSpeedTest(rfm.RegressionTest):
    hugepages = parameter(['no', '2M'])
    sourcepath = 'alloc_speed.cpp'
    valid_systems = ['+remote']
    valid_prog_environs = ['+alloc_speed']
    build_system = 'SingleSource'
    tags = {'production', 'craype'}

    @run_after('init')
    def set_descr(self):
        self.descr = (f'Time to allocate 4096 MB using {self.hugepages} '
                      f'hugepages')

    @run_after('setup')
    def set_modules(self):
        if self.hugepages == 'no':
            return

        variant = f'hugepages{self.hugepages}'
        if variant in self.current_environ.extras:
            self.modules = self.current_environ.extras[variant]
        else:
            self.skip(f'No hugepage {self.hugepages} module')

    @run_before('compile')
    def set_cxxflags(self):
        self.build_system.cxxflags = ['-O3', '-std=c++11']

    @sanity_function
    def assert_4GB(self):
        return sn.assert_found('4096 MB', self.stdout)

    @run_before('performance')
    def set_reference(self):
        base_perf = 0.12
        sys_reference = {
            'no': {
                'hohgant:nvgpu': {
                    'time': (base_perf, None, 0.15, 's')
                },
                'dom:mc': {
                    'time': (1.51, None, 0.15, 's')
                },
                'daint:gpu': {
                    'time': (1.32, None, 0.15, 's')
                },
                'daint:mc': {
                    'time': (1.51, None, 0.15, 's')
                },
                'eiger:mc': {
                    'time': (0.14, None, 0.15, 's')
                },
                'pilatus:mc': {
                    'time': (0.14, None, 0.15, 's')
                },
                'hohgant:cpu': {
                    'time': (base_perf, None, 0.15, 's')
                }
            },
            '2M': {
                'hohgant:nvgpu': {
                    'time': (base_perf/2, None, 0.15, 's')
                },
                'hohgant:amdgpu': {
                    'time': (base_perf/2, None, 0.15, 's')
                },
                'daint:gpu': {
                    'time': (0.11, None, 0.15, 's')
                },
                'daint:mc': {
                    'time': (0.20, None, 0.15, 's')
                },
                'eiger:mc': {
                    'time': (0.07, None, 0.15, 's')
                },
                'pilatus:mc': {
                    'time': (0.07, None, 0.15, 's')
                },
                '*': {
                    'time': (0, None, None, 's')
                }
            },
        }
        self.reference = sys_reference[self.hugepages]

    @performance_function('s')
    def time(self):
        return sn.extractsingle(r'4096 MB, allocation time (?P<time>\S+)',
                                self.stdout, 'time', float)
