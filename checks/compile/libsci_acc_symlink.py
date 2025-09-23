# Copyright 2016 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause


import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class LibSciAccSymLinkTest(rfm.RunOnlyRegressionTest):
    executable = 'ls'
    executable_opts = ['-al', '/opt/cray/pe/lib64/libsci_a*']
    valid_systems = ['daint:login', 'daint:normal']
    valid_prog_environs = ['builtin']
    lib_name = parameter([
        'libsci_acc_cray_nv90', 'libsci_acc_gnu_nv90'
    ])

    tags = {'craype', 'health'}

    @run_after('init')
    def set_descr(self): 
        self.descr = f'LibSciAcc symlink check of {self.lib_name}'

    @sanity_function
    def assert_found_lib(self):
        return sn.assert_found(f'{self.lib_name}.so', self.stdout)
