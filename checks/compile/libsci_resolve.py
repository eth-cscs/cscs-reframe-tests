# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


class LibSciResolveBaseTest(rfm.CompileOnlyRegressionTest):
    sourcesdir = 'src/libsci_resolve'
    sourcepath = 'libsci_resolve.f90'
    executable = 'libsciresolve.x'
    valid_systems = ['daint:login', 'daint:normal']
    maintainers = ['AJ', 'LM']
    tags = {'production', 'craype'}

    @run_after('setup')
    def set_postbuild_cmds(self):
        self.postbuild_cmds = [f'readelf -d {self.executable}']


@rfm.simple_test
class NvidiaResolveTest(LibSciResolveBaseTest):
    accel_nvidia_version = parameter(['90'])
    valid_prog_environs = ['PrgEnv-cray', 'PrgEnv-gnu']
    build_system = 'SingleSource'

    @run_after('init')
    def set_description(self):
        self.descr = (f'Module craype-accel-nvidia{self.accel_nvidia_version} '
                      f'resolves libsci_acc')

    @run_after('init')
    def update_tags(self):
        self.tags.add('health')

    @run_after('setup')
    def set_modules(self):
        self.modules += [
            'cudatoolkit', f'craype-accel-nvidia{self.accel_nvidia_version}',
            'cray-libsci_acc'
        ]

    @sanity_function
    def libsci_acc_resolve(self):
        # here lib_name is in the format: libsci_acc_gnu_nv35.so or
        #                                 libsci_acc_cray_nv35.so
        regex = (r'.*\(NEEDED\).*libsci_acc_(?P<prgenv>[A-Za-z]+)_'
                 r'(?P<version>\S+)\.so')
        prgenv = self.current_environ.name.split('-')[1]
        mod_name = f'nv{self.accel_nvidia_version}'
        return sn.all([
            sn.assert_eq(
                sn.extractsingle(regex, self.stdout, 'prgenv'), prgenv),
            sn.assert_eq(
                sn.extractsingle(regex, self.stdout, 'version'), mod_name)
        ])


@rfm.simple_test
class MKLResolveTest(LibSciResolveBaseTest):
    descr = '-mkl Resolves to MKL'
    valid_prog_environs = ['PrgEnv-intel']
    build_system = 'SingleSource'

    @run_before('compile')
    def set_fflags(self):
        self.build_system.fflags = ['-mkl']

    @sanity_function
    def libmkl_resolve(self):
        regex = (r'.*\(NEEDED\).*libmkl_(?P<prgenv>[A-Za-z]+)_(?P<version>\S+)'
                 r'\.so')
        return sn.all([
            sn.assert_eq(
                sn.extractsingle(regex, self.stdout, 'prgenv'), 'intel'),
            sn.assert_eq(
                sn.extractsingle(regex, self.stdout, 'version'), 'lp64')
        ])
