# Copyright Swiss National Supercomputing Centre
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


# --------------------------------------------------
# PING TESTS (exit code based)
# --------------------------------------------------

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class PingCheck(rfm.RunOnlyRegressionTest):
    descr = 'Network connectivity check (ping)'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-net'}


    target = parameter([
        ('localhost', '127.0.0.1'),
        ('external-ip', '8.8.8.8'),
        ('external-dns', 'www.google.com'),
        ('ldap', 'ldap.cscs.ch')
    ])

    executable = 'ping'

    def __init__(self):
        self.executable_opts = ['-n', '-q', '-c', '5', self.target[1]]

    @sanity_function
    def validate(self):
        return sn.assert_eq(self.job.exitcode, 0)


# --------------------------------------------------
# HTTP / PROXY TEST
# --------------------------------------------------

@rfm.simple_test
class ProxyHttpAccess(rfm.RunOnlyRegressionTest):
    descr = 'HTTP connectivity check'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-PROXY'}

    executable = 'curl'
    executable_opts = ['-sSf', 'http://www.google.com', '-o', '/dev/null']

    @sanity_function
    def assert_http_access(self):
        return sn.assert_eq(
            self.job.exitcode, 0,
            msg='[ERROR] HTTP access failed (curl)'
        )


# --------------------------------------------------
# DNS TESTS
# --------------------------------------------------

@rfm.simple_test
class DNSCheck(rfm.RunOnlyRegressionTest):
    descr = 'DNS resolution checks (parameterized)'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-DNS'}

    case = parameter([
        ('invalid', 'Xgit.cscs.ch', False),
        ('internal', 'git.cscs.ch', True),
        ('external', 'www.google.com', True),
    ])

    executable = 'nslookup'

    def __init__(self):
        self.executable_opts = [self.case[1]]

    @sanity_function
    def assert_dns(self):
        name, host, should_resolve = self.case

        if should_resolve:
            return sn.assert_eq(
                self.job.exitcode, 0,
                msg=f"[ERROR] DNS resolution FAILED for {name} host: {host}"
            )
        else:
            return sn.assert_ne(
                self.job.exitcode, 0,
                msg=f"[ERROR] Invalid hostname unexpectedly resolved: {host}"
            )


# --------------------------------------------------
# NETWORK INTERFACE TESTS
# --------------------------------------------------

@rfm.simple_test
class NetworkInterfaceCheck(rfm.RunOnlyRegressionTest):
    descr = 'Network interface validation (state + IP)'
    valid_systems = ['daint', 'eiger']
    valid_prog_environs = ['builtin']
    tags = {'production', 'sysint-NETIFACE'}

    iface = parameter([
        ('nmn0', r'10\.100\..*/22'),
        ('hsn0', r'172\.28\..*/16'),
        ('hsn1', r'172\.28\..*/16'),
        ('hsn2', r'172\.28\..*/16'),
        ('hsn3', r'172\.28\..*/16'),
    ])

    executable = 'ip'

    def __init__(self):
        self.executable_opts = ['address', 'show', self.iface[0]]

    @sanity_function
    def validate_interface(self):
        iface, ip_pattern = self.iface

        return sn.all([
            sn.assert_found(
                rf'{iface}.*state UP',
                self.stdout,
                msg=f"[ERROR] Interface {iface} is not UP"
            ),
            sn.assert_found(
                rf'inet {ip_pattern}',
                self.stdout,
                msg=f"[ERROR] Interface {iface} has incorrect IP range"
            )
        ])
