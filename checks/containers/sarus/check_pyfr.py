# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class SarusPyFRCheck(rfm.RunOnlyRegressionTest):
    backend = parameter(['cuda', 'openmp'])
    sourcesdir = None
    valid_prog_environs = ['builtin']
    container_platform = 'Sarus'
    num_tasks = 1
    num_tasks_per_node = 1

    @run_after('init')
    def set_valid_systems(self):
        if self.backend == 'cuda':
            self.valid_systems = ['+sarus +nvgpu']
        else:
            self.valid_systems = ['+sarus']

    @run_after('setup')
    def set_cuda_visible_devices(self):
        if self.backend == 'cuda':
            curr_part = self.current_partition
            gpu_count = curr_part.select_devices('gpu')[0].num_devices
            cuda_visible_devices = ','.join(f'{i}' for i in range(gpu_count))
            self.env_vars['CUDA_VISIBLE_DEVICES'] = cuda_visible_devices
            self.num_gpus_per_node = gpu_count

    @run_after('setup')
    def setup_container_platform(self):
        image_tag = '1.15.0-cpu-mpich4.1-ubuntu22.04'
        if self.backend == 'cuda':
            image_tag = '1.14.0-cuda11.7-mpich3.1.4-ubuntu22.04'

        self.container_platform.image = f'ethcscs/pyfr:{image_tag}'

        self.prerun_cmds = [
             r'sarus --version',
             r'wget -q https://raw.githubusercontent.com/PyFR/PyFR-Test-Cases/'
             r'main/2d-euler-vortex/euler-vortex.ini',
             r'wget -q https://raw.githubusercontent.com/PyFR/PyFR-Test-Cases/'
             r'main/2d-euler-vortex/euler-vortex.msh',
        ]
        import_mesh_command = ('pyfr import ./euler-vortex.msh '
                               './euler-vortex.pyfrm')
        compute_command = (f'pyfr run --backend {self.backend} '
                           f'./euler-vortex.pyfrm ./euler-vortex.ini')
        self.container_platform.command = (
            f'bash -c "{import_mesh_command} && {compute_command} && '
            f'echo CHECK SUCCESSFUL"'
        )

    @sanity_function
    def assert_sanity(self):
        return sn.assert_found(r'CHECK SUCCESSFUL', self.stdout)
