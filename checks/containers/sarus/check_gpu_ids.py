# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))

from cuda_visible_devices_all import CudaVisibleDevicesAllMixin  # noqa: E402


@rfm.simple_test
class SarusNvidiaSmiCheck(CudaVisibleDevicesAllMixin,
                          rfm.RunOnlyRegressionTest):
    valid_systems = ['+nvgpu +sarus']
    valid_prog_environs = ['builtin']
    num_tasks = 1
    num_tasks_per_node = 1
    container_platform = 'Sarus'

    # https://catalog.ngc.nvidia.com/orgs/nvidia/teams/k8s/containers/cuda-sample/tags  # noqa: E501
    image = 'nvidia/cuda:11.8.0-base-ubuntu18.04'

    @run_after('setup')
    def setup_sarus(self):
        self.container_platform.image = self.image
        self.prerun_cmds = ['sarus --version', 'nvidia-smi -L > native.out']
        self.env_vars['XDG_RUNTIME_DIR'] = ''
        self.container_platform.command = 'nvidia-smi -L > sarus.out'

    @sanity_function
    def assert_same_output(self):
        native_output = sn.extractall('GPU.*', 'native.out')
        sarus_output = sn.extractall('GPU.*', 'sarus.out')
        return sn.all([
            sn.assert_eq(native_output, sarus_output),
            sn.assert_eq(sn.len(native_output), self.num_gpus_per_node)
        ])
