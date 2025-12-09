# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
from uenv import uarch


@rfm.simple_test
class SphExa(rfm.RegressionTest):
    descr = 'SphExa test'
    valid_systems = ['+amdgpu +uenv', '+nvgpu +uenv']
    valid_prog_environs = ['+uenv +prgenv +rocm', '+uenv +prgenv +cuda']
    maintainers = ['SSA']
    tags = {'production', 'uenv', 'benchmark', 'maintenance'}

    branch = variable(str, value='develop')
    build_system = 'CMake'
    time_limit = '3m'
    build_locally = False
    sph_testing = variable(bool, value=False)
    sph_analytical = variable(bool, value=False)
    sph_build_type = parameter(['Release'])

    url = variable(
        str, value='https://jfrog.svc.cscs.ch/artifactory/cscs-reframe-tests')
    sph_infile = parameter(['50c.h5'])
    num_gpus = parameter([4])
    sph_testcase = parameter(['evrard'])
    sph_steps = parameter([2])
    sph_side = parameter([150])
    ntasks_per_node = variable(int, value=4)
    regex_elapsed = (
        r'Total execution time of (?P<steps>\d+) iterations of \S+ '
        r'up to t = \S+: (?P<sec>\S+)s$')

    @run_before('compile')
    def build_step(self):
        self.prebuild_cmds = [
                f'git clone --depth=1 --branch={self.branch} '
                f'https://github.com/sphexa-org/sphexa.git sphexa.git',
                f'cd sphexa.git ; git log -n1 ; cd ..',
        ]
        self.build_system.configuredir = 'sphexa.git'
        self.build_system.builddir = 'build'
        self.build_system.config_opts = [
            # f'-S sphexa.git',
            # f'-B build',
            # f'-DCMAKE_C_COMPILER=mpicc',
            # f'-DCMAKE_CXX_COMPILER=mpicxx',
            f'-DCSTONE_WITH_GPU_AWARE_MPI=ON',
            f'-DBUILD_TESTING={self.sph_testing}',
            f'-DBUILD_ANALYTICAL={self.sph_analytical}',
            f'-DCMAKE_BUILD_TYPE={self.sph_build_type}',
        ]
        self.build_system.max_concurrency = 64
        gpu_arch = self.current_partition.select_devices('gpu')[0].arch
        if 'rocm' in self.current_environ.features:
            self.build_system.config_opts += [
                f'-DCMAKE_CUDA_COMPILER=',
                f'-DCMAKE_HIP_ARCHITECTURES="{gpu_arch}"'
            ]
            self.build_system.make_opts = ['sphexa-hip']
        else:  # cuda
            gpu_arch = (
                gpu_arch[len("sm_"):]
                if gpu_arch.startswith("sm_")
                else gpu_arch
            )
            self.build_system.config_opts += [
                f'-DCMAKE_CUDA_COMPILER=nvcc',
                f'-DCMAKE_CUDA_FLAGS=-ccbin=mpicxx',
                f'-DCMAKE_CUDA_ARCHITECTURES="{gpu_arch}"'
            ]

    @run_before('run')
    def set_executable(self):
        gpu_arch = self.current_partition.select_devices('gpu')[0].arch
        if 'rocm' in self.current_environ.features:
            _affinity_script = (
                "./scripts/mi300-vars.sh"
                if gpu_arch == "gfx942"
                else "./scripts/mi200-vars.sh"
            )
            _executable = os.path.join(self.build_system.builddir, 'main',
                                       'src', 'sphexa', 'sphexa-hip')
        else:
            _affinity_script = './scripts/cuda-vars.sh'
            _executable = os.path.join(self.build_system.builddir, 'main',
                                       'src', 'sphexa', 'sphexa-cuda')

        self.executable = f'{_affinity_script} {_executable}'
        self.executable_opts = [
            f'--init {self.sph_testcase}',
            f'--glass ./{self.sph_infile}',
            f'-n {self.sph_side}',
            f'-s {self.sph_steps}',
        ]
        self.num_tasks = self.num_gpus
        self.num_tasks_per_node = self.ntasks_per_node
        self.skip_if_no_procinfo()
        self.num_cpus_per_task = (
            self.current_partition.processor.info["num_cpus"]
            // self.current_partition.processor.info["num_cpus_per_core"]
            // self.num_tasks_per_node
        )
        self.job.options = [
            f'--nodes={int(self.num_gpus / self.num_tasks_per_node)}'
            if self.num_tasks > self.num_tasks_per_node else '--nodes=1',
        ]
        self.env_vars = {'OMP_NUM_THREADS': '$SLURM_CPUS_PER_TASK'}
        self.prerun_cmds = [
            f'echo "# SLURM_JOBID=$SLURM_JOBID"',
            f'wget --quiet {self.url}/sphexa/50c.h5',
        ]

    @sanity_function
    def assert_results(self):
        """
# Total execution time of 2 iterations of evrard up to t = 0.000231: 13.7324s
        """
        s1 = sn.assert_found(self.regex_elapsed, self.stdout)
        return sn.all([s1])

    @performance_function('s')
    def elapsed(self):
        return sn.extractsingle(self.regex_elapsed, self.stdout, 'sec', float)

    @performance_function('s')
    def sec_per_step(self):
        sec = sn.extractsingle(self.regex_elapsed, self.stdout, 'sec', float)
        steps = sn.extractsingle(self.regex_elapsed, self.stdout, 'steps',
                                 float)
        return sec / steps

    _ref_sec_per_step = {
        'evrard': {
            'mi200': 5.6,
            'mi300': 5.1,
            'gh200': 0.9},
    }

    @run_before('performance')
    def set_perf_reference(self):
        self.uarch = uarch(self.current_partition)
        ref_sec_per_step = self._ref_sec_per_step.get(
            self.sph_testcase, {}).get(self.uarch)
        if ref_sec_per_step is not None:
            self.reference = {
                self.current_partition.fullname: {
                    'sec_per_step': (ref_sec_per_step, None, 0.15, 's')
                }
            }
