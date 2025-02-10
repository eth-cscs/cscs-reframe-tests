# Copyright 2016-2025 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import shutil

import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps
import uenv

dlaf_references = {
    "eigensolver": {"gh200": {"time_run": (30.5, -1.0, 0.1, "s")}},
    "gen_eigensolver": {"gh200": {"time_run": (33.5, -1.0, 0.1, "s")}},
}


slurm_config = {
    "eigensolver": {
        "gh200": {
            "nodes": 2,
            "ntasks-per-node": 4,
            "cpus-per-task": 72,
            "walltime": "0d0h5m0s",
            "gpu": True,
        }
    },
    "gen_eigensolver": {
        "gh200": {
            "nodes": 2,
            "ntasks-per-node": 4,
            "cpus-per-task": 72,
            "walltime": "0d0h5m0s",
            "gpu": True,
        }
    },
}


class DlafCheck(rfm.RunOnlyRegressionTest):
    maintainers = ["SSA"]
    valid_systems = ["*"]

    # Finds two factors of `n` that are as close to each other as possible.
    #
    # Note: the second factor is larger or equal to the first factor
    def _sq_factor(self, n):
        for i in range(1, int(n**0.5) + 1):
            if n % i == 0:
                f = (i, n // i)
        return f

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
        self.job.launcher.options = ["--cpu-bind=cores"]
        if self.uarch == "gh200":
            self.job.launcher.options += ["--gpus-per-task=1"]

        # environment variables
        self.env_vars["PIKA_THREADS"] = str(self.num_cpus_per_task - 1)
        self.env_vars["MIMALLOC_ALLOW_LARGE_OS_PAGES"] = "1"
        self.env_vars["MIMALLOC_EAGER_COMMIT_DELAY"] = "0"
        self.env_vars["FI_MR_CACHE_MONITOR"] = "disabled"

        if self.uarch == "gh200":
            self.env_vars["MPICH_GPU_SUPPORT_ENABLED"] = "1"
            self.env_vars["DLAF_BT_BAND_TO_TRIDIAG_HH_APPLY_GROUP_SIZE"] = "128"
            self.env_vars["DLAF_UMPIRE_DEVICE_MEMORY_POOL_ALIGNMENT_BYTES"] = str(2**21)

        grid_cols, grid_rows = self._sq_factor(self.num_tasks)
        self.executable_opts += [f"--grid-cols={grid_cols}", f"--grid-rows={grid_rows}"]

        # set reference
        if self.uarch is not None and self.uarch in dlaf_references[self.test_name]:
            self.reference = {
                self.current_partition.fullname: dlaf_references[self.test_name][
                    self.uarch
                ]
            }

    # TODO
    @sanity_function
    def assert_accuracy(self):
        return True

    @performance_function("s")
    def time_run(self):
        return sn.extractsingle(r"^\[0\]\s+(?P<perf>\S+)s\s+.*", self.stdout, "perf", float)


class DlafCheckEigensolverBase(DlafCheck):
    executable_opts = [
        "--type=d",
        "--matrix-size=40960",
        "--block-size=1024",
        "--check=last",
        "--nwarmups=1",
        "--nruns=1",
    ]


class DlafCheckEigensolver(DlafCheckEigensolverBase):
    test_name = "eigensolver"
    executable = "miniapp_eigensolver"


class DlafCheckGenEigensolver(DlafCheckEigensolverBase):
    test_name = "gen_eigensolver"
    executable = "miniapp_gen_eigensolver"


@rfm.simple_test
class DlafCheckEigensolverUenvExec(DlafCheckEigensolver):
    valid_prog_environs = ["+dlaf"]
    tags = {"uenv", "production"}


@rfm.simple_test
class DlafCheckGenEigensolverUenvExec(DlafCheckGenEigensolver):
    valid_prog_environs = ["+dlaf"]
    tags = {"uenv", "production"}
