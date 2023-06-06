# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))

from cuda_visible_devices_all import CudaVisibleDevicesAllMixin
from extra_launcher_options import ExtraLauncherOptionsMixin


@rfm.simple_test
class CUDAFortranCheck(CudaVisibleDevicesAllMixin, ExtraLauncherOptionsMixin,
                       rfm.RegressionTest):
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['+cuda-fortran']
    sourcepath = 'vecAdd_cuda.cuf'
    build_system = 'SingleSource'
    tags = {'production', 'craype'}

    @sanity_function
    def assert_correct_result(self):
        result = sn.extractsingle(r'final result:\s+(?P<result>\d+\.?\d*)',
                                  self.stdout, 'result', float)
        return sn.assert_reference(result, 1., -1e-5, 1e-5)
