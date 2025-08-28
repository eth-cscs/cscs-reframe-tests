# Copyright 2016-2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import pathlib
import sys
import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent / 'mixins'))
from container_engine import ContainerEngineCPEMixin  # noqa: E402


@rfm.simple_test
class MpiInitTest(rfm.RegressionTest, ContainerEngineCPEMixin):
    '''
    This test checks the value returned by calling MPI_Init_thread.
    '''
    required_threads = ['funneled', 'serialized', 'multiple']
    valid_prog_environs = ['+mpi +prgenv']
    valid_systems = ['+remote']
    build_system = 'Make'
    sourcesdir = 'src/mpi_thread'
    executable = 'mpi_init_thread_single.exe'
    time_limit = '2m'
    build_locally = False
    env_vars = {'MPICH_GPU_SUPPORT_ENABLED': 0}
    tags = {'production', 'craype', 'uenv'}

    @run_before('run')
    def set_job_parameters(self):
        # To avoid: "MPIR_pmi_init(83)....: PMI2_Job_GetId returned 14"
        self.job.launcher.options += (
            self.current_environ.extras.get('launcher_options', [])
        )

    @run_before('run')
    def pre_launch(self):
        cmd = self.job.launcher.run_command(self.job)
        self.prerun_cmds = [
            f'{cmd} mpi_init_thread_{ii}.exe &> {ii}.rpt'
            for ii in self.required_threads
        ]
        self.postrun_cmds = ['ln -s rfm_job.out single.rpt']

    @run_before('sanity')
    def set_sanity(self):
        # {{{ CRAY MPICH version:
        # - 7.7.15 (ANL base 3.2)
        # - 8.0.16.17 (ANL base 3.3)
        # - 8.1.4.31,8.1.5.32,8.1.18.4,8.1.21.11,8.1.25.17 (ANL base 3.4a2)
        regex = r'= MPI VERSION\s+: CRAY MPICH version \S+ \(ANL base (\S+)\)'
        stdout = os.path.join(self.stagedir, sn.evaluate(self.stdout))
        mpich_version = sn.extractsingle(regex, stdout, 1)
        self.mpithread_version = {
            '3.2': {
                'MPI_THREAD_SINGLE': 0,
                'MPI_THREAD_FUNNELED': 1,
                'MPI_THREAD_SERIALIZED': 2,
                'MPI_THREAD_MULTIPLE': 2
                # req=MPI_THREAD_MULTIPLE -> supported=MPI_THREAD_SERIALIZED
            },
            'other': {
                'MPI_THREAD_SINGLE': 0,
                'MPI_THREAD_FUNNELED': 1,
                'MPI_THREAD_SERIALIZED': 2,
                'MPI_THREAD_MULTIPLE': 3
            },
        }
        # }}}
        # {{{ regexes:
        regex = (r'^mpi_thread_required=(\w+)\s+mpi_thread_supported=\w+'
                 r'\s+mpi_thread_queried=\w+\s+(\d)')
        # single:
        req_thread_si = sn.extractsingle(regex, stdout, 1)
        runtime_mpithread_si = sn.extractsingle(
            regex, stdout, 2, int)
        # funneled:
        req_thread_f = sn.extractsingle(
            regex, f'{self.stagedir}/funneled.rpt', 1)
        runtime_mpithread_f = sn.extractsingle(
            regex, f'{self.stagedir}/funneled.rpt', 2, int)
        # serialized:
        req_thread_s = sn.extractsingle(
            regex, f'{self.stagedir}/serialized.rpt', 1)
        runtime_mpithread_s = sn.extractsingle(
            regex, f'{self.stagedir}/serialized.rpt', 2, int)
        # multiple:
        req_thread_m = sn.extractsingle(
            regex, f'{self.stagedir}/multiple.rpt', 1)
        runtime_mpithread_m = sn.extractsingle(
            regex, f"{self.stagedir}/multiple.rpt", 2, int)
        # }}}

        mpich_anl_version = sn.evaluate(mpich_version)
        if mpich_anl_version not in self.mpithread_version:
            mpich_anl_version = 'other'

        self.sanity_patterns = sn.all([
            sn.assert_found(r'tid=0 out of 1 from rank 0 out of 1',
                            stdout, msg='sanity: not found'),
            sn.assert_eq(runtime_mpithread_si,
                         self.mpithread_version[mpich_anl_version]
                                               [sn.evaluate(req_thread_si)],
                         msg='sanity_eq: {0} != {1}'),
            sn.assert_eq(runtime_mpithread_f,
                         self.mpithread_version[mpich_anl_version]
                                               [sn.evaluate(req_thread_f)],
                         msg='sanity_eq: {0} != {1}'),
            sn.assert_eq(runtime_mpithread_s,
                         self.mpithread_version[mpich_anl_version]
                                               [sn.evaluate(req_thread_s)],
                         msg='sanity_eq: {0} != {1}'),
            sn.assert_eq(runtime_mpithread_m,
                         self.mpithread_version[mpich_anl_version]
                                               [sn.evaluate(req_thread_m)],
                         msg='sanity_eq: {0} != {1}'),
        ])


@rfm.simple_test
class MpiGpuDirectOOM(rfm.RegressionTest, ContainerEngineCPEMixin):
    '''
    This test checks the issue reported in:
    https://github.com/eth-cscs/alps-gh200-reproducers/tree/main/gpudirect-oom
    '''
    maintainers = ['SSA']
    gh = 'https://github.com/eth-cscs/alps-gh200-reproducers'
    ipc = parameter(['0', '1'])
    # ipc ON is only a workaround (i.e slower perf.)
    valid_systems = ['+remote +nvgpu', '+remote +amdgpu']
    # DGPUDIRECT_OOM_HIP
    valid_prog_environs = ['+mpi +cuda +prgenv -cpe', '+mpi +rocm +prgenv -cpe']
    build_system = 'SingleSource'
    sourcesdir = 'src/alps-gh200-reproducers'
    sourcepath = 'gpudirect_oom.cpp'
    time_limit = '1m'
    build_locally = False
    env_vars = {'MPICH_GPU_SUPPORT_ENABLED': 1}
    regex = r'rank: \d, gpu_free: (?P<bytes>\d+), gpu_total:'
    tags = {'production', 'uenv', 'craype'}

    @run_before('compile')
    def set_gpu_flags(self):
        flags_d = {
            'sm_90': '-I ${CUDATOOLKIT_HOME:-$CUDA_HOME}/include',   # GH200
            'gfx942': '-D__HIP_PLATFORM_AMD__ -DGPUDIRECT_OOM_HIP',  # mi300
            'gfx90a': '-D__HIP_PLATFORM_AMD__ -DGPUDIRECT_OOM_HIP',  # mi200
        }
        ldflags_d = {
            'sm_90': '-L ${CUDATOOLKIT_HOME:-$CUDA_HOME}/lib64 -lcudart',
            'gfx942': '-lamdhip64',
            'gfx90a': '-lamdhip64',
        }
        gpu_arch = self.current_partition.select_devices('gpu')[0].arch
        self.build_system.cxxflags = [flags_d[gpu_arch]]
        self.build_system.ldflags = [ldflags_d[gpu_arch]]

    @run_before('run')
    def use_hpe_workaround(self):
        self.num_tasks = 2
        self.prerun_cmds = [f'# {self.gh}/blob/main/gpudirect-oom/README.md']
        if self.ipc == '1':
            self.env_vars['MPICH_GPU_IPC_ENABLED'] = 'ON'

    @sanity_function
    def set_sanity(self):
        return sn.assert_found(self.regex, self.stderr)

    @performance_function('bytes')
    def gpu_free(self):
        """
        with MPICH_GPU_IPC_ENABLED=ON, gpu_free should remain mostly constant
        without it, GPU0 will run out of memory (that is a bug)
        """
        return sn.min(sn.extractall(self.regex, self.stderr, 'bytes', float))
