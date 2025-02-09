# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class BoostPythonBindingsTest(rfm.RegressionTest):
    descr = 'Test for Boost with Python bindings'
    valid_systems = ['eiger:mc', 'pilatus:mc']
    valid_prog_environs = ['cpeGNU']
    modules = [f'Boost']
    executable = 'python3 hello.py'
    version_cmd = ('python3 -c \'import sys; '
                   'ver=sys.version_info; '
                   'print(f"{ver.major}{ver.minor}")\'')
    env_vars = {
        'PYTHON_INCLUDE': '$(python3-config --includes)',
        'PYTHON_BOOST_LIB': f'boost_python$({version_cmd})'
    }
    maintainers = ['TM', 'AJ']
    tags = {'scs', 'production'}

    @sanity_function
    def assert_success(self):
        return sn.assert_found('hello, world', self.stdout)

