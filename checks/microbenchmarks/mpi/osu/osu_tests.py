# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import contextlib
import reframe as rfm

from hpctestlib.microbenchmarks.mpi.osu import (build_osu_benchmarks,
                                                osu_build_run)


class cscs_build_osu_benchmarks(build_osu_benchmarks):
    build_type = parameter(['cpu', 'cuda'])

    @run_after('init')
    def setup_modules(self):
        if self.build_type != 'cuda':
            return

        if self.current_system.name in ('daint', 'dom'):
            self.modules = ['cudatoolkit/21.3_11.2']
        elif self.current_system.name in ('arolla', 'tsa'):
            self.modules = ['cuda/10.1.243']
            self.build_system.ldflags = ['-L$EBROOTCUDA/lib64',
                                         '-lcudart', '-lcuda']


class cscs_osu_benchmarks(osu_build_run):
    exclusive_access = True
    tags = {'production', 'benchmark', 'craype'}
    maintainers = ['@rsarm']


@rfm.simple_test
class cscs_osu_pt2pt_check(cscs_osu_benchmarks):
    valid_systems = ['daint:gpu', 'daint:mc', 'dom:gpu', 'dom:mc',
                     'eiger:mc', 'pilatus:mc', 'arolla:cn', 'tsa:cn']
    valid_prog_environs = ['PrgEnv-gnu']
    benchmark_info = parameter([
        ('mpi.pt2pt.osu_bw', 'bandwidth'),
        ('mpi.pt2pt.osu_latency', 'latency')
    ], fmt=lambda x: x[0], loggable=True)
    osu_binaries = fixture(cscs_build_osu_benchmarks, scope='environment')
    allref = {
        'mpi.pt2pt.osu_bw': {
            'cpu': {
                'daint:gpu': {
                    'bandwidth': (9153.637, -0.10, None, 'MB/s')
                },
                'daint:mc': {
                    'bandwidth': (7650.943, -0.10, None, 'MB/s')
                },
                'dom:gpu': {
                    'bandwidth': (9140.621, -0.10, None, 'MB/s')
                },
                'dom:mc': {
                    'bandwidth': (8632.197, -0.10, None, 'MB/s')
                },
                'eiger:mc': {
                    'bandwidth': (12240.41, -0.10, None, 'MB/s')
                },
                'pilatus:mc': {
                    'bandwidth': (12240.476, -0.10, None, 'MB/s')
                }
            },
            'cuda': {
                'daint:gpu': {
                    'bandwidth': (8431.02, -0.10, None, 'MB/s')
                },
                'dom:gpu': {
                    'bandwidth': (8637.693, -0.10, None, 'MB/s')
                }
            }
        },
        'mpi.pt2pt.osu_latency': {
            'cpu': {
                'daint:gpu': {
                    'latency': (1.651, None, 0.10, 'us')
                },
                'daint:mc': {
                    'latency': (2.175, None, 0.10, 'us')
                },
                'dom:gpu': {
                    'latency': (1.314, None, 0.10, 'us')
                },
                'dom:mc': {
                    'latency': (1.439, None, 0.10, 'us')
                },
                'eiger:mc': {
                    'latency': (2.76, None, 0.15, 'us')
                },
                'pilatus:mc': {
                    'latency': (2.413, None, 0.15, 'us')
                }
            },
            'cuda': {
                'daint:gpu': {
                    'latency': (8.907, None, 0.10, 'us')
                },
                'dom:gpu': {
                    'latency': (6.043, None, 0.10, 'us')
                },
            }
        }
    }

    @run_after('init')
    def setup_per_build_type(self):
        build_type = self.osu_binaries.build_type
        if build_type == 'cuda':
            self.device_buffers = 'cuda'
            self.num_gpus_per_node = 1
            self.valid_systems = ['daint:gpu',
                                  'dom:gpu', 'arolla:cn', 'tsa:cn']
            if self.current_system.name in ('daint', 'dom'):
                self.valid_prog_environs = ['PrgEnv-nvidia']
                self.variables = {'MPICH_RDMA_ENABLED_CUDA': '1'}

        if self.current_system.name in {'arolla', 'tsa'}:
            num_iters = 100

        with contextlib.suppress(KeyError):
            self.reference = self.allref[self.benchmark_info[0]][build_type]


@rfm.simple_test
class cscs_osu_collective_check(cscs_osu_benchmarks):
    benchmark_info = parameter([
        ('mpi.collective.osu_alltoall', 'latency'),
        ('mpi.collective.osu_allreduce', 'latency'),
    ], fmt=lambda x: x[0], loggable=True)
    num_nodes = parameter([6, 16])
    extra_resources = {
        'switches': {
            'num_switches': 1
        }
    }
    valid_systems = ['daint:gpu', 'daint:mc']
    valid_prog_environs = ['PrgEnv-gnu']
    osu_binaries = fixture(cscs_build_osu_benchmarks, scope='environment')
    allref = {
        'mpi.collective.osu_allreduce': {
            6: {
                'dom:gpu': {
                    'latency': (6.26, None, 0.10, 'us')
                },
                'dom:mc': {
                    'latency': (7.235, None, 0.10, 'us')
                },
                'daint:gpu': {
                    'latency': (18.012, None, 0.10, 'us')
                },
                'daint:mc': {
                    'latency': (18.016, None, 0.10, 'us')
                }
            },
            16: {
                'daint:gpu': {
                    'latency': (28.925, None, 0.10, 'us')
                },
                'daint:mc': {
                    'latency': (39.147, None, 0.10, 'us')
                }
            }
        },
        'mpi.collective.osu_alltoall': {
            6: {
                'dom:gpu': {
                    'latency': (8.23, None, 0.10, 'us')
                },
                'daint:gpu': {
                    'latency': (20.73, None, 0.10, 'us')
                },
                'dom:mc': {
                    'latency': (0, None, None, 'us')
                },
                'daint:mc': {
                    'latency': (0, None, None, 'us')
                }
            },
            16: {
                'daint:gpu': {
                    'latency': (0, None, None, 'us')
                },
                'daint:mc': {
                    'latency': (0, None, None, 'us')
                }
            }
        }
    }

    @run_after('init')
    def setup_by_scale(self):
        if self.osu_binaries.build_type == 'cuda':
            # Filter out CUDA-aware versions
            self.valid_systems = []
            return

        self.num_tasks = self.num_nodes
        if self.num_nodes == 6:
            self.valid_systems += ['dom:gpu', 'dom:mc']

        with contextlib.suppress(KeyError):
            self.reference = self.allref[self.num_nodes]
