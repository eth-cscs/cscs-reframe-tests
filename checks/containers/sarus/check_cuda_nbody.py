# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class SarusCudaNBodyCheck(rfm.RunOnlyRegressionTest):
    valid_systems = ['+sarus +nvgpu']
    valid_prog_environs = ['builtin']
    sourcesdir = None
    container_platform = 'Sarus'
    num_tasks = 1
    num_tasks_per_node = 1
    reference = {
        '*': {
            'gflops': (2860., -0.10, None, 'Gflop/s')
        },
        'hohgant:nvgpu': {
            'gflops': (30900., -0.15, None, 'Gflop/s')
        }
    }

    image = variable(
        str, value='nvcr.io/nvidia/k8s/cuda-sample:nbody-cuda11.7.1'
    )

    num_bodies_per_gpu = variable(int, value=200000)

    @run_after('setup')
    def set_cuda_visible_devices(self):
        curr_part = self.current_partition
        self.gpu_count = curr_part.select_devices('gpu')[0].num_devices
        cuda_visible_devices = ','.join(f'{i}' for i in range(self.gpu_count))
        self.env_vars['CUDA_VISIBLE_DEVICES'] = cuda_visible_devices

    @run_after('setup')
    def setup_executable(self):
        nbody_exec = '/cuda-samples/nbody'
        self.container_platform.image = self.image
        self.prerun_cmds = ['sarus --version', 'unset XDG_RUNTIME_DIR']
        self.container_platform.command = (
            f'{nbody_exec} -benchmark -fp64 '
            f'-numbodies={self.num_bodies_per_gpu * self.gpu_count} '
            f'-numdevices={self.gpu_count}'
        )

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
