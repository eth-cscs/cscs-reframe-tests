# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.osext as osext
import reframe.utility.sanity as sn


@rfm.simple_test
class DefaultPrgEnvCheck(rfm.RunOnlyRegressionTest):
    descr = 'Ensure PrgEnv-cray is loaded by default'
    valid_prog_environs = ['builtin']
    valid_systems = ['daint:login', 'eiger:login', 'pilatus:login']
    modules = ['cray']
    executable = 'module'
    executable_opts = ['--terse', 'list']
    tags = {'production', 'craype'}

    @sanity_function
    def assert_cray(self):
        return sn.assert_found(r'^PrgEnv-cray', self.stderr)


@rfm.simple_test
class EnvironmentCheck(rfm.RunOnlyRegressionTest):
    descr = 'Ensure programming environment is loaded correctly'
    valid_systems = ['daint:login', 'eiger:login', 'pilatus:login']

    # FIXME: PrgEnv-nvidia is not found when loaded
    valid_prog_environs = ['PrgEnv-aocc', 'PrgEnv-cray', 'PrgEnv-gnu']
    executable = 'module'
    executable_opts = ['--terse', 'list']
    tags = {'production', 'craype'}

    @sanity_function
    def assert_found_module(self):
        module_patt = rf'^{self.current_environ.name}'
        return sn.assert_found(module_patt, self.stderr)


class CrayVariablesCheck(rfm.RunOnlyRegressionTest):
    cray_module = parameter()
    descr = 'Check for standard Cray variables'
    valid_prog_environs = ['builtin']
    executable = 'module'
    modules = ['cray']
    tags = {'production', 'craype'}

    @run_before('run')
    def set_exec_opts(self):
        self.executable_opts = ['show', self.cray_module]

    @run_after('init')
    def skip_modules(self):
        # FIXME: These modules should be fixed in later releases
        if self.cray_module in {'cray-fftw', 'cray-libsci', 'cray-python'}:
            self.valid_systems = []

    @sanity_function
    def assert_variables_set(self):
        envvar_prefix = self.cray_module.upper().replace('-', '_')
        return sn.all([
            sn.assert_found(f'{envvar_prefix}_PREFIX', self.stderr),
            sn.assert_found(f'{envvar_prefix}_VERSION', self.stderr)
        ])


@rfm.simple_test
class CrayVariablesCheckDaint(CrayVariablesCheck):
    cray_module = parameter([
        'cray-fftw', 'cray-hdf5', 'cray-hdf5-parallel', 'cray-libsci',
        'cray-mpich', 'cray-python', 'cray-R', 'cudatoolkit', 'papi',
    ])
    valid_systems = ['daint:login']


@rfm.simple_test
class CrayVariablesCheckEiger(CrayVariablesCheck):
    cray_module = parameter([
        'cray-fftw', 'cray-hdf5', 'cray-hdf5-parallel',
        'cray-mpich', 'cray-openshmemx', 'cray-parallel-netcdf', 'cray-pmi',
        'cray-python', 'cray-R', 'papi'
    ])
    valid_systems = ['eiger:login', 'pilatus:login']
