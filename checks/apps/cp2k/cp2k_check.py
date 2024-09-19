# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn
import uenv
import os


class cp2k_download(rfm.RunOnlyRegressionTest):
    """
    Download CP2K source code.
    """
    version = variable(str, value="2024.3")
    descr = "Fetch CP2K source code"
    sourcedir = None
    executable = "wget"
    executable_opts = [
        f"https://github.com/cp2k/cp2k/archive/refs/tags/v{version}.tar.gz",
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
    descr = "CP2K Build Test"
    valid_systems = ['*']
    valid_prog_environs = ['+cp2k-dev']
    build_system = "CMake"
    sourcesdir = None
    maintainers = ["RMeli"]
    cp2k_sources = fixture(cp2k_download, scope="session") # TODO: Change scope, other tests don't need source code
    build_locally = False

    @run_before("compile")
    def prepare_build(self):
        self.uarch = uenv.uarch(self.current_partition)
        self.build_system.builddir = os.path.join(self.stagedir, "build")
        self.build_system.max_concurrency = 64
        
        tarsource = os.path.join(self.cp2k_sources.stagedir, f"v{self.cp2k_sources.version}.tar.gz")

        # Extract source code
        self.prebuild_cmds = [
            f"tar --strip-components=1 -xzf {tarsource} -C {self.stagedir}"
        ] 

        # TODO: Use Ninja generator
        self.build_system.config_opts = [
            "-DCP2K_ENABLE_REGTESTS=ON", # Puts executables under exe/local_cuda/
            "-DCP2K_USE_LIBXC=ON",
            "-DCP2K_USE_LIBINT2=ON",
            "-DCP2K_USE_SPGLIB=ON",
            "-DCP2K_USE_ELPA=ON",
            "-DCP2K_USE_SPLA=ON",
            "-DCP2K_USE_SIRIUS=ON",
            "-DCP2K_USE_COSMA=ON",
            "-DCP2K_USE_PLUMED=ON",
        ]

        if self.uarch == "gh200":
            self.build_system.config_opts += [
                "-DCP2K_USE_ACCEL=CUDA",
                "-DCP2K_WITH_GPU=H100",
            ]

    @sanity_function
    def validate_test(self):
        # INFO: Executables are in exe/local_cuda because -DCP2K_ENABLE_REGTEST=ON
        # INFO: With -DCP2K_ENABLE_REGTEST=OFF, executables are in build/bin/ as expected
        executable = os.path.join(self.stagedir,"exe", "local_cuda", "cp2k.psmp")
        return os.path.isfile(executable)

# class Cp2kCheck(rfm.RunOnlyRegressionTest):
#     modules = ['CP2K']
#     executable = 'cp2k.psmp'
#     executable_opts = ['H2O-256.inp']
#     maintainers = ['LM']
#     tags = {'scs'}
#     strict_check = False
#     extra_resources = {
#         'switches': {
#             'num_switches': 1
#         }
#     }
#
#     @run_after('init')
#     def set_prgenv(self):
#         if self.current_system.name in ['eiger', 'pilatus']:
#             self.valid_prog_environs = ['cpeGNU']
#         else:
#             self.valid_prog_environs = ['builtin']
#
#     @sanity_function
#     def assert_energy_diff(self):
#         energy = sn.extractsingle(
#             r'\s+ENERGY\| Total FORCE_EVAL \( QS \) '
#             r'energy [\[\(]a\.u\.[\]\)]:\s+(?P<energy>\S+)',
#             self.stdout, 'energy', float, item=-1
#         )
#         energy_reference = -4404.2323
#         energy_diff = sn.abs(energy-energy_reference)
#         return sn.all([
#             sn.assert_found(r'PROGRAM STOPPED IN', self.stdout),
#             sn.assert_eq(sn.count(sn.extractall(
#                 r'(?i)(?P<step_count>STEP NUMBER)',
#                 self.stdout, 'step_count')), 10),
#             sn.assert_lt(energy_diff, 1e-4)
#         ])
#
#     @performance_function('s')
#     def time(self):
#         return sn.extractsingle(r'^ CP2K(\s+[\d\.]+){4}\s+(?P<perf>\S+)',
#                                 self.stdout, 'perf', float)
#
#
# @rfm.simple_test
# class Cp2kCpuCheck(Cp2kCheck):
#     scale = parameter(['small', 'large'])
#     valid_systems = ['daint:mc', 'eiger:mc', 'pilatus:mc']
#     refs_by_scale = {
#         'small': {
#             'dom:mc': {'time': (169.619, None, 0.10, 's')},
#             'daint:mc': {'time': (208.108, None, 0.10, 's')},
#             'eiger:mc': {'time': (76.116, None, 0.08, 's')},
#             'pilatus:mc': {'time': (70.568, None, 0.08, 's')}
#         },
#         'large': {
#             'daint:mc': {'time': (114.629, None, 0.10, 's')},
#             'eiger:mc': {'time': (54.381, None, 0.05, 's')},
#             'pilatus:mc': {'time': (49.916, None, 0.05, 's')}
#         }
#     }
#
#     @run_after('init')
#     def setup_by__scale(self):
#         self.descr = f'CP2K CPU check (version: {self.scale})'
#         self.tags |= {'maintenance', 'production'}
#         if self.scale == 'small':
#             self.valid_systems += ['dom:mc']
#             if self.current_system.name in ['daint', 'dom']:
#                 self.num_tasks = 216
#                 self.num_tasks_per_node = 36
#             elif self.current_system.name in ['eiger', 'pilatus']:
#                 self.num_tasks = 96
#                 self.num_tasks_per_node = 16
#                 self.num_cpus_per_task = 16
#                 self.num_tasks_per_core = 1
#                 self.use_multithreading = False
#                 self.env_vars = {
#                     'MPICH_OFI_STARTUP_CONNECT': 1,
#                     'OMP_NUM_THREADS': 8,
#                     'OMP_PLACES': 'cores',
#                     'OMP_PROC_BIND': 'close'
#                 }
#         else:
#             if self.current_system.name in ['daint', 'dom']:
#                 self.num_tasks = 576
#                 self.num_tasks_per_node = 36
#             elif self.current_system.name in ['eiger', 'pilatus']:
#                 self.num_tasks = 256
#                 self.num_tasks_per_node = 16
#                 self.num_cpus_per_task = 16
#                 self.num_tasks_per_core = 1
#                 self.use_multithreading = False
#                 self.env_vars = {
#                     'MPICH_OFI_STARTUP_CONNECT': 1,
#                     'OMP_NUM_THREADS': 8,
#                     'OMP_PLACES': 'cores',
#                     'OMP_PROC_BIND': 'close'
#                 }
#
#         self.reference = self.refs_by_scale[self.scale]
#
#     @run_before('run')
#     def set_task_distribution(self):
#         self.job.options = ['--distribution=block:block']
#
#     @run_before('run')
#     def set_cpu_binding(self):
#         self.job.launcher.options = ['--cpu-bind=cores']
#
#
# @rfm.simple_test
# class Cp2kGpuCheck(Cp2kCheck):
#     scale = parameter(['small', 'large'])
#     valid_systems = ['daint:gpu']
#     num_gpus_per_node = 1
#     num_tasks_per_node = 6
#     num_cpus_per_task = 2
#     env_vars = {
#         'CRAY_CUDA_MPS': '1',
#         'OMP_NUM_THREADS': str(num_cpus_per_task)
#     }
#     refs_by_scale = {
#         'small': {
#             'dom:gpu': {'time': (176.153, None, 0.10, 's')},
#             'daint:gpu': {'time': (179.683, None, 0.10, 's')}
#         },
#         'large': {
#             'daint:gpu': {'time': (140.498, None, 0.10, 's')}
#         }
#     }
#
#     @run_after('init')
#     def setup_by_scale(self):
#         self.descr = f'CP2K GPU check (version: {self.scale})'
#         if self.scale == 'small':
#             self.valid_systems += ['dom:gpu']
#             self.num_tasks = 36
#         else:
#             self.num_tasks = 96
#
#         self.reference = self.refs_by_scale[self.scale]
#         self.tags |= {'maintenance', 'production'}
