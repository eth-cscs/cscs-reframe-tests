# Copyright 2016-2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import shutil

import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps
import uenv

cp2k_references = {
    'pbe': {'gh200': {'time_run': (65, None, 0.05, 's')}},
    'rpa': {'gh200': {'time_run': (575, None, 0.05, 's')}},
}


slurm_config = {
    'pbe': {
        'gh200': {
            'nodes': 8,
            'ntasks-per-node': 16,
            'cpus-per-task': 16,
            'walltime': '0d0h5m0s',
            'gpu': True,
        }
    },
    'rpa': {
        'gh200': {
            'nodes': 8,
            'ntasks-per-node': 16,
            'cpus-per-task': 16,
            'walltime': '0d0h15m0s',
            'gpu': True,
        }
    },
}


class cp2k_download(rfm.RunOnlyRegressionTest):
    """
    Download CP2K source code.
    """

    version = variable(str, value='2024.3')
    descr = 'Fetch CP2K source code'
    sourcedir = None
    executable = 'wget'
    executable_opts = [
        f'https://github.com/cp2k/cp2k/archive/refs/tags/v{version}.tar.gz',
    ]
    local = True

    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)


@rfm.simple_test
class Cp2kBuildTest(rfm.CompileOnlyRegressionTest):
    """
    Test CP2K build from source.
    """

    descr = 'CP2K Build Test'
    valid_prog_environs = ['+cp2k-dev']
    valid_systems = ['*']
    build_system = 'CMake'
    sourcesdir = None
    maintainers = ['SSA']
    cp2k_sources = fixture(cp2k_download, scope='session')
    build_locally = False
    tags = {'uenv'}

    @run_before('compile')
    def prepare_build(self):
        self.uarch = uenv.uarch(self.current_partition)
        self.build_system.builddir = os.path.join(self.stagedir, 'build')
        self.skip_if_no_procinfo()
        cpu = self.current_partition.processor
        self.build_system.max_concurrency = cpu.info['num_cpus_per_socket']

        tarsource = os.path.join(
            self.cp2k_sources.stagedir, f'v{self.cp2k_sources.version}.tar.gz'
        )

        # Extract source code
        self.prebuild_cmds = [
            f'tar --strip-components=1 -xzf {tarsource} -C {self.stagedir}'
        ]

        # TODO: Use Ninja generator
        self.build_system.config_opts = [
            '-DCP2K_ENABLE_REGTESTS=ON',
            # Puts executables under exe/local_cuda/
            '-DCP2K_USE_LIBXC=ON',
            '-DCP2K_USE_LIBINT2=ON',
            '-DCP2K_USE_SPGLIB=ON',
            '-DCP2K_USE_ELPA=ON',
            '-DCP2K_USE_SPLA=ON',
            '-DCP2K_USE_SIRIUS=ON',
            '-DCP2K_USE_COSMA=ON',
            '-DCP2K_USE_PLUMED=ON',
        ]

        if self.uarch == 'gh200':
            self.build_system.config_opts += [
                '-DCP2K_USE_ACCEL=CUDA',
                '-DCP2K_WITH_GPU=H100',
            ]

    @sanity_function
    def validate_test(self):
        # INFO: Executables are in exe/FOLDER because -DCP2K_ENABLE_REGTEST=ON
        # INFO: With -DCP2K_ENABLE_REGTEST=OFF, executables are in build/bin/
        folder = 'local_cuda' if self.uarch == 'gh200' else 'local'
        self.cp2k_executable = os.path.join(self.stagedir, 'exe', folder,
                                            'cp2k.psmp')
        return os.path.isfile(self.cp2k_executable)


class Cp2kCheck(rfm.RunOnlyRegressionTest):
    executable = './mps-wrapper.sh cp2k.psmp'
    maintainers = ['SSA']
    valid_systems = ['*']

    @run_before('run')
    def prepare_run(self):
        self.uarch = uenv.uarch(self.current_partition)
        config = slurm_config[self.test_name][self.uarch]
        # sbatch options
        self.job.options = [
            f'--nodes={config["nodes"]}',
        ]
        self.num_tasks_per_node = config['ntasks-per-node']
        self.num_tasks = config['nodes'] * self.num_tasks_per_node
        self.num_cpus_per_task = config['cpus-per-task']
        self.ntasks_per_core = 1
        self.time_limit = config['walltime']

        # srun options
        self.job.launcher.options = ['--cpu-bind=cores']

        # environment variables
        self.env_vars['OMP_NUM_THREADS'] = str(
            self.num_cpus_per_task - 1
        )  # INFO: OpenBLAS adds one thread
        self.env_vars['OMP_PLACES'] = 'cores'
        self.env_vars['OMP_PROC_BIND'] = 'close'
        if self.uarch == 'gh200':
            self.env_vars['MPICH_GPU_SUPPORT_ENABLED'] = '1'
            self.env_vars['CUDA_CACHE_DISABLE'] = '1'

        # set reference
        if self.uarch is not None and
        self.uarch in cp2k_references[self.test_name]:
            self.reference = {
                self.current_partition.fullname:
                    cp2k_references[self.test_name][self.uarch]
            }

    @sanity_function
    def assert_energy_diff(self):
        energy = sn.extractsingle(
            r'\s+ENERGY\| Total FORCE_EVAL \( QS \) '
            r'energy [\[\(]a\.u\.[\]\)]:\s+(?P<energy>\S+)',
            self.stdout,
            'energy',
            float,
            item=-1,
        )
        energy_diff = sn.abs(energy - self.energy_reference)
        successful_termination = sn.assert_found(r'PROGRAM STOPPED IN',
                                                 self.stdout)
        correct_energy = sn.assert_lt(energy_diff, 1e-4)
        return sn.all([
            successful_termination,
            correct_energy,
        ])

    # INFO: The name of this function needs to match with the reference dict!
    @performance_function('s')
    def time_run(self):
        return sn.extractsingle(
            r'^ CP2K(\s+[\d\.]+){4}\s+(?P<perf>\S+)',
            self.stdout, 'perf', float
        )


class Cp2kCheckPBE(Cp2kCheck):
    test_name = 'pbe'
    executable_opts = ['-i', 'H2O-128-PBE-TZ.inp']
    energy_reference = -2206.2426491358

    @run_after('init')
    def set_wfn(self):
        self.wfn_file = 'H2O-128-PBE-TZ-RESTART.wfn'


@rfm.simple_test
class Cp2kCheckPBEUenvExec(Cp2kCheckPBE):
    valid_prog_environs = ['+cp2k']
    tags = {'uenv', 'production'}


@rfm.simple_test
class Cp2kCheckPBECustomExec(Cp2kCheckPBE):
    """
    Same test as above, but using executables built by Cp2kBuildTest.
    """

    valid_prog_environs = ['+cp2k-dev']
    tags = {'uenv'}

    @run_after('init')
    def setup_dependency(self):
        self.depends_on('Cp2kBuildTest', udeps.fully)

    @run_after('setup')
    def setup_executable(self):
        parent = self.getdep('Cp2kBuildTest')
        self.executable = f'./mps-wrapper.sh {parent.cp2k_executable}'


@rfm.simple_test
class Cp2kCheckRPA(Cp2kCheck):
    test_name = 'rpa'
    valid_prog_environs = ['+cp2k']
    executable_opts = ['-i', 'H2O-128-RI-dRPA-TZ.inp']
    energy_reference = -2217.36884935325
    tags = {'maintenance'}

    def __init__(self):
        super().__init__()

    @run_after('init')
    def setup_dependency(self):
        # Depend on PBE ouput
        self.depends_on('Cp2kCheckPBEUenvExec', udeps.fully)

    @run_after('setup')
    def copy_wnf(self):
        parent = self.getdep('Cp2kCheckPBEUenvExec')
        src = os.path.join(parent.stagedir, parent.wfn_file)
        dest = os.path.join(self.stagedir, parent.wfn_file)
        shutil.copyfile(src, dest)
