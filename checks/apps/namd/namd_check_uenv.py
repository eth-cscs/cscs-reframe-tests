# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os

import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps
import uenv

namd_references = {
    'stmv': {
        'gh200': {'ns_day': (91, -0.05, None, 'ns/day')}, 
        'zen2': {'ns_day': (4.7, -0.05, None, 'ns/day')}
    },
}

slurm_config = {
    'stmv': {
        'gh200': {
            'nodes': 1,
            'ntasks-per-node': 1,
            'cpus-per-task': 29,
            'walltime': '0d0h5m0s',
            'gpu': True,
        },
        'zen2': {
            'nodes': 4,
            'ntasks-per-node': 128,
            'cpus-per-task': 1,
            'walltime': '0d0h5m0s',
            'gpu': False,
        },
    }
}


class namd_download(rfm.RunOnlyRegressionTest):
    '''
    Download NAMD source code.
    '''

    version = variable(str, value='3.0')
    artifactory = variable(str, value='https://jfrog.svc.cscs.ch/artifactory')
    descr = 'Fetch NAMD source code'
    sourcesdir = None
    executable = 'curl'
    local = True

    @run_before('run')
    def set_args(self):
        self.executable_opts = [
            '-f',  # Try to have curl not return 0 on server error
            '-u', '${CSCS_REGISTRY_USERNAME}:${CSCS_REGISTRY_PASSWORD}',
            f'{self.artifactory}/'
            f'uenv-sources/namd/NAMD_{self.version}_Source.tar.gz',
            '--output', f'NAMD_{self.version}_Source.tar.gz',
        ]

    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)


class namd_input_download(rfm.RunOnlyRegressionTest):
    '''
    Download NAMD input files.
    '''

    artifactory = variable(str, value='https://jfrog.svc.cscs.ch/artifactory')
    descr = 'Fetch NAMD input files'
    sourcesdir = None
    executable = 'curl'
    local = True

    @run_before('run')
    def set_args(self):
        self.executable_opts = [
            '-f',  # Try to have curl not return 0 on server error
            f'{self.artifactory}/cscs-reframe-tests/NAMD-uenv.tar.gz',
            '--output', f'NAMD-uenv.tar.gz',
        ]

    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)


class AutotoolsCustom(rfm.core.buildsystems.Autotools):
    '''
    Custom build system deriving from autotools.
    NAMD uses a ./config script instead of ./configure
    '''

    def __init__(self):
        super().__init__()

    def emit_build_commands(self, environ):
        prepare_cmd = []
        if self.srcdir:
            prepare_cmd += [f'cd {self.srcdir}']

        if self.builddir:
            prepare_cmd += [f'mkdir -p {self.builddir}', f'cd {self.builddir}']

        if self.builddir:
            configure_cmd = [
                os.path.join(
                    os.path.relpath(self.configuredir, self.builddir), 'config'
                )
            ]
        else:
            configure_cmd = [os.path.join(self.configuredir, 'config')]

        if self.config_opts:
            configure_cmd += self.config_opts

        config_dir = 'Linux-ARM64-g++.cuda'

        make_cmd = ['make -j']
        if self.max_concurrency is not None:
            make_cmd += [str(self.max_concurrency)]

        if self.make_opts:
            make_cmd += self.make_opts

        return prepare_cmd + [
            ' '.join(configure_cmd),  # Run ./config
            f'cd {config_dir}',  # cd to directory created by .config
            ' '.join(make_cmd),  # make
        ]


@rfm.simple_test
class NamdBuildTest(rfm.CompileOnlyRegressionTest):
    '''
    Test NAMD build from source.
    '''

    descr = 'NAMD Build Test'
    valid_prog_environs = ['+namd-single-node-dev']
    valid_systems = ['+nvgpu +uenv']
    build_system = AutotoolsCustom()
    sourcesdir = None
    maintainers = ['RM', 'JPC', 'SSA']
    namd_sources = fixture(namd_download, scope='session')
    build_locally = False
    tags = {'uenv'}

    @run_before('compile')
    def prepare_build(self):
        self.uarch = uenv.uarch(self.current_partition)
        self.build_system.builddir = self.stagedir
        self.skip_if_no_procinfo()
        cpu = self.current_partition.processor
        self.build_system.max_concurrency = cpu.info['num_cpus_per_socket']

        tarsource = os.path.join(
            self.namd_sources.stagedir,
            f'NAMD_{self.namd_sources.version}_Source.tar.gz',
        )

        # Extract source code and compiler bundled Charm++
        self.prebuild_cmds = [
            f'tar --strip-components=1 -xzf {tarsource} -C {self.stagedir}',
            'tar -xf charm-8.0.0.tar',  # INFO: Depends on the NAMD version
            'cd charm-8.0.0',
            './build charm++ multicore-linux-arm8 gcc --with-production '
            f'--enable-tracing -j {self.build_system.max_concurrency}',
            'cd ..',
            # Link against tcl8.6 (provided by the UENV)
            'sed -i \'s/-ltcl8.5/-ltcl8.6/g\' arch/Linux-ARM64.tcl',
        ]

        # UENV_MOUNT_POINT is not available outside of an UENV
        prefix = os.path.join('/user-environment', 'env',
                              'develop-single-node')

        self.build_system.config_opts = [
            'Linux-ARM64-g++.cuda',
            '--charm-arch multicore-linux-arm8-gcc',
            f'--charm-base {self.stagedir}/charm-8.0.0',
            '--with-tcl',
            f'--tcl-prefix {prefix}',
            '--with-fftw',
            '--with-fftw3',
            f'--fftw-prefix {prefix}',
        ]

        if self.uarch == 'gh200':
            self.build_system.config_opts += [
                '--with-single-node-cuda',
                '--with-cuda',
                '--cuda-gencode arch=compute_90,code=sm_90',
            ]

    @sanity_function
    def validate_test(self):
        self.namd_executable = os.path.join(
            self.stagedir, 'Linux-ARM64-g++.cuda', 'namd3'
        )
        return os.path.isfile(self.namd_executable)


class NamdCheckUENV(rfm.RunOnlyRegressionTest):
    descr = 'NAMD STMV Benchmark'
    test_name = 'stmv'
    valid_systems = ['+uenv']
    executable = 'namd3'
    maintainers = ['SSA']
    namd_input = fixture(namd_input_download, scope='session')

    @run_before('run')
    def prepare_run(self):
        tarsource = os.path.join(
            self.namd_input.stagedir,
            f'NAMD-uenv.tar.gz',
        )

        self.prerun_cmds = [
            f'tar -xzf {tarsource} -C {self.stagedir}',
        ]

        self.uarch = uenv.uarch(self.current_partition)
        config = slurm_config[self.test_name][self.uarch]

        self.num_tasks_per_node = config['ntasks-per-node']
        self.num_tasks = config['nodes'] * self.num_tasks_per_node
        self.num_cpus_per_task = config['cpus-per-task']
        self.ntask_per_core = 1
        self.time_limit = config['walltime']

        self.executable_opts = [
            f'+p {self.num_cpus_per_task}',
            '+setcpuaffinity',
        ]

        if self.uarch == 'gh200':
            self.executable_opts += ['+pmepes 5']
            self.executable_opts += ['+devices 0,1,2,3']
            # It is required to make all the GPUs visible
            self.extra_resources = {
                'gres': {'gres': 'gpu:4'},
            }

        if self.uarch == 'gh200':
            self.executable_opts += ['stmv_gpures_nve.namd']
        else:
            self.executable_opts += ['stmv_nogpu_nve.namd']

        if self.uarch is not None and \
           self.uarch in namd_references[self.test_name]:
            self.reference = {
                self.current_partition.fullname:
                    namd_references[self.test_name][self.uarch]
            }

    @sanity_function
    def validate_energy(self):
        energy = sn.avg(
            sn.extractall(
                r'ENERGY:([ \t]+\S+){10}[ \t]+(?P<energy>\S+)',
                self.stdout,
                'energy',
                float,
            )
        )

        energy_reference = -2869519.8
        energy_diff = sn.abs(energy - energy_reference)

        return sn.all(
            [
                sn.assert_eq(
                    sn.count(
                        sn.extractall(
                            r'TIMING: (?P<step_num>\S+)  CPU:',
                            self.stdout, 'step_num'
                        )
                    ),
                    25,  # 500 steps and output frequency of 20
                ),
                sn.assert_lt(energy_diff, 2720),
            ]
        )

    @performance_function('ns/day')
    def ns_day(self):
        return sn.avg(
            sn.extractall(
                r'PERFORMANCE:.* averaging (?P<ns_day>\S+) ns/day',
                self.stdout,
                'ns_day',
                float,
            )
        )


@rfm.simple_test
class NamdCheckUENVExec(NamdCheckUENV):
    valid_prog_environs = ['+namd-single-node', '+namd']
    tags = {'uenv', 'production'}


@rfm.simple_test
class NamdCheckUENVCustomExec(NamdCheckUENV):
    valid_prog_environs = ['+namd-single-node-dev']
    tags = {'uenv'}

    @run_after('init')
    def setup_dependency(self):
        self.depends_on('NamdBuildTestUENV', udeps.fully)

    @run_after('setup')
    def setup_executable(self):
        parent = self.getdep('NamdBuildTestUENV')
        self.executable = f'{parent.namd_executable}'
