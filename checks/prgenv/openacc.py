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
from extra_launcher_options import ExtraLauncherOptionsMixin


class OpenACCFortranBase(rfm.RegressionTest, CudaVisibleDevicesAllMixin,
                         ExtraLauncherOptionsMixin):
    sourcesdir = 'src/openacc'
    build_system = 'SingleSource'
    num_tasks = 1
    num_tasks_per_node = 1
    build_locally = False
    num_tasks = 2
    sourcepath = 'vecAdd_openacc.F90'

    @run_before('compile')
    def set_compiler_flags(self):
        self.build_system.fflags += ['-D_MPI']

    @run_before('run')
    def set_debug(self):
        self.env_vars['NVCOMPILER_ACC_NOTIFY'] = '1'
        self.env_vars['CRAY_ACC_DEBUG'] = '1'

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


@rfm.simple_test
class CPE_OpenACCFortranCheck(OpenACCFortranBase):
    valid_systems = ['+nvgpu +remote']
    valid_prog_environs = ['+openacc +mpi -uenv']
    tags = {'production', 'craype'}

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


@rfm.simple_test
class UENV_OpenACCFortranCheck(OpenACCFortranBase):
    valid_systems = ['+nvgpu +remote']
    valid_prog_environs = ['+openacc +mpi +uenv']
    tags = {'production', 'uenv'}

    @run_after('setup')
    def set_compilers(self):
        # Remove sm_ prefix from gpu arch
        gpu_arch = self.current_partition.select_devices('gpu')[0].arch[3:]

        # Options only for the Nvidia Fortran compiler
        self.build_system.fflags += ['-acc', f'-gpu=cc{gpu_arch}']
