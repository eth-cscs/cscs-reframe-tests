# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
import os

import reframe as rfm
import reframe.utility.sanity as sn
from uenv import uarch

gromacs_references = {
    'STMV': {
        'gh200': {
            'perf': (117, -0.02, None, 'ns/day'),
            'totalenergy': (-1.17527e+07, -0.01, None, 'kJ/mol'),
        },
        'zen2': {
            'perf': (3.6, -0.02, None, 'ns/day'),
            'totalenergy': (-1.43595e+07, -0.01, None, 'kJ/mol'),
        },
    },
 }

slurm_config = {
    'STMV': {
        'gh200': {
            'nodes': 1,
            'ntasks-per-node': 8,
            'cpus-per-task': 32,
            'walltime': '0d0h5m0s',
            'gpu': True,
        },
        'zen2': {
            'nodes': 4,
            'ntasks-per-node': 16,
            'cpus-per-task': 8,
            'walltime': '0d0h5m0s',
            'gpu': False,
        }
    },
    'hEGFRDimerPair': {
        'gh200': {
            'nodes': 1,
            'ntasks-per-node': 8,
            'cpus-per-task': 32,
            'walltime': '0d0h5m0s',
            'gpu': True,
        },
    },
}


class gromacs_download(rfm.RunOnlyRegressionTest):
    descr = 'Fetch GROMACS source code'
    maintainers = ['pkanduri', 'sebkelle', 'romeli', 'SSA']
    version = variable(str, value='2024.3')
    sourcesdir = None
    executable = 'wget'
    executable_opts = [
        '--quiet',
        'https://jfrog.svc.cscs.ch/artifactory/cscs-reframe-tests/gromacs/'
        f'v{version}.tar.gz',
        # https://github.com/gromacs/gromacs/archive/refs/tags/v2024.3.tar.gz
    ]
    local = True

    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)


@rfm.simple_test
class gromacs_build_test(rfm.CompileOnlyRegressionTest):
    """
    Test GROMACS build from source using the develop view
    """
    descr = 'GROMACS Build Test'
    valid_prog_environs = ['+gromacs-dev']
    valid_systems = ['+uenv']
    build_system = 'CMake'
    maintainers = ['SSA']
    sourcesdir = None
    gromacs_sources = fixture(gromacs_download, scope='session')
    build_locally = False
    tags = {'uenv', 'maintenance'}

    @run_before('compile')
    def prepare_build(self):
        self.uarch = uarch(self.current_partition)
        self.skip_if_no_procinfo()
        cpu = self.current_partition.processor
        self.build_system.max_concurrency = cpu.info['num_cpus_per_socket']
        tarsource = os.path.join(
            self.gromacs_sources.stagedir,
            f'v{self.gromacs_sources.version}.tar.gz'
        )
        self.prebuild_cmds = [f'tar --strip-components=1 -xzf {tarsource}']
        self.build_system.config_opts = [
            '-DREGRESSIONTEST_DOWNLOAD=OFF',
            '-DGMX_MPI=ON',
            '-DGMX_BUILD_OWN_FFTW=OFF',
            '-DGMX_HWLOC=ON',
            '-DGMX_INSTALL_NBLIB_API=ON',
        ]
        if self.uarch == 'gh200':
            self.build_system.config_opts += [
                '-DGMX_SIMD=ARM_NEON_ASIMD',
                '-DGMX_GPU=CUDA'
            ]
        elif self.uarch == 'zen2':
            self.build_system.config_opts += [
                '-DGMX_SIMD=AUTO',
            ]

    @sanity_function
    def validate_test(self):
        self.gromacs_executable = os.path.join('bin', 'gmx_mpi')
        return os.path.isfile(self.gromacs_executable)


@rfm.simple_test
class gromacs_run_test(rfm.RunOnlyRegressionTest):
    executable = 'gmx_mpi mdrun -s stmv2.tpr'
    executable_opts = [
        '-dlb no', '-npme 1', '-pin off', '-v', '-noconfout', '-nstlist 300'
    ]
    maintainers = ['SSA']
    valid_systems = ['*']
    test_name = variable(str, value='STMV')
    valid_prog_environs = ['+gromacs']
    tags = {'uenv', 'production', 'maintenance'}

    @run_before('run')
    def prepare_run(self):
        self.uarch = uarch(self.current_partition)
        config = slurm_config[self.test_name][self.uarch]
        self.job.options = [
            f'--nodes={config["nodes"]}',
        ]
        self.num_tasks_per_node = config['ntasks-per-node']
        self.num_tasks = config['nodes'] * self.num_tasks_per_node
        self.num_cpus_per_task = config['cpus-per-task']
        self.time_limit = config['walltime']
        # environment variables
        self.env_vars['OMP_NUM_THREADS'] = str(self.num_cpus_per_task)
        self.env_vars['FI_CXI_RX_MATCH_MODE'] = 'software'

        self.executable_opts.append(f'-ntomp {self.num_cpus_per_task}')

        if self.uarch == 'gh200':
            self.executable = './mps-wrapper.sh -- ' + self.executable

            self.executable_opts += [
                '-pme gpu', '-nb gpu', '-update gpu', '-nsteps 10000'
            ]

            self.env_vars['MPICH_GPU_SUPPORT_ENABLED'] = '1'
            self.env_vars['GMX_GPU_DD_COMMS'] = 'true'
            self.env_vars['GMX_GPU_PME_PP_COMMS'] = 'true'
            self.env_vars['GMX_ENABLE_DIRECT_GPU_COMM'] = '1'
            self.env_vars['GMX_FORCE_GPU_AWARE_MPI'] = '1'
        else:
            self.executable_opts += ['-nsteps 1000']

        # set reference
        if self.uarch is not None and \
           self.uarch in gromacs_references[self.test_name]:
            self.reference = {
                self.current_partition.fullname:
                    gromacs_references[self.test_name][self.uarch]
            }

        # set input files
        if self.test_name == 'STMV':
            jfrog = 'https://jfrog.svc.cscs.ch/artifactory/cscs-reframe-tests/'
            self.prerun_cmds = [f'wget {jfrog}/gromacs/STMV/stmv2.tpr --quiet']

    @run_after('setup')
    def postproc_run(self):
        """
        Extract Total Energy from the binary .edr file and write it to a
        readable .xvg file and then write it to stdout
        """
        self.postrun_cmds = [
            'echo -e "12\\n" |'
            'gmx_mpi energy -f ener.edr -o ener.xvg',
            'cat ener.xvg'
        ]

    @sanity_function
    def validate_job(self):
        regex1 = r'^Total Energy\s+\S+\s+'
        regex2 = r'^Performance:\s+\S+\s+'
        self.sanity_patterns = sn.all([
            sn.assert_found(regex1, self.stdout, msg='regex1 failed'),
            sn.assert_found(regex2, self.stderr, msg='regex2 failed'),
        ])
        return self.sanity_patterns

    @performance_function('ns/day')
    def perf(self):
        regex = r'^Performance:\s+(?P<ns_day>\S+)\s+'
        return sn.extractsingle(regex, self.stderr, 'ns_day', float)

    @performance_function('kJ/mol')
    def totalenergy(self):
        regex = r'^Total Energy\s+(?P<total_energy>\S+)\s+'
        return sn.extractsingle(regex, self.stdout, 'total_energy', float)
