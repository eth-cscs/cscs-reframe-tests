# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class NvmlCheck(rfm.RegressionTest):
    descr = 'Checks that nvml can report GPU informations'
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['+cuda']
    build_system = 'SingleSource'
    sourcesdir = None
    tags = {'production', 'craype', 'external-resources', 'health'}

    @run_after('setup')
    def setup_modules(self):
        if 'PrgEnv-nvhpc' != self.current_environ.name:
            sm = self.current_partition.select_devices('gpu')[0].arch[-2:]
            self.modules = ['cudatoolkit', f'craype-accel-nvidia{sm}']
            self.sourcepath = '$CUDATOOLKIT_HOME/nvml/example/example.c'
        else:
            self.sourcepath = '$NVIDIA_PATH/cuda/bin/../nvml/example/example.c'

    @run_before('compile')
    def set_build_flags(self):
        self.prebuild_cmds = ['echo CUDATOOLKIT_HOME=$CUDATOOLKIT_HOME']
        self.build_system.cflags = ['-I $CUDATOOLKIT_HOME/include']
        self.build_system.ldflags = ['-L $CUDATOOLKIT_HOME/lib64 -lnvidia-ml']

    @run_before('sanity')
    def set_sanity_patterns(self):
        """
        Listing devices:
        0. NVIDIA A100-SXM4-80GB [00000000:03:00.0]
        Changing device's compute mode from 'Exclusive Process' to 'Prohibited'
        Need root privileges to do that: Insufficient Permissions # <-- OK
        """
        regex_devices = r'Found \d+ devices'
        regex_pciinfo = r'\d+. NVIDIA.*\[\S+\]'
        regex_mode = 'Need root privileges to do that: Insufficient Permission'
        self.sanity_patterns = sn.all([
            sn.assert_found(regex_devices, self.stdout),
            sn.assert_found(regex_pciinfo, self.stdout),
            sn.assert_found(regex_mode, self.stdout),
        ])
