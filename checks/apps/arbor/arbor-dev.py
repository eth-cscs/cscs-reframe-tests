# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps

class arbor_download(rfm.RunOnlyRegressionTest):
    version = variable(str, value='0.9.0')
    descr = 'Fetch Arbor sources code'
    executable = 'wget'
    executable_opts = [
        f'https://github.com/arbor-sim/arbor/archive/refs/tags/v{version}.tar.gz'
    ]
    local = True

    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)

class arbor_build(rfm.CompileOnlyRegressionTest):
    descr = 'Build Arbor'
    valid_systems = ['*']
    valid_prog_environs = ['+arbor']
    build_system = 'CMake'
    maintainers = ['bcumming']
    arbor_sources = fixture(arbor_download, scope='session')

    @run_before('compile')
    def prepare_build(self):
        self.build_system.builddir = os.path.join(self.stagedir, 'build')
        tarball = f'v{self.arbor_sources.version}.tar.gz'

        tarsource = os.path.join(self.arbor_sources.stagedir, tarball)
        self.prebuild_cmds = [
            f'tar --strip-components=1 -xzf{tarsource} -C {self.stagedir}'
        ]

        self.build_system.config_opts = [
            '-DARB_WITH_MPI=on',
            '-DARB_WITH_PYTHON=on',
        ]
        ##if self.target == 'gh200':
        self.build_system.config_opts += [
            '-DCMAKE_CUDA_ARCHITECTURES=90',
            '-DARB_GPU=cuda',
        ]

        self.build_system.max_concurrency = 128

        self.build_system.make_opts = ['pyarb', 'examples', 'unit']


@rfm.simple_test
class arbor_unit(rfm.RunOnlyRegressionTest):
    descr = 'Run the arbor unit tests'
    valid_systems = ['*']
    valid_prog_environs = ['+arbor']
    maintainers = ['bcumming']
    arbor_build = fixture(arbor_build, scope='environment')

    @run_before('run')
    def prepare_run(self):
        self.executable = os.path.join(self.arbor_build.stagedir, 'build', 'bin', 'unit')
        self.executable_opts = []

    @sanity_function
    def validate_test(self):
        return sn.assert_found(r'PASSED', self.stdout)

@rfm.simple_test
class arbor_busyring(rfm.RunOnlyRegressionTest):
    descr = 'Run the arbor unit tests'
    valid_systems = ['*']
    valid_prog_environs = ['+arbor']
    maintainers = ['bcumming']
    arbor_build = fixture(arbor_build, scope='environment')

    @run_before('run')
    def prepare_run(self):
        self.executable = os.path.join(self.arbor_build.stagedir, 'build', 'bin', 'unit')
        self.executable_opts = []

    @sanity_function
    def validate_test(self):
        return sn.assert_found(r'PASSED', self.stdout)

#@rfm.simple_test
#class arbor_build_check(rfm.CompileOnlyRegressionTest):
    #valid_systems = ['*']
    #valid_prog_environs = ['*']
    #valid_prog_environs = ['arbor']
    #sourcesdir = 'https://github.com/arbor-sim/arbor/archive/refs/tags/v0.9.0.tar.gz'
    #build_system = 'CMake'
    #maintainers = ['bcumming']
#
    #@run_before('compile')
    #def prepare_build(self):
        #self.build_system.config_opts = [
            #'-DCMAKE_CXX_COMPILER=mpicxx',
            #'-DCMAKE_C_COMPILER=mpicc',
            #'-DARB_WITH_MPI=on',
            #'-DARB_WITH_PYTHON=on',
        #]
        ##if self.target == 'gh200':
        #self.build_system.config_opts += [
            #'-DCMAKE_CUDA_ARCHITECTURES=90',
            #'-DARB_GPU=cuda',
        #]
#
        #self.build_system.flags_from_environ = False
        #self.build_system.make_opts = ['examples', 'tests', 'pyarb']
        #self.build_system.max_concurrency = 64
#
    #@sanity_function
    #def validate_build(self):
        ## If compilation fails, the test would fail in any case
        #return True

#@rfm.simple_test
#class stream_test(rfm.RunOnlyRegressionTest):
#    valid_systems = ['*']
#    valid_prog_environs = ['*']
#    executable = 'stream.x'
#
#    @sanity_function
#    def validate(self):
#        return sn.assert_found(r'Solution Validates', self.stdout)
#
#    @performance_function('MB/s')
#    def copy_bw(self):
#        return sn.extractsingle(r'Copy:\s+(\S+)', self.stdout, 1, float)
#
#    @performance_function('MB/s')
#    def triad_bw(self):
#        return sn.extractsingle(r'Triad:\s+(\S+)', self.stdout, 1, float)

