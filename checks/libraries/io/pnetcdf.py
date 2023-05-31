# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.osext as osext
import reframe.utility.sanity as sn


@rfm.simple_test
class PnetCDFTest(rfm.RegressionTest):
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
        if self.lang == 'f90' and self.current_environ.name == 'PrgEnv-gnu':
            self.build_system.fflags = [
                '-w', '-fallow-argument-mismatch', 'utils.F90'
            ]
        else:
            self.build_system.fflags = ['utils.F90']

    @run_before('run')
    def fix_cpe(self):
        # fix for "GLIBCXX_3.4.29 not found" error:
        if self.lang == 'cpp' and self.current_environ.name == 'PrgEnv-gnu':
            # pkg-config --variable path gcc-toolchain -> /opt/cray/pe/gcc/12.2.0/snos
            # LD_PRELOAD=/opt/cray/pe/gcc/12.2.0/snos/lib64/libstdc++.so
            self.env_vars = {
                'LD_PRELOAD': '/opt/cray/pe/gcc/12.2.0/snos/lib64/libstdc++.so'
            }

    @run_before('run')
    def set_job_parameters(self):
        # To avoid: "MPIR_pmi_init(83)....: PMI2_Job_GetId returned 14"
        self.job.launcher.options += (
            [self.current_environ.extras['launcher_options']]
            if 'launcher_options' in self.current_environ.extras
            else ''
        )

    @run_before('sanity')
    def set_sanity(self):
        regex = {
            'cpp': 'File "testfile.nc" is a valid NetCDF classic CDF-5 file.',
            'f90': 'File "testfile.nc" is a valid NetCDF classic CDF-1 file.'
        }
        self.sanity_patterns = sn.assert_found(regex[self.lang], self.stdout)
