# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.osext as osext
import reframe.utility.sanity as sn


@rfm.simple_test
class HDF5Test(rfm.RegressionTest):
    """
    Create a file and dataset and select/read a subset from the dataset
    https://portal.hdfgroup.org/display/HDF5/Examples+from+Learning+the+Basics
    """
    lang = parameter(['cpp', 'f90'])
    valid_systems = ['+remote']
    valid_prog_environs = ['+mpi']
    build_system = 'SingleSource'
    modules = ['cray-hdf5']
    num_tasks = 1
    postrun_cmds = ['h5ls *.h5']
    tags = {'production', 'craype', 'health'}

    @run_before('compile')
    def set_source(self):
        repo = 'https://raw.githubusercontent.com/HDFGroup/hdf5/develop'
        src = {
            'cpp': 'c++/examples/h5tutr_subset.cpp',
            'f90': 'fortran/examples/h5_subset.f90'
        }
        # self.prebuild_cmds = [f'wget --quiet {repo}/{src[self.lang]}']
        self.sourcepath = src[self.lang].split("/")[-1]

    @run_before('sanity')
    def set_sanity(self):
        self.sanity_patterns = sn.assert_found(r'IntArray\s+Dataset \{8, 10\}',
                                               self.stdout)

    # NOTE: keeping (reference to old workarounds) as reminder:
    # https://github.com/eth-cscs/cscs-reframe-tests/blob/v23.05/checks/
    # -> libraries/io/hdf5_compile_run.py#L51
