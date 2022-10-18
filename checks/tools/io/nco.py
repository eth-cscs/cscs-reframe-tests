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


class NCOBaseTest(rfm.RunOnlyRegressionTest):
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
            self.modules = ['nco', 'netcdf-fortran']
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
            self.modules = ['NCO']


# Check that the netCDF loaded by the nco module supports the nc4 filetype
# (nc4 support must be explicitly activated when the netCDF library is
# compiled...).
@rfm.simple_test
class NCO_DependencyTest(NCOBaseTest):
    descr = ('verifies that the netCDF loaded by the NCO module '
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
class NCO_NC4SupportTest(NCOBaseTest):
    descr = ('verifies that nco supports the nc4 filetype')
    sourcesdir = None

    @run_before('run')
    def setup_per_partition_name(self):
        if 'squashfs' in self.current_partition.name:
            self.executable = f'bash {self.squashfs_script}'
            self.executable_opts = ['ncks', '-r', '2>&1']
        else:
            self.executable = 'ncks'
            self.executable_opts = ['-r', '2>&1']

    @sanity_function
    def assert_output(self):
        return sn.all([
            sn.assert_found(r'^netCDF4/HDF5 (support|available)\s+Yes\W',
                            self.stdout),
            sn.assert_found(r'^netCDF4/HDF5 (support|enabled)\s+Yes\W',
                            self.stdout)
        ])


# All nco check load the nco module (see ncoBaseTest). This test tries to load
# then the NCO module to see if there appear any conflicts. If there are no
# conflicts then self.stdout and self.stderr are empty. Note that the command
# 'module load NCO' cannot be passed via self.executable to srun as 'module'
# is not an executable. Thus, we run the command as a prerun_cmds command and
# define as executable just an echo with no arguments.
@rfm.simple_test
class NCO_CDOModuleCompatibilityTest(NCOBaseTest):
    descr = ('verifies compatibility with the CDO module')
    sourcesdir = None
    executable = 'echo'

    @run_before('run')
    def setup_nco_modulefile_name(self):
        self.skip_if('squashfs' in self.current_partition.name,
                     'skip NCO_CDOModuleCompatibilityTest with squashfs pe')
        if self.current_system.name in ['arolla', 'tsa']:
            nco_name = 'cdo'
        else:
            nco_name = 'CDO'

        self.prerun_cmds += [f'module load {nco_name}']

    @sanity_function
    def assert_output(self):
        return sn.assert_not_found(r'(?i)error|conflict|unsupported|failure',
                                   self.stderr)


@rfm.simple_test
class NCO_InfoNCTest(NCOBaseTest):
    test_filename = parameter([
        'sresa1b_ncar_ccsm3-example.nc',
        'test_echam_spectral-deflated_wind10_wl_ws.nc4',
        'test_echam_spectral-deflated_wind10_wl_ws.nc4c',
    ])
    descr = ('verifies reading info of a netCDF file')

    @run_before('run')
    def copy_input_data(self):
        in_file = os.path.join(self.current_system.resourcesdir, 'CDO-NCO',
                               self.test_filename)
        self.prerun_cmds += [f'cp {in_file} .']

    @run_before('run')
    def setup_per_partition_name(self):
        self.executable = (
            f'bash {self.squashfs_script} ncks'
            if 'squashfs' in self.current_partition.name else 'ncks')

        self.executable_opts = ['-M', self.test_filename, '2>&1']

    @sanity_function
    def assert_output(self):
        value = {
            'sresa1b_ncar_ccsm3-example.nc': 'model_name_english.*NCAR CCSM',
            'test_echam_spectral-deflated_wind10_wl_ws.nc4':
                r'physics.*Modified ECMWF physics',
            'test_echam_spectral-deflated_wind10_wl_ws.nc4c':
                r'physics.*Modified ECMWF physics',
        }
        return sn.assert_found(value[self.test_filename], self.stdout)


@rfm.simple_test
class NCO_MergeNCTest(NCOBaseTest):
    test_type = parameter(['nc', 'nc4', 'nc4c'])
    descr = ('verifies merging of 2 netCDF files')
    # NOTE: we only verify that there is no error produced. We do not
    # verify the resulting file. Verifying would not be straight forward
    # as the following does not work (it seems that there is a timestamp
    # of file creation inserted in the metadata or similar):
    # diff sresa1b_ncar_ccsm3-example_tas.nc \
    #      sresa1b_ncar_ccsm3-example_pr_tas.nc

    @run_before('run')
    def copy_input_data(self):
        inputs = {
            'nc': ['sresa1b_ncar_ccsm3-example_pr.nc',
                   'sresa1b_ncar_ccsm3-example_tas.nc'],
            'nc4': ['test_echam_spectral-deflated_wind10.nc4',
                    'test_echam_spectral-deflated_wl.nc4'],
            'nc4c': ['test_echam_spectral-deflated_wind10.nc4c',
                     'test_echam_spectral-deflated_wl.nc4c'],
        }
        input_path = os.path.join(self.current_system.resourcesdir, 'CDO-NCO')
        for idx in range(2):
            self.prerun_cmds += [
                f'cp {input_path}/{inputs[self.test_type][idx]} .']

    @run_before('run')
    def setup_per_partition_name(self):
        self.executable = (
            f'bash {self.squashfs_script} ncks'
            if 'squashfs' in self.current_partition.name else 'nco')

        self.executable_opts = ['-A', f'*.{self.test_type}']

    @sanity_function
    def assert_output(self):
        return sn.all([
            sn.assert_not_found(r'(?i)unsupported|error', self.stdout)
            # sn.assert_not_found(r'(?i)unsupported|error', self.stderr),
        ])
