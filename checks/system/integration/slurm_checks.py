# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class SlurmConfigExists(rfm.RunOnlyRegressionTest):
    descr = 'Slurm check - verify slurm.conf configuration file exists'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-SLURM'} 
    executable = 'test'
    executable_opts = ['-f', '/run/slurm/conf/slurm.conf']

    @sanity_function
    def assert_config_exists(self):
        return sn.assert_eq(self.job.exitcode, 0)


@rfm.simple_test
class SlurmInfoAvailable(rfm.RunOnlyRegressionTest):
    descr = 'Slurm check - verify sinfo command is available'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-SLURM'}
    executable = 'which'
    executable_opts = ['sinfo']

    @sanity_function
    def assert_command_available(self):
        return sn.assert_eq(self.job.exitcode, 0)


@rfm.simple_test
class MungeDaemonRunning(rfm.RunOnlyRegressionTest):
    descr = 'Slurm check - verify munge daemon is running'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-SLURM'}
    executable = 'ps'
    executable_opts = ['aux']

    @sanity_function
    def assert_munge_running(self):
        return sn.assert_found(r'/usr/sbin/munged', self.stdout)


@rfm.simple_test
class SlurmctldResponsive(rfm.RunOnlyRegressionTest):
    descr = 'Slurm check - verify Slurmctld controller is running and responsive'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-SLURM'}
    executable = 'scontrol'
    executable_opts = ['ping']

    @sanity_function
    def assert_controller_up(self):
        return sn.assert_found(r'Slurmctld\(primary\) at .* is UP', self.stdout)
