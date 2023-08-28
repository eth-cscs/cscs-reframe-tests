# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent / 'mixins'))

from cuda_visible_devices_all import CudaVisibleDevicesAllMixin


@rfm.simple_test
class OpenACCFortranCheck(CudaVisibleDevicesAllMixin, rfm.RegressionTest):
    variant = parameter(['mpi'])
    valid_systems = ['+nvgpu']
    sourcesdir = 'src/openacc'
    build_system = 'SingleSource'
    num_tasks = 1
    num_tasks_per_node = 1
    build_locally = False

    @run_after('init')
    def set_valid_prgenv(self):
        self.valid_prog_environs = ['+openacc']
        if self.variant == 'mpi':
            self.valid_systems = ['+remote +nvgpu']
            self.valid_prog_environs = ['+openacc +mpi']

    @run_after('init')
    def set_mpi(self):
        self.sourcepath = 'vecAdd_openacc.F90'
        if self.variant == 'mpi':
            self.build_system.fflags = ['-D_MPI']
            self.num_tasks = 2

    @run_after('setup')
    def set_compilers(self):
        # Remove sm_ prefix from gpu arch
        gpu_arch = self.current_partition.select_devices('gpu')[0].arch[3:]

        # Options only for the Nvidia Fortran compiler
        self.build_system.fflags += ['-acc', f'-gpu=cc{gpu_arch}']

    @run_before('run')
    def set_debug(self):
        self.env_vars['NVCOMPILER_ACC_NOTIFY'] = '1'

    @run_before('run')
    def set_single_gpu_per_node(self):
        self.num_gpus_per_node = 1

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
