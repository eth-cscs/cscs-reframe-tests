# Copyright 2026 ETHZ/CSCS
# See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os

import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps


@rfm.simple_test
class fio_compile_test(rfm.RegressionTest):
    """
    Check title: Check if we can compile fio

    This test was taken from https://github.com/victorusu/reframe-tests-library
    """

    descr = "Make sure that we can compile fio."
    executable = "./fio"
    executable_opts = ["--version"]
    valid_systems = ["+remote"]
    valid_prog_environs = ["builtin"]
    build_system = "Autotools"
    tags = {"maintenance"}
    maintainers = ["VCUE", "gppezzi"]

    @run_after("setup")
    def set_num_procs(self):
        proc = self.current_partition.processor
        if proc:
            self.num_cpus_per_task = max(proc.num_cores, 8)
        else:
            self.num_cpus_per_task = 1

    @run_before("compile")
    def set_download_fio_cmds(self):
        self.prebuild_cmds = [
            '_rfm_download_time="$(date +%s%N)"',
            r"/usr/bin/curl -s https://api.github.com/repos/axboe/fio/releases/latest | /bin/grep tarball_url | /bin/awk -F'\"' '{print $4}' | /usr/bin/xargs -I{} /usr/bin/curl -LJ {} -o fio.tar.gz",
            '_rfm_download_time="$(($(date +%s%N)-_rfm_download_time))"',
            'echo "Download time (ns): $_rfm_download_time"',
            '_rfm_extract_time="$(date +%s%N)"',
            rf"/bin/tar xf fio.tar.gz --strip-components=1 -C {self.stagedir}",
            '_rfm_extract_time="$(($(date +%s%N)-_rfm_extract_time))"',
            'echo "Extraction time (ns): $_rfm_extract_time"',
        ]

    @run_before("compile")
    def set_build_opts(self):
        self.build_system.flags_from_environ = False
        self.prebuild_cmds += ['_rfm_build_time="$(date +%s%N)"']
        self.postbuild_cmds += [
            '_rfm_build_time="$(($(date +%s%N)-_rfm_build_time))"',
            'echo "Compilation time (ns): $_rfm_build_time"',
        ]

    @performance_function("s")
    def compilation_time(self):
        return (
            sn.extractsingle(
                r"Compilation time \(ns\): (\d+)", self.build_stdout, 1, float
            )
            * 1.0e-9
        )

    @performance_function("s")
    def download_time(self):
        return (
            sn.extractsingle(
                r"Download time \(ns\): (\d+)", self.build_stdout, 1, float
            )
            * 1.0e-9
        )

    @performance_function("s")
    def extraction_time(self):
        return (
            sn.extractsingle(
                r"Extraction time \(ns\): (\d+)", self.build_stdout, 1, float
            )
            * 1.0e-9
        )

    @sanity_function
    def assert_sanity(self):
        return sn.assert_found(r"fio-\S+", self.stdout)


@rfm.simple_test
class stuck_gpu_mem_test(rfm.RunOnlyRegressionTest):
    """
    Check for stuck GPU memory on GH200.

    This simple reproducer does three things:
    - Allocate 95% of GPU memory. This should pass on a freshly assigned node.
    - Create and read a 100GB file on scratch.
    - Attempt to allocate 95% of GPU memory again.

    This test should pass if the driver correctly evicts OS file caches, but fails on the second allocation attempt if the bug is present.

    Original reproducer: https://github.com/eth-cscs/alps-gh200-reproducers/tree/main/gpu-stuck-memory
    """

    valid_prog_environs = ["builtin"]
    valid_systems = ["+remote +nvgpu"]
    descr = "Check for stuck GPU memory on GH200"
    tags = {"maintenance"}
    maintainers = ["VCUE", "gppezzi"]

    # One can parametrise these parameters or make them variables
    test_name = "cachetest"
    benchmark = "read"
    block_size = "1M"
    file_size = "100G"
    engine = "sync"
    num_jobs = 1
    iodepth = 1
    filename = variable(str, value="/iopsstor/scratch/cscs/$USER/gpu-stuckmem.tmp")

    @run_after("init")
    def set_parent(self):
        self.depends_on("fio_compile_test", how=udeps.by_env)

    @run_before("run")
    def set_executable_and_opts(self):
        parent = self.getdep("fio_compile_test")
        fio_cmd = os.path.join(parent.stagedir, parent.executable)
        self.executable = " ".join(["numactl", "--membind=0", fio_cmd])
        self.executable_opts += [
            f"--name={self.test_name}",
            f"--rw={self.benchmark}",
            f"--bs={self.block_size}",
            f"--numjobs={self.num_jobs}",
            f"--iodepth={self.iodepth}",
            f"--size={self.file_size}",
            f"--ioengine={self.engine}",
            f"--filename={self.filename}",
            "--direct=0",
        ]

    @run_before("run")
    def set_experiment_opts(self):
        self.prerun_cmds += [
            "function fail() { echo $1; exit 1; }",
            '/usr/bin/parallel_allocate_free_gpu_mem 95 || fail "First allocation failed. Is this a clean node with file cached already flushed?"',
            "/usr/bin/nvidia-smi",
            '/usr/bin/numastat -m -z | grep -v "not in hash table"',
        ]
        self.postrun_cmds += [
            "/usr/bin/nvidia-smi",
            '/usr/bin/numastat -m -z | grep -v "not in hash table"',
            '/usr/bin/parallel_allocate_free_gpu_mem 95 || fail "Last allocation failed. Stuck memory bug still present. Check FilePages in numastat output above."',
            f"rm {self.filename}",
        ]

    @sanity_function
    def assert_passed(self):
        return sn.assert_eq(self.job.exitcode, 0)
