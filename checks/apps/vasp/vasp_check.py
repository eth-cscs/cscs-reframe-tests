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

vasp_references = {
        'CeO2': {'gh200': {
            1: {'elapsed_time': (71, None, 0.10, 's')},
            2: {'elapsed_time': (90, None, 0.10, 's')}
        }},
}


slurm_config = {
    'CeO2': {
        'gh200': {
            'ntasks-per-node': 4,
            'cpus-per-task': 16,
            'walltime': '0d0h5m0s',
        }
    },
}


@rfm.simple_test
class VaspCheck(rfm.RunOnlyRegressionTest):
    executable = 'vasp_std'
    maintainers = ['SSA']
    valid_systems = ['*']

    valid_prog_environs = ['+vasp']
    test_name = 'CeO2'
    force_reference = -.85026214E+03
    num_nodes = parameter([1, 2], loggable=True)
    tags = {'uenv', 'production'}

    @run_before('run')
    def prepare_run(self):
        self.uarch = uenv.uarch(self.current_partition)
        config = slurm_config[self.test_name][self.uarch]
        # sbatch options
        self.job.options = [
            f'--nodes={self.num_nodes}',
        ]
        self.num_tasks_per_node = config['ntasks-per-node']
        self.num_tasks = self.num_nodes * self.num_tasks_per_node
        self.num_cpus_per_task = config['cpus-per-task']
        self.num_tasks_per_socket = 1
        self.ntasks_per_core = 1
        self.time_limit = config['walltime']

        # srun options
        self.job.launcher.options = [
                '--cpu-bind=cores',
                # For multi-node, VASP gpu selection doesn't work properly.
                # CUDA_VISIBLE_DEVICES must be set to one GPU.
                '--gpus-per-task=1'
                ]

        # environment variables
        self.env_vars['OMP_NUM_THREADS'] = self.num_cpus_per_task

        if self.uarch == 'gh200':
            self.env_vars['MPICH_GPU_SUPPORT_ENABLED'] = '1'
            self.env_vars['NCCL_IGNORE_CPU_AFFINITY'] = '1'

        # set reference
        if self.uarch is not None and \
           self.uarch in vasp_references[self.test_name]:
            self.reference = {
                self.current_partition.fullname:
                    vasp_references[self.test_name][self.uarch][self.num_nodes]
            }

    @sanity_function
    def assert_reference(self):
        force = sn.extractsingle(r'1 F=\s+(?P<result>\S+)',
                                 self.stdout, 'result', float)
        return sn.assert_reference(force, self.force_reference, -1e-5, 1e-5)

    # INFO: The name of this function needs to match with the reference dict!
    @performance_function('s')
    def elapsed_time(self):
        return sn.extractsingle(r'Elapsed time \(sec\):'
                                r'\s+(?P<time>\S+)', 'OUTCAR',
                                'time', float)


@rfm.simple_test
class VaspBuildTest(rfm.CompileOnlyRegressionTest):
    '''
    Test VASP build from source.
    '''

    descr = 'VASP Build Test'
    version = variable(str, value='6.4.3')
    valid_prog_environs = ['+vasp-dev']
    valid_systems = ['*']
    build_system = 'Make'
    # only build std target
    maintainers = ['SSA']
    # run on node to load uenv
    build_locally = False
    tags = {'uenv'}

    @run_before('compile')
    def prepare_build(self):
        self.build_system.options = ['DEPS=1', 'std']

        self.skip_if_no_procinfo()
        cpu = self.current_partition.processor
        self.build_system.max_concurrency = cpu.info['num_cpus_per_socket']

        # Don't set FC variable, which breaks the makefile
        self.build_system.flags_from_environ = False

        self.uarch = uenv.uarch(self.current_partition)
        self.build_system.builddir = self.stagedir
        self.build_time_limit = '0d1h0m0s'

        makefile = f'makefile.include.{self.uarch}'
        makefile_path = os.path.join(self.prefix, self.sourcesdir, makefile)

        if not os.path.isfile(makefile_path):
            self.skip(f'No makefile for uarch {self.uarch}')

        vasp_download_cmd = (
            f'curl --retry 5 '
            f'-u ${{CSCS_REGISTRY_USERNAME}}:${{CSCS_REGISTRY_PASSWORD}} '
            '-X GET https://jfrog.svc.cscs.ch/artifactory'
            f'/uenv-sources/vasp/vasp-{self.version}.tar.bz2 '
            '-o vasp_src.tar.bz2'
        )

        # Download source and copy makfile matching uarch
        self.prebuild_cmds = [
            vasp_download_cmd,
            'tar -xf vasp_src.tar.bz2',
            # The vasp tar ball contains inconsistent directory names between
            # versions, so we find the directory name and change it to vasp_src
            'find . -maxdepth 1 -type d -name "vasp*" -exec mv {} vasp_src \\;',
            'cd vasp_src',
            f'cp ../{makefile} makefile.include'
        ]

        self.vasp_std_executable = os.path.join(
            self.stagedir, 'vasp_src', 'bin', 'vasp_std'
        )

    @sanity_function
    def validate_test(self):
        return os.path.isfile(self.vasp_std_executable)


@rfm.simple_test
class VaspBuildCheck(VaspCheck):
    valid_prog_environs = ['+vasp-dev']
    tags = {'uenv'}

    @run_after('init')
    def setup_dependency(self):
        self.depends_on('VaspBuildTest', udeps.fully)

    @run_after('setup')
    def setup_executable(self):
        parent = self.getdep('VaspBuildTest')
        self.executable = f'{parent.vasp_std_executable}'
        # VASP checks for CUDA aware MPI, which does not work with cray-mpich
        # The uenv version is patched, but for the source build we set this
        # as a workaround
        self.env_vars['PMPI_GPU_AWARE'] = '1'

