# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import contextlib
import os
import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(
    str(pathlib.Path(__file__).parent.parent.parent.parent / 'mixins')
)

from extra_launcher_options import ExtraLauncherOptionsMixin
from container_engine import ContainerEngineCPEMixin
from slurm_mpi_options import SlurmMpiOptionsMixin


class fetch_osu_benchmarks(rfm.RunOnlyRegressionTest):
    '''Fixture for fetching the OSU benchmarks.'''

    #: The version of the benchmarks to fetch.
    #:
    #: :type: :class:`str`
    #: :default: ``'7.2'``
    version = variable(str, value='7.2')

    local = True
    osu_file_name = f'osu-micro-benchmarks-{version}.tar.gz'
    executable = f'curl -LJO http://mvapich.cse.ohio-state.edu/download/mvapich/{osu_file_name}'  # noqa: E501

    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)


class build_osu_benchmarks(rfm.CompileOnlyRegressionTest,
                           ContainerEngineCPEMixin):
    '''Fixture for building the OSU benchmarks'''

    #: Build variant parameter.
    #:
    #: :type: :class:`str`
    #: :values: ``'cpu', 'cuda'``
    build_type = parameter(['cpu', 'cuda'])

    build_system = 'Autotools'
    build_prefix = variable(str)
    build_locally = False

    #: The fixture object that retrieves the benchmarks
    #:
    #: :type: :class:`fetch_osu_benchmarks`
    #: :scope: *session*
    osu_benchmarks = fixture(fetch_osu_benchmarks, scope='session')

    # FIXME: version of clang compiler with the default cudatoolkit
    @run_after('setup')
    def skip_incompatible_envs_cuda(self):
        if self.build_type == 'cuda':
            if self.current_environ.name in {'PrgEnv-cray'}:
                self.skip(
                    f'environ {self.current_environ.name!r} incompatible with'
                    f'default cudatoolkit')

    @run_after('setup')
    def setup_compilers(self):
        if self.build_type == 'cuda':
            curr_part = self.current_partition
            gpu_arch = curr_part.select_devices('gpu')[0].arch
            environ_name = self.current_environ.name

            if environ_name.startswith('PrgEnv-'):
                if 'containerized_cpe' in self.current_environ.features:
                    self.build_system.ldflags = [
                        '-L${CUDA_HOME}/lib64',
                        '-L${CRAY_MPICH_ROOTDIR}/gtl/lib -lmpi_gtl_cuda'
                    ]
                    self.build_system.cppflags = [
                        '-I${CUDA_HOME}/include',
                    ]
                elif environ_name != 'PrgEnv-nvhpc':
                    self.build_system.ldflags = [
                        '${CRAY_CUDATOOLKIT_POST_LINK_OPTS}',
                        '-L${CRAY_MPICH_ROOTDIR}/gtl/lib -lmpi_gtl_cuda'
                    ]
                else:
                    self.build_system.ldflags = [
                        '-L${CRAY_NVIDIA_PREFIX}/cuda/lib64',
                        '-L${CRAY_MPICH_ROOTDIR}/gtl/lib -lmpi_gtl_cuda'
                    ]

            else:
                self.build_system.ldflags = [
                    '-L${CUDA_HOME}/lib64',
                ]
                self.build_system.cppflags = [
                    '-I${CUDA_HOME}/include',
                ]

            # Remove the '^sm_' prefix from the arch, e.g sm_80 -> 80
            if gpu_arch.startswith('sm_'):
                accel_compute_capability = gpu_arch[len('sm_'):]

            if self.current_environ.name in {'PrgEnv-cray', 'PrgEnv-gnu'}:
                self.modules = [
                    'cudatoolkit',
                    f'craype-accel-nvidia{accel_compute_capability}'
                ]

    @run_before('compile')
    def prepare_build(self):
        tarball = f'osu-micro-benchmarks-{self.osu_benchmarks.version}.tar.gz'
        self.build_prefix = tarball[:-7]  # remove .tar.gz extension
        fullpath = os.path.join(self.osu_benchmarks.stagedir, tarball)

        self.prebuild_cmds += [
            f'cp {fullpath} {self.stagedir}',
            f'tar xzf {tarball}',
            f'cd {self.build_prefix}'
        ]
        if self.build_type != 'cpu':
            self.build_system.config_opts = [f'--enable-{self.build_type}']

        # Change to the c/mpi directory to avoid building the
        # non-mpi benchmarks
        self.build_system.make_opts = ['-C', 'c/mpi']
        self.build_system.max_concurrency = 8

    @sanity_function
    def validate_build(self):
        # If build fails, the test will fail before reaching this point.
        return True


class osu_benchmark(rfm.RunOnlyRegressionTest, ExtraLauncherOptionsMixin,
                    ContainerEngineCPEMixin):
    '''OSU benchmark test base class.'''

    #: Number of warmup iterations.
    #:
    #: This value is passed to the excutable through the -x option.
    #:
    #: :type: :class:`int`
    #: :default: ``10``
    num_warmup_iters = variable(int, value=10)

    #: Number of iterations.
    #:
    #: This value is passed to the excutable through the -i option.
    #:
    #: :type: :class:`int`
    #: :default: ``100``
    num_iters = variable(int, value=100)

    #: Maximum message size.
    #:
    #: Both the performance and the sanity checks will be done
    #: for this message size.
    #:
    #: This value is set to ``8`` for latency benchmarks and to ``4194304`` for
    #: bandwidth benchmarks.
    #:
    #: :type: :class:`int`
    message_size = variable(int)

    #: Device buffers.
    #:
    #: Use accelerator device buffers.
    #: Valid values are ``cpu``, ``cuda``, ``openacc`` or ``rocm``.
    #:
    #: :type: :class:`str`
    #: :default: ``'cpu'``
    device_buffers = variable(str, value='cpu')

    #: Number of tasks to use.
    #:
    #: This variable is required.
    #: It is set to ``2`` for point to point benchmarks, but it is undefined
    #: for collective benchmarks
    #:
    #: :required: Yes
    num_tasks = required
    num_tasks_per_node = 1

    #: Parameter indicating the available benchmark to execute.
    #:
    #: :type: 2-element tuple containing the benchmark name and whether latency
    #:   or bandwidth is to be measured.
    #:
    #: :values:
    #:   ``mpi.collective.blocking.osu_alltoall``,
    #:   ``mpi.collective.blocking.osu_allreduce``,
    #:   ``mpi.pt2pt.standard.osu_bw``,
    #:   ``mpi.pt2pt.standard.osu_latency``
    benchmark_info = parameter([
        ('mpi.collective.blocking.osu_alltoall', 'latency'),
        ('mpi.collective.blocking.osu_allreduce', 'latency'),
        ('mpi.pt2pt.standard.osu_bw', 'bandwidth'),
        ('mpi.pt2pt.standard.osu_latency', 'latency')
    ], fmt=lambda x: x[0], loggable=True)

    tags = {'craype'}

    @run_before('setup')
    def setup_per_benchmark(self):
        bench, bench_metric = self.benchmark_info
        if bench_metric == 'latency':
            self.message_size = 8
            unit = 'us'
        elif bench_metric == 'bandwidth':
            self.message_size = 4194304
            unit = 'MB/s'
        else:
            raise ValueError(f'unknown benchmark metric: {bench_metric}')

        self.executable = bench.split('.')[-1]
        self.executable_opts = ['-m', f'{self.message_size}',
                                '-x', f'{self.num_warmup_iters}',
                                '-i', f'{self.num_iters}', '-c']

        if self.device_buffers != 'cpu':
            self.executable_opts += ['-d', self.device_buffers]

        if bench.startswith('mpi.pt2pt'):
            self.executable_opts += ['D', 'D']
            self.num_tasks = 2

        self.perf_variables = {
            bench_metric: sn.make_performance_function(
                self._extract_metric, unit
            )
        }

    @sanity_function
    def validate_test(self):
        return sn.assert_found(rf'^{self.message_size}.*Pass', self.stdout)

    @deferrable
    def _extract_metric(self):
        return sn.extractsingle(rf'^{self.message_size}\s+(\S+)',
                                self.stdout, 1, float)


class osu_build_run(osu_benchmark, SlurmMpiOptionsMixin):
    '''OSU benchmark test (build and run)'''

    #: The fixture object that builds the OSU binaries
    #:
    #: :type: :class:`build_osu_benchmarks`
    #: :scope: *environment*
    osu_binaries = fixture(build_osu_benchmarks, scope='environment')

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
            curr_part = self.current_partition
            gpu_arch = curr_part.select_devices('gpu')[0].arch

            if gpu_arch.startswith('sm_'):
                accel_compute_capability = gpu_arch[len('sm_'):]

            if self.current_environ.name in {'PrgEnv-cray', 'PrgEnv-gnu'}:
                self.modules = [
                    'cudatoolkit',
                    f'craype-accel-nvidia{accel_compute_capability}'
                ]
        else:
            self.env_vars = {
                'MPICH_GPU_SUPPORT_ENABLED': 0
            }

    @run_before('run')
    def prepend_build_prefix(self):
        bench_path = self.benchmark_info[0].replace('.', '/')
        self.executable = os.path.join(
            self.osu_binaries.stagedir, self.osu_binaries.build_prefix,
            'c', bench_path)


@rfm.simple_test
class osu_pt2pt_check(osu_build_run):
    benchmark_info = parameter([
        ('mpi.pt2pt.standard.osu_bw', 'bandwidth'),
        ('mpi.pt2pt.standard.osu_latency', 'latency')
    ], fmt=lambda x: x[0], loggable=True)

    allref = {
        'mpi.pt2pt.standard.osu_bw': {
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
        'mpi.pt2pt.standard.osu_latency': {
            'cpu': {
                '*': {
                    'latency': (3.8, None, 0.15, 'us')
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
class osu_collective_check(osu_build_run):
    benchmark_info = parameter([
        ('mpi.collective.blocking.osu_alltoall', 'latency'),
        ('mpi.collective.blocking.osu_allreduce', 'latency'),
    ], fmt=lambda x: x[0], loggable=True)

    num_nodes = parameter([6])
    osu_binaries = fixture(build_osu_benchmarks, scope='environment')

    allref = {
        'mpi.collective.blocking.osu_allreduce': {
            6: {
                '*': {
                    'latency': (8.45, None, 0.10, 'us')
                },
            },
        },
        'mpi.collective.blocking.osu_alltoall': {
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
