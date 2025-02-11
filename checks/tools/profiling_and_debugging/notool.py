# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class JacobiNoToolHybrid(rfm.RegressionTest):
    lang = parameter(['C++', 'F90'])
    time_limit = '10m'
    valid_systems = ['daint:gpu', 'daint:mc', 'dom:gpu', 'dom:mc',
                     'eiger:mc', 'pilatus:mc']
    valid_prog_environs = ['PrgEnv-gnu', 'PrgEnv-cray']
    build_system = 'Make'
    executable = './jacobi'
    num_tasks = 3
    num_tasks_per_node = 3
    num_cpus_per_task = 4
    num_tasks_per_core = 1
    use_multithreading = False
    num_iterations = variable(int, value=100)
    maintainers = ['JG', 'MKr']
    tags = {'production'}

    @run_after('init')
    def set_descr_name(self):
        self.descr = f'Jacobi (without tool) {self.lang} check'

    # keeping as a reminder:
    # @run_after('init')
    # def remove_buggy_prgenv(self):
    #     # skipping to avoid "Fatal error in PMPI_Init_thread"
    #     self.valid_prog_environs.remove('PrgEnv-nvidia')

    @run_before('compile')
    def set_sources_dir(self):
        self.sourcesdir = os.path.join('src', self.lang)

    @run_before('compile')
    def restrict_f90_concurrency(self):
        # NOTE: Restrict concurrency to allow creation of Fortran modules
        if self.lang == 'F90':
            self.build_system.max_concurrency = 1

    @run_before('compile')
    def set_env_variables(self):
        self.env_vars = {
            'CRAYPE_LINK_TYPE': 'dynamic',
            'ITERATIONS': self.num_iterations,
            'OMP_NUM_THREADS': self.num_cpus_per_task,
            'OMP_PROC_BIND': 'true',
        }

    @run_before('compile')
    def set_flags(self):
        self.prebuild_cmds += ['module list']
        self.prgenv_flags = {
            'PrgEnv-aocc': ['-O2', '-g', '-fopenmp'],
            'PrgEnv-cray': ['-O2', '-g',
                            '-homp' if self.lang == 'F90' else '-fopenmp'],
            'PrgEnv-gnu': ['-O2', '-g', '-fopenmp',
                           '-fallow-argument-mismatch' if self.lang == 'F90'
                           else ''],
            'PrgEnv-intel': ['-O2', '-g', '-qopenmp'],
            'PrgEnv-pgi': ['-O2', '-g', '-mp'],
            'PrgEnv-nvidia': ['-O2', '-g', '-mp']
        }
        envname = self.current_environ.name
        # if generic, falls back to -g:
        prgenv_flags = self.prgenv_flags.get(envname, ['-g'])
        self.build_system.cflags = prgenv_flags
        self.build_system.cxxflags = prgenv_flags
        self.build_system.fflags = prgenv_flags

    @run_before('run')
    def set_prerun_cmds(self):
        if self.current_system.name in {'dom', 'daint', 'eiger', 'pilatus'}:
            # get general info about the environment:
            self.prerun_cmds += ['module list']
            self.prerun_cmds += [
                # cray/aocc compilers version are needed but others won't hurt:
                f'echo CRAY_CC_VERSION=$CRAY_CC_VERSION',
                f'echo CRAY_AOCC_VERSION=$CRAY_AOCC_VERSION',
                f'echo GNU_VERSION=$GNU_VERSION',
                f'echo PGI_VERSION=$PGI_VERSION',
                f'echo INTEL_VERSION=$INTEL_VERSION',
                f'echo INTEL_COMPILER_TYPE=$INTEL_COMPILER_TYPE',
            ]

    @sanity_function
    def assert_success(self):
        """
        - Read compiler version from environment variables:
            CRAY_CC_VERSION=17.0.0  -> 17
            CRAY_AOCC_VERSION=4.1.0 -> 4
            INTEL_VERSION=2023.2.0  -> 2023
            GNU_VERSION=12.3        -> 12

        - OpenMP support between compilers:
                     C++ - F90
            cce - 202011 - 201511
           aocc - 201811 - 201307
          intel - 201811 - 201611
            gnu - 201511 - 201511
             nv - 201307 - 201307
            pgi - 201307 - 201307

        - Another way to find OpenMP version:
            echo | CC -fopenmp -dM -E - | grep _OPENMP
        """
        # {{{ reference dict of openmp_versions:
        openmp_versions = {
            'PrgEnv-cray': {
                'C++': {10: 201511, 12: 201811, 13: 201811, 14: 201811,
                        17: 202011},
                'F90': {'*': 201511},
            },
            'PrgEnv-gnu': {
                'C++': {'*': 201511},
                'F90': {'*': 201511},
            },
            # 'PrgEnv-nvidia': {'C++': 201307, 'F90': 201307}
            # 'PrgEnv-pgi': {'C++': 201307, 'F90': 201307},
        }
        # }}}
        # {{{ current_environ compiler versions:
        envname = self.current_environ.name
        rptf = os.path.join(self.stagedir, sn.evaluate(self.stdout))
        compiler_version = {}
        if envname == 'PrgEnv-cray':
            compiler_version['PrgEnv-cray'] = \
                sn.extractsingle(r'CRAY_CC_VERSION=(\d+)\.\S+', rptf, 1, int)
        elif envname == 'PrgEnv-aocc':
            compiler_version['PrgEnv-aocc'] = \
                sn.extractsingle(r'CRAY_AOCC_VERSION=(\d+)\.\S+', rptf, 1, int)
        elif envname == 'PrgEnv-gnu':
            compiler_version['PrgEnv-gnu'] = \
                sn.extractsingle(r'GNU_VERSION=(\d+)\.\S+', rptf, 1, int)

        # }}}
        compiler_v = sn.evaluate(compiler_version[envname])
        #
        runtime_openmp_v = sn.extractsingle(r'OpenMP-\s*(\d+)', self.stdout, 1,
                                            int)
        try:
            return sn.all([
                sn.assert_found('SUCCESS', self.stdout),
                sn.assert_eq(runtime_openmp_v,
                             openmp_versions[envname][self.lang][compiler_v])
            ])
        except KeyError:
            return sn.all([
                sn.assert_found('SUCCESS', self.stdout),
                sn.assert_eq(runtime_openmp_v,
                             openmp_versions[envname][self.lang]['*'])
            ])

    @performance_function('s')
    def elapsed_time(self):
        return sn.extractsingle(
            r'Elapsed Time\s*:\s+(\S+)', self.stdout, 1, float)
