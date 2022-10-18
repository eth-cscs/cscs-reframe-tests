# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
# {{{ The first of the following tests verify the installation. The remaining
# tests operate on files. All netCDF files incl CDL metadata were
# downloaded from:
# https://www.unidata.ucar.edu/software/netcdf/examples/files.html
# To avoid large test files some of the originally downloaded files were split
# using 'cdo splitname <varname> <varname>_'.
# CDO has over 700 operators. To verify the basic functioning of CDO, I
# selected 'info' and 'merge'. The rationale of this selection is:
# - 'info' is probably the most basic operator and it verifies that metadata
# can be accessed correctly;
# - 'merge' is a rather complex operator which verifies that data and metadata
# can be read and written.
# The next step to enlarge the CDO verification would probably be to perform
# the test with different files having different structures and organisation.
# In fact, the test InfoNC4Test for example fails if the file is changed to
# 'test_hgroups.nc4'; it gives the error:
#   cdo info: Open failed on >test_hgroups.nc4<
#   Unsupported file structure"
# }}}
import os

import reframe as rfm
import reframe.utility.sanity as sn


class CDOBaseTest(rfm.RunOnlyRegressionTest):
    valid_systems = ['daint:gpu', 'daint:mc', 'dom:gpu',
                     'dom:mc', 'arolla:pn', 'tsa:pn',
                     'eiger:mc', 'pilatus:mc',
                     'manali:gpu-squashfs', 'balfrin:gpu-squashfs']
    # TODO: update maintainers ?
    maintainers = ['SO', 'CB']
    tags = {'production', 'mch', 'external-resources'}

    @run_after('init')
    def setup_valid_pe(self):
        if self.current_system.name in ['arolla', 'tsa']:
            self.exclusive_access = True
            self.valid_prog_environs = ['PrgEnv-gnu', 'PrgEnv-gnu-nompi']
            self.modules = ['cdo', 'netcdf-fortran']
        elif self.current_system.name in ['eiger', 'pilatus']:
            self.valid_prog_environs = ['cpeGNU']
            self.modules = ['CDO']
        elif self.current_system.name in ['manali', 'balfrin']:
            self.valid_prog_environs = ['PrgEnv-gnu']
            self.modules = ['cdo', 'netcdf-fortran']
            self.squashfs_script = './exe.sh'
            # until VCMSA-102 is resolved:
            if self.current_system.name in ['balfrin']:
                self.prerun_cmds += [
                    r'echo "export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:'
                    rf'\$SCRATCH/balfrin/lib64" >> {self.squashfs_script}'
                ]
            self.prerun_cmds += [
                f'grep ^module rfm_job.sh |grep -v unuse >> '
                f'{self.squashfs_script}',
                f'echo "\\$*" >> {self.squashfs_script}',
            ]
        else:
            self.valid_prog_environs = ['builtin']
            self.modules = ['CDO']


# Check that the netCDF loaded by the CDO module supports the nc4 filetype
# (nc4 support must be explicitly activated when the netCDF library is
# compiled...).
@rfm.simple_test
class CDO_DependencyTest(CDOBaseTest):
    descr = ('verifies that the netCDF loaded by the CDO module '
             'supports the nc4 filetype')
    sourcesdir = None

    @run_before('run')
    def setup_per_partition_name(self):
        if 'squashfs' in self.current_partition.name:
            self.executable = f'bash {self.squashfs_script}'
            self.executable_opts = ['nf-config', '--has-nc4']
        else:
            self.executable = 'nc-config'
            self.executable_opts = ['--has-nc4']

    @sanity_function
    def assert_output(self):
        return sn.assert_found(r'^yes', self.stdout)


@rfm.simple_test
class CDO_NC4SupportTest(CDOBaseTest):
    descr = ('verifies that the CDO supports the nc4 filetype')
    sourcesdir = None

    @run_before('run')
    def setup_per_partition_name(self):
        if 'squashfs' in self.current_partition.name:
            self.executable = f'bash {self.squashfs_script}'
            self.executable_opts = ['cdo', '-V', '2>&1']
        else:
            self.executable = 'cdo'
            self.executable_opts = ['-V', '2>&1']

    @sanity_function
    def assert_output(self):
        return sn.assert_found(r'types:.*\snc4\snc4c\W', self.stdout)


# All CDO check load the CDO module (see CDOBaseTest). This test tries to load
# then the NCO module to see if there appear any conflicts. If there are no
# conflicts then self.stdout and self.stderr are empty. Note that the command
# 'module load NCO' cannot be passed via self.executable to srun as 'module'
# is not an executable. Thus, we run the command as a prerun_cmds command and
# define as executable just an echo with no arguments.
@rfm.simple_test
class CDO_NCOModuleCompatibilityTest(CDOBaseTest):
    descr = ('verifies compatibility with the NCO module')
    sourcesdir = None
    executable = 'echo'

    @run_before('run')
    def setup_nco_modulefile_name(self):
        self.skip_if('squashfs' in self.current_partition.name,
                     'skip CDO_NCOModuleCompatibilityTest with squashfs pe')
        if self.current_system.name in ['arolla', 'tsa']:
            nco_name = 'nco'
        else:
            nco_name = 'NCO'

        self.prerun_cmds += [f'module load {nco_name}']

    @sanity_function
    def assert_output(self):
        return sn.assert_not_found(r'(?i)error|conflict|unsupported|failure',
                                   self.stderr)


@rfm.simple_test
class CDO_InfoNCTest(CDOBaseTest):
    test_filename = parameter([
        'sresa1b_ncar_ccsm3-example.nc',
        'test_echam_spectral-deflated_wind10_wl_ws.nc4',
        'test_echam_spectral-deflated_wind10_wl_ws.nc4c',
    ])
    descr = ('verifies reading info of a netCDF file')
    # TODO: Add here also Warning? then it fails currently...

    @run_before('run')
    def copy_input_data(self):
        in_file = os.path.join(self.current_system.resourcesdir, 'CDO-NCO',
                               self.test_filename)
        self.prerun_cmds += [f'cp {in_file} .']

    @run_before('run')
    def setup_per_partition_name(self):
        self.executable = (
            f'bash {self.squashfs_script} cdo'
            if 'squashfs' in self.current_partition.name else 'cdo')

        self.executable_opts = ['info', self.test_filename, '2>&1']

    @sanity_function
    def assert_output(self):
        value = {
            'sresa1b_ncar_ccsm3-example.nc': '688128',
            'test_echam_spectral-deflated_wind10_wl_ws.nc4': '442368',
            'test_echam_spectral-deflated_wind10_wl_ws.nc4c': '442368',
        }
        regex = (
            f'info: Processed {value[self.test_filename]} values from '
            r'(5|3) variables over (1|8) timestep'
        )
        return sn.assert_found(regex, self.stdout)


@rfm.simple_test
class CDO_MergeNCTest(CDOBaseTest):
    test_type = parameter(['nc', 'nc4', 'nc4c'])
    descr = ('verifies merging of 3 netCDF files')

    @run_before('run')
    def copy_input_data(self):
        inputs = {
            'nc': ['sresa1b_ncar_ccsm3-example_pr.nc',
                   'sresa1b_ncar_ccsm3-example_tas.nc',
                   'sresa1b_ncar_ccsm3-example_area.nc'],
            'nc4': ['test_echam_spectral-deflated_wind10.nc4',
                    'test_echam_spectral-deflated_wl.nc4',
                    'test_echam_spectral-deflated_ws.nc4'],
            'nc4c': ['test_echam_spectral-deflated_wind10.nc4c',
                     'test_echam_spectral-deflated_wl.nc4c',
                     'test_echam_spectral-deflated_ws.nc4c'],
        }
        input_path = os.path.join(self.current_system.resourcesdir, 'CDO-NCO')
        for idx in range(3):
            self.prerun_cmds += [
                f'cp {input_path}/{inputs[self.test_type][idx]} .']

    @run_before('run')
    def setup_per_partition_name(self):
        self.executable = (
            f'bash {self.squashfs_script} cdo'
            if 'squashfs' in self.current_partition.name else 'cdo')

        self.executable_opts = [
            '-O', 'merge', f'*.{self.test_type}',
            f'merged.{self.test_type}', '2>&1'
        ]

    @sanity_function
    def assert_output(self):
        value = {'nc': '98304', 'nc4': '442368', 'nc4c': '442368'}
        regex = (
            f'merge: Processed {value[self.test_type]} values from 3 variables'
        )
        return sn.assert_found(regex, self.stdout)
