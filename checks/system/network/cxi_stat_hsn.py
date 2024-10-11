# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class CXIStatHSN(rfm.RunOnlyRegressionTest):
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['builtin']
    cxi_device_count = 4
    sourcesdir = None
    num_tasks_per_node = 1
    executable = 'cxi_stat'

    @sanity_function
    def assert_hsn_count(self):
        expected_devices = {f'hsn{i}' for i in range(self.cxi_device_count)}
        network_devices = sn.extractall(
            rf'Network device:\s*(?P<name>\S+)', self.stdout, 'name'
        )
        return sn.assert_eq(expected_devices, set(network_devices))
