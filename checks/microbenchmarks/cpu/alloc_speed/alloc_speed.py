# Copyright 2016 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


class AllocSpeedTestBase(rfm.RegressionTest):
    sourcepath = 'alloc_speed.cpp'
    build_system = 'SingleSource'
    valid_prog_environs = ['*']

    @run_after('init')
    def set_descr(self):
        self.descr = (f'Time to allocate 4096 MB using {self.hugepages} '
                      f'hugepages')

    @run_before('compile')
    def set_cxxflags(self):
        self.build_system.cxxflags = ['-O3', '-std=c++11']

    @sanity_function
    def assert_4GB(self):
        return sn.assert_found('4096 MB', self.stdout)

    @run_before('performance')
    def set_reference(self):
        base_perf = 0.2
        sys_reference = {
            'no': {
                '*': {
                    'time': (base_perf, None, 0.15, 's')
                }
            },
            '2M': {
                '*': {
                    'time': (base_perf/2, None, 0.15, 's')
                }
            },
        }
        self.reference = sys_reference[self.hugepages]

    @performance_function('s')
    def time(self):
        return sn.extractsingle(r'4096 MB, allocation time (?P<time>\S+)',
                                self.stdout, 'time', float)


@rfm.simple_test
class CPE_AllocSpeedTest(AllocSpeedTestBase):
    hugepages = parameter(['no', '2M'])
    valid_systems = ['+remote -uenv']
    tags = {'production', 'craype'}

    @run_after('setup')
    def set_modules(self):
        if self.hugepages == 'no':
            return

        self.modules += [f'craype-hugepages{self.hugepages}']


@rfm.simple_test
class UENV_AllocSpeedTest(AllocSpeedTestBase):
    hugepages = parameter(['no'])
    valid_systems = ['+remote +uenv']
    tags = {'production', 'uenv'}
