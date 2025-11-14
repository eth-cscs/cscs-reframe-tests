# Copyright 2016-2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import shutil

import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps
from uenv import uarch

cp2k_references = {
    'md': {
        'gh200': {'time_run': (69, None, 0.05, 's')},
        'zen2': {'time_run': (91, None, 0.05, 's')}
    },
    'pbe': {
        'gh200': {'time_run': (67, None, 0.05, 's')},
        'zen2': {'time_run': (68, None, 0.05, 's')}
    },
    'rpa': {
        'gh200': {'time_run': (575, None, 0.05, 's')}
    },
}


slurm_config = {
    'md': {
        'gh200': {
            'nodes': 1,
            'ntasks-per-node': 16,
            'cpus-per-task': 16,
            'walltime': '0d0h5m0s',
            'gpu': True,
        },
        'zen2': {
            'nodes': 1,
            'ntasks-per-node': 32,
            'cpus-per-task': 4,
            'walltime': '0d0h5m0s',
            'gpu': False,
        },
    },
    'pbe': {
        'gh200': {
            'nodes': 2,
            'ntasks-per-node': 16,
            'cpus-per-task': 16,
            'walltime': '0d0h5m0s',
            'gpu': True,
        },
        'zen2': {
            'nodes': 2,
            'ntasks-per-node': 32,
            'cpus-per-task': 4,
            'walltime': '0d0h5m0s',
            'gpu': True,
        },
    },
    'rpa': {
        'gh200': {
            'nodes': 8,
            'ntasks-per-node': 16,
            'cpus-per-task': 16,
            'walltime': '0d0h15m0s',
            'gpu': True,
        },
    },
}


def version_from_uenv():
    return os.environ['UENV'].split('/')[1].split(':')[0]


@rfm.xfail("CP2K 2025.1 issues with libxc linking.", lambda test: test.version == "v2025.1")
class cp2k_download(rfm.RunOnlyRegressionTest):
    '''
    Download CP2K source code.
    '''

    version = variable(str, value='')
    descr = 'Fetch CP2K source code'
    sourcesdir = None
    executable = 'wget'
    local = True

    @run_before('run')
    def set_version(self):
        uenv_version = version_from_uenv()
        self.version = f'v{uenv_version}' if self.version == '' else self.version

        url = 'https://jfrog.svc.cscs.ch/artifactory/cscs-reframe-tests'

        self.executable_opts = [
            '--quiet',
            f'{url}/cp2k/{self.version}.tar.gz'
        ]

    @sanity_function
    def validate_download(self):
        # Manual compilation of v2025.1 with CMake is known to fail at link time,
        # because of issues with the libxc integration.
        return sn.and_(sn.assert_eq(self.job.exitcode, 0), sn.assert_ne(self.version, 'v2025.1'))
    

@rfm.simple_test
class Cp2kBuildTestUENV(rfm.CompileOnlyRegressionTest):
    '''
    Test CP2K build from source.
    '''

    descr = 'CP2K Build Test'
    valid_prog_environs = ['+cp2k-dev -dlaf']
    valid_systems = ['+uenv']
    build_system = 'CMake'
    sourcesdir = None
    maintainers = ['tmathieu', 'romeli', 'abussy', 'simbergm',  'SSA']
    cp2k_sources = fixture(cp2k_download, scope='session')
    build_locally = False
    tags = {'uenv'}

    @run_before('compile')
    def prepare_build(self):
        self.uarch = uarch(self.current_partition)
        self.build_system.builddir = os.path.join(self.stagedir, 'build')
        self.skip_if_no_procinfo()
        cpu = self.current_partition.processor
        self.build_system.max_concurrency = cpu.info['num_cpus_per_socket']

        self.time_limit = "0d0h30m0s"

        tarsource = os.path.join(
            self.cp2k_sources.stagedir, f'{self.cp2k_sources.version}.tar.gz'
        )

        # Extract source code
        self.prebuild_cmds = [
            f'tar --strip-components=1 -xzf {tarsource} -C {self.stagedir}'
        ]

        self.build_system.config_opts = [
            '-DCMAKE_BUILD_TYPE=Release',
            '-DCP2K_USE_LIBXC=ON',
            '-DCP2K_USE_LIBINT2=ON',
            '-DCP2K_USE_FFTW3=ON',
            '-DCP2K_USE_SPGLIB=ON',
            '-DCP2K_USE_ELPA=ON',
            '-DCP2K_USE_SPLA=ON',
            '-DCP2K_USE_SIRIUS=ON',
            '-DCP2K_USE_COSMA=ON',
            '-DCP2K_USE_PLUMED=ON',
        ]

        # CP2K CMake changed default values from 2025.2 onwards
        # CMake options below are chosen depending on the version of CP2K
        version = float(version_from_uenv())

        if version > 2025.1:
            self.build_system.config_opts += [
                '-DCP2K_USE_MPI=ON',
                '-DCP2K_USE_LIBVORI=ON',
            ]

        if self.uarch == 'gh200':
            self.build_system.config_opts += [
                '-DCP2K_USE_ACCEL=CUDA',
                '-DCP2K_USE_SPLA_GEMM_OFFLOADING=ON',
                '-DCMAKE_CUDA_HOST_COMPILER=mpicc',
            ]
            if version > 2025.1:
                self.build_system.config_opts += [
                    '-DCMAKE_CUDA_ARCHITECTURES=90',
                ]
            else:
                self.build_system.config_opts += [
                    '-DCP2K_WITH_GPU=H100',
                ]

    @sanity_function
    def validate_test(self):
        # INFO: Executables are in exe/FOLDER because -DCP2K_ENABLE_REGTEST=ON
        # INFO: With -DCP2K_ENABLE_REGTEST=OFF, executables are in build/bin/
        #folder = 'local_cuda' if self.uarch == 'gh200' else 'local'
        #self.cp2k_executable = os.path.join(self.stagedir, 'exe', folder,
        #                                    'cp2k.psmp')
        self.cp2k_executable = os.path.join(self.stagedir, 'build', 'bin',
                                            'cp2k.psmp')
        return os.path.isfile(self.cp2k_executable)


class Cp2kCheck_UENV(rfm.RunOnlyRegressionTest):
    maintainers = ['SSA']
    valid_systems = ['+uenv']
    valid_prog_environs = ['+cp2k -dlaf']

    @run_after('setup')
    def setup_wrapper(self):
        """Setup wrapper script"""
        self.uarch = uarch(self.current_partition)
        self.wrapper = './mps-wrapper.sh' if self.uarch == 'gh200' else ''
    
    @run_before('run')
    def prepare_run(self):
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

        self.env_vars["MIMALLOC_ALLOW_LARGE_OS_PAGES"] = "1"
        self.env_vars["MIMALLOC_EAGER_COMMIT_DELAY"] = "0"

        if self.uarch == "zen2":
            self.env_vars["PIKA_THREADS"] = str((self.num_cpus_per_task // 2) - 1)
        else:
            self.env_vars["PIKA_THREADS"] = str(self.num_cpus_per_task - 1)

        if self.uarch == 'gh200':
            self.env_vars['MPICH_GPU_SUPPORT_ENABLED'] = '1'
            self.env_vars['CUDA_CACHE_DISABLE'] = '1'
            self.env_vars["DLAF_BT_BAND_TO_TRIDIAG_HH_APPLY_GROUP_SIZE"] = \
                "128"
            self.env_vars["DLAF_UMPIRE_DEVICE_MEMORY_POOL_ALIGNMENT_BYTES"] = \
                str(2**21)

        # set reference
        if self.uarch is not None and \
           self.uarch in cp2k_references[self.test_name]:
            self.reference = {
                self.current_partition.fullname:
                    cp2k_references[self.test_name][self.uarch]
            }

    @run_before('run')
    def setup_executable(self):
        self.executable = f'{self.wrapper} ./pika-bind.sh cp2k.psmp'

    @sanity_function
    def assert_energy_diff(self):
        regex = (
            r'\s+ENERGY\| Total FORCE_EVAL \( QS \) energy \[(a.u.|hartree)\]'
            r':?\s+(?P<energy>\S+)$'
        )
        energy = sn.extractsingle(regex, self.stdout, 'energy', float, item=-1)
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


# {{{ MD
class Cp2kCheckMD_UENV(Cp2kCheck_UENV):
    test_name = 'md'
    executable_opts = ['-i', 'H2O-128.inp']
    energy_reference = -2202.179145784019511


@rfm.simple_test
class Cp2kCheckMD_UENVExec(Cp2kCheckMD_UENV):
    valid_prog_environs = ['+cp2k -dlaf']
    tags = {'uenv', 'production'}


@rfm.simple_test
class Cp2kCheckMD_UENVCustomExec(Cp2kCheckMD_UENV):
    '''
    Same test as above, but using executables built by Cp2kBuildTestUENV.
    '''

    valid_prog_environs = ['+cp2k-dev -dlaf']
    tags = {'uenv'}
 
    @run_after('init')
    def setup_dependency(self):
        self.depends_on('Cp2kBuildTestUENV', udeps.fully)

    @run_before('run')
    def setup_executable(self):
        parent = self.getdep('Cp2kBuildTestUENV')
        self.executable = f'{self.wrapper} ./pika-bind.sh {parent.cp2k_executable}'


# }}}
# {{{ PBE
class Cp2kCheckPBE_UENV(Cp2kCheck_UENV):
    test_name = 'pbe'
    valid_prog_environs = ['+cp2k -dlaf']
    tags = {'uenv', 'production'}
    energy_reference = -2206.2426491358

    @run_after('init')
    def setup_input_and_wf(self):
        # Define input file depending on version
        # CP2K 2025.2 counts SCF steps differently
        # Since this first inner SCF step does converge
        # a different count means a different runtime with the same input file
        # See https://github.com/cp2k/cp2k/pull/4141
        version = float(version_from_uenv())
        if version > 2025.1:
            # Refuce max_scf to 16 to reproduce previous behaviour
            self.executable_opts = ['-i', 'H2O-128-PBE-TZ-max_scf_16.inp']
        else:
            self.executable_opts = ['-i', 'H2O-128-PBE-TZ.inp']

        # Define WF file for restart (needed by RPA test)
        self.wfn_file = 'H2O-128-PBE-TZ-RESTART.wfn'

@rfm.simple_test
class Cp2kCheckPBE_UENVExec(Cp2kCheckPBE_UENV):
    valid_prog_environs = ['+cp2k -dlaf']
    tags = {'uenv', 'production'}


@rfm.simple_test
class Cp2kCheckPBE_UENVCustomExec(Cp2kCheckPBE_UENV):
    '''
    Same test as above, but using executables built by Cp2kBuildTestUENV.
    '''

    valid_prog_environs = ['+cp2k-dev -dlaf']
    tags = {'uenv'}

    @run_after('init')
    def setup_dependency(self):
        self.depends_on('Cp2kBuildTestUENV', udeps.fully)

    @run_before('run')
    def setup_executable(self):
        parent = self.getdep('Cp2kBuildTestUENV')
        self.executable = f'{self.wrapper} ./pika-bind.sh {parent.cp2k_executable}'


# }}}
# {{{ RPA
@rfm.simple_test
class Cp2kCheckRPA_UENVExec(Cp2kCheck_UENV):
    test_name = 'rpa'
    valid_prog_environs = ['+cp2k -dlaf']
    executable_opts = ['-i', 'H2O-128-RI-dRPA-TZ.inp']
    energy_reference = -2217.36884935325
    tags = {'maintenance'}
    valid_systems = ['+nvgpu']

    def __init__(self):
        super().__init__()

    @run_after('init')
    def setup_dependency(self):
        # Depend on PBE ouput
        self.depends_on('Cp2kCheckPBE_UENVExec', udeps.fully)

    @run_after('setup')
    def copy_wnf(self):
        parent = self.getdep('Cp2kCheckPBE_UENVExec')
        src = os.path.join(parent.stagedir, parent.wfn_file)
        dest = os.path.join(self.stagedir, parent.wfn_file)
        shutil.copyfile(src, dest)
# }}}
