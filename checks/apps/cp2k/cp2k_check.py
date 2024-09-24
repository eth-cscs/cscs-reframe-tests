# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import shutil

import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps
import uenv

cp2k_references = {
    "pbe": {"gh200": {"time_run": (65, None, 5, "s")}},
    "rpa": {"gh200": {"time_run": (560, None, 5, "s")}},
}


slurm_config = {
    "pbe": {
        "gh200": {"nodes": 8, "ntasks-per-node": 16, "cpus-per-task": 16, "gpu": True}
    },
    "rpa": {
        "gh200": {"nodes": 8, "ntasks-per-node": 16, "cpus-per-task": 16, "gpu": True}
    },
}


class cp2k_download(rfm.RunOnlyRegressionTest):
    """
    Download CP2K source code.
    """

    version = variable(str, value="2024.3")  # TODO: Do not hard-code
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


# @rfm.simple_test
# class Cp2kBuildTest(rfm.CompileOnlyRegressionTest):
#     """
#     Test CP2K build from source.
#     """
#     descr = "CP2K Build Test"
#     valid_systems = ['*']
#     valid_prog_environs = ['+cp2k-dev']
#     build_system = "CMake"
#     sourcesdir = None
#     maintainers = ["RMeli"]
#     cp2k_sources = fixture(cp2k_download, scope="session") # TODO: Change scope, other tests don't need source code
#     build_locally = False
#
#     @run_before("compile")
#     def prepare_build(self):
#         self.uarch = uenv.uarch(self.current_partition)
#         self.build_system.builddir = os.path.join(self.stagedir, "build")
#         self.build_system.max_concurrency = 64
#
#         tarsource = os.path.join(self.cp2k_sources.stagedir, f"v{self.cp2k_sources.version}.tar.gz")
#
#         # Extract source code
#         self.prebuild_cmds = [
#             f"tar --strip-components=1 -xzf {tarsource} -C {self.stagedir}"
#         ]
#
#         # TODO: Use Ninja generator
#         self.build_system.config_opts = [
#             "-DCP2K_ENABLE_REGTESTS=ON", # Puts executables under exe/local_cuda/
#             "-DCP2K_USE_LIBXC=ON",
#             "-DCP2K_USE_LIBINT2=ON",
#             "-DCP2K_USE_SPGLIB=ON",
#             "-DCP2K_USE_ELPA=ON",
#             "-DCP2K_USE_SPLA=ON",
#             "-DCP2K_USE_SIRIUS=ON",
#             "-DCP2K_USE_COSMA=ON",
#             "-DCP2K_USE_PLUMED=ON",
#         ]
#
#         if self.uarch == "gh200":
#             self.build_system.config_opts += [
#                 "-DCP2K_USE_ACCEL=CUDA",
#                 "-DCP2K_WITH_GPU=H100",
#             ]
#
#     @sanity_function
#     def validate_test(self):
#         # INFO: Executables are in exe/local_cuda because -DCP2K_ENABLE_REGTEST=ON
#         # INFO: With -DCP2K_ENABLE_REGTEST=OFF, executables are in build/bin/ as expected
#         executable = os.path.join(self.stagedir,"exe", "local_cuda", "cp2k.psmp")
#         return os.path.isfile(executable)


# @rfm.simple_test
# class Cp2kCheck(rfm.RunOnlyRegressionTest):
#     executable = "cp2k.psmp"
#     executable_opts = ["H2O-256.inp"]
#     maintainers = ["RMeli"]
#     valid_systems = ["*"]
#     valid_prog_environs = ["+cp2k", "+cuda", "+mpi"]
#
#     @run_before("run")
#     def prepare_run(self):
#         self.uarch = uenv.uarch(self.current_partition)
#
#         # SBATCH options
#         # TODO: Enable running with MPS
#         self.num_tasks = slurm_config[self.uarch]["ranks"]
#         self.num_cpus_per_task = slurm_config[self.uarch]["cores"]
#
#         # srun options
#         self.job.launcher.options = ["--cpu-bind=cores"]
#
#         # Environment variables
#         self.env_vars["MPICH_GPU_SUPPORT_ENABLED"] = "1"
#         self.env_vars["OMP_NUM_THREADS"] = str(
#             self.num_cpus_per_task - 1
#         )  # INFO: OpenBLAS adds one thread
#         self.env_vars["OMP_PLACES"] = "cores"
#         self.env_vars["OMP_PROC_BIND"] = "close"
#         self.env_vars["CUDA_CACHE_DISABLE"] = "1"
#
#         # Set reference
#         if self.uarch is not None and self.uarch in cp2k_references:
#             self.reference = {
#                 self.current_partition.fullname: cp2k_references[self.uarch]
#             }
#
#     @sanity_function
#     def assert_energy_diff(self):
#         energy = sn.extractsingle(
#             r"\s+ENERGY\| Total FORCE_EVAL \( QS \) "
#             r"energy [\[\(]a\.u\.[\]\)]:\s+(?P<energy>\S+)",
#             self.stdout,
#             "energy",
#             float,
#             item=-1,
#         )
#         energy_reference = -4404.2323
#         energy_diff = sn.abs(energy - energy_reference)
#
#         successful_termination = sn.assert_found(r"PROGRAM STOPPED IN", self.stdout)
#         correct_number_of_md_steps = sn.assert_eq(
#             sn.count(
#                 sn.extractall(
#                     r"(?i)(?P<step_count>STEP NUMBER)", self.stdout, "step_count"
#                 )
#             ),
#             10,
#         )
#         correct_energy = sn.assert_lt(energy_diff, 1e-4)
#
#         return sn.all(
#             [
#                 successful_termination,
#                 correct_number_of_md_steps,
#                 correct_energy,
#             ]
#         )
#
#     # INFO: The name of this function needs to match with the reference dict!
#     @performance_function("s")
#     def time_run(
#         self,
#     ):
#         return sn.extractsingle(
#             r"^ CP2K(\s+[\d\.]+){4}\s+(?P<perf>\S+)", self.stdout, "perf", float
#         )


@rfm.simple_test
class Cp2kCheckPBE(rfm.RunOnlyRegressionTest):
    executable = "./mps-wrapper.sh cp2k.psmp"
    executable_opts = ["-i", "H2O-128-PBE-TZ.inp"]
    maintainers = ["RMeli"]
    valid_systems = ["*"]
    valid_prog_environs = ["+cp2k"]
    test_name = "pbe"

    @run_before("run")
    def prepare_run(self):
        self.uarch = uenv.uarch(self.current_partition)

        # SBATCH options
        # TODO: Enable running with MPS
        nodes = slurm_config[self.test_name][self.uarch]["nodes"]

        self.job.options = [
            f"--nodes={nodes}",
            "--ntasks-per-core=1",
            "--time 00:05:00",
            "--reservation=daint",
        ]  # TODO: Remove reservation
        self.num_tasks_per_node = slurm_config[self.test_name][self.uarch][
            "ntasks-per-node"
        ]
        self.num_tasks = nodes * self.num_tasks_per_node
        self.num_cpus_per_task = slurm_config[self.test_name][self.uarch][
            "cpus-per-task"
        ]

        # srun options
        self.job.launcher.options = ["--cpu-bind=cores"]

        # Environment variables
        self.env_vars["MPICH_GPU_SUPPORT_ENABLED"] = "1"
        self.env_vars["OMP_NUM_THREADS"] = str(
            self.num_cpus_per_task - 1
        )  # INFO: OpenBLAS adds one thread
        self.env_vars["OMP_PLACES"] = "cores"
        self.env_vars["OMP_PROC_BIND"] = "close"
        self.env_vars["CUDA_CACHE_DISABLE"] = "1"

        # Set reference
        if self.uarch is not None and self.uarch in cp2k_references[self.test_name]:
            self.reference = {
                self.current_partition.fullname: cp2k_references[self.test_name][
                    self.uarch
                ]
            }

    @sanity_function
    def assert_energy_diff(self):
        energy = sn.extractsingle(
            r"\s+ENERGY\| Total FORCE_EVAL \( QS \) "
            r"energy [\[\(]a\.u\.[\]\)]:\s+(?P<energy>\S+)",
            self.stdout,
            "energy",
            float,
            item=-1,
        )
        energy_reference = -2206.2426491358
        energy_diff = sn.abs(energy - energy_reference)

        successful_termination = sn.assert_found(r"PROGRAM STOPPED IN", self.stdout)
        correct_energy = sn.assert_lt(energy_diff, 1e-4)

        return sn.all(
            [
                successful_termination,
                correct_energy,
            ]
        )

    # INFO: The name of this function needs to match with the reference dict!
    @performance_function("s")
    def time_run(
        self,
    ):
        return sn.extractsingle(
            r"^ CP2K(\s+[\d\.]+){4}\s+(?P<perf>\S+)", self.stdout, "perf", float
        )


@rfm.simple_test
class Cp2kCheckRPA(rfm.RunOnlyRegressionTest):
    executable = "./mps-wrapper.sh cp2k.psmp"
    maintainers = ["RMeli"]
    valid_systems = ["*"]
    valid_prog_environs = ["+cp2k"]

    test_name = "rpa"
    executable_opts = ["-i", "H2O-128-RI-dRPA-TZ.inp"]

    def __init__(self):
        self.depends_on("Cp2kCheckPBE", udeps.fully)

    @require_deps
    def copy_file(self, Cp2kCheckPBE):
        pbe_wfn = "H2O-128-PBE-TZ-RESTART.wfn"
        src = os.path.join(Cp2kCheckPBE().stagedir, pbe_wfn)
        dest = os.path.join(self.stagedir, pbe_wfn)
        shutil.copyfile(src, dest)

    @run_before("run")
    def prepare_run(self):
        self.uarch = uenv.uarch(self.current_partition)

        # SBATCH options
        # TODO: Enable running with MPS
        nodes = slurm_config[self.test_name][self.uarch]["nodes"]

        self.job.options = [
            f"--nodes={nodes}",
            "--ntasks-per-core=1",
            "--time 00:15:00",
            "--reservation=daint",
        ]  # TODO: Remove reservation
        self.num_tasks_per_node = slurm_config[self.test_name][self.uarch][
            "ntasks-per-node"
        ]
        self.num_tasks = nodes * self.num_tasks_per_node
        self.num_cpus_per_task = slurm_config[self.test_name][self.uarch][
            "cpus-per-task"
        ]

        # srun options
        self.job.launcher.options = ["--cpu-bind=cores"]

        # Environment variables
        self.env_vars["MPICH_GPU_SUPPORT_ENABLED"] = "1"
        self.env_vars["OMP_NUM_THREADS"] = str(
            self.num_cpus_per_task - 1
        )  # INFO: OpenBLAS adds one thread
        self.env_vars["OMP_PLACES"] = "cores"
        self.env_vars["OMP_PROC_BIND"] = "close"
        self.env_vars["CUDA_CACHE_DISABLE"] = "1"

        # Set reference
        if self.uarch is not None and self.uarch in cp2k_references[self.test_name]:
            self.reference = {
                self.current_partition.fullname: cp2k_references[self.test_name][
                    self.uarch
                ]
            }

    @sanity_function
    def assert_energy_diff(self):
        energy = sn.extractsingle(
            r"\s+ENERGY\| Total FORCE_EVAL \( QS \) "
            r"energy [\[\(]a\.u\.[\]\)]:\s+(?P<energy>\S+)",
            self.stdout,
            "energy",
            float,
            item=-1,
        )
        energy_reference = -2217.36884935325
        energy_diff = sn.abs(energy - energy_reference)

        successful_termination = sn.assert_found(r"PROGRAM STOPPED IN", self.stdout)
        correct_energy = sn.assert_lt(energy_diff, 1e-4)

        return sn.all(
            [
                successful_termination,
                correct_energy,
            ]
        )

    # INFO: The name of this function needs to match with the reference dict!
    @performance_function("s")
    def time_run(
        self,
    ):
        return sn.extractsingle(
            r"^ CP2K(\s+[\d\.]+){4}\s+(?P<perf>\S+)", self.stdout, "perf", float
        )
