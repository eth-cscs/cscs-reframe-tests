# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


class openmp_offload_base(rfm.RegressionTest):
    descr = 'Simple openmp offload GPU test'
    valid_systems = ['+nvgpu']
    build_system = 'SingleSource'
    sourcesdir = 'src/openmp'
    sourcepath = 'offload.F90'
    executable = './offload.exe'
    time_limit = '2m'
    num_tasks = 1
    num_tasks_per_node = 1
    build_locally = False
    env_vars = {'OMP_TARGET_OFFLOAD': 'MANDATORY'}
    tags = {'uenv'}
    maintainers = ['SSA', 'VCUE']

    @sanity_function
    def validate(self):
        """
         ndev=           4 gpu= T
        """
        isgpu = sn.assert_found(r' ndev=\s+\d gpu=\s+T', self.stdout)
        _ngpu = sn.extractsingle(r' ndev=\s+(?P<ngpu>\d)', self.stdout,
                                 'ngpu', int)
        ngpu = sn.assert_eq(
            _ngpu,
            self.current_partition.select_devices('gpu')[0].num_devices)

        return sn.all([isgpu, ngpu])


@rfm.simple_test
class openmp_offload_gfortran_test(openmp_offload_base):
    valid_prog_environs = ['+openmp +offload_gnu']

    @run_before('compile')
    def set_fflags(self):
        self.build_system.ftn = 'gfortran'
        self.build_system.fflags = ['-fopenmp', '-foffload=nvptx-none']


@rfm.simple_test
class openmp_offload_nvfortran_test(openmp_offload_base):
    valid_prog_environs = ['+openmp +offload_nvhpc']

    @run_before('compile')
    def set_fflags(self):
        gpu_arch = self.current_partition.select_devices('gpu')[0].arch[3:]
        self.build_system.ftn = 'nvfortran'
        self.build_system.fflags = ['-mp=gpu', f'-gpu=cc{gpu_arch}']
