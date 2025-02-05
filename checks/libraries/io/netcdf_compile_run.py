# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os

import reframe as rfm
import reframe.utility.osext as osext
import reframe.utility.sanity as sn


@rfm.simple_test
class NetCDFTest(rfm.RegressionTest):
    lang = parameter(['cpp', 'c', 'f90'])
    linkage = parameter(['dynamic'])
    valid_systems = ['eiger:mc', 'pilatus:mc']
    valid_prog_environs = ['PrgEnv-aocc', 'PrgEnv-cray', 'PrgEnv-gnu']
    modules = ['cray-hdf5', 'cray-netcdf']
    build_system = 'SingleSource'
    num_tasks = 1
    num_tasks_per_node = 1
    maintainers = ['AJ', 'SO']
    tags = {'production', 'craype', 'external-resources', 'health'}
    lang_names = {
            'c': 'C',
            'cpp': 'C++',
            'f90': 'Fortran 90'
    }

    @run_after('init')
    def set_description(self):
        self.descr = (f'{self.lang_names[self.lang]} NetCDF '
                      f'{self.linkage.capitalize()}')

    @run_before('compile')
    def set_sources(self):
        self.sourcesdir = os.path.join(self.current_system.resourcesdir,
                                       'netcdf')
        self.sourcepath = f'netcdf_read_write.{self.lang}'

    @run_before('compile')
    def setflags(self):
        self.build_system.ldflags = [f'-{self.linkage}']

    @run_before('sanity')
    def set_sanity(self):
        self.sanity_patterns = sn.assert_found(r'SUCCESS', self.stdout)
