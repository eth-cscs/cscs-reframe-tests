# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
import os
import shutil
import reframe as rfm
import reframe.utility.sanity as sn

from uenv import uarch

dlaf_references = {
    "eigensolver": {
        "gh200": {
            "time_run": (24.0, -1.0, 0.1, "s"),
        },
        "zen2": {
            "time_run": (165.0, -1.0, 0.1, "s"),
        }
    },
    "gen_eigensolver": {
        "gh200": {
            "time_run": (26.0, -1.0, 0.1, "s")
        },
        "zen2": {
            "time_run": (200.0, -1.0, 0.1, "s"),
        }
    },
}

slurm_config = {
    "eigensolver": {
        "gh200": {
            "nodes": 2,
            "ntasks-per-node": 4,
            "cpus-per-task": 72,
            "walltime": "0d0h5m0s",
            "gpu": True,
        },
        "zen2": {
            "nodes": 2,
            "ntasks-per-node": 16,
            "cpus-per-task": 16,
            "walltime": "0d0h10m0s",
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
        },
        "zen2": {
            "nodes": 2,
            "ntasks-per-node": 16,
            "cpus-per-task": 16,
            "walltime": "0d0h10m0s",
            "gpu": True,
        }
    },
}


class dlaf_base(rfm.RunOnlyRegressionTest):
    valid_systems = ['+uenv']
    valid_prog_environs = ['+dlaf']
    maintainers = ["SSA"]

    def _sq_factor(self, n):
        """
        Finds two factors of `n` that are as close to each other as possible.
        Note: the second factor is larger or equal to the first factor
        """
        for i in range(1, int(n**0.5) + 1):
            if n % i == 0:
                f = (i, n // i)
        return f

    @run_before("run")
    def prepare_run(self):
        self.uarch = uarch(self.current_partition)

        # slurm configuration
        config = slurm_config[self.test_name][self.uarch]
        self.job.options = [f'--nodes={config["nodes"]}']
        self.num_tasks_per_node = config["ntasks-per-node"]
        self.num_tasks = config["nodes"] * self.num_tasks_per_node
        self.num_cpus_per_task = config["cpus-per-task"]
        self.ntasks_per_core = 1
        self.time_limit = config["walltime"]
        self.job.launcher.options = ["--cpu-bind=cores"]
        if self.uarch == "gh200":
            self.job.launcher.options += ["--gpus-per-task=1"]

        # environment variables
        if self.uarch == "zen2":
            self.env_vars["PIKA_THREADS"] = str((self.num_cpus_per_task // 2) - 1)
        else:
            self.env_vars["PIKA_THREADS"] = str(self.num_cpus_per_task - 1)
        self.env_vars["MIMALLOC_ALLOW_LARGE_OS_PAGES"] = "1"
        self.env_vars["MIMALLOC_EAGER_COMMIT_DELAY"] = "0"
        if self.uarch == "gh200":
            self.env_vars["FI_MR_CACHE_MONITOR"] = "disabled"
            self.env_vars["MPICH_GPU_SUPPORT_ENABLED"] = "1"
            self.env_vars["DLAF_BT_BAND_TO_TRIDIAG_HH_APPLY_GROUP_SIZE"] = \
                "128"
            self.env_vars["DLAF_UMPIRE_DEVICE_MEMORY_POOL_ALIGNMENT_BYTES"] = \
                str(2**21)

        # executable options
        grid_cols, grid_rows = self._sq_factor(self.num_tasks)
        self.executable_opts += [
            f"--grid-cols={grid_cols}",
            f"--grid-rows={grid_rows}"
        ]
        if self.uarch == "gh200":
            self.executable_opts.append("--block-size=1024")
        else:
            self.executable_opts.append("--block-size=512")

        # set performance reference
        if self.uarch is not None and \
           self.uarch in dlaf_references[self.test_name]:
            self.reference = {
                self.current_partition.fullname:
                    dlaf_references[self.test_name][self.uarch]
            }

    @sanity_function
    def assert_job(self):
        """
       [0] 29.7415s dL (40960, 40960) (0, 40960) (1024, 1024) 128 (4, 2) 71 GPU
       Max Diff / Max A: 1.19349e-13
        """
        regex1 = r'^\[0\]\s+(?P<perf>\S+)s\s+'
        regex2 = r'^Max Diff / Max A.*: \S+'
        self.sanity_patterns = sn.all([
            sn.assert_found(regex1, self.stdout, msg='regex1 failed'),
            sn.assert_found(regex2, self.stdout, msg='regex2 failed')
        ])

        return self.sanity_patterns

    @performance_function("s")
    def time_run(self):
        regex = r"^\[0\]\s+(?P<perf>\S+)s\s+"
        return sn.extractsingle(regex, self.stdout, "perf", float)


@rfm.simple_test
class dlaf_check_uenv(dlaf_base):
    tags = {"uenv", "production"}
    test_name = parameter(["gen_eigensolver", "eigensolver"])
    executable_opts = [
        "--type=d",
        "--matrix-size=40960",
        "--check=last",
        "--nwarmups=1",
        "--nruns=1",
    ]

    @run_before("run")
    def set_executable(self):
        self.executable = (
            "miniapp_gen_eigensolver" if self.test_name == "gen_eigensolver"
            else "miniapp_eigensolver"
        )
