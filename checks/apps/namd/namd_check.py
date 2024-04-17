# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os

import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps
import uenv

namd_references = {
    'stmv': {'gh200': {'ns_day': (93, -0.05, None, 'ns/day')}},
}

slurm_config = {
    'stmv': {
        'gh200': {
            'nodes': 1,
            'ntasks-per-node': 1,
            'cpus-per-task': 29,
            'walltime': '0d0h5m0s',
            'gpu': True,
        }
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

    valid_prog_environs = ['builtin', 'cpeGNU']
    modules = ['NAMD']
    executable = 'namd2'
    use_multithreading = True
    num_tasks_per_core = 2
    maintainers = ['CB', 'LM']
    tags = {'scs', 'external-resources'}
    extra_resources = {
        'switches': {
            'num_switches': 1
        }
    }

    @run_after('init')
    def adapt_description(self):
        self.descr = f'NAMD check ({self.arch})'
        self.tags |= {'maintenance', 'production'}

    @run_after('init')
    def adapt_valid_systems(self):
        if self.arch == 'gpu':
            self.valid_systems = ['daint:gpu']
            if self.scale == 'small':
                self.valid_systems += ['dom:gpu']
        else:
            self.valid_systems = ['daint:mc', 'eiger:mc', 'pilatus:mc']
            if self.scale == 'small':
                self.valid_systems += ['dom:mc']

    @run_after('init')
    def adapt_valid_prog_environs(self):
        if self.current_system.name in ['eiger', 'pilatus']:
            self.valid_prog_environs.remove('builtin')

    @run_after('init')
    def setup_parallel_run(self):
        if self.arch == 'gpu':
            self.executable_opts = ['+idlepoll', '+ppn 23', 'stmv.namd']
            self.num_cpus_per_task = 24
            self.num_gpus_per_node = 1
        else:
            # On Eiger a no-smp NAMD version is the default
            if self.current_system.name in ['eiger', 'pilatus']:
                self.executable_opts = ['+idlepoll', 'stmv.namd']
                self.num_cpus_per_task = 2
            else:
                self.executable_opts = ['+idlepoll', '+ppn 71', 'stmv.namd']
                self.num_cpus_per_task = 72
        if self.scale == 'small':
            # On Eiger a no-smp NAMD version is the default
            if self.current_system.name in ['eiger', 'pilatus']:
                self.num_tasks = 768
                self.num_tasks_per_node = 128
            else:
                self.num_tasks = 6
                self.num_tasks_per_node = 1
        else:
            if self.current_system.name in ['eiger', 'pilatus']:
                self.num_tasks = 2048
                self.num_tasks_per_node = 128
            else:
                self.num_tasks = 16
                self.num_tasks_per_node = 1

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


class NamdCheck(rfm.RunOnlyRegressionTest):
    descr = 'NAMD STMV Benchmark'
    test_name = 'stmv'
    valid_systems = ['+nvgpu +uenv']
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
            '+pmepes 5',
            '+setcpuaffinity',
        ]

        if self.uarch == 'gh200':
            self.executable_opts += ['+devices 0,1,2,3']
            # It is required to make all the GPUs visible
            self.extra_resources = {
                'gres': {'gres': 'gpu:4'},
            }

        self.executable_opts += ['stmv_gpures_nve.namd']

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

    @run_before('performance')
    def set_reference(self):
        if self.arch == 'gpu':
            if self.scale == 'small':
                self.reference = {
                    'dom:gpu': {'days_ns': (0.149, None, 0.10, 'days/ns')},
                    'daint:gpu': {'days_ns': (0.178, None, 0.10, 'days/ns')}
                }
            else:
                self.reference = {
                    'daint:gpu': {'days_ns': (0.072, None, 0.15, 'days/ns')}
                }
        else:
            if self.scale == 'small':
                self.reference = {
                    'dom:mc': {'days_ns': (0.543, None, 0.10, 'days/ns')},
                    'daint:mc': {'days_ns': (0.513, None, 0.10, 'days/ns')},
                    'eiger:mc': {'days_ns': (0.126, None, 0.05, 'days/ns')},
                    'pilatus:mc': {'days_ns': (0.128, None, 0.05, 'days/ns')},
                }
            else:
                self.reference = {
                    'daint:mc': {'days_ns': (0.425, None, 0.10, 'days/ns')},
                    'eiger:mc': {'days_ns': (0.057, None, 0.05, 'days/ns')},
                    'pilatus:mc': {'days_ns': (0.054, None, 0.10, 'days/ns')}
                }

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
class NamdCheckUenvExec(NamdCheck):
    valid_prog_environs = ['+namd-single-node']
    tags = {'uenv', 'production'}


@rfm.simple_test
class NamdCheckCustomExec(NamdCheck):
    valid_prog_environs = ['+namd-single-node-dev']
    tags = {'uenv'}

    @run_after('init')
    def setup_dependency(self):
        self.depends_on('NamdBuildTest', udeps.fully)

    @run_after('setup')
    def setup_executable(self):
        parent = self.getdep('NamdBuildTest')
        self.executable = f'{parent.namd_executable}'
