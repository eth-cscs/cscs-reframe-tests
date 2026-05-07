# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn

# --------------------------------------------------
# MOUNT CHECKS FOR EACH CLUSTER
# --------------------------------------------------

@rfm.simple_test
class MountCheckBase(rfm.RunOnlyRegressionTest):
    descr = 'Filesystem mount validation'
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-MOUNTS'}

    mount = parameter([])
    executable = 'cat'
    executable_opts = ['/proc/mounts']

    @sanity_function
    def validate_mount(self):
        pattern, name = self.mount
        return sn.assert_found(
            pattern, self.stdout,
            msg=f"[ERROR] Mount '{name}' missing or incorrect"
        )

@rfm.simple_test
class DaintMountCheck(MountCheckBase):
    descr = 'Daint filesystem mount validation'
    valid_systems = ['daint']
    mount = parameter([
        (r'/capstor/scratch/cscs .* lustre', 'scratch'),
        (r'/capstor/store/cscs .* lustre', 'store'),
    ])

@rfm.simple_test
class EigerMountCheck(MountCheckBase):
    descr = 'Eiger filesystem mount validation'
    valid_systems = ['eiger']
    mount = parameter([
        (r'/capstor/scratch/cscs .* lustre', 'scratch'),
        (r'/capstor/store/cscs .* lustre', 'store'),
        (r'/users .* nfs', 'users'),
        (r'pe_opt_cray_pe .* /opt/cray/pe', 'cray-pe'),
        (r'pe_opt_AMD .* /opt/AMD', 'amd'),
        (r'pe_opt_intel .* /opt/intel', 'intel'),
    ])

# --------------------------------------------------
# ENV VAR EXISTS (replaces 4 separate tests)
# --------------------------------------------------

@rfm.simple_test
class EnvVarSet(rfm.RunOnlyRegressionTest):
    descr = 'Ensure required environment variables are set'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-MOUNTS'}

    var = parameter(['SCRATCH', 'PROJECT', 'STORE', 'HOME'])

    executable = 'printenv'

    def __init__(self):
        self.executable_opts = [self.var]

    @sanity_function
    def validate(self):
        return sn.assert_eq(
            self.job.exitcode, 0,
            msg=f"[ERROR] Environment variable {self.var} is not set"
        )


# --------------------------------------------------
# ENV VAR PATH CHECK 
# --------------------------------------------------

@rfm.simple_test
class EnvVarPathCheck(rfm.RunOnlyRegressionTest):
    descr = 'Validate environment variable path prefixes for' \
    ' SCRATCH, PROJECT, STORE, HOME'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-MOUNTS'}

    var = parameter([
        ('SCRATCH', r'^/capstor/scratch/cscs/'),
        ('PROJECT', r'^/capstor/store/cscs/'),
        ('STORE',   r'^/capstor/store/cscs/'),
        ('HOME',    r'^/users/')
    ])

    executable = 'printenv'

    def __init__(self):
        self.executable_opts = [self.var[0]]

    @sanity_function
    def validate(self):
        name, pattern = self.var

        return sn.assert_true(
            sn.findall(pattern, self.stdout),
        msg=f"[ERROR] {name} has incorrect value:\n{self.stdout}"
      )


# --------------------------------------------------
# TMP MUST NOT BE SET (robust)
# --------------------------------------------------

@rfm.simple_test
class EnvVarTmpNotSet(rfm.RunOnlyRegressionTest):
    descr = 'Ensure TMP is not set'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-MOUNTS'}

    executable = 'printenv'
    executable_opts = ['TMP']

    @sanity_function
    def validate(self):
        return sn.assert_ne(
            self.job.exitcode, 0,
            msg='[ERROR] TMP should NOT be set (but it is present)'
        )



# --------------------------------------------------
# EIGER-SPECIFIC ENV VAR
# --------------------------------------------------

@rfm.simple_test
class EnvVarApps(rfm.RunOnlyRegressionTest):
    descr = 'Check APPS variable exists'
    valid_systems = ['eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-MOUNTS'}

    executable = 'printenv'
    executable_opts = ['APPS']

    @sanity_function
    def validate(self):
        return sn.assert_eq(
            self.job.exitcode, 0,
            msg='[ERROR] APPS environment variable is not set'
        )
