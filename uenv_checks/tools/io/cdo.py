# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib

import reframe as rfm
import reframe.utility.sanity as sn


class CDO_base(rfm.RunOnlyRegressionTest):
    '''
    https://www.unidata.ucar.edu/software/netcdf/examples/files.html
    '''
    valid_systems = ['+remote']
    valid_prog_environs = ['+cdo']
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
class CDO_nc_config_test(CDO_base):
    '''
    checks that nc-config is built with nc4 support
    '''
    executable = 'nc-config'
    executable_opts = ['--has-nc4']

    @sanity_function
    def assert_output(self):
        return sn.assert_found(r'^yes', self.stdout)


@rfm.simple_test
class CDO_nf_config_test(CDO_base):
    '''
    checks that nf-config is built with nc4 support
    '''
    executable = 'nf-config'
    executable_opts = ['--has-nc4']

    @sanity_function
    def assert_output(self):
        return sn.assert_found(r'^yes', self.stdout)


@rfm.simple_test
class CDO_version_test(CDO_base):
    '''
    checks that cdo is built with nc4* file types support:
      CDI file types: srv ext ieg grb1 grb2 nc1 nc2 nc4 nc4c nc5
    '''
    executable = 'cdo'
    executable_opts = ['--version', '2>&1']

    @sanity_function
    def assert_output(self):
        return sn.assert_found(r'types:.*\snc4\snc4c\W', self.stdout)


@rfm.simple_test
class CDO_info_test(CDO_base):
    '''
    checks that `cdo info` works with nc, nc4 and nc4c files
    '''
    needs_input = True
    test_filename = parameter([
        ['sresa1b_ncar_ccsm3-example.nc'],
        ['test_echam_spectral-deflated_wind10_wl_ws.nc4'],
        ['test_echam_spectral-deflated_wind10_wl_ws.nc4c'],
    ])
    executable = 'cdo'

    @run_before('run')
    def set_executable_opts(self):
        self.executable_opts = ['info', self.test_filename[0], '2>&1']

    @sanity_function
    def assert_output(self):
        ref_values = {
            'sresa1b_ncar_ccsm3-example.nc': '688128',
            'test_echam_spectral-deflated_wind10_wl_ws.nc4': '442368',
            'test_echam_spectral-deflated_wind10_wl_ws.nc4c': '442368',
        }
        regex = (
            f'info: Processed {ref_values[self.test_filename[0]]} values from '
            r'(5|3) variables over (1|8) timestep'
            # different output with different cdo versions
        )
        return sn.assert_found(regex, self.stdout)


@rfm.simple_test
class CDO_merge_test(CDO_base):
    '''
    checks that `cdo merge` works with nc, nc4 and nc4c files
    '''
    needs_input = True
    test_filename = parameter([
        ['sresa1b_ncar_ccsm3-example_pr.nc',
         'sresa1b_ncar_ccsm3-example_tas.nc',
         'sresa1b_ncar_ccsm3-example_area.nc'],
        ['test_echam_spectral-deflated_wind10.nc4',
         'test_echam_spectral-deflated_wl.nc4',
         'test_echam_spectral-deflated_ws.nc4'],
        ['test_echam_spectral-deflated_wind10.nc4c',
         'test_echam_spectral-deflated_wl.nc4c',
         'test_echam_spectral-deflated_ws.nc4c'],
    ])
    executable = 'cdo'

    @run_before('run')
    def set_executable_opts(self):
        test_type = pathlib.Path(self.test_filename[0]).suffix
        # TODO: extra = '-z zip' if test_type == '.nc4c' else ''
        self.executable_opts = [
            '-O', 'merge', self.test_filename[0], f'merged{test_type}', '2>&1'
        ]

    @sanity_function
    def assert_output(self):
        ref_values = {
            '.nc': '32768',
            '.nc4': '147456',
            '.nc4c': '147456',
        }
        test_type = pathlib.Path(self.test_filename[0]).suffix
        regex = f'merge: Processed {ref_values[test_type]} values from'
        return sn.assert_found(regex, self.stdout)
