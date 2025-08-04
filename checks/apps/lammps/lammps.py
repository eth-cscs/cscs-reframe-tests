# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
import os

import reframe as rfm
import reframe.utility.sanity as sn
from uenv import uarch

lammps_references = {
    'lj_gpu': {
        'gh200': {'time_run': (45, None, 0.05, 's')},
    },
    'lj_kokkos': {
        'gh200': {'time_run': (5, None, 0.05, 's')},
        'zen2': {'time_run': (26, None, 0.05, 's')}
    },
}

slurm_config = {

    "lj_gpu": {
        "gh200": {
            "nodes": 2,
            "ntasks-per-node": 4,
            "gpus-per-node": 4,
            "walltime": "10m",
            "gpu": True,
        },
    },

    "lj_kokkos": {
        "gh200": {
            "nodes": 2,
            "ntasks-per-node": 4,
            "gpus-per-node": 4,
            "walltime": "10m",
            "gpu": True,
        },
        "zen2": {
            "nodes": 4,
            "ntasks-per-node": 32,
            "cpus-per-task": 4,
            "walltime": "10m",
            "gpu": False,
        },
    },
}


class lammps_download(rfm.RunOnlyRegressionTest):
    descr = 'Download LAMMPS source code'
    version = variable(str, value='20230802.3')
    sourcesdir = None
    executable = 'wget'
    executable_opts = [
        '--quiet',
        'https://jfrog.svc.cscs.ch/artifactory/cscs-reframe-tests/lammps/'
        'LAMMPS_20230802.3_Source.tar.gz',
    ]
    local = True

    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)


@rfm.simple_test
class lammps_build_test(rfm.CompileOnlyRegressionTest):
    '''
    Test LAMMPS build from source using the develop-kokkos view
    '''
    descr = 'LAMMPS Build Test'
    valid_prog_environs = ['+lammps-kokkos-dev']
    valid_systems = ['+gpu']
    maintainers = ['SSA']
    sourcesdir = None
    lammps_sources = fixture(lammps_download, scope='environment')
    build_system = 'CMake'
    tags = {'uenv', 'production'}
    build_locally = False

    @run_before('compile')
    def prepare_build(self):
        self.build_system.builddir = 'build'
        self.build_system.config_opts = [
            f'-C ../lammps-2Aug2023/cmake/presets/kokkos-cuda.cmake',
            '-DKokkos_ENABLE_IMPL_CUDA_MALLOC_ASYNC=OFF',
            '-DKokkos_ARCH_NATIVE=ON',
            '-DKokkos_ARCH_PASCAL60=OFF',
            '-DKokkos_ARCH_HOPPER90=ON',
            '../lammps-2Aug2023/cmake/',
        ]
        self.build_system.max_concurrency = 64
        tarsource = os.path.join(
            self.lammps_sources.stagedir,
            f'LAMMPS_{self.lammps_sources.version}_Source.tar.gz',
        )
        # Extract source code
        self.prebuild_cmds = [f'tar zxf {tarsource}']

    @sanity_function
    def validate_test(self):
        self.lammps_executable = os.path.join(self.stagedir, "build", "lmp")
        return os.path.isfile(self.lammps_executable)


@rfm.simple_test
class lammps_gpu_test(rfm.RunOnlyRegressionTest):
    """
    Test LAMMPS run using the run-gpu:gpu view
    Untested views:
        build-gpu: develop-gpu
        build-kokkos: develop-kokkos
        run-kokkos: kokkos
    """
    executable = 'lmp'
    valid_prog_environs = ['+lammps-gpu-prod']
    valid_systems = ['+uenv']
    maintainers = ['SSA']
    test_name = variable(str, value='lj_gpu')
    energy_reference = -4.620456
    tags = {'uenv', 'production'}

    @run_before('run')
    def prepare_run(self):
        self.uarch = uarch(self.current_partition)
        config = slurm_config[self.test_name][self.uarch]
        self.job.options = [f'--nodes={config["nodes"]}']
        self.num_tasks_per_node = config['ntasks-per-node']
        self.num_tasks = config['nodes'] * self.num_tasks_per_node
        self.ntasks_per_core = 1
        self.time_limit = config['walltime']
        self.executable_opts = [f'-i {self.test_name}.in']

        if self.uarch == 'gh200':
            self.env_vars['MPICH_GPU_SUPPORT_ENABLED'] = '1'
            self.job.launcher.options += [
                f'--gpus-per-node={config["gpus-per-node"]}'
            ]
            self.executable_opts = [
                f'-sf gpu -pk gpu {config["gpus-per-node"]} -i {self.test_name}.in']
        else:
            self.executable_opts = [f'-i {self.test_name}.in']

    @run_before('run')
    def prepare_reference(self):
        self.uarch = uarch(self.current_partition)
        if self.uarch is not None and \
           self.uarch in lammps_references[self.test_name]:
            self.reference = {
                self.current_partition.fullname:
                    lammps_references[self.test_name][self.uarch]
            }

    @sanity_function
    def assert_energy_diff(self):
        successful_termination = \
            sn.assert_found(r'Total wall time', self.stdout)

        energy = sn.extractsingle(
            r'^\s*1000(\s+\S+){5}\s+(?P<energy>-?\d+\.\d+)\s+',
            self.stdout, 'energy', float)
        energy_diff = sn.abs(energy - self.energy_reference)
        correct_energy = sn.assert_lt(energy_diff, 1e-4)

        return sn.all([successful_termination, correct_energy])

    # INFO: The name of this function needs to match with the reference dict!
    @performance_function('s')
    def time_run(self):
        regex = r'Total wall time: (?P<hh>\S+):(?P<mm>\S+):(?P<ss>\S+)'
        hh = sn.extractsingle(regex, self.stdout, 'hh', int)
        mm = sn.extractsingle(regex, self.stdout, 'mm', int)
        ss = sn.extractsingle(regex, self.stdout, 'ss', int)
        return (hh*3600 + mm*60 + ss)


@rfm.simple_test
class lammps_kokkos_test(rfm.RunOnlyRegressionTest):
    """
    Test LAMMPS run using the run-gpu:gpu view
    Untested views:
        build-gpu: develop-gpu
        build-kokkos: develop-kokkos
        run-gpu: gpu
    """
    executable = 'lmp'
    valid_prog_environs = ['+lammps-kokkos-prod']
    valid_systems = ['+uenv']
    maintainers = ['SSA']
    test_name = variable(str, value='lj_kokkos')
    energy_reference = -4.620456
    tags = {'uenv', 'production'}

    @run_before('run')
    def prepare_run(self):
        self.uarch = uarch(self.current_partition)
        config = slurm_config[self.test_name][self.uarch]
        self.job.options = [f'--nodes={config["nodes"]}']
        self.num_tasks_per_node = config['ntasks-per-node']
        self.num_tasks = config['nodes'] * self.num_tasks_per_node
        self.ntasks_per_core = 1
        self.time_limit = config['walltime']
        self.executable_opts = [f'-i {self.test_name}.in']

        if self.uarch == 'gh200':
            self.env_vars['MPICH_GPU_SUPPORT_ENABLED'] = '1'
            self.job.launcher.options += [
                f'--gpus-per-node={config["gpus-per-node"]}',
                f'--gpus-per-task=1'
            ]
            self.executable_opts = [
                f'-k on g 1 -sf kk -pk kokkos gpu/aware on -i {self.test_name}.in']
        else:
            self.job.launcher.options += ["--cpu-bind=cores"]
            self.env_vars['OMP_NUM_THREADS'] = config["cpus-per-task"]
            self.env_vars['OMP_PROC_BIND'] = 'spread'
            self.env_vars['OMP_PLACES'] = 'threads'
            self.executable_opts = [
                f'-k on t {config["cpus-per-task"]} -sf kk -i {self.test_name}.in']

    @run_before('run')
    def prepare_reference(self):
        self.uarch = uarch(self.current_partition)
        if self.uarch is not None and \
           self.uarch in lammps_references[self.test_name]:
            self.reference = {
                self.current_partition.fullname:
                    lammps_references[self.test_name][self.uarch]
            }

    @sanity_function
    def assert_energy_diff(self):
        successful_termination = \
            sn.assert_found(r'Total wall time', self.stdout)

        energy = sn.extractsingle(
            r'^\s*1000(\s+\S+){5}\s+(?P<energy>-?\d+\.\d+)\s+',
            self.stdout, 'energy', float)
        energy_diff = sn.abs(energy - self.energy_reference)
        correct_energy = sn.assert_lt(energy_diff, 1e-4)

        return sn.all([successful_termination, correct_energy])

    # INFO: The name of this function needs to match with the reference dict!
    @performance_function('s')
    def time_run(self):
        regex = r'Total wall time: (?P<hh>\S+):(?P<mm>\S+):(?P<ss>\S+)'
        hh = sn.extractsingle(regex, self.stdout, 'hh', int)
        mm = sn.extractsingle(regex, self.stdout, 'mm', int)
        ss = sn.extractsingle(regex, self.stdout, 'ss', int)
        return (hh*3600 + mm*60 + ss)
