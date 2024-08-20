# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn


class arbor_download_check(rfm.CompileOnlyRegressionTest):
    descr = 'Arbor download sources'
    valid_prog_environs = ['builtin']
    executable = 'git'
    executable_opts = ['--recursive', '-b', 'v0.9.0', 'https://github.com/arbor-sim/arbor.git']
    postrun_cmds = []

    @sanity_function
    def validate_download(self):
        return sn.assert_true(os.path.exists('arbor'))


class arbor_build_check(rfm.CompileOnlyRegressionTest):
    valid_systems = ['*']
    valid_prog_environs = ['arbor-dev']
    sourcesdir = None
    build_system = 'CMake'
    maintainers = ['bcumming']

    @run_before('compile')
    def prepare_build(self):
        self.build_system.config_opts = [
            '-DCMAKE_CXX_COMPILER=mpicxx',
            '-DCMAKE_C_COMPILER=mpicc',
            '-DARB_WITH_MPI=on',
            '-DARB_WITH_PYTHON=on',
        ]
        if self.target == 'gh200':
            self.build_system.config_opts += [
                '-DCMAKE_CUDA_ARCHITECTURES=90',
                '-DARB_GPU=cuda',
            ]
        elif self.target == 'a100':
            self.build_system.config_opts += [
                '-DCMAKE_CUDA_ARCHITECTURES=80',
                '-DARB_GPU=cuda',
            ]

        self.build_system.flags_from_environ = False
        self.build_system.make_opts = ['examples', 'tests', 'pyarb']
        self.build_system.max_concurrency = 64

    @sanity_function
    def validate_build(self):
        # If compilation fails, the test would fail in any case
        return True


