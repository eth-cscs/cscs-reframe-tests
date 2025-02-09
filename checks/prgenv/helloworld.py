# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib
import re
import sys
import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent / 'mixins'))
from extra_launcher_options import ExtraLauncherOptionsMixin


class HelloWorldBaseTest(rfm.RegressionTest, ExtraLauncherOptionsMixin):
    linking = parameter(['dynamic'])
    lang = parameter(['c', 'cpp', 'F90'])
    sourcesdir = 'src/hello'
    sourcepath = 'hello'
    executable = '$SLURM_SUBMIT_DIR/hello.exe'
    build_locally = False
    build_system = 'SingleSource'
    prebuild_cmds = ['_rfm_build_time="$(date +%s%N)"']
    postbuild_cmds = [
        '_rfm_build_time="$(($(date +%s%N)-_rfm_build_time))"',
        'echo "Compilations time (ns): $_rfm_build_time"'
    ]
    valid_systems = ['+remote', '+cpe_ce']
    reference = {
        '*': {
            'compilation_time': (60, None, 0.1, 's')
        }
    }
    exclusive_access = True

    # This is valid only for non-cray MPICH
    env_vars = {
        'MPIR_CVAR_ENABLE_GPU': 0,
    }
    tags = {'production', 'craype', 'uenv'}

    @run_after('init')
    def set_description(self):
        lang_names = {
            'c': 'C',
            'cpp': 'C++',
            'F90': 'Fortran 90'
        }
        self.descr = f'{lang_names[self.lang]} Hello, World'

    @run_before('compile')
    def prepare_build(self):
        self.env_vars['CRAYPE_LINK_TYPE'] = self.linking

    @sanity_function
    def assert_hello_world(self):
        result = sn.findall(r'Hello, World from thread\s*(\d+) out '
                            r'of\s*(\d+)\s*from rank\s*(\d+) out of'
                            r'\s*(\d+)', self.stdout)

        num_tasks = sn.getattr(self, 'num_tasks')
        num_cpus_per_task = sn.getattr(self, 'num_cpus_per_task')

        def tid(match):
            return int(match.group(1))

        def num_threads(match):
            return int(match.group(2))

        def rank(match):
            return int(match.group(3))

        def num_ranks(match):
            return int(match.group(4))

        return sn.all(sn.chain(
                [sn.assert_eq(sn.count(result), num_tasks*num_cpus_per_task)],
                sn.map(lambda x: sn.assert_lt(tid(x), num_threads(x)), result),
                sn.map(lambda x: sn.assert_lt(rank(x), num_ranks(x)), result),
                sn.map(
                    lambda x: sn.assert_lt(tid(x), num_cpus_per_task), result
                ),
                sn.map(
                    lambda x: sn.assert_eq(num_threads(x), num_cpus_per_task),
                    result
                ),
                sn.map(lambda x: sn.assert_lt(rank(x), num_tasks), result),
                sn.map(
                    lambda x: sn.assert_eq(num_ranks(x), num_tasks), result
                ),
            )
        )

    @performance_function('s')
    def compilation_time(self):
        return sn.extractsingle(r'Compilations time \(ns\): (\d+)',
                                self.build_stdout, 1, float) * 1.0e-9


@rfm.simple_test
class HelloWorldTestSerial(HelloWorldBaseTest):
    num_tasks = 1
    num_tasks_per_node = 1
    num_cpus_per_task = 1
    valid_prog_environs = ['+serial']

    @run_after('init')
    def update_description(self):
        self.descr += f' Serial {self.linking.capitalize()}'

    @run_before('compile')
    def update_sourcepath(self):
        self.sourcepath += f'.{self.lang}'


@rfm.simple_test
class HelloWorldTestOpenMP(HelloWorldBaseTest):
    num_tasks = 1
    num_tasks_per_node = 1
    num_cpus_per_task = 4
    valid_prog_environs = ['+openmp']

    @run_before('compile')
    def set_openmp_flags(self):
        self.build_system.cflags = self.current_environ.extras.get(
            'c_openmp_flags', ['-fopenmp'])
        self.build_system.cxxflags = self.build_system.cflags
        self.build_system.fflags = self.current_environ.extras.get(
            'f_openmp_flags', self.build_system.cflags )

    @run_after('init')
    def update_description(self):
        self.descr += f' OpenMP {self.linking.capitalize()}'

    @run_before('compile')
    def update_sourcepath(self):
        self.sourcepath += '.' + self.lang

    @run_before('run')
    def set_omp_env_variable(self):
        # On SLURM there is no need to set OMP_NUM_THREADS if one defines
        # num_cpus_per_task, but adding for completeness and portability
        self.env_vars['OMP_NUM_THREADS'] = self.num_cpus_per_task


@rfm.simple_test
class HelloWorldTestMPI(HelloWorldBaseTest):
    # for the MPI test the self.num_tasks_per_node should always be one. If
    # not, the test will fail for the total number of lines in the output
    # file is different then self.num_tasks * self.num_tasks_per_node
    num_tasks = 2
    num_tasks_per_node = 1
    num_cpus_per_task = 1
    valid_prog_environs = ['+mpi']

    @run_after('init')
    def update_description(self):
        self.descr += f' MPI {self.linking.capitalize()}'

    @run_before('compile')
    def update_sourcepath(self):
        self.sourcepath += '.' + self.lang
        self.build_system.cppflags += ['-DUSE_MPI']


@rfm.simple_test
class HelloWorldTestMPIOpenMP(HelloWorldBaseTest):
    num_tasks = 6
    num_tasks_per_node = 3
    num_cpus_per_task = 4
    valid_prog_environs = ['+mpi +openmp']

    @run_after('init')
    def update_description(self):
        self.descr += f' MPI + OpenMP {self.linking.capitalize()}'

    @run_before('compile')
    def set_openmp_flags(self):
        self.build_system.cflags = self.current_environ.extras.get(
            'c_openmp_flags', ['-fopenmp'])
        self.build_system.cxxflags = self.build_system.cflags
        self.build_system.fflags = self.current_environ.extras.get(
            'f_openmp_flags',  self.build_system.cflags)

    @run_before('compile')
    def update_sourcepath(self):
        self.sourcepath += '.' + self.lang
        self.build_system.cppflags += ['-DUSE_MPI']

    @run_before('run')
    def set_omp_env_variable(self):
        # On SLURM there is no need to set OMP_NUM_THREADS if one defines
        # num_cpus_per_task, but adding for completeness and portability
        self.env_vars['OMP_NUM_THREADS'] = self.num_cpus_per_task
