# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class NvmlTest(rfm.RegressionTest):
    descr = 'Checks that nvml can report GPU informations'
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['+cuda']
    build_system = 'SingleSource'
    sourcesdir = None
    sourcepath = '$CUDA_HOME/nvml/example/example.c'
    build_locally = False
    tags = {'production', 'craype', 'external-resources', 'health'}

    @run_before('compile')
    def set_build_flags(self):
        self.prebuild_cmds = [f'echo "# {self.sourcepath}"']
        self.build_system.cflags = ['-I $CUDA_HOME/include']
        self.build_system.ldflags = ['-L $CUDA_HOME/lib64 -lnvidia-ml']

    @sanity_function
    def set_sanity(self):
        """
        Listing devices:
        0. NVIDIA A100-SXM4-80GB [00000000:03:00.0]
        Changing device's compute mode from 'Exclusive Process' to 'Prohibited'
        Need root privileges to do that: Insufficient Permissions # <-- OK
        """
        cp = self.current_partition
        self.gpu_count = cp.select_devices('gpu')[0].num_devices
        regex_devices = rf'Found {self.gpu_count} devices'
        regex_pciinfo = r'\d+. NVIDIA.*\[\S+\]'
        regex_mode = 'Need root privileges to do that: Insufficient Permission'
        return sn.all([
            sn.assert_found(regex_devices, self.stdout),
            sn.assert_found(regex_pciinfo, self.stdout),
            sn.assert_found(regex_mode, self.stdout),
        ])
