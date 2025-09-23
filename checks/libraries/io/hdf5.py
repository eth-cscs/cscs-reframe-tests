# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os

import reframe as rfm
import reframe.utility.sanity as sn


class HDF5TestBase(rfm.RegressionTest):
    """
    Create a file and dataset and select/read a subset from the dataset
    https://portal.hdfgroup.org/display/HDF5/Examples+from+Learning+the+Basics
    """
    lang = parameter(['cpp', 'f90'])
    build_system = 'SingleSource'
    num_tasks = 1
    build_locally = False
    postrun_cmds = ['h5ls *.h5']

    @run_before('compile')
    def set_source(self):
        repo = 'https://raw.githubusercontent.com/HDFGroup/hdf5/develop'
        src = {
            'cpp': 'c++/examples/h5tutr_subset.cpp',
            'f90': 'fortran/examples/h5_subset.f90'
        }
        self.sourcepath = src[self.lang].split("/")[-1]

    @run_before('sanity')
    def set_sanity(self):
        self.sanity_patterns = sn.assert_found(r'IntArray\s+Dataset \{8, 10\}',
                                               self.stdout)

    # NOTE: keeping (reference to old workarounds) as reminder:
    # https://github.com/eth-cscs/cscs-reframe-tests/blob/v23.05/checks/
    # -> libraries/io/hdf5_compile_run.py#L51


@rfm.simple_test
class CPE_HDF5Test(HDF5TestBase):
    modules = ['cray-hdf5']
    valid_systems = ['+remote']
    valid_prog_environs = ['+cpe -uenv']
    tags = {'health', 'craype'}

    @run_after('init')
    def skip_uenv_tests(self):
        # it seems that valid_prog_environs ignores -uenv
        self.skip_if(os.environ.get("UENV") is not None)


@rfm.simple_test
class Uenv_HDF5Test(HDF5TestBase):
    valid_prog_environs = ['-cpe +uenv +prgenv']
    valid_systems = ['+remote']
    tags = {'production', 'health', 'uenv'}

    @run_before('compile')
    def set_build_flags(self):
        pkgconfig = {
            'cpp': '`pkg-config --libs hdf5_cpp`',
            'f90': '`pkg-config --libs hdf5_fortran`'
        }
        self.build_system.cppflags = ['`pkg-config --cflags hdf5`']
        self.build_system.ldflags = [
            pkgconfig[self.lang],
            '-Wl,-rpath,`pkg-config --variable=libdir hdf5`'
        ]
