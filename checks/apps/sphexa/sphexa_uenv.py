# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
import os
import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps


@rfm.simple_test
class sphexa_build(rfm.RunOnlyRegressionTest):
    descr = 'Clone and Build SPHEXA'
    maintainers = ['SSA']
    valid_systems = ['+uenv']
    valid_prog_environs = ['+mpi +cuda -cpe', '+rocm']
    sourcesdir = None
    branch = variable(str, value='develop')
    build_system = 'CustomBuild'
    url = variable(
        str, value='https://jfrog.svc.cscs.ch/artifactory/cscs-reframe-tests')
    sph_testing = parameter(['OFF'])
    sph_analytical = parameter(['OFF'])
    sph_build_type = parameter(['Release'])
    tags = {'uenv'}

    @run_before('run')
    def prepare_build(self):
        self.prerun_cmds = [
            f'git clone --branch={self.branch} --depth=1 '
            f'https://github.com/sphexa-org/sphexa.git sphexa.git',
            f'wget --quiet {self.url}/sphexa/50c.h5'
        ]
        self.job.options = ['--nodes=1']
        self.executable = 'hostname'
        self.executable_opts = ['| grep -m1 nid']
        self.exename = 'sphexa-hip' if 'rocm' in self.current_environ.features else 'sphexa-cuda' 
        cmakeArgs = [
            '-DCMAKE_C_COMPILER=mpicc',
            '-DCMAKE_CXX_COMPILER=mpicxx',
            '-DCSTONE_WITH_GPU_AWARE_MPI=ON',
            f'-DBUILD_TESTING={self.sph_testing}',
            f'-DBUILD_ANALYTICAL={self.sph_analytical}',
            f'-DCMAKE_BUILD_TYPE={self.sph_build_type}',
        ]

        if 'rocm' in self.current_environ.features:
            cmakeArgs += [
                '-DCMAKE_HIP_ARCHITECTURES="gfx90a;gfx942"',
            ]
        else:
            cmakeArgs += [
                '-DCMAKE_CUDA_COMPILER=nvcc',
                '-DCMAKE_CUDA_ARCHITECTURES=90',
                '-DCMAKE_CUDA_FLAGS=-ccbin=mpicxx',
            ]
            
        self.postrun_cmds = [
            # git log:
            'cd sphexa.git ; git log -n1 ; cd ..',
            # cmake configure step:
            'cmake -S sphexa.git -B build ' + ' '.join(cmakeArgs),
            # NOTE: -G Ninja is possible too
            f'cmake --build build -j `/usr/bin/nproc` -t {self.exename}'
        ]

    @sanity_function
    def validate_build(self):
        self._executable = os.path.join(self.stagedir, 'build',
                                        'main', 'src', 'sphexa', self.exename)
        return os.path.isfile(self._executable)


class sphexa_strong_scaling(rfm.RunOnlyRegressionTest):
    descr = 'Run SPHEXA'
    maintainers = ['SSA']
    valid_systems = ['+uenv']
    valid_prog_environs = ['+mpi +cuda -cpe', '+rocm']

    @run_after('init')
    def setup_dependency(self):
        self.depends_on('sphexa_build', udeps.fully)

    @require_deps
    def prepare_build(self, sphexa_build):
        self.build_dir = sphexa_build(
            part='normal',
            environ=f'{self.current_environ.name}').stagedir

    @run_after('setup')
    def set_executable(self):
        sphexa = 'sphexa-hip'
        executable = os.path.join(
            self.build_dir, 'build', 'main', 'src', 'sphexa', sphexa)
        infile = os.path.join(self.build_dir, self.sph_infile)
        self.prerun_cmds += [
            f'cp {executable} .',
            f'cp {infile} .',
            f'ldd {sphexa}',
        ]
        self.executable = f'./mi200-vars.sh ./{sphexa}'

    @run_before('run')
    def set_exe_opts(self):
        self.executable_opts = [
            f'--init {self.sph_testcase}',
            f'--glass ./{self.sph_infile}',
            f'-n {self.sph_side}',
            f'-s {self.sph_steps}',
        ]
        self.num_tasks = self.num_gpus
        self.num_tasks_per_node = self.nt_per_node
        self.num_cpus_per_task = 7
        self.job.options = [
            f'--nodes={int(self.num_gpus / self.num_tasks_per_node)}'
            if self.num_tasks > self.num_tasks_per_node else '--nodes=1',
        ]
        self.env_vars = {'OMP_NUM_THREADS': f'{self.omp}'}

    @sanity_function
    def validate_job(self):
        """
# Total execution time of 2 iterations of evrard up to t = 0.000231: 13.7324s
        """
        regex_t = (
            r'Total execution time of \d+ iterations of \S+ '
            r'up to t = \S+: \S+s$')
        return sn.all([
            sn.assert_found(regex_t, self.stdout)
        ])

    @performance_function('s')
    def elapsed(self):
        regex_t = (
            r'Total execution time of \d+ iterations of \S+ '
            r'up to t = \S+: (?P<sec>\S+)s$')
        return sn.extractsingle(regex_t, self.stdout, 'sec', float)

    @performance_function('s')
    def sec_per_step(self):
        regex_t = (
            r'Total execution time of (?P<steps>\d+) iterations of \S+ '
            r'up to t = \S+: (?P<sec>\S+)s$')
        sec = sn.extractsingle(regex_t, self.stdout, 'sec', float)
        steps = sn.extractsingle(regex_t, self.stdout, 'steps', float)
        return sec / steps


@rfm.simple_test
class sphexa_evrard_strong_scaling(sphexa_strong_scaling):
    tags = {'uenv'}
    # run a simple setup in the CI:
    num_gpus = parameter([4, 8])
    sph_testcase = parameter(['evrard'])
    sph_steps = parameter([2])
    sph_side = parameter([100])
    sph_infile = parameter(['50c.h5'])
    # or:
    # num_gpus = parameter([1, 2, 4, 8, 16, 24, 32, 64])
    # sph_steps = parameter([20])
    # sph_side = parameter([1000])
    nt_per_node = variable(int, value=4)
    omp = parameter([64])
    # TODO: external prebuilt exe = variable(str, value='...')
