# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class CXIGPULoopbackBW(rfm.RunOnlyRegressionTest):
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['builtin']
    cxi_device_count = 4
    sourcesdir = None
    num_tasks_per_node = 1
    executable = 'bash'
    executable_opts = [
        f"-c",
        f"'for (( j=0; j<{cxi_device_count}; j++ )); "
        f"do cxi_gpu_loopback_bw -d cxi$j; done'"
    ]
    reference = {
        '*': {
            'min_gpu_bw': (187.0, -0.02, None, 'Gb/s')
        }
    }

    @sanity_function
    def assert_cxi_count(self):
        cxi_count = sn.count(
            sn.extractall(rf'CXI Loopback Bandwidth Test', self.stdout))
        return sn.assert_eq(4, cxi_count)

    @performance_function('Gb/s')
    def min_gpu_bw(self):
        regex = r'^\s+\d+(\s+\d+)\s+(?P<bw>\S+)\s+\S+\s*'
        return sn.min(sn.extractall(regex, self.stdout, 'bw', float))
