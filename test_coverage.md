# Test coverage on Alps

The tests have one of the following states:

| Status | Meaning |
|:---|:---|
| covered | a test in the production or maintenance suite checks this |
| partial | a test in those suites checks something adjacent, but not the item as described |
| stale | a test exists but does not carry the `production` or `maintenance` tag, or its `valid_systems` no longer matches any system, so it never runs |
| missing | nothing in the repo |

## System & Runtime Environment

| Item | Status | Test | Notes |
|:---|:---|:---|:---|
| OS consistency across nodes (cat /etc/os-release) | partial | `os-version-check-*` in [alps.py](checks/system/integration/alps.py) | Pins the expected `PRETTY_NAME` on one node. No cross-node diff. |
| Kernel version consistency (uname -r across nodes) | missing | | No `uname -r` anywhere. |
| Time synchronization (timedatectl, compare nodes) | missing | | No chrony/ntp/timedatectl check. |
| Hostname + domain consistency (hostname -f) | partial | `HostnameCheck` in [slurm.py](checks/system/slurm/slurm.py) | Checks the `nidNNNNNN` pattern only, not `hostname -f`. |
| CPU topology consistency (lscpu diff across nodes) | missing | | `DefaultRequest` in slurm.py would do `lscpu` but is disabled and hardcodes 288. |
| NUMA topology (numactl --hardware) | stale | `OneTaskPerNumaNode` in [affinity_check.py](checks/prgenv/affinity_check.py) | Tags `scs`, `craype` only. Validates placement against the ReFrame config, not against `numactl --hardware` on the node. |
| Environment variables inside job vs login | partial | `EnvironmentVariableCheck` in slurm.py, `env-*` in alps.py | Propagation and presence are tested. No login-vs-compute diff; `LoginEnvCheck` in prgenv_check.py is disabled. |
| Container runtime sanity (run minimal Apptainer container) | covered | `RunJobCE` in [ce_import_run_image.py](checks/system/ce/ce_import_run_image.py) | Uses the Container Engine, not Apptainer. |

## Scheduler & Resource Management

| Item | Status | Test | Notes |
|:---|:---|:---|:---|
| Single-node allocation correctness (srun -N1 hostname) | covered | `HostnameCheck` in slurm.py | |
| Multi-node allocation correctness (srun -N2 hostname) | partial | `HelloWorldTestMPI` in [helloworld.py](checks/prgenv/helloworld.py) | 2 nodes via MPI hello world. `HostnameCheck` itself is single task. |
| CPU count matches request (srun -c X nproc) | stale | affinity tests in affinity_check.py | Tags `scs`, `craype` only. Indirect: they assert the whole allocated CPU set is consumed. No `srun -c X nproc`. |
| Memory limit enforcement (allocate beyond limit → fail) | covered | `MemoryOverconsumptionCheck`, `MemoryOomMpiCheck` in slurm.py | |
| Walltime enforcement (job killed at limit) | missing | | The `timeout-*` checks in alps.py test coreutils `timeout`, not Slurm. |
| Job array execution (sbatch --array) | missing | | |
| Constraint/feature scheduling (srun -C \<feature>) | covered | `SlurmTransparentHugepagesCheck` in slurm.py | `-C thp_*`, verified on the node. |
| GPU isolation between jobs (nvidia-smi per job) | missing | | `nvidia_smi_check` (Exclusive_Process) is disabled. |

## CPU & Memory

| Item | Status | Test | Notes |
|:---|:---|:---|:---|
| STREAM bandwidth (small size) | covered | `CPUNodeBurnStreamCE` in [node-burn-ce.py](checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) | The dedicated [stream.py](checks/microbenchmarks/cpu/stream/stream.py) has no tags, so it is stale. |
| Small DGEMM (matrix multiply sanity) | partial | `CPUNodeBurnGemmCE` in node-burn-ce.py | 20 s burn through the CE, not a small sanity matmul. [dgemm.py](checks/microbenchmarks/cpu/dgemm/dgemm.py) is pinned to old systems. |
| Single vs multi-core scaling (1 vs N threads) | missing | | Every CPU test runs at full width only. |
| OpenMP thread placement (OMP_DISPLAY_ENV=true) | stale | 9 tests in affinity_check.py | Tags `scs`, `craype` only. Real pinning via `sched_getaffinity`; `OMP_DISPLAY_ENV` itself is never checked. |
| CPU frequency under load (lscpu + stress test) | missing | | |
| Memory allocation stress (malloc loop test) | covered | [alloc_speed.py](checks/microbenchmarks/cpu/alloc_speed/alloc_speed.py) | References only for `eiger:mc`/`pilatus:mc`, so no perf gate on Alps. |
| Cache behavior (simple stride access test) | stale | [strides.py](checks/microbenchmarks/cpu/strided_bandwidth/strides.py), [latency.py](checks/microbenchmarks/cpu/latency/latency.py) | Tags `benchmark`, `diagnostic`; pinned to `eiger:mc`/`pilatus:mc`. |
| NUMA locality performance (local vs remote memory) | stale | `CPUBandwidthCrossSocket` in [check_cpu_bandwith.py](checks/microbenchmarks/cpu/likwid/check_cpu_bandwith.py) | Disabled (`valid_systems = []`). |

## Network / Slingshot

| Item | Status | Test | Notes |
|:---|:---|:---|:---|
| libfabric provider list (fi_info) | missing | | alps.py only checks that `/opt/cray/libfabric` paths exist. |
| CXI provider detection (fi_info -p cxi) | partial | [xccl_tests.py](checks/microbenchmarks/xccl/xccl_tests.py) | NCCL log says `provider is cxi`. Nothing checks plain MPI or CPU-only partitions. [cxi_stat_hsn.py](checks/system/network/cxi_stat_hsn.py) lists hsn0-3 but has no tags. |
| MPI rank distribution (srun -N2 -n8 hostname) | missing | | `cpi_build_test` in mpi_cpi.py overrides `num_tasks` to 1 (see bugs). |
| MPI latency (OSU osu_latency) | stale | `OSULatency` in [osu_run.py](checks/microbenchmarks/mpi/osu/osu_run.py), `osu_pt2pt_check` in [osu_tests.py](checks/microbenchmarks/mpi/osu/osu_tests.py) | Tags `uenv` and `craype` respectively, so neither is in a suite. |
| MPI bandwidth (OSU osu_bw) | covered | `OMB_MPICH_CE`, `OMB_OMPI_CE` in [omb.py](checks/containers/container_engine/omb.py) | `OSUBandwidth` in osu_run.py and `osu_pt2pt_check` also exist but are untagged. |
| MPI allreduce sanity (osu_allreduce) | stale | `osu_collective_check` in osu_tests.py | Tag `craype` only, and the reference lookup is broken (see bugs). Not in the uenv or CE variants. |
| Multi-node scaling sanity (2 vs 4 nodes timing) | stale | [halo_cell_exchange.py](checks/microbenchmarks/mpi/halo_exchange/halo_cell_exchange.py) | Tag `benchmark`, old systems only. All live MPI tests use one fixed node count. |
| MPI fabric debug (MPICH_OFI_VERBOSE=1) | missing | | No `MPICH_OFI_VERBOSE` anywhere. |

## GPU / Accelerators

| Item | Status | Test | Notes |
|:---|:---|:---|:---|
| GPU visibility (nvidia-smi / rocm-smi) | partial | `NvidiaSmiDriverVersion` in slurm.py | Only greps the driver banner. No `rocm-smi` check at all. |
| GPU count vs allocation (srun --gpus=X) | partial | [nvidia_device_count.py](checks/system/nvidia/nvidia_device_count.py), [cuda_nvml.py](checks/prgenv/cuda/cuda_nvml.py), `SlurmGPUGresTest` in slurm.py | Count vs config is solid. Nothing requests `--gpus=1` on a 4-GPU node and checks what the process sees. |
| GPU driver/runtime compatibility | partial | `SlurmUvmPerfAccessCounterMigration` in slurm.py, `deviceQuery` in [cuda_samples.py](checks/prgenv/cuda/cuda_samples.py) | No explicit driver-vs-runtime version assertion. |
| CUDA/HIP basic execution (small kernel) | partial | cuda_samples.py, [cuda_fortran.py](checks/prgenv/cuda_fortran.py), [opencl.py](checks/prgenv/opencl.py), [openacc.py](checks/prgenv/openacc.py) | CUDA is covered. No HIP smoke test. |
| GPU memory allocation test | partial | pre-check in [fio.py](checks/system/io/fio.py) | Allocates 95% VRAM as a side effect. [cuda_memtest_check.py](checks/prgenv/cuda/cuda_memtest_check.py) is pinned to old systems. |
| GPU memory bandwidth test | partial | `RunNVGPUJobCE` in ce_import_run_image.py, `CudaNodeBurnStreamCE` in node-burn-ce.py | Device-local STREAM only. H2D/D2H ([memory_bandwidth.py](checks/microbenchmarks/gpu/memory_bandwidth/memory_bandwidth.py)) is pinned to old systems. |
| Multi-GPU visibility (same node) | covered | nvidia_device_count.py, [coralgemm.py](checks/microbenchmarks/gpu/dgemm/coralgemm.py) | |
| GPU topology (nvidia-smi topo -m) | missing | | No `nvidia-smi topo -m` or link-matrix check. |
| GPU + MPI interaction (multi-rank GPU test) | covered | [cuda_aware_mpi.py](checks/prgenv/cuda/cuda_aware_mpi.py), xccl_tests.py | No CPE variant of cuda_aware_mpi. `OSU*Cuda` in osu_run.py is untagged. |
| GPU isolation between jobs | missing | | |

## Storage & Filesystems

| Item | Status | Test | Notes |
|:---|:---|:---|:---|
| Home filesystem read/write | missing | | `IorCheck` for `/users` is pinned to `fulen:normal`, which no longer exists. |
| Scratch filesystem read/write | partial | [dd_blk_size.py](checks/system/io/dd_blk_size.py), `stuck_gpu_mem_test` in fio.py | Writes happen but nothing reports bandwidth. [mlperf_storage_ce.py](checks/apps/pytorch/mlperf_storage_ce.py) does, but is 32 nodes and tagged `ce` only. |
| Project filesystem read/write | missing | | Only mount and env-var presence checks. |
| Metadata test (create/delete many small files) | missing | | No mdtest. |
| Sequential write throughput (small file) | stale | `IorWriteCheck` in [ior_check.py](checks/system/io/ior_check.py) | Has the `production` tag but `valid_systems` matches no current system, and every reference is `(0, None, None)`. |
| Sequential read throughput (small file) | stale | `IorReadCheck` in ior_check.py | Same. |
| Parallel write (multi-process write test) | partial | [h5py_mpi.py](checks/libraries/io/h5py_mpi.py), [netcdf.py](checks/libraries/io/netcdf.py), [pnetcdf.py](checks/libraries/io/pnetcdf.py) | Correctness only, 4 tasks, written to the stage dir. |
| File visibility across nodes (write on one, read on another) | missing | | |

## Bugs found while auditing

Small fixes, each can be its own PR:

- [osu_tests.py:379](checks/microbenchmarks/mpi/osu/osu_tests.py#L379): `self.allref[self.num_nodes]` indexes the wrong level of the dict. The `KeyError` is suppressed, so `osu_collective_check` never gets a performance reference.
- [mpi_cpi.py:23](checks/prgenv/mpi_cpi.py#L23): `setup_job` overwrites `num_tasks = -2` with `num_tasks_per_node` (1). The appscheckout MPI test runs on a single rank.
- [coralgemm.py:221](checks/microbenchmarks/gpu/dgemm/coralgemm.py#L221): the phantom-GPU guard looks for `device_{n+1}` but the first unexpected device is `device_{n}`.
- [dd_blk_size.py:40](checks/system/io/dd_blk_size.py#L40): the `for ntasks in 1 2` loop never changes the task count, it runs the same single-process `dd` twice.
- [omb.py:110](checks/containers/container_engine/omb.py#L110): `osu_alltoall` is skipped unconditionally ("known performance regression"), so the CE suite has no collective at all.
- No `production` or `maintenance` tag, so never selected by a suite even though they run fine on Alps: [affinity_check.py](checks/prgenv/affinity_check.py) (`scs`, `craype`), [osu_run.py](checks/microbenchmarks/mpi/osu/osu_run.py) (`uenv`), [osu_tests.py](checks/microbenchmarks/mpi/osu/osu_tests.py) (`craype`), and with no tags at all: [stream.py](checks/microbenchmarks/cpu/stream/stream.py), [cxi_stat_hsn.py](checks/system/network/cxi_stat_hsn.py), [cxi_gpu_loopback_bw.py](checks/system/network/cxi_gpu_loopback_bw.py), [baremetal-node-burn.py](checks/microbenchmarks/gpu/node_burn/baremetal-node-burn.py), [cdo.py](checks/tools/io/cdo.py), [nco.py](checks/tools/io/nco.py).
- `MountPointExistsTest` in [v-cluster_config.py](checks/system/integration/v-cluster_config.py) runs on login nodes only (`valid_systems = ['-remote']`).
