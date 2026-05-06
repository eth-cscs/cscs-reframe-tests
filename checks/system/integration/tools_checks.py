# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class ToolZypperAvailable(rfm.RunOnlyRegressionTest):
    descr = 'Tools check - verify zypper package manager is available'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-TOOLS'}
    executable = 'bash'
    executable_opts = ['-c', 'which zypper || echo FAILED']

    @sanity_function
    def assert_tool_available(self):
        return sn.assert_not_found(r'FAILED', self.stdout)


@rfm.simple_test
class ToolVimAvailable(rfm.RunOnlyRegressionTest):
    descr = 'Tools check - verify vim text editor is available'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-TOOLS'}
    executable = 'bash'
    executable_opts = ['-c', 'which vim || echo FAILED']

    @sanity_function
    def assert_tool_available(self):
        return sn.assert_not_found(r'FAILED', self.stdout)


@rfm.simple_test
class ToolGccAvailable(rfm.RunOnlyRegressionTest):
    descr = 'Tools check - verify GCC compiler is available'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-TOOLS'}
    executable = 'bash'
    executable_opts = ['-c', 'which gcc || echo FAILED']

    @sanity_function
    def assert_tool_available(self):
        return sn.assert_not_found(r'FAILED', self.stdout)


@rfm.simple_test
class ToolGcc12Available(rfm.RunOnlyRegressionTest):
    descr = 'Tools check - verify GCC version 12 is available'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-TOOLS'}
    executable = 'bash'
    executable_opts = ['-c', 'which gcc-12 || echo FAILED']

    @sanity_function
    def assert_tool_available(self):
        return sn.assert_not_found(r'FAILED', self.stdout)


@rfm.simple_test
class ToolJqAvailable(rfm.RunOnlyRegressionTest):
    descr = 'Tools check - verify jq JSON query tool is available'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-TOOLS'}
    executable = 'bash'
    executable_opts = ['-c', 'which jq || echo FAILED']

    @sanity_function
    def assert_tool_available(self):
        return sn.assert_not_found(r'FAILED', self.stdout)

@rfm.simple_test
class ToolEmacsAvailable(rfm.RunOnlyRegressionTest):
    descr = 'Tools check - verify emacs is available on Eiger'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-TOOLS'}
    executable = 'bash'
    executable_opts = ['-c', 'which emacs || echo FAILED']

    @sanity_function
    def assert_tool_available(self):
        return sn.assert_not_found(r'FAILED', self.stdout)
    
@rfm.simple_test
class ToolEmacsAvailable(rfm.RunOnlyRegressionTest):
    descr = 'Tools check - verify emacs is available on Eiger'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-TOOLS'}
    executable = 'bash'
    executable_opts = ['-c', 'which emacs || echo FAILED']

    @sanity_function
    def assert_tool_available(self):
        return sn.assert_not_found(r'FAILED', self.stdout)
