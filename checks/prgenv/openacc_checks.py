# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class OpenACCFortranCheck(rfm.RegressionTest):
    variant = parameter(['mpi', 'nompi'])
    valid_systems = ['+nvgpu']
    sourcesdir = 'src/openacc'
    build_system = 'SingleSource'
    modules = ['cudatoolkit']
    num_gpus_per_node = 1
    num_tasks_per_node = 1
    tags = {'production', 'craype'}

    @run_after('init')
    def set_valid_prgenv(self):
        self.valid_prog_environs = ['+openacc']
        if self.variant == 'mpi':
            self.valid_prog_environs = ['+openacc +mpi']

    @run_after('init')
    def set_numtasks(self):
        if self.variant == 'nompi':
            self.num_tasks = 1
            self.sourcepath = 'vecAdd_openacc_nompi.f90'
        else:
            self.num_tasks = 2
            self.sourcepath = 'vecAdd_openacc_mpi.f90'

    @run_after('setup')
    def set_modules(self):
        curr_part = self.current_partition
        gpu_arch = curr_part.select_devices('gpu')[0].arch

        # Remove the '^sm_' prefix from the arch, e.g sm_80 -> 80
        if gpu_arch.startswith('sm_'): 
            accel_compute_capability = gpu_arch[len('sm_'):]
        else:
            accel_compute_capability = '80'

        self.modules += [f'craype-accel-nvidia{accel_compute_capability}']

    @run_before('run')
    def setup_mpi_gpu_support(self):
        if self.variant == 'mpi':
            self.env_vars['MPICH_GPU_SUPPORT_ENABLED'] = 1

    @run_before('run')
    def set_laucnher_options(self):
        self.job.launcher.options += [
            self.current_environ.extras.get('launcher_options', '')
        ]

    @run_before('run')
    def set_cuda_visible_devices(self):
        curr_part = self.current_partition
        self.gpu_count = curr_part.select_devices('gpu')[0].num_devices
        cuda_visible_devices = ','.join(f'{i}' for i in range(self.gpu_count))
        self.env_vars['CUDA_VISIBLE_DEVICES'] = cuda_visible_devices

    @sanity_function
    def assert_correct_result(self):
        result = sn.extractsingle(r'final result:\s+(?P<result>\d+\.?\d*)',
                                  self.stdout, 'result', float)
        return sn.assert_reference(result, 1., -1e-5, 1e-5)
