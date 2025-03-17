# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


class netCDFBase(rfm.RegressionTest):
    """
    Write sample data then read it back, using parallel netcdf-hdf5:
    - F90: https://github.com/Unidata/netcdf-fortran/tree/main/examples/F90/
    - C: https://github.com/Unidata/netcdf-c/blob/main/nc_test4/tst_parallel.c
    - C++: https://github.com/Unidata/netcdf-cxx4/tree/master/examples/
    - TODO: compare tst_parallel.c with tst_parallel*.c
    """
    lang = parameter(['f90', 'c', 'cpp'])
    build_locally = False
    build_system = 'Make'
    # modules = ['cray-netcdf-hdf5parallel']  # can't use because of VCUE-100
    executable = 'wr.exe'

    @run_before('compile')
    def set_source(self):
        self.sourcesdir = f'src/netcdf-hdf5parallel/{self.lang}'

    @run_before('run')
    def set_serial_cpp_test(self):
        self.num_tasks = 1 if self.lang == 'cpp' else 4

    @run_before('run')
    def set_job_parameters(self):
        # To avoid: "MPIR_pmi_init(83)....: PMI2_Job_GetId returned 14"
        self.job.launcher.options += (
            self.current_environ.extras.get('launcher_options', [])
        )
        if self.lang in ['f90', 'cpp']:
            launcher = (
                f"{self.job.launcher.registered_name} "
                f"{self.job.launcher.options[0]}"
                if self.job.launcher.options
                else self.job.launcher.registered_name
            )
            self.postrun_cmds = [f'{launcher} rd.exe']

    @run_before('sanity')
    def set_sanity(self):
        regex = {
            'f90': 'SUCCESS reading example file simple_xy_par.nc',  # //
            'c': 'tst_parallel.*ok.$',                               # //
            'cpp': 'SUCCESS reading example file simple_xy.nc',      # not //
        }
        self.sanity_patterns = sn.assert_found(regex[self.lang], self.stdout)


@rfm.simple_test
class CPE_NetcdfTest(netCDFBase):
    valid_systems = ['+remote']
    valid_prog_environs = ['+mpi +netcdf-hdf5parallel -uenv']
    env_vars = {'MPICH_GPU_SUPPORT_ENABLED': 0}
    tags = {'production', 'health', 'craype'}


@rfm.simple_test
class UENV_NetcdfTest(netCDFBase):
    valid_systems = ['+remote']
    valid_prog_environs = ['+mpi +netcdf-hdf5parallel +uenv']
    env_vars = {'PE_ENV': 'UENV'}
    tags = {'production', 'health', 'uenv'}
