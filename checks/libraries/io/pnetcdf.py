# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib
import sys

import reframe as rfm
import reframe.utility.osext as osext
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))
from extra_launcher_options import ExtraLauncherOptionsMixin


@rfm.simple_test
class PnetCDFTest(rfm.RegressionTest, ExtraLauncherOptionsMixin):
    """
    Write 6 3D integer array variables into a file. Each variable in the file
    is a dimensional transposed array from the one stored in memory.
    https://github.com/Parallel-NetCDF/PnetCDF
    """
    lang = parameter(['cpp', 'f90'])
    valid_systems = ['+remote']
    valid_prog_environs = ['+mpi +pnetcdf']
    build_system = 'SingleSource'
    modules = ['cray-parallel-netcdf']
    num_tasks = 4
    postrun_cmds = ['ncvalidator testfile.nc']
    sourcesdir = 'src/pnetcdf'
    env_vars = {'MPICH_GPU_SUPPORT_ENABLED': 0}
    tags = {'production', 'craype', 'health'}

    @run_before('compile')
    def set_source(self):
        repo = 'https://raw.githubusercontent.com/Parallel-NetCDF/PnetCDF'
        src = {
            'cpp': 'master/examples/CXX/transpose.cpp',
            'f90': 'master/examples/F90/transpose.f90'
        }
        self.sourcepath = src[self.lang].split("/")[-1]

    @run_before('compile')
    def setflags(self):
        cdt_version = osext.cray_cdt_version() or 'N/A'
        if self.lang == 'f90' and self.current_environ.name == 'PrgEnv-gnu':
            self.build_system.fflags = [
                '-w', '-fallow-argument-mismatch', 'utils.F90'
            ]
        elif (cdt_version != 'N/A' and cdt_version >= '23.05' and
              self.lang == 'f90' and
              self.current_environ.name == 'PrgEnv-cray'):
            self.build_system.fflags = [
                '-L/opt/cray/pe/cce/16.0.0/cce-clang/x86_64/lib/'
                'x86_64-unknown-linux-gnu -lunwind',
                'utils.F90'
            ]
        else:
            self.build_system.fflags = ['utils.F90']

        # FIXME: hidden symbol `_Unwind_Resume' ...  is referenced by DSO
        if (cdt_version != 'N/A' and cdt_version >= '23.05' and
            self.lang == 'f90' and
            self.current_environ.name == 'PrgEnv-cray'):
            self.build_system.ldlags = [
                '-L/opt/cray/pe/cce/16.0.0/cce-clang/x86_64/lib/'
                'x86_64-unknown-linux-gnu -lunwind',
            ]

    @run_before('sanity')
    def set_sanity(self):
        regex = {
            'cpp': 'File "testfile.nc" is a valid NetCDF classic CDF-5 file.',
            'f90': 'File "testfile.nc" is a valid NetCDF classic CDF-1 file.'
        }
        self.sanity_patterns = sn.assert_found(regex[self.lang], self.stdout)
