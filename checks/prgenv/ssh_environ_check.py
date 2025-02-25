# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class SSHLoginEnvCheck(rfm.RunOnlyRegressionTest):
    descr = ('Check the values of a set of environment variables '
             'when accessing remotely over SSH')
    valid_systems = []
    sourcesdir = None
    valid_prog_environs = ['PrgEnv-cray']
    var_ref = {
        'CRAY_CPU_TARGET': ('arm-grace'),
        'CRAYPE_NETWORK_TARGET': 'ofi',
        'MODULEPATH': r'[\S+]',
        'MODULESHOME': r'/opt/cray/pe/lmod/\S+',
        'PE_PRODUCT_LIST': 'CRAYPE_ARM_GRACE:CRAYPE:PERFTOOLS:CRAYPAT',
        'SCRATCH': r'/(capstor|iopstor)/\S+',
        'XDG_RUNTIME_DIR': r'/run/user/[\d+]'
    }
    executable = 'ssh'
    tags = {'maintenance', 'production', 'craype'}

    @run_before('run')
    def set_exec_opts(self):
        echo_args = ' '.join(f'{i}=${i}' for i in self.var_ref.keys())
        self.executable_opts = [self.current_system.name, 'echo',
                                f"'{echo_args}'"]

    @sanity_function
    def assert_found_all(self):
        return sn.all(
            sn.map(lambda x: sn.assert_found('='.join(x), self.stdout),
                   list(self.var_ref.items()))
        )
