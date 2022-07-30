# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys

import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility as rfm_util

sys.path.append(os.path.abspath(os.path.join(__file__, '../../..')))
import microbenchmarks.gpu.hooks as hooks


@rfm.simple_test
class cuda_aware_mpi_check(rfm.CompileOnlyRegressionTest):
    descr = 'Cuda-aware MPI test from the NVIDIA repo.'
    sourcesdir = ('https://github.com/NVIDIA-developer-blog/'
                  'code-samples.git')
    valid_systems = [
        'daint:gpu', 'dom:gpu', 'arolla:cn', 'tsa:cn',
        'ault:amdv100', 'ault:intelv100'
    ]
    prebuild_cmds = ['cd posts/cuda-aware-mpi-example/src']
    build_system = 'Make'
    postbuild_cmds = ['ls ../bin']
    maintainers = ['JO']
    tags = {'production', 'scs'}

    gpu_arch = variable(str, type(None))

    @run_after('init')
    def set_valid_prog_environs(self):
        if self.current_system.name in ['arolla', 'tsa']:
            self.valid_prog_environs = ['PrgEnv-gnu']
        elif self.current_system.name in ['ault']:
            self.valid_prog_environs = ['PrgEnv-gnu']
        else:
            self.valid_prog_environs = ['PrgEnv-cray', 'PrgEnv-gnu',
                                        'PrgEnv-pgi', 'PrgEnv-nvidia']

        if self.current_system.name in ['arolla', 'tsa', 'ault']:
            self.exclusive_access = True

    run_after('setup')(bind(hooks.set_gpu_arch))
    run_after('setup')(bind(hooks.set_num_gpus_per_node))

    @run_before('compile')
    def set_compilers(self):
        if self.current_environ.name == 'PrgEnv-pgi':
            self.build_system.cflags = ['-std=c99', ' -O3']
        elif self.current_environ.name == 'PrgEnv-nvidia':
            self.variables = {
                'CUDA_HOME': '$CRAY_NVIDIA_PREFIX/cuda'
            }

        gcd_flgs = (
            '-gencode arch=compute_{0},code=sm_{0}'.format(self.gpu_arch)
        )
        self.build_system.options = [
            'CUDA_INSTALL_PATH=$CUDA_HOME',
            'MPI_HOME=$CRAY_MPICH_PREFIX',
            'GENCODE_FLAGS="%s"' % (gcd_flgs),
            'MPICC="%s"' % self.current_environ.cc,
            'MPILD="%s"' % self.current_environ.cxx
        ]

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found(r'jacobi_cuda_aware_mpi',
                                               self.stdout)


class CudaAwareMpiRuns(rfm.RunOnlyRegressionTest):

    prerun_cmds = ['export MPICH_RDMA_ENABLED_CUDA=1']
    valid_systems = [
        'daint:gpu', 'dom:gpu', 'arolla:cn', 'tsa:cn',
        'ault:amdv100', 'ault:intelv100'
    ]

    @run_after('init')
    def set_valid_prog_environs(self):
        if self.current_system.name in ['arolla', 'tsa']:
            self.valid_prog_environs = ['PrgEnv-gnu']
        elif self.current_system.name in ['ault']:
            self.valid_prog_environs = ['PrgEnv-gnu']
        else:
            self.valid_prog_environs = ['PrgEnv-cray', 'PrgEnv-gnu',
                                        'PrgEnv-pgi', 'PrgEnv-nvidia']

        if self.current_system.name in ['arolla', 'tsa', 'ault']:
            self.exclusive_access = True

    @run_after('init')
    def add_deps(self):
        self.depends_on('cuda_aware_mpi_check')

    run_after('setup')(bind(hooks.set_gpu_arch))
    run_after('setup')(bind(hooks.set_num_gpus_per_node))

    @require_deps
    def set_executable(self, cuda_aware_mpi_check):
        self.executable = os.path.join(
            cuda_aware_mpi_check().stagedir,
            'posts', 'cuda-aware-mpi-example',
            'bin', 'jacobi_cuda_aware_mpi'
        )

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found(r'Stopped after 1000 iterations'
                                               r' with residue 0.00024',
                                               self.stdout)


@rfm.simple_test
class cuda_aware_mpi_one_node_check(CudaAwareMpiRuns):
    '''Run the case in one node.'''

    prerun_cmds += ['export CRAY_CUDA_MPS=1']

    @run_before('run')
    def set_num_tasks(self):
        self.num_tasks = 2 * self.num_gpus_per_node
        self.num_tasks_per_node = self.num_tasks
        self.executable_opts = [f'-t {self.num_tasks/2} 2']


@rfm.simple_test
class cuda_aware_mpi_two_nodes_check(CudaAwareMpiRuns):
    '''Run the case across two nodes.'''

    @run_before('run')
    def set_num_tasks(self):
        self.num_tasks = 2
        self.num_tasks_per_node = 1
        self.num_gpus_per_node = 1
        self.executable_opts = ['-t %d 1' % self.num_tasks]


class gpu_direct(rfm.RegressionTest):
    descr = 'gpuDirect cray-mpich test'
    build_system = 'SingleSource'
    sourcepath = 'gpudirect.cpp'
    maintainers = ['JG']
    tags = {'production'}

    run_after('setup')(bind(hooks.set_num_gpus_per_node))
    # unused to avoid loading cudatoolkit:
    # run_after('setup')(bind(hooks.set_gpu_arch))

    @run_before('run')
    def set_env(self):
        self.variables['MPICH_RDMA_ENABLED_CUDA'] = '1'
        self.variables['MPICH_VERSION_DISPLAY'] = '1'

    @run_before('run')
    def set_num_tasks(self):
        self.num_tasks = 2
        self.num_tasks_per_node = 1

    @run_before('sanity')
    def set_sanity_patterns(self):
        result = sn.count(sn.extractall(r'^(PASS):', self.stdout, 1))
        self.sanity_patterns = sn.assert_reference(result, 2, 0, 0)

    @performance_function('')
    def rpt_mpi_version(self):
        cs = self.current_system.name
        if cs in ['dom', 'daint']:
            regex = r'MPI VERSION\s+: CRAY MPICH version (\S+) '
        else:
            regex = r'\s+Ident string: (\S+)'

        version = sn.extractsingle(regex, self.stderr, 1,
                                   conv=lambda x: int(x.replace('.', '')))
        return version

    @performance_function('')
    def rpt_num_pass(self):
        return sn.count(sn.extractall(r'^(PASS):', self.stdout, 1))


@rfm.simple_test
class gpu_direct_cdt(gpu_direct):
    valid_systems = ['dom:gpu', 'daint:gpu']
    valid_prog_environs = ['PrgEnv-cray']
    module_info = parameter(rfm_util.find_modules('cdt/'))
    prerun_cmds = ['module list']
    variables['LD_LIBRARY_PATH'] = '$CRAY_LD_LIBRARY_PATH:$LD_LIBRARY_PATH'

    @run_after('setup')
    def apply_module_info(self):
        bad_pe = ['cdt/21.09', 'cdt/20.08']
        # test will fail when built with cdt<=21.09 (cray-mpich<=7.7.18):
        # PASS:rk=1     // 1st call
        # FAIL:rk=1:-1  //  2d call
        s, e, m = self.module_info
        self.skip_if(s not in self.valid_systems,
                     f'{s} not in {self.valid_systems}')
        self.skip_if(e not in self.valid_prog_environs,
                     f'{e} not in {self.valid_prog_environs}')
        self.skip_if(m in bad_pe, f'{m} in old {bad_pe}')
        self.modules = ['cudatoolkit', m]
        self.build_system.cxxflags = [
            '-I/usr/local/cuda/targets/x86_64-linux/include'
        ]
        self.build_system.ldflags = [
            '-L/usr/local/cuda/targets/x86_64-linux/lib', '-lcudart',
        ]


@rfm.simple_test
class gpu_direct_cpe(gpu_direct):
    valid_systems = ['hohgant:mc']  # , 'manali:mc']
    valid_prog_environs = ['PrgEnv-cray']
    module_info = parameter(rfm_util.find_modules('cpe/'))
    # This conflicts with self.module_info:
    #   run_after('setup')(bind(hooks.set_gpu_arch))

    @run_after('setup')
    def apply_module_info(self):
        bad_pe = ['cpe/21.12']
        s, e, m = self.module_info
        self.skip_if(s not in self.valid_systems,
                     f'{s} not in {self.valid_systems}')
        self.skip_if(e not in self.valid_prog_environs,
                     f'{e} not in {self.valid_prog_environs}')
        self.skip_if(m in bad_pe, f'{m} in old {bad_pe}')
        self.modules = ['cudatoolkit', m]


@rfm.simple_test
class gpu_direct_spack(gpu_direct):
    #           build   run
    # manali:   ok      ok
    # hohgant:  ok      SD-56044
    # balfrin:  ok      ok
    # TODO:
    # export UCX_POSIX_USE_PROC_LINK=n
    # mpicc program.c -Wl,--disable-new-dtags
    # NOTE:
    # error: squashfs-mount: Failed to unshare the mount namespace:
    #                        Operation not permitted
    # -> it happens when you run it twice, nested calls are not supported.
    valid_systems = ['manali:mc', 'hohgant:mc', 'balfrin:mc']
    valid_prog_environs = ['builtin']

    @run_before('compile')
    def set_sw_paths(self):
        self.sw_versions = {
            'manali': {
                'sw_path':
                    '/apps/manali/UES/store/linux-sles15-zen3/gcc-11.3.0/',
                'gcc': 'gcc-11.3.0-bjbwwem6nthpp4b5frzkkqlokk572yk2',
                'mpi': 'openmpi-4.1.3-hmzuovhyviaub7wbbftmzddluvgqt46z',
                'hdf': 'hdf5-1.12.2-r44u5dw3sshw7vig4lapub65pz3b54mj',
                'cuda': 'cuda-11.7.0-hzaujtmp3mutt7a4cj74sc2svpbpz6tv',
            },
            'hohgant': {
                'squashfs_file': '/scratch/e1000/hstoppel/store.v2.squashfs',
                'sw_path': '/user-environment/linux-sles15-zen3/gcc-11.3.0',
                'gcc': 'gcc-11.3.0-dqccstgdahnk2quv4smmr5vn2lk5k7qj',
                'mpi': 'openmpi-4.1.4-wj2jhjjcgnpwuihb5tlca6i44cyk6blw',
                'hdf': 'hdf5-1.12.2-r44u5dw3sshw7vig4lapub65pz3b54mj',
                'cuda': 'cuda-11.7.0-4jqg4mez27qxjssygwth5u4wkobco7ma',
            },
        }
        self.sw_versions['balfrin'] = self.sw_versions['hohgant']  # hard copy
        #
        cs = self.current_system.name
        sw_path = self.sw_versions[cs]['sw_path']
        self.gcc_root = f"{sw_path}/{self.sw_versions[cs]['gcc']}"
        self.mpi_root = f"{sw_path}/{self.sw_versions[cs]['mpi']}"
        self.hdf5_root = f"{sw_path}/{self.sw_versions[cs]['hdf']}"
        self.cuda_root = f"{sw_path}/{self.sw_versions[cs]['cuda']}"

    @run_before('compile')
    def set_build_script(self):
        build_script = 'rfm_b.sh'
        self.build_system.cxx = f'echo "{self.mpi_root}/bin/mpicxx'
        self.build_system.cxxflags = [
            f'-I{self.cuda_root}/targets/x86_64-linux/include',
        ]
        self.build_system.ldflags = [
            f'-L{self.cuda_root}/extras/CUPTI/lib64',
            f'-L{self.cuda_root}/lib64', '-lcudart', '-g',
            f'" > {build_script}',
        ]
        cs = self.current_system.name
        squashfs_cmd = \
            '' if cs in ['manali'] \
            else f"squashfs-run {self.sw_versions[cs]['squashfs_file']}"

        self.postbuild_cmds += [
            f'cat {build_script}',
            f'chmod 700 {build_script}',
            f'{squashfs_cmd} ./{build_script}',
        ]

    @run_before('run')
    def set_job_script(self):
        job_script = 'rfm_j.sh'
        self.prerun_cmds += [
            f"echo '#!/bin/bash' > {job_script}",
            f"echo '{self.mpi_root}/bin/ompi_info | grep Ident >&2' "
            f">> {job_script}",
            f"echo 'export MPICH_RDMA_ENABLED_CUDA=1' >> {job_script}",
            f"echo 'export LD_LIBRARY_PATH={self.cuda_root}/lib64:"
            f"$LD_LIBRARY_PATH' >> {job_script}",
            f"echo 'exec $*' >> {job_script}",
            f'cat {job_script}',
            f'chmod 700 {job_script}',
        ]
        cs = self.current_system.name
        squashfs_cmd = \
            '' if cs in ['manali'] \
            else f"squashfs-run {self.sw_versions[cs]['squashfs_file']}"
        self.job.launcher.options = [squashfs_cmd, f'./{job_script}']
