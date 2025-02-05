# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib

import reframe as rfm
import reframe.utility.sanity as sn


class NCO_base(rfm.RunOnlyRegressionTest):
    '''
    - 'ncks -r' corresponds to 'cdo --version'
    - 'ncks -M' corresponds to 'cdo info'
    - 'ncks -A' corresponds to 'cdo merge'

    https://www.unidata.ucar.edu/software/netcdf/examples/files.html
    '''
    valid_systems = ['+remote']
    valid_prog_environs = ['+nco']
    resource_dir = variable(
        str, value='/apps/common/UES/reframe/resources/CDO-NCO')
    needs_input = False

    @run_before('run')
    def get_inputfile(self):
        if self.needs_input:
            self.prerun_cmds += [
                f'cp {self.resource_dir}/{input_file} .'
                for input_file in self.test_filename
            ]


@rfm.simple_test
class NCO_nc_config_test(NCO_base):
    '''
    checks that nc-config is built with nc4 support
    '''
    executable = 'nc-config'
    executable_opts = ['--has-nc4']

    @sanity_function
    def assert_output(self):
        return sn.assert_found(r'^yes', self.stdout)


@rfm.simple_test
class NCO_nf_config_test(NCO_base):
    '''
    checks that nf-config is built with nc4 support
    '''
    executable = 'nf-config'
    executable_opts = ['--has-nc4']

    @sanity_function
    def assert_output(self):
        return sn.assert_found(r'^yes', self.stdout)


@rfm.simple_test
class NCO_version_test(NCO_base):
    '''
    checks that nco is built with nc4* file types support:
      netCDF4/HDF5 support  Yes http://nco.sf.net/nco.html#nco4
    '''
    executable = 'ncks'
    executable_opts = ['-r', '2>&1']

    @sanity_function
    def assert_output(self):
        return sn.assert_found(r'^netCDF4/HDF5 support\s+Yes\s', self.stdout)


@rfm.simple_test
class NCO_info_test(NCO_base):
    '''
    checks that `ncks -M` works with nc, nc4 and nc4c files
    '''
    needs_input = True
    test_filename = parameter([
        ['sresa1b_ncar_ccsm3-example.nc'],
        ['test_echam_spectral-deflated_wind10_wl_ws.nc4'],
        ['test_echam_spectral-deflated_wind10_wl_ws.nc4c'],
    ])
    executable = 'ncks'

    @run_before('run')
    def set_executable_opts(self):
        self.executable_opts = ['-M', self.test_filename[0], '2>&1']

    @sanity_function
    def assert_output(self):
        regexes = {
            '.nc': r'model_name_english.*NCAR CCSM',
            '.nc4': r'physics.*Modified ECMWF physics',
            '.nc4c': r'physics.*Modified ECMWF physics',
        }
        test_type = pathlib.Path(self.test_filename[0]).suffix
        return sn.all([
            sn.assert_found(regexes[test_type], self.stdout),
            sn.assert_not_found(r'(?i)unsupported|error', self.stderr),
        ])


@rfm.simple_test
class NCO_merge_test(NCO_base):
    '''
    checks that `ncks -A` works with nc, nc4 and nc4c files
    '''
    needs_input = True
    test_filename = parameter([
        ['sresa1b_ncar_ccsm3-example_pr.nc',
         'sresa1b_ncar_ccsm3-example_tas.nc'],
        #
        ['test_echam_spectral-deflated_wind10.nc4',
         'test_echam_spectral-deflated_wl.nc4'],
        #
        ['test_echam_spectral-deflated_wind10.nc4c',
         'test_echam_spectral-deflated_wl.nc4c'],
    ])
    executable = 'ncks'

    @run_before('run')
    def set_executable_opts(self):
        test_type = pathlib.Path(self.test_filename[0]).suffix
        extra = '-L 2' if test_type == '.nc4c' else ''
        self.executable_opts = ['-A', extra, self.test_filename[0], '2>&1']

    @sanity_function
    def assert_output(self):
        return sn.all([
            sn.assert_not_found(r'(?i)unsupported|error', self.stderr),
            sn.assert_not_found(r'(?i)unsupported|error', self.stdout)
        ])
