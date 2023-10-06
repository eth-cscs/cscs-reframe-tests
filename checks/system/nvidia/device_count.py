# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))
from cuda_visible_devices_all import CudaVisibleDevicesAllMixin


class build_device_count(rfm.CompileOnlyRegressionTest):
    '''Fixture for building the device count binary'''
    valid_systems = ['*']
    valid_prog_environs = ['+cuda']
    build_system = 'SingleSource'
    sourcepath = 'deviceCount.cu'
    executable = 'deviceCount'
    num_tasks_per_node = 1

    @run_before('compile')
    def setup_compilers(self):
        self.build_system.ldflags = ['-lnvidia-ml']

    @sanity_function
    def validate_build(self):
        # If build fails, the test will fail before reaching this point.
        return True


@rfm.simple_test
class NVIDIA_device_count(CudaVisibleDevicesAllMixin,
                          rfm.RunOnlyRegressionTest):
    '''Checks that the number of NVIDIA gpu devices detected by NVML is the
       same with the one detected by CUDA.
       The test can easily run in multiple nodes by using the cli argument
       `-S 'NVIDIA_device_count.num_tasks=<num_nodes>'`.
       The above option can be combined with a particular nodelist to check
       the health of the nodes on demand.
    '''
    valid_systems = ['+remote +nvgpu']
    valid_prog_environs = ['+cuda']
    num_tasks_per_node = 1
    num_tasks = 1
    device_count_bin = fixture(build_device_count, scope='environment')

    @property
    @deferrable
    def num_tasks_assigned(self):
        return self.job.num_tasks

    @run_before('run')
    def set_executable(self):
        self.executable = os.path.join(
            self.device_count_bin.stagedir, self.device_count_bin.executable
        )

    @sanity_function
    def validate_passed(self):
        healthy_node_match = (
            rf'\S+: NVML device count == Cuda device count == '
            rf'{self.num_gpus_per_node}'
        )
        return sn.assert_eq(
            sn.count(sn.findall(healthy_node_match, self.stdout)),
            self.num_tasks_assigned
        )
