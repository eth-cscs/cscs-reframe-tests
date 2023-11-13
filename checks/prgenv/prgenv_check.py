# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os

import reframe as rfm
import reframe.utility.sanity as sn


@sn.deferrable
def my_join(s, iterable):
    return s.join(iterable)


@rfm.simple_test
class LoginEnvCheck(rfm.RunOnlyRegressionTest):
    variant = parameter(['rpm', 'modules', 'env'])
    valid_systems = ['daint:login', 'dom:login', 'eiger:login']
    valid_prog_environs = ['builtin']
    ref_file = variable(str)
    diff_file = variable(str)
    captured_file = variable(str)
    maintainers = ['RS', 'VH']
    tags = {'production'}

    @run_after('init')
    def set_descr(self):
        self.descr = f'Environment check: {self.variant}'

    @run_after('setup')
    def set_sourcesdir(self):
        self.sourcesdir = os.path.join(self.current_system.resourcesdir,
                                       'LoginEnvCheck')

    @run_after('setup')
    def set_keep_files(self):
        if self.variant == 'rpm':
            self.ref_file = f'ref_rpm_{self.current_system.name}.log'
        elif self.variant == 'modules':
            self.ref_file = f'ref_modules_{self.current_system.name}.log'
        else:
            self.ref_file = f'ref_env_{self.current_system.name}.log'

        self.diff_file = f'diff_{self.variant}.log'
        self.captured_file = f'captured_{self.variant}.log'
        self.keep_files = [self.diff_file, self.captured_file, self.ref_file]

    @run_before('run')
    def set_executable(self):
        if self.variant == 'rpm':
            self.executable = 'rpm'
        elif self.variant == 'modules':
            self.executable = 'module'
        else:
            self.executable = 'env'

    @run_before('run')
    def set_executable_opts(self):
        if self.variant == 'rpm':
            self.executable_opts = ['-qa']
        elif self.variant == 'modules':
            self.executable_opts = ['-t', 'avail', '2>&1']
        else:
            whitelist = [
                '^PE', '^XALT', '^CRAY', '^NVIDIA', '^SLURM',
                '^LIBSCI', '^MPICH', '^PAT_', '^XTPE_NETWORK_TARGET',
                '^PKG_CONFIG_PATH_', '^MODULE_', '^PKGCONFIG_',
                '^MODULESHOME', '^INCLUDE', '^DVS', '^FTN_', '^GCC_',
                '^CC_', '^ASSEMBLER_', '^FORTRAN', '^ATP', '^ALLINEA',
                '^ALT_', '^LINKER'
            ]
            self.executable_opts = [
                '|', 'egrep',
                "'(" + '|'.join(whitelist) + ")'",

                # Ignore variables with empty values; these are not present in
                # the environment, when reframe runs within a Jenkins instance
                '|', 'grep', '-v', "'=$'",

                # Ignore variable XALT_DATE_TIME since it changes continuously,
                # as well as XALT_RUN_UUID since it changes according to user.
                '|', 'egrep', '-v', "'(XALT_DATE_TIME|XALT_RUN_UUID)'",

                # Trim trailing whitespace
                '|', 'sed', "'s/[[:space:]]*$//'"
            ]

        self.executable_opts += ['|', 'sort', '-f', '>', self.captured_file]

    @run_before('run')
    def setup_postrun_cmds(self):
        self.postrun_cmds = [
            f'diff -u0 {self.ref_file} {self.captured_file} > {self.diff_file}'
        ]

    @sanity_function
    def assert_unchanged_environ(self):
        lines = sn.extractall(r'.+', self.diff_file)
        stderr_lines = sn.extractall(r'.+', self.stderr)
        return sn.all([
            sn.assert_eq(sn.count(lines), 0,
                'Login environment has changed:\n' + my_join('\n', lines)),
            sn.assert_eq(sn.count(stderr_lines), 0, my_join('', stderr_lines))
        ])
