# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import re

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class LibSciAccSymLinkTest(rfm.RunOnlyRegressionTest):
    lib_name = parameter([
        'libsci_acc_cray_nv90', 'libsci_acc_gnu_nv90'
    ])

    def __init__(self):
        self.descr = f'LibSciAcc symlink check of {self.lib_name}'
        self.valid_systems = [
            'daint:login', 'daint:normal'
        ]

        # The prgenv is irrelevant for this case, so just chose one
        self.valid_prog_environs = ['builtin']
        self.executable = 'ls'
        self.executable_opts = ['-al', '/opt/cray/pe/lib64/libsci_a*']
        self.sanity_patterns = sn.assert_found(f'{self.lib_name}.so',
                                               self.stdout)

        self.maintainers = ['AJ', 'LM']
        self.tags = {'production', 'craype', 'health'}
