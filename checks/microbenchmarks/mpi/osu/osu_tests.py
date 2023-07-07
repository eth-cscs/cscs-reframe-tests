# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import contextlib
import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(
    str(pathlib.Path(__file__).parent.parent.parent.parent / 'mixins')
)

from extra_launcher_options import ExtraLauncherOptionsMixin
from hpctestlib.microbenchmarks.mpi.osu import (build_osu_benchmarks,
                                                osu_build_run)


class cscs_build_osu_benchmarks(build_osu_benchmarks):
    build_type = parameter(['cpu', 'cuda'])

    @run_after('setup')
    def setup_compilers(self):
        if self.build_type == 'cuda':
            curr_part = self.current_partition
            gpu_arch = curr_part.select_devices('gpu')[0].arch
            self.build_system.ldflags = [
                '${CRAY_CUDATOOLKIT_POST_LINK_OPTS}',
                '-L${CRAY_MPICH_ROOTDIR}/gtl/lib -lmpi_gtl_cuda'
            ]

            # Remove the '^sm_' prefix from the arch, e.g sm_80 -> 80
            if gpu_arch.startswith('sm_'):
                accel_compute_capability = gpu_arch[len('sm_'):]
            else:
                accel_compute_capability = '80'

            if self.current_environ.name in {'PrgEnv-cray', 'PrgEnv-gnu'}:
                self.modules = [
                    'cudatoolkit',
                    f'craype-accel-nvidia{accel_compute_capability}'
                ]


class cscs_osu_benchmarks(osu_build_run, ExtraLauncherOptionsMixin):
    osu_binaries = fixture(cscs_build_osu_benchmarks, scope='environment')
    num_iters = 100

    @run_after('init')
    def set_valid_systems_envs(self):
        build_type = self.osu_binaries.build_type
        if build_type == 'cuda':
            self.valid_systems = ['+remote +nvgpu']
            self.valid_prog_environs = ['+mpi +cuda']
        else:
            self.valid_systems = ['+remote']
            self.valid_prog_environs = ['+mpi']

    @run_before('run')
    def set_environment(self):
        build_type = self.osu_binaries.build_type
        if build_type == 'cuda':
            self.env_vars = {
                # Enable GPU support for cray-mpich
                'MPICH_GPU_SUPPORT_ENABLED': 1,

                # Use only the first CUDA GPU
                'CUDA_VISIBLE_DEVICES': 0,
            }

    exclusive_access = True
    tags = {'cpe'}


@rfm.simple_test
class cscs_osu_pt2pt_check(cscs_osu_benchmarks):
    benchmark_info = parameter([
        ('mpi.pt2pt.osu_bw', 'bandwidth'),
        ('mpi.pt2pt.osu_latency', 'latency')
    ], fmt=lambda x: x[0], loggable=True)
    allref = {
        'mpi.pt2pt.osu_bw': {
            'cpu': {
                '*': {
                    'bandwidth': (24000.0, -0.10, None, 'MB/s')
                }
            },
            'cuda': {
                '*': {
                    'bandwidth': (24000.0, -0.10, None, 'MB/s')
                }
            }
        },
        'mpi.pt2pt.osu_latency': {
            'cpu': {
                '*': {
                    'latency': (2.0, None, 0.15, 'us')
                }
            },
            'cuda': {
                '*': {
                    'latency': (10.0, None, 0.15, 'us')
                }
            }
        }
    }

    @run_after('init')
    def setup_per_build_type(self):
        build_type = self.osu_binaries.build_type
        if build_type == 'cuda':
            self.device_buffers = 'cuda'
            self.num_gpus_per_node = 1
            self.env_vars = {'MPICH_RDMA_ENABLED_CUDA': 1}

        with contextlib.suppress(KeyError):
            self.reference = self.allref[self.benchmark_info[0]][build_type]


@rfm.simple_test
class cscs_osu_collective_check(cscs_osu_benchmarks):
    benchmark_info = parameter([
        ('mpi.collective.osu_alltoall', 'latency'),
        ('mpi.collective.osu_allreduce', 'latency'),
    ], fmt=lambda x: x[0], loggable=True)

    num_nodes = parameter([6])
    osu_binaries = fixture(cscs_build_osu_benchmarks, scope='environment')

    allref = {
        'mpi.collective.osu_allreduce': {
            6: {
                '*': {
                    'latency': (8.45, None, 0.10, 'us')
                },
            },
        },
        'mpi.collective.osu_alltoall': {
            6: {
                '*': {
                    'latency': (14.50, None, 0.10, 'us')
                },
            },
        }
    }

    @run_after('init')
    def setup_by_scale(self):
        self.num_tasks = self.num_nodes
        with contextlib.suppress(KeyError):
            self.reference = self.allref[self.num_nodes]
