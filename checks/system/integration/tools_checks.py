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
    executable = 'which'
    executable_opts = ['zypper']

    @sanity_function
    def assert_tool_available(self):
        return sn.assert_eq(self.job.exitcode, 0)


@rfm.simple_test
class ToolVimAvailable(rfm.RunOnlyRegressionTest):
    descr = 'Tools check - verify vim text editor is available'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-TOOLS'}
    executable = 'which'
    executable_opts = ['vim']

    @sanity_function
    def assert_tool_available(self):
        return sn.assert_eq(self.job.exitcode, 0)


@rfm.simple_test
class ToolGccAvailable(rfm.RunOnlyRegressionTest):
    descr = 'Tools check - verify GCC compiler is available'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-TOOLS'}
    executable = 'which'
    executable_opts = ['gcc']

    @sanity_function
    def assert_tool_available(self):
        return sn.assert_eq(self.job.exitcode, 0)


@rfm.simple_test
class ToolGcc12Available(rfm.RunOnlyRegressionTest):
    descr = 'Tools check - verify GCC version 12 is available'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-TOOLS'}
    executable = 'which'
    executable_opts = ['gcc-12']

    @sanity_function
    def assert_tool_available(self):
        return sn.assert_eq(self.job.exitcode, 0)


@rfm.simple_test
class ToolJqAvailable(rfm.RunOnlyRegressionTest):
    descr = 'Tools check - verify jq JSON query tool is available'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-TOOLS'}
    executable = 'which'
    executable_opts = ['jq']

    @sanity_function
    def assert_tool_available(self):
        return sn.assert_eq(self.job.exitcode, 0)


@rfm.simple_test
class ToolEmacsAvailable(rfm.RunOnlyRegressionTest):
    descr = 'Tools check - verify emacs is available'
    valid_systems = ['eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-TOOLS'}
    executable = 'which'
    executable_opts = ['emacs']

    @sanity_function
    def assert_tool_available(self):
        return sn.assert_eq(self.job.exitcode, 0)
    