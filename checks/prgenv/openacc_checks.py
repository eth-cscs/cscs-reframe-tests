# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class OpenACCFortranCheck(rfm.RegressionTest):
    variant = parameter(['mpi'])
    valid_systems = ['+nvgpu']
    sourcesdir = 'src/openacc'
    build_system = 'SingleSource'
    num_tasks = 1
    num_gpus_per_node = 1
    num_tasks_per_node = 1
    tags = {'production', 'craype'}

    @run_after('init')
    def set_valid_prgenv(self):
        self.valid_prog_environs = ['+openacc']
        if self.variant == 'mpi':
            self.valid_prog_environs = ['+openacc +mpi']

    @run_after('init')
    def set_mpi(self):
        self.sourcepath = 'vecAdd_openacc.F90'
        if self.variant == 'mpi':
            self.build_system.fflags = ['-D_MPI']
            self.num_tasks = 2

    @run_after('setup')
    def set_compilers(self):
        curr_part = self.current_partition
        gpu_arch = curr_part.select_devices('gpu')[0].arch

        # Remove the '^sm_' prefix from the arch, e.g sm_80 -> 80
        if gpu_arch.startswith('sm_'):
            accel_compute_capability = gpu_arch[len('sm_'):]
        else:
            accel_compute_capability = '80'

        if self.current_environ.name == 'PrgEnv-cray':
            self.modules = [
                'cudatoolkit',
                f'craype-accel-nvidia{accel_compute_capability}'
            ]
            self.build_system.fflags += ['-hacc', '-hnoomp']
        else:
            self.build_system.fflags += [
                '-acc', f'-gpu=cc{accel_compute_capability}'
            ]


    @run_before('run')
    def set_launcher_options(self):
        self.job.launcher.options += [
            self.current_environ.extras.get('launcher_options', '')
        ]

    @run_before('run')
    def set_cuda_visible_devices(self):
        curr_part = self.current_partition
        self.gpu_count = curr_part.select_devices('gpu')[0].num_devices
        cuda_visible_devices = ','.join(f'{i}' for i in range(self.gpu_count))
        self.env_vars['CUDA_VISIBLE_DEVICES'] = cuda_visible_devices

    @run_before('run')
    def set_debug(self):
        self.env_vars['NVCOMPILER_ACC_NOTIFY'] = '1'
        self.env_vars['CRAY_ACC_DEBUG'] = '1'

    @run_before('sanity')
    def set_sanity(self):
        regex_result = r'final result:\s+1'
        regex_version = r'_OPENACC:\s+(\d+)'
        regex_nv = r'num_gangs=\d+ num_workers=\d+ vector_length=\d+ grid='
        regex_cce = r'to acc 0 bytes, to host \d+ bytes'
        regex_kernel = f'({regex_nv}|{regex_cce})'
        self.sanity_patterns = sn.all([
            sn.assert_found(regex_result, self.stdout),
            sn.assert_found(regex_version, self.stdout),
            sn.assert_found(regex_kernel, self.stderr),
        ])
