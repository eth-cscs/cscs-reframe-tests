# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps
import uenv

arbor_references = {
    'gh200': {
        'serial': {
            'small': {
                'time_run':  (9.25, -0.1, 0.1, 's'),
            },
            'medium': {
                'time_run':  (35.0, -0.05, 0.05, 's'),
            }
        },
        'distributed': {
            'medium': {
                'time_run':  (9.2, -0.05, 0.05, 's'),
            }
        },
    }
}


class arbor_download(rfm.RunOnlyRegressionTest):
    version = variable(str, value='0.9.0')
    descr = 'Fetch Arbor sources code'
    sourcesdir = None
    executable = 'wget'
    executable_opts = [
        '--quiet',
        f'https://github.com/arbor-sim/arbor/archive/refs/tags/v{version}.tar.gz'
    ]
    local = True

    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)


class arbor_build(rfm.CompileOnlyRegressionTest):
    descr = 'Build Arbor'
    valid_systems = ['*']
    valid_prog_environs = ['+arbor-dev']
    build_system = 'CMake'
    sourcesdir = None
    maintainers = ['bcumming', 'SSA']
    arbor_sources = fixture(arbor_download, scope='session')
    # NOTE: required so that the build stage is performed on
    # a compute node using an sbatch job.
    # This will force the uenv and view to be loaded using
    # "#SBATCH --uenv=" etc
    build_locally = False

    @run_before('compile')
    def prepare_build(self):
        self.uarch = uenv.uarch(self.current_partition)
        self.build_system.builddir = os.path.join(self.stagedir, 'build')
        tarball = f'v{self.arbor_sources.version}.tar.gz'

        tarsource = os.path.join(self.arbor_sources.stagedir, tarball)
        self.prebuild_cmds = [
            f'tar --strip-components=1 -xzf {tarsource} -C {self.stagedir}'
        ]

        self.build_system.config_opts = [
            '-DARB_WITH_MPI=on',
            '-DARB_WITH_PYTHON=on',
        ]
        # set architecture-specific flags
        if self.uarch == 'gh200':
            self.build_system.config_opts += [
                '-DCMAKE_CUDA_ARCHITECTURES=90',
                '-DARB_GPU=cuda',
            ]
        elif self.uarch == 'a100':
            self.build_system.config_opts += [
                '-DCMAKE_CUDA_ARCHITECTURES=80',
                '-DARB_GPU=cuda',
                '-DARB_VECTORIZE=on'
            ]
        elif self.uarch == 'zen2':
            self.build_system.config_opts += ['-DARB_VECTORIZE=on']

        self.build_system.max_concurrency = 64

        self.build_system.make_opts = ['pyarb', 'examples', 'unit']


@rfm.simple_test
class arbor_unit(rfm.RunOnlyRegressionTest):
    descr = 'Run the arbor unit tests'
    valid_systems = ['*']
    valid_prog_environs = ['+arbor-dev']
    time_limit = '5m'
    maintainers = ['bcumming']
    arbor_build = fixture(arbor_build, scope='environment')

    @run_before('run')
    def prepare_run(self):
        self.executable = os.path.join(self.arbor_build.stagedir,
                                       'build', 'bin', 'unit')
        self.executable_opts = []

    @sanity_function
    def validate_test(self):
        return sn.assert_found(r'PASSED', self.stdout)


@rfm.simple_test
class arbor_busyring(rfm.RunOnlyRegressionTest):
    """
    run the arbor busyring example in small and medium model configurations
    """
    descr = 'arbor busyring model'
    valid_systems = ['*']
    valid_prog_environs = ['+arbor-dev']
    maintainers = ['bcumming']
    model_size = parameter(['small', 'medium'])

    arbor_build = fixture(arbor_build, scope='environment')

    @run_before('run')
    def prepare_run(self):
        self.executable = os.path.join(self.arbor_build.stagedir,
                                       'build', 'bin', 'busyring')
        self.executable_opts = [f'busyring-input-{self.model_size}.json']

        # Instead of explicitly listing performance targets for all possible
        # system:partition combinations, set the reference targets to those
        # for the uarch of the current partition.
        # * self.uarch is one of the alps arch: gh200, zen2, a100, ... or None
        # * self.current_partition.fullname is the vcluster:partition string,
        #   for example "daint:normal" or "todi:debug".
        self.uarch = uenv.uarch(self.current_partition)
        if (self.uarch is not None) and (self.uarch in arbor_references):
            self.reference = {
                self.current_partition.fullname:
                    arbor_references[self.uarch]['serial'][self.model_size]
            }

    @sanity_function
    def validate_test(self):
        # if the meters are printed, the simulation ran to completion
        return sn.assert_found(r'meter-total', self.stdout)

    @performance_function('s')
    def time_run(self):
        return sn.extractsingle(r'model-run\s+(\S+)', self.stdout, 1, float)


slurm_config = {
    'gh200': {"ranks": 4, "cores": 64, "gpu": True},
    'zen2':  {"ranks": 2, "cores": 64, "gpu": False},
}


@rfm.simple_test
class arbor_busyring_mpi(arbor_busyring):
    """
    adapt the busyring test to check paralle MPI execution
    """

    descr = 'arbor busyring model MPI on a single node'
    model_size = parameter(['medium'])

    @run_before('run')
    def prepare_run(self):
        self.uarch = uenv.uarch(self.current_partition)
        self.executable = os.path.join(self.arbor_build.stagedir,
                                       'build', 'bin', 'busyring')
        self.executable_opts = [f'busyring-input-{self.model_size}.json']

        self.num_tasks = slurm_config[self.uarch]["ranks"]
        self.num_cpus_per_task = slurm_config[self.uarch]["cores"]
        if slurm_config[self.uarch]["gpu"]:
            self.job.options = ['--gpus-per-task=1']

        self.uarch = uenv.uarch(self.current_partition)
        if (self.uarch is not None) and (self.uarch in arbor_references):
            self.reference = {
                self.current_partition.fullname:
                    arbor_references[self.uarch]['distributed'][self.model_size]
            }
