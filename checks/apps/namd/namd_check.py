# Copyright 2016-2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
from types import FunctionType

import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps
import uenv


class namd_download(rfm.RunOnlyRegressionTest):
    """
    Download NAMD source code.
    """

    version = variable(str, value="3.0")
    descr = "Fetch NAMD source code"
    sourcedir = None
    executable = "curl"
    executable_opts = [
        "-f",  # Try to have curl not return 0 on server error
        "-u",
        "${CSCS_REGISTRY_USERNAME}:${CSCS_REGISTRY_PASSWORD}",
        f"https://jfrog.svc.cscs.ch/artifactory/uenv-sources/namd/NAMD_{version}_Source.tar.gz",
        "--output",
        f"NAMD_{version}_Source.tar.gz",
    ]
    local = True

    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)


class AutotoolsCustom(rfm.core.buildsystems.Autotools):
    """
    Custom build system deriving from autotools.
    NAMD uses a ./config script instead of ./configure
    """

    def __init__(self):
        super().__init__()

    def emit_build_commands(self, environ):
        prepare_cmd = []
        if self.srcdir:
            prepare_cmd += [f"cd {self.srcdir}"]

        if self.builddir:
            prepare_cmd += [f"mkdir -p {self.builddir}", f"cd {self.builddir}"]

        if self.builddir:
            configure_cmd = [
                os.path.join(
                    os.path.relpath(self.configuredir, self.builddir), "config"
                )
            ]
        else:
            configure_cmd = [os.path.join(self.configuredir, "config")]

        if self.config_opts:
            configure_cmd += self.config_opts

        config_dir = "Linux-ARM64-g++.cuda"

        make_cmd = ["make -j"]
        if self.max_concurrency is not None:
            #make_cmd += [str(self.max_concurrency)]
            make_cmd += ["1"]

        if self.make_opts:
            make_cmd += self.make_opts

        return prepare_cmd + [
            " ".join(configure_cmd), # Run ./config
            f"cd {config_dir}", # cd to directory created by .config
            " ".join(make_cmd), # make
        ]


@rfm.simple_test
class NamdBuildTest(rfm.CompileOnlyRegressionTest):
    """
    Test NAMD build from source.
    """

    descr = "NAMD Build Test"
    valid_prog_environs = ["+namd-single-node-dev"]
    valid_systems = ["*"]
    build_system = AutotoolsCustom()
    sourcesdir = None
    maintainers = ["SSA"]
    namd_sources = fixture(namd_download, scope="session")
    build_locally = False
    tags = {"uenv"}

    @run_before("compile")
    def prepare_build(self):
        self.uarch = uenv.uarch(self.current_partition)
        self.build_system.builddir = self.stagedir
        self.skip_if_no_procinfo()
        cpu = self.current_partition.processor
        self.build_system.max_concurrency = cpu.info["num_cpus_per_socket"]

        tarsource = os.path.join(
            self.namd_sources.stagedir,
            f"NAMD_{self.namd_sources.version}_Source.tar.gz",
        )

        # Extract source code and compiler bundled Charm++
        self.prebuild_cmds = [
            f"tar --strip-components=1 -xzf {tarsource} -C {self.stagedir}",
            "tar -xf charm-8.0.0.tar",  # INFO: Depends on the NAMD version
            "cd charm-8.0.0",
            f"./build charm++ multicore-linux-arm8 gcc --with-production --enable-tracing -j {self.build_system.max_concurrency}",
            "cd ..",
            # Link against tcl8.6 (provided by the UENV)
            "sed -i 's/-ltcl8.5/-ltcl8.6/g' arch/Linux-ARM64.tcl"
        ]

        prefix = "/user-environment/env/develop-single-node"

        self.build_system.config_opts = [
            "Linux-ARM64-g++.cuda",
            "--charm-arch multicore-linux-arm8-gcc",
            f"--charm-base {self.stagedir}/charm-8.0.0",
            "--with-tcl",
            f"--tcl-prefix {prefix}",
            "--with-fftw",
            "--with-fftw3",
            f"--fftw-prefix {prefix}",
        ]

        if self.uarch == "gh200":
            self.build_system.config_opts += [
                "--with-single-node-cuda",
                "--with-cuda",
                "--cuda-gencode arch=compute_90,code=sm_90",
            ]

    @sanity_function
    def validate_test(self):
        self.namd_executable = os.path.join(
            self.stagedir, "Linux-ARM64-g++.cuda", "namd3"
        )
        return os.path.isfile(self.namd_executable)


#
#
# @rfm.simple_test
# class NamdCheck(rfm.RunOnlyRegressionTest):
#     scale = parameter(['small', 'large'])
#     arch = parameter(['gpu', 'cpu'])
#
#     valid_prog_environs = ['builtin', 'cpeGNU']
#     modules = ['NAMD']
#     executable = 'namd2'
#     use_multithreading = True
#     num_tasks_per_core = 2
#     maintainers = ['CB', 'LM']
#     tags = {'scs', 'external-resources'}
#     extra_resources = {
#         'switches': {
#             'num_switches': 1
#         }
#     }
#
#     @run_after('init')
#     def adapt_description(self):
#         self.descr = f'NAMD check ({self.arch})'
#         self.tags |= {'maintenance', 'production'}
#
#     @run_after('init')
#     def adapt_valid_systems(self):
#         if self.arch == 'gpu':
#             self.valid_systems = ['daint:gpu']
#             if self.scale == 'small':
#                 self.valid_systems += ['dom:gpu']
#         else:
#             self.valid_systems = ['daint:mc', 'eiger:mc', 'pilatus:mc']
#             if self.scale == 'small':
#                 self.valid_systems += ['dom:mc']
#
#     @run_after('init')
#     def adapt_valid_prog_environs(self):
#         if self.current_system.name in ['eiger', 'pilatus']:
#             self.valid_prog_environs.remove('builtin')
#
#     @run_after('init')
#     def setup_parallel_run(self):
#         if self.arch == 'gpu':
#             self.executable_opts = ['+idlepoll', '+ppn 23', 'stmv.namd']
#             self.num_cpus_per_task = 24
#             self.num_gpus_per_node = 1
#         else:
#             # On Eiger a no-smp NAMD version is the default
#             if self.current_system.name in ['eiger', 'pilatus']:
#                 self.executable_opts = ['+idlepoll', 'stmv.namd']
#             else:
#                 self.executable_opts = ['+idlepoll', '+ppn 71', 'stmv.namd']
#                 self.num_cpus_per_task = 72
#         if self.scale == 'small':
#             # On Eiger a no-smp NAMD version is the default
#             if self.current_system.name in ['eiger', 'pilatus']:
#                 self.num_tasks = 768
#                 self.num_tasks_per_node = 128
#             else:
#                 self.num_tasks = 6
#                 self.num_tasks_per_node = 1
#         else:
#             if self.current_system.name in ['eiger', 'pilatus']:
#                 self.num_tasks = 2048
#                 self.num_tasks_per_node = 128
#             else:
#                 self.num_tasks = 16
#                 self.num_tasks_per_node = 1
#
#     @run_before('compile')
#     def prepare_build(self):
#         # Reset sources dir relative to the SCS apps prefix
#         self.sourcesdir = os.path.join(self.current_system.resourcesdir,
#                                        'NAMD', 'prod')
#
#     @sanity_function
#     def validate_energy(self):
#         energy = sn.avg(sn.extractall(
#             r'ENERGY:([ \t]+\S+){10}[ \t]+(?P<energy>\S+)',
#             self.stdout, 'energy', float)
#         )
#         energy_reference = -2451359.5
#         energy_diff = sn.abs(energy - energy_reference)
#         return sn.all([
#             sn.assert_eq(sn.count(sn.extractall(
#                          r'TIMING: (?P<step_num>\S+)  CPU:',
#                          self.stdout, 'step_num')), 50),
#             sn.assert_lt(energy_diff, 2720)
#         ])
#
#     @run_before('performance')
#     def set_reference(self):
#         if self.arch == 'gpu':
#             if self.scale == 'small':
#                 self.reference = {
#                     'dom:gpu': {'days_ns': (0.149, None, 0.10, 'days/ns')},
#                     'daint:gpu': {'days_ns': (0.178, None, 0.10, 'days/ns')}
#                 }
#             else:
#                 self.reference = {
#                     'daint:gpu': {'days_ns': (0.072, None, 0.15, 'days/ns')}
#                 }
#         else:
#             if self.scale == 'small':
#                 self.reference = {
#                     'dom:mc': {'days_ns': (0.543, None, 0.10, 'days/ns')},
#                     'daint:mc': {'days_ns': (0.513, None, 0.10, 'days/ns')},
#                     'eiger:mc': {'days_ns': (0.126, None, 0.05, 'days/ns')},
#                     'pilatus:mc': {'days_ns': (0.128, None, 0.05, 'days/ns')},
#                 }
#             else:
#                 self.reference = {
#                     'daint:mc': {'days_ns': (0.425, None, 0.10, 'days/ns')},
#                     'eiger:mc': {'days_ns': (0.057, None, 0.05, 'days/ns')},
#                     'pilatus:mc': {'days_ns': (0.054, None, 0.05, 'days/ns')}
#                 }
#
#     @performance_function('days/ns')
#     def days_ns(self):
#         return sn.avg(sn.extractall(
#             r'Info: Benchmark time: \S+ CPUs \S+ '
#             r's/step (?P<days_ns>\S+) days/ns \S+ MB memory',
#             self.stdout, 'days_ns', float))
