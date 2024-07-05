# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))

from container_engine import ContainerEngineMixin  # noqa: E402


@rfm.simple_test
class CudaNBodyCheckCE(rfm.RunOnlyRegressionTest, ContainerEngineMixin):
    valid_systems = ['+ce +nvgpu']
    valid_prog_environs = ['builtin']
    sourcesdir = None
    num_tasks = 1
    num_tasks_per_node = 1
    executable = 'nbody'
    container_image = 'jfrog.svc.cscs.ch#reframe-oci/cuda_samples:nbody-12.3'

    # Allow running with an older Cuda driver
    env_vars = {
        'NVIDIA_DISABLE_REQUIRE': 1
    }
    reference = {
        '*': {
            'gflops': (28000., -0.05, None, 'Gflop/s')
        }
    }

    num_bodies_per_gpu = variable(int, value=200000)
    tags = {'production', 'ce'}

    @run_after('setup')
    def set_num_gpus_per_node(self):
        curr_part = self.current_partition
        self.num_gpus_per_node = curr_part.select_devices('gpu')[0].num_devices

    @run_after('setup')
    def set_executable_opts(self):
        self.executable_opts = [
            f'-benchmark', f'-fp64',
            f'-numbodies={self.num_bodies_per_gpu * self.num_gpus_per_node}',
            f'-numdevices={self.num_gpus_per_node}'
        ]

    @sanity_function
    def assert_sanity(self):
        return sn.assert_found(r'.+double-precision GFLOP/s.+', self.stdout)

    @run_before('performance')
    def set_perf(self):
        self.perf_patterns = {
            'gflops': sn.extractsingle(
                r'= (?P<gflops>\S+)\sdouble-precision GFLOP/s.+',
                self.stdout, 'gflops', float)
        }
