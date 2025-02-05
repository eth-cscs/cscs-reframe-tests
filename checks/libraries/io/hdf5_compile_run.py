# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class HDF5Test(rfm.RegressionTest):
    lang = parameter(['c', 'f90'])
    linkage = parameter(['dynamic'])
    valid_prog_environs = ['PrgEnv-aocc', 'PrgEnv-cray', 'PrgEnv-gnu']
    valid_systems = ['eiger:mc', 'pilatus:mc']
    build_system = 'SingleSource'
    modules = ['cray-hdf5']
    keep_files = ['h5dump_out.txt']
    num_tasks = 1
    num_tasks_per_node = 1
    postrun_cmds = ['h5dump h5ex_d_chunk.h5 > h5dump_out.txt']
    maintainers = ['SO', 'RS']
    tags = {'production', 'craype', 'health'}

    @run_after('init')
    def set_description(self):
        lang_names = {
            'c': 'C',
            'f90': 'Fortran 90'
        }
        self.descr = (f'{lang_names[self.lang]} HDF5 '
                      f'{self.linkage.capitalize()}')

    @run_after('setup')
    def aocc(self):
        #FIXME HPE support case 5365481562 with PrgEnv-aocc 
        if self.current_environ.name == 'PrgEnv-aocc':
            self.env_vars = {
                'LD_LIBRARY_PATH': '$CRAY_LD_LIBRARY_PATH:$LD_LIBRARY_PATH'
            }

    @run_before('compile')
    def set_sourcepath(self):
        self.sourcepath = f'h5ex_d_chunk.{self.lang}'

    @run_before('compile')
    def set_ldflags(self):
        self.build_system.ldflags = [f'-{self.linkage}']

    @run_before('sanity')
    def set_sanity(self):
        # C and Fortran write transposed matrix
        if self.lang == 'c':
            self.sanity_patterns = sn.all([
                sn.assert_found(r'Data as written to disk by hyberslabs',
                                self.stdout),
                sn.assert_found(r'Data as read from disk by hyperslab',
                                self.stdout),
                sn.assert_found(r'\(0,0\): 0, 1, 0, 0, 1, 0, 0, 1,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(0,0\): 0, 1, 0, 0, 1, 0, 0, 1,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(1,0\): 1, 1, 0, 1, 1, 0, 1, 1,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(2,0\): 0, 0, 0, 0, 0, 0, 0, 0,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(3,0\): 0, 1, 0, 0, 1, 0, 0, 1,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(4,0\): 1, 1, 0, 1, 1, 0, 1, 1,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(5,0\): 0, 0, 0, 0, 0, 0, 0, 0',
                                'h5dump_out.txt'),
            ])
        else:
            self.sanity_patterns = sn.all([
                sn.assert_found(r'Data as written to disk by hyberslabs',
                                self.stdout),
                sn.assert_found(r'Data as read from disk by hyperslab',
                                self.stdout),
                sn.assert_found(r'\(0,0\): 0, 1, 0, 0, 1, 0,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(1,0\): 1, 1, 0, 1, 1, 0,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(2,0\): 0, 0, 0, 0, 0, 0,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(3,0\): 0, 1, 0, 0, 1, 0,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(4,0\): 1, 1, 0, 1, 1, 0,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(5,0\): 0, 0, 0, 0, 0, 0,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(6,0\): 0, 1, 0, 0, 1, 0,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(7,0\): 1, 1, 0, 1, 1, 0',
                                'h5dump_out.txt'),
            ])
