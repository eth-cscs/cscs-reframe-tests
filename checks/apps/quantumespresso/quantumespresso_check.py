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


qe_references = {
    "Au surf": {
        "gh200": {"time_run": (14.02, None, 0.05, "s")},
        "zen2": {"time_run": (99.45, None, 0.05, "s")},  # 1m44s
    },
}


slurm_config = {
    "Au surf": {
        "gh200": {
            "nodes": 1,
            "ntasks-per-node": 4,
            "cpus-per-task": 72,
            "walltime": "0d0h20m0s",
            "gpu": True,
        },
        "zen2": {
            "nodes": 1,
            "ntasks-per-node": 128,
            "cpus-per-task": 1,
            "walltime": "0d0h20m0s",
            "gpu": False,
        },
    },
}


class qe_download(rfm.RunOnlyRegressionTest):
    """
    Download QE source code.
    """

    version = variable(str, value="7.3.1")
    valid_systems = ["*"]
    valid_prog_environs = ["*"]
    descr = "Fetch QE source code"
    sourcesdir = None
    executable = "wget"
    local = True

    @run_before('run')
    def set_args(self):
        self.executable_opts = [
            '--quiet',
            'https://gitlab.com/QEF/q-e/-/archive/'
            f'qe-{self.version}/q-e-qe-{self.version}.tar.gz',
        ]

    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)


@rfm.simple_test
class QeBuildTest(rfm.CompileOnlyRegressionTest):
    """
    Test QE build from source.
    """

    descr = "QuantumESPRESSO Build Test"
    valid_prog_environs = ["+qe-dev"]
    valid_systems = ["*"]
    build_system = "CMake"
    sourcesdir = None
    maintainers = ["SSA"]
    qe_sources = fixture(qe_download, scope="environment")
    build_locally = False
    tags = {"uenv"}
    build_time_limit = "0d0h30m0s"
    pwx_executable = None

    @run_before("compile")
    def prepare_build(self):
        self.uarch = uenv.uarch(self.current_partition)
        self.build_system.builddir = os.path.join(self.stagedir, "build")
        self.skip_if_no_procinfo()
        cpu = self.current_partition.processor
        self.build_system.max_concurrency = cpu.info["num_cpus_per_socket"]

        tarsource = os.path.join(
            self.qe_sources.stagedir,
            f"q-e-qe-{self.qe_sources.version}.tar.gz"
        )

        # Extract source code
        self.prebuild_cmds = [
            f"tar --strip-components=1 -xzf {tarsource} -C {self.stagedir}"
        ]

        # TODO: Use Ninja generator
        self.build_system.config_opts = [
            "-DQE_ENABLE_MPI=ON ",
            "-DQE_ENABLE_OPENMP=ON",
            "-DQE_ENABLE_SCALAPACK:BOOL=ON",
            "-DQE_ENABLE_LIBXC=ON",
            "-DQE_CLOCK_SECONDS:BOOL=OFF",
        ]

        if self.uarch == "gh200":
            self.build_system.config_opts += [
                "-DQE_ENABLE_CUDA=ON",
                "-DQE_ENABLE_MPI_GPU_AWARE:BOOL=ON",
                "-DQE_ENABLE_OPENACC=ON",
            ]

    @sanity_function
    def validate_test(self):
        self.pwx_executable = os.path.join(self.stagedir,
                                           "build", "bin", "pw.x")
        return os.path.isfile(self.pwx_executable)


class QeCheck(rfm.RunOnlyRegressionTest):
    pwx_executable = "pw.x"
    maintainers = ["SSA"]
    valid_systems = ["*"]

    @run_before("run")
    def prepare_run(self):
        self.uarch = uenv.uarch(self.current_partition)
        config = slurm_config[self.test_name][self.uarch]
        # sbatch options
        self.job.options = [
            f'--nodes={config["nodes"]}',
        ]
        self.num_tasks_per_node = config["ntasks-per-node"]
        self.num_tasks = config["nodes"] * self.num_tasks_per_node
        self.num_cpus_per_task = config["cpus-per-task"]
        self.ntasks_per_core = 1
        self.time_limit = config["walltime"]

        # srun options
        self.job.launcher.options = ["--cpu-bind=socket"]

        # environment variables
        self.env_vars["OMP_NUM_THREADS"] = str(1)
        if self.uarch == "gh200":
            self.env_vars["MPICH_GPU_SUPPORT_ENABLED"] = "1"
            self.env_vars["OMP_NUM_THREADS"] = str(20)

        # set reference
        if self.uarch is not None and \
           self.uarch in qe_references[self.test_name]:
            self.reference = {
                self.current_partition.fullname:
                    qe_references[self.test_name][self.uarch]
            }

    @sanity_function
    def assert_energy_diff(self):
        # TODO, update for QE
        energy = sn.extractsingle(
            r"^!\s+total energy\s+=\s+(?P<energy>\S+)",
            self.stdout,
            "energy",
            float,
            item=-1,
        )
        energy_diff = sn.abs(energy - self.energy_reference)
        successful_termination = sn.assert_found(r"JOB DONE", self.stdout)
        correct_energy = sn.assert_lt(energy_diff, 1e-4)
        return sn.all(
            [
                successful_termination,
                correct_energy,
            ]
        )

    # INFO: The name of this function needs to match with the reference dict!
    @performance_function("s")
    def time_run(self):
        return sn.extractsingle(r'electrons.+\s(?P<wtime>\S+)s WALL',
                                self.stdout, 'wtime', float)


class QeCheckAuSurf(QeCheck):
    test_name = "Au surf"
    executable_opts = ["-i", "ausurf.in"]
    energy_reference = -11427.09017218


@rfm.simple_test
class QeCheckAuSurfUenvExec(QeCheckAuSurf):
    valid_prog_environs = ["+qe"]
    tags = {"uenv", "production"}

    @run_after("setup")
    def setup_executable(self):
        self.executable = f"pw.x"
        uarch = uenv.uarch(self.current_partition)
        if uarch == 'gh200':
            self.executable = f"./mps-wrapper.sh pw.x"


@rfm.simple_test
class QeCheckAuSurfCustomExec(QeCheckAuSurf):
    """
    Same test as above, but using executables built by QeBuildTest.
    """

    valid_prog_environs = ["+qe-dev"]
    tags = {"uenv"}

    @run_after("init")
    def setup_dependency(self):
        self.depends_on("QeBuildTest", udeps.fully)

    @run_after("setup")
    def setup_executable(self):
        parent = self.getdep("QeBuildTest")

        self.executable = f"{parent.pwx_executable}"
        uarch = uenv.uarch(self.current_partition)
        if uarch == 'gh200':
            self.executable = f"./mps-wrapper.sh {parent.pwx_executable}"
