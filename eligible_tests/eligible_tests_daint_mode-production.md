## Eligible ReFrame Tests on daint

- Filters:
  - system: `daint`
  - mode: `production`
  - checks: `165`
- Generated: `2026-05-05 15:15:52 +0200`

| Test name | Description | Category |
|----------|-------------|----------|
| [uenv_status](../checks/system/uenv/uenv_status.py) | — | [system/uenv](../checks/system/uenv/) |
| [uenv_status](../checks/system/uenv/uenv_status.py) | — | [system/uenv](../checks/system/uenv/) |
| [DcgmRpmCheck](../checks/system/gssr/dcgm_hook.py) | Check DCGM executable and libraries are installed | [system/gssr](../checks/system/gssr/) |
| [GssrCeHookCheck](../checks/system/gssr/dcgm_hook.py)<br>• %pytorch_image_tag=25.01-py3_nvrtc-12.9 | Check DCGM CE hook is working with gssr | [system/gssr](../checks/system/gssr/) |
| [InvalidAccount](../checks/system/slurm/invalid_acc.py) | Check if Slurm accepts job submission using an invalid<br>        account. Reframe should raise a failure if the job starts. | [system/slurm](../checks/system/slurm/) |
| [HostnameCheck](../checks/system/slurm/slurm.py) | Check hostname pattern nidXXXXXX on the CN | [system/slurm](../checks/system/slurm/) |
| [EnvironmentVariableCheck](../checks/system/slurm/slurm.py) | Test if user env variables are propagated to CN | [system/slurm](../checks/system/slurm/) |
| [NvidiaSmiDriverVersion](../checks/system/slurm/slurm.py) | Nvidia-smi sanity check (output driver version) | [system/slurm](../checks/system/slurm/) |
| [DefaultRequestGPUSetsGRES](../checks/system/slurm/slurm.py) | Checks slurm config for 4-GPUs per node | [system/slurm](../checks/system/slurm/) |
| [slurm_response_check](../checks/system/slurm/slurm.py)<br>• %command=squeue | Slurm basic commands test (squeue, sacct) | [system/slurm](../checks/system/slurm/) |
| [slurm_response_check](../checks/system/slurm/slurm.py)<br>• %command=sacct | Slurm basic commands test (squeue, sacct) | [system/slurm](../checks/system/slurm/) |
| [SlurmQueueStatusCheck](../checks/system/slurm/slurm.py)<br>• %slurm_partition=debug | check system queue status (# of nodes) | [system/slurm](../checks/system/slurm/) |
| [SlurmQueueStatusCheck](../checks/system/slurm/slurm.py)<br>• %slurm_partition=normal* | check system queue status (# of nodes) | [system/slurm](../checks/system/slurm/) |
| [SlurmTransparentHugepagesCheck](../checks/system/slurm/slurm.py)<br>• %hugepages_options=default | Check Slurm transparent hugepages configuration | [system/slurm](../checks/system/slurm/) |
| [SlurmTransparentHugepagesCheck](../checks/system/slurm/slurm.py)<br>• %hugepages_options=always | Check Slurm transparent hugepages configuration | [system/slurm](../checks/system/slurm/) |
| [SlurmTransparentHugepagesCheck](../checks/system/slurm/slurm.py)<br>• %hugepages_options=madvise | Check Slurm transparent hugepages configuration | [system/slurm](../checks/system/slurm/) |
| [SlurmTransparentHugepagesCheck](../checks/system/slurm/slurm.py)<br>• %hugepages_options=never | Check Slurm transparent hugepages configuration | [system/slurm](../checks/system/slurm/) |
| [SlurmParanoidCheck](../checks/system/slurm/slurm.py) | Check that perf_event_paranoid enables per-process and system wideperformance monitoring | [system/slurm](../checks/system/slurm/) |
| [SlurmNoIsolCpus](../checks/system/slurm/slurm.py) | Check that isolcpus isn't enabled as it prevents threads from migrating<br>    between cores. This makes e.g. make jobs or OpenMPI threads all be stuck to<br>    one core. See e.g.<br>    https://www.kernel.org/doc/html/latest/admin-guide/kernel-parameters.html<br>    and https://access.redhat.com/solutions/480473 for more details. | [system/slurm](../checks/system/slurm/) |
| [NVreg_RestrictProfilingToAdminUsers](../checks/system/slurm/slurm.py) | Allow access to the GPU Performance Counters for NVIDIA tools:<br>    https://developer.nvidia.com/nvidia-development-tools-solutions-err_nvgpuctrperm-permission-issue-performance-counters | [system/slurm](../checks/system/slurm/) |
| [SlurmUvmPerfAccessCounterMigration](../checks/system/slurm/slurm.py) | Check that uvm_perf_access_counter_mimc_migration_enable is set to 0<br>    as it is buggy in older drivers. If the driver is at least version 565, the<br>    name of the option is different and should be set to the default (-1). | [system/slurm](../checks/system/slurm/) |
| [SlurmGPUGresTest](../checks/system/slurm/slurm.py) | Ensure that the Slurm GRES (Generic REsource Scheduling) of the<br>       number of gpus is correctly set on all the nodes of each partition.<br><br>       For the current partition, the test performs the following steps:<br>        1) count the number of nodes (node_count)<br>        2) count the number of nodes having Gres=gpu:N (gres_count) where<br>           N=num_devices from the configuration<br>        3) ensure that 1) and 2) match | [system/slurm](../checks/system/slurm/) |
| [Check_0001_SLEEP](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0001_SLEEP](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0002_SLEEP](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0002_SLEEP](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0003_FS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0003_FS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0004_FS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0004_FS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0005_PING](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0005_PING](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0006_PING](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0007_PING](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0008_PROXY](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0008_PROXY](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0009_DNS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0009_DNS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0010_DNS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0010_DNS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0011_DNS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0011_DNS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0012_NETIFACE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0012_NETIFACE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0013_NETIFACE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0013_NETIFACE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0014_NETIFACE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0014_NETIFACE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0015_NETIFACE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0015_NETIFACE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0016_NETIFACE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0016_NETIFACE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0017_NETIFACE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0017_NETIFACE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0018_NETIFACE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0018_NETIFACE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0019_NETIFACE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0019_NETIFACE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0020_NETIFACE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0020_NETIFACE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0021_NETIFACE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0021_NETIFACE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0022_LDAP](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0022_LDAP](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0023_LDAP](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0023_LDAP](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0024_OSINSTALL](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0024_OSINSTALL](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0025_OSINSTALL](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0025_OSINSTALL](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0026_OSSERVICE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0026_OSSERVICE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0027_OSSERVICE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0027_OSSERVICE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0028_OSSERVICE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0028_OSSERVICE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0029_TOOLS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0029_TOOLS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0030_TOOLS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0030_TOOLS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0031_TOOLS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0031_TOOLS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0032_TOOLS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0032_TOOLS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0033_TOOLS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0033_TOOLS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0034_MOUNTS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0034_MOUNTS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0035_MOUNTS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0035_MOUNTS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0036_MOUNTS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0036_MOUNTS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0037_MOUNTS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0037_MOUNTS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0038_MOUNTS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0038_MOUNTS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0039_MOUNTS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0039_MOUNTS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0040_MOUNTS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0040_MOUNTS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0041_MOUNTS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0041_MOUNTS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0042_MOUNTS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0042_MOUNTS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0043_MOUNTS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0043_MOUNTS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0044_MOUNTS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0044_MOUNTS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0045_MOUNTS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0045_MOUNTS](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0046_SLURM](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0047_SLURM](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0047_SLURM](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0048_SLURM](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0048_SLURM](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0049_SLURM](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0049_SLURM](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0050_VSBASE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0050_VSBASE](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0051_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0051_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0052_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0052_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0053_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0053_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0054_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0054_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0055_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0055_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0056_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0056_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0057_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0057_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0058_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0058_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0059_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0059_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0060_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0060_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0061_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0061_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0062_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0062_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0063_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0063_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0064_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [Check_0064_VSERVICES](../checks/system/integration/daint.py) | — | [system/integration](../checks/system/integration/) |
| [CXIGPULoopbackBW](../checks/system/network/cxi_gpu_loopback_bw.py) | — | [system/network](../checks/system/network/) |
| [CXIStatHSN](../checks/system/network/cxi_stat_hsn.py) | — | [system/network](../checks/system/network/) |
| [stuck_gpu_mem_test](../checks/system/io/fio.py) | Check for stuck GPU memory on GH200 | [system/io](../checks/system/io/) |
| [↳ fio_compile_test](../checks/system/io/fio.py) | Make sure that we can compile fio. | [system/io](../checks/system/io/) |
| [ddBlockSizeTest](../checks/system/io/dd_blk_size.py) | dd write tests with different block sizes | [system/io](../checks/system/io/) |
| [ddBlockSizeTest](../checks/system/io/dd_blk_size.py) | dd write tests with different block sizes | [system/io](../checks/system/io/) |
| [RunJobCE](../checks/system/ce/ce_import_run_image.py) | CE check with Dockerhub import and simple image run (ubuntu) | [system/ce](../checks/system/ce/) |
| [↳ enroot_import_image_dockerhub ~daint](../checks/system/ce/ce_import_run_image.py) | — | [system/ce](../checks/system/ce/) |
| [RunNVGPUJobCE](../checks/system/ce/ce_import_run_image.py) | CE check with NGC import and Stream job on GPU | [system/ce](../checks/system/ce/) |
| [↳ enroot_import_image_ngc ~daint](../checks/system/ce/ce_import_run_image.py) | — | [system/ce](../checks/system/ce/) |
| [NCCLTestsCE](../checks/microbenchmarks/xccl/xccl_tests.py)<br>• %test_name=all_reduce<br>• %image_tag=cuda12.9.1-ubuntu24.04 | Point-to-Point and All-Reduce NCCL tests with CE | [microbenchmarks/xccl](../checks/microbenchmarks/xccl/) |
| [NCCLTestsCE](../checks/microbenchmarks/xccl/xccl_tests.py)<br>• %test_name=sendrecv<br>• %image_tag=cuda12.9.1-ubuntu24.04 | Point-to-Point and All-Reduce NCCL tests with CE | [microbenchmarks/xccl](../checks/microbenchmarks/xccl/) |
| [StreamTest](../checks/microbenchmarks/cpu/stream/stream.py) | STREAM Benchmark | [microbenchmarks/cpu/stream](../checks/microbenchmarks/cpu/stream/) |
| [baremetal_cuda_node_burn](../checks/microbenchmarks/gpu/node_burn/baremetal-node-burn.py) | — | [microbenchmarks/gpu/node_burn](../checks/microbenchmarks/gpu/node_burn/) |
| [osu_pt2pt_check](../checks/microbenchmarks/mpi/osu/osu_tests.py)<br>• %benchmark_info=mpi.pt2pt.standard.osu_bw<br>• %osu_binaries.build_type=cpu | — | [microbenchmarks/mpi/osu](../checks/microbenchmarks/mpi/osu/) |
| [↳ build_osu_benchmarks ~daint:normal+PrgEnv-ce](../checks/microbenchmarks/mpi/osu/osu_tests.py)<br>• %build_type=cpu | — | [microbenchmarks/mpi/osu](../checks/microbenchmarks/mpi/osu/) |
| [↳ fetch_osu_benchmarks ~daint](../checks/microbenchmarks/mpi/osu/osu_tests.py) | — | [microbenchmarks/mpi/osu](../checks/microbenchmarks/mpi/osu/) |
| [osu_pt2pt_check](../checks/microbenchmarks/mpi/osu/osu_tests.py)<br>• %benchmark_info=mpi.pt2pt.standard.osu_latency<br>• %osu_binaries.build_type=cpu | — | [microbenchmarks/mpi/osu](../checks/microbenchmarks/mpi/osu/) |
| [↳ build_osu_benchmarks ~daint:normal+PrgEnv-ce](../checks/microbenchmarks/mpi/osu/osu_tests.py)<br>• %build_type=cpu | — | [microbenchmarks/mpi/osu](../checks/microbenchmarks/mpi/osu/) |
| [↳ fetch_osu_benchmarks ~daint](../checks/microbenchmarks/mpi/osu/osu_tests.py) | — | [microbenchmarks/mpi/osu](../checks/microbenchmarks/mpi/osu/) |
| [osu_collective_check](../checks/microbenchmarks/mpi/osu/osu_tests.py)<br>• %benchmark_info=mpi.collective.blocking.osu_alltoall<br>• %num_nodes=6<br>• %osu_binaries.build_type=cpu | — | [microbenchmarks/mpi/osu](../checks/microbenchmarks/mpi/osu/) |
| [↳ build_osu_benchmarks ~daint:normal+PrgEnv-ce](../checks/microbenchmarks/mpi/osu/osu_tests.py)<br>• %build_type=cpu | — | [microbenchmarks/mpi/osu](../checks/microbenchmarks/mpi/osu/) |
| [↳ fetch_osu_benchmarks ~daint](../checks/microbenchmarks/mpi/osu/osu_tests.py) | — | [microbenchmarks/mpi/osu](../checks/microbenchmarks/mpi/osu/) |
| [osu_collective_check](../checks/microbenchmarks/mpi/osu/osu_tests.py)<br>• %benchmark_info=mpi.collective.blocking.osu_allreduce<br>• %num_nodes=6<br>• %osu_binaries.build_type=cpu | — | [microbenchmarks/mpi/osu](../checks/microbenchmarks/mpi/osu/) |
| [↳ build_osu_benchmarks ~daint:normal+PrgEnv-ce](../checks/microbenchmarks/mpi/osu/osu_tests.py)<br>• %build_type=cpu | — | [microbenchmarks/mpi/osu](../checks/microbenchmarks/mpi/osu/) |
| [↳ fetch_osu_benchmarks ~daint](../checks/microbenchmarks/mpi/osu/osu_tests.py) | — | [microbenchmarks/mpi/osu](../checks/microbenchmarks/mpi/osu/) |
| [CudaNodeBurnGemmCE](../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) | GPU Node burn GEMM test for A100/GH200 using CE | [microbenchmarks/cpu_gpu/node_burn](../checks/microbenchmarks/cpu_gpu/node_burn/) |
| [CPUNodeBurnGemmCE](../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) | CPU Node burn GEMM test for A100/GH200-nodes using CE | [microbenchmarks/cpu_gpu/node_burn](../checks/microbenchmarks/cpu_gpu/node_burn/) |
| [CudaNodeBurnStreamCE](../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) | GPU Node burn Stream test for A100/GH200 using CE | [microbenchmarks/cpu_gpu/node_burn](../checks/microbenchmarks/cpu_gpu/node_burn/) |
| [CPUNodeBurnStreamCE](../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) | CPU Node burn Stream test for A100/GH200-nodes using CE | [microbenchmarks/cpu_gpu/node_burn](../checks/microbenchmarks/cpu_gpu/node_burn/) |
| [PyTorchMegatronLM_CE](../checks/apps/pytorch/pytorch_megatronlm.py)<br>• %model=llama3-8b | — | [apps/pytorch](../checks/apps/pytorch/) |
| [PyTorchMegatronLM_CE](../checks/apps/pytorch/pytorch_megatronlm.py)<br>• %model=llama3-70b | — | [apps/pytorch](../checks/apps/pytorch/) |
| [PyTorchMegatronLM_CE_apertus70b](../checks/apps/pytorch/pytorch_megatronlm.py)<br>• %model=apertus3-70b | — | [apps/pytorch](../checks/apps/pytorch/) |
| [PyTorchNCCLAllReduce](../checks/apps/pytorch/pytorch_allreduce.py)<br>• %image=nvcr.io#nvidia/pytorch:25.06-py3 | All-reduce PyTorch benchmark with CE (NCCL version) | [apps/pytorch](../checks/apps/pytorch/) |
| [test_image_tag_retrieval](../checks/apps/pytorch/pytorch_nvidia.py) | — | [apps/pytorch](../checks/apps/pytorch/) |
| [PyTorchDdpCeNv](../checks/apps/pytorch/pytorch_nvidia.py)<br>• %num_nodes=1<br>• %aws_ofi_nccl=True<br>• %image=nvcr.io#nvidia/pytorch:25.06-py3 | Check the training throughput using the ContainerEngine and NVIDIA NGC | [apps/pytorch](../checks/apps/pytorch/) |
| [PyTorchDdpCeNvlarge](../checks/apps/pytorch/pytorch_nvidia.py)<br>• %num_nodes=3<br>• %aws_ofi_nccl=True<br>• %image=nvcr.io#nvidia/pytorch:25.06-py3 | Check the training throughput using the ContainerEngine and NVIDIA NGC | [apps/pytorch](../checks/apps/pytorch/) |
| [PyTorchDdpCeNvlarge](../checks/apps/pytorch/pytorch_nvidia.py)<br>• %num_nodes=8<br>• %aws_ofi_nccl=True<br>• %image=nvcr.io#nvidia/pytorch:25.06-py3 | Check the training throughput using the ContainerEngine and NVIDIA NGC | [apps/pytorch](../checks/apps/pytorch/) |
| [MLperfStorageCECleanup](../checks/apps/pytorch/mlperf_storage_ce.py)<br>• %mlperf.mlperf_data.base_dir=/capstor/scratch/cscs/ | — | [apps/pytorch](../checks/apps/pytorch/) |
| [↳ MLperfStorageCE ~daint:normal+builtin](../checks/apps/pytorch/mlperf_storage_ce.py)<br>• %mlperf_data.base_dir=/capstor/scratch/cscs/ | — | [apps/pytorch](../checks/apps/pytorch/) |
| [↳ mlperf_storage_datagen_ce ~daint:normal+builtin](../checks/apps/pytorch/mlperf_storage_ce.py)<br>• %base_dir=/capstor/scratch/cscs/ | — | [apps/pytorch](../checks/apps/pytorch/) |
| [MLperfStorageCECleanup](../checks/apps/pytorch/mlperf_storage_ce.py)<br>• %mlperf.mlperf_data.base_dir=/iopsstor/scratch/cscs/ | — | [apps/pytorch](../checks/apps/pytorch/) |
| [↳ MLperfStorageCE ~daint:normal+builtin](../checks/apps/pytorch/mlperf_storage_ce.py)<br>• %mlperf_data.base_dir=/iopsstor/scratch/cscs/ | — | [apps/pytorch](../checks/apps/pytorch/) |
| [↳ mlperf_storage_datagen_ce ~daint:normal+builtin](../checks/apps/pytorch/mlperf_storage_ce.py)<br>• %base_dir=/iopsstor/scratch/cscs/ | — | [apps/pytorch](../checks/apps/pytorch/) |
| [LibSciAccSymLinkTest](../checks/compile/libsci_acc_symlink.py)<br>• %lib_name=libsci_acc_cray_nv90 | LibSciAcc symlink check of libsci_acc_cray_nv90 | [compile](../checks/compile/) |
| [LibSciAccSymLinkTest](../checks/compile/libsci_acc_symlink.py)<br>• %lib_name=libsci_acc_cray_nv90 | LibSciAcc symlink check of libsci_acc_cray_nv90 | [compile](../checks/compile/) |
| [LibSciAccSymLinkTest](../checks/compile/libsci_acc_symlink.py)<br>• %lib_name=libsci_acc_gnu_nv90 | LibSciAcc symlink check of libsci_acc_gnu_nv90 | [compile](../checks/compile/) |
| [LibSciAccSymLinkTest](../checks/compile/libsci_acc_symlink.py)<br>• %lib_name=libsci_acc_gnu_nv90 | LibSciAcc symlink check of libsci_acc_gnu_nv90 | [compile](../checks/compile/) |
| [DefaultPrgEnvCheck](../checks/prgenv/environ_check.py) | Ensure PrgEnv-cray is loaded by default | [prgenv](../checks/prgenv/) |
| [CrayVariablesCheckDaint](../checks/prgenv/environ_check.py)<br>• %cray_module=cray-hdf5 | Check for standard Cray variables | [prgenv](../checks/prgenv/) |
| [CrayVariablesCheckDaint](../checks/prgenv/environ_check.py)<br>• %cray_module=cray-hdf5-parallel | Check for standard Cray variables | [prgenv](../checks/prgenv/) |
| [CrayVariablesCheckDaint](../checks/prgenv/environ_check.py)<br>• %cray_module=cray-mpich | Check for standard Cray variables | [prgenv](../checks/prgenv/) |
| [CrayVariablesCheckDaint](../checks/prgenv/environ_check.py)<br>• %cray_module=cray-R | Check for standard Cray variables | [prgenv](../checks/prgenv/) |
| [CrayVariablesCheckDaint](../checks/prgenv/environ_check.py)<br>• %cray_module=cudatoolkit | Check for standard Cray variables | [prgenv](../checks/prgenv/) |
| [CrayVariablesCheckDaint](../checks/prgenv/environ_check.py)<br>• %cray_module=papi | Check for standard Cray variables | [prgenv](../checks/prgenv/) |
| [OneThreadPerLogicalCoreOpenMP](../checks/prgenv/affinity_check.py) | Pin one OMP thread per CPU. | [prgenv](../checks/prgenv/) |
| [↳ CompileAffinityTool ~daint:normal+PrgEnv-ce](../checks/prgenv/affinity_check.py) | — | [prgenv](../checks/prgenv/) |
| [OneThreadPerPhysicalCoreOpenMP](../checks/prgenv/affinity_check.py) | Pin one OMP thread per core. | [prgenv](../checks/prgenv/) |
| [↳ CompileAffinityTool ~daint:normal+PrgEnv-ce](../checks/prgenv/affinity_check.py) | — | [prgenv](../checks/prgenv/) |
| [OneThreadPerPhysicalCoreOpenMPnomt](../checks/prgenv/affinity_check.py) | Pin one OMP thread per core wo. multithreading. | [prgenv](../checks/prgenv/) |
| [↳ CompileAffinityTool ~daint:normal+PrgEnv-ce](../checks/prgenv/affinity_check.py) | — | [prgenv](../checks/prgenv/) |
| [OneThreadPerSocketOpenMP](../checks/prgenv/affinity_check.py) | Pin one OMP thread per socket. | [prgenv](../checks/prgenv/) |
| [↳ CompileAffinityTool ~daint:normal+PrgEnv-ce](../checks/prgenv/affinity_check.py) | — | [prgenv](../checks/prgenv/) |
| [OneTaskPerSocketOpenMPnomt](../checks/prgenv/affinity_check.py) | One task per socket - wo. multithreading. | [prgenv](../checks/prgenv/) |
| [↳ CompileAffinityTool ~daint:normal+PrgEnv-ce](../checks/prgenv/affinity_check.py) | — | [prgenv](../checks/prgenv/) |
| [OneTaskPerSocketOpenMP](../checks/prgenv/affinity_check.py) | One task per socket - w. multithreading. | [prgenv](../checks/prgenv/) |
| [↳ CompileAffinityTool ~daint:normal+PrgEnv-ce](../checks/prgenv/affinity_check.py) | — | [prgenv](../checks/prgenv/) |
| [ConsecutiveSocketFilling](../checks/prgenv/affinity_check.py) | — | [prgenv](../checks/prgenv/) |
| [↳ CompileAffinityTool ~daint:normal+PrgEnv-ce](../checks/prgenv/affinity_check.py) | — | [prgenv](../checks/prgenv/) |
| [AlternateSocketFilling](../checks/prgenv/affinity_check.py) | — | [prgenv](../checks/prgenv/) |
| [↳ CompileAffinityTool ~daint:normal+PrgEnv-ce](../checks/prgenv/affinity_check.py) | — | [prgenv](../checks/prgenv/) |
| [OneTaskPerNumaNode](../checks/prgenv/affinity_check.py) | — | [prgenv](../checks/prgenv/) |
| [↳ CompileAffinityToolNoOmp ~daint:normal+PrgEnv-ce](../checks/prgenv/affinity_check.py) | — | [prgenv](../checks/prgenv/) |
| [MpiInitTest](../checks/prgenv/mpi.py) | — | [prgenv](../checks/prgenv/) |
| [cpi_build_test](../checks/prgenv/mpi_cpi.py) | Simple mpi test | [prgenv](../checks/prgenv/) |
| [HelloWorldTestSerial](../checks/prgenv/helloworld.py)<br>• %linking=dynamic<br>• %lang=c | C Hello, World Serial Dynamic | [prgenv](../checks/prgenv/) |
| [HelloWorldTestSerial](../checks/prgenv/helloworld.py)<br>• %linking=dynamic<br>• %lang=cpp | C++ Hello, World Serial Dynamic | [prgenv](../checks/prgenv/) |
| [HelloWorldTestSerial](../checks/prgenv/helloworld.py)<br>• %linking=dynamic<br>• %lang=F90 | Fortran 90 Hello, World Serial Dynamic | [prgenv](../checks/prgenv/) |
| [HelloWorldTestOpenMP](../checks/prgenv/helloworld.py)<br>• %linking=dynamic<br>• %lang=c | C Hello, World OpenMP Dynamic | [prgenv](../checks/prgenv/) |
| [HelloWorldTestOpenMP](../checks/prgenv/helloworld.py)<br>• %linking=dynamic<br>• %lang=cpp | C++ Hello, World OpenMP Dynamic | [prgenv](../checks/prgenv/) |
| [HelloWorldTestOpenMP](../checks/prgenv/helloworld.py)<br>• %linking=dynamic<br>• %lang=F90 | Fortran 90 Hello, World OpenMP Dynamic | [prgenv](../checks/prgenv/) |
| [HelloWorldTestMPI](../checks/prgenv/helloworld.py)<br>• %linking=dynamic<br>• %lang=c | C Hello, World MPI Dynamic | [prgenv](../checks/prgenv/) |
| [HelloWorldTestMPI](../checks/prgenv/helloworld.py)<br>• %linking=dynamic<br>• %lang=cpp | C++ Hello, World MPI Dynamic | [prgenv](../checks/prgenv/) |
| [HelloWorldTestMPI](../checks/prgenv/helloworld.py)<br>• %linking=dynamic<br>• %lang=F90 | Fortran 90 Hello, World MPI Dynamic | [prgenv](../checks/prgenv/) |
| [HelloWorldTestMPIOpenMP](../checks/prgenv/helloworld.py)<br>• %linking=dynamic<br>• %lang=c | C Hello, World MPI + OpenMP Dynamic | [prgenv](../checks/prgenv/) |
| [HelloWorldTestMPIOpenMP](../checks/prgenv/helloworld.py)<br>• %linking=dynamic<br>• %lang=cpp | C++ Hello, World MPI + OpenMP Dynamic | [prgenv](../checks/prgenv/) |
| [HelloWorldTestMPIOpenMP](../checks/prgenv/helloworld.py)<br>• %linking=dynamic<br>• %lang=F90 | Fortran 90 Hello, World MPI + OpenMP Dynamic | [prgenv](../checks/prgenv/) |
| [SSH_CE](../checks/containers/container_engine/ssh.py) | Checks if SSH is available with CE | [containers/container_engine](../checks/containers/container_engine/) |
| [OMB_MPICH_CE](../checks/containers/container_engine/omb.py)<br>• %test_name=pt2pt/osu_bw | OSU Micro-benchmarks for MPICH/CE (Point-to-Point and All-to-All) | [containers/container_engine](../checks/containers/container_engine/) |
| [OMB_MPICH_CE](../checks/containers/container_engine/omb.py)<br>• %test_name=collective/osu_alltoall | OSU Micro-benchmarks for MPICH/CE (Point-to-Point and All-to-All) | [containers/container_engine](../checks/containers/container_engine/) |
| [OMB_OMPI_CE](../checks/containers/container_engine/omb.py)<br>• %test_name=pt2pt/osu_bw | OSU Micro-benchmarks for OpenMPI/CE (Point-to-Point and All-to-All) | [containers/container_engine](../checks/containers/container_engine/) |
| [OMB_OMPI_CE](../checks/containers/container_engine/omb.py)<br>• %test_name=collective/osu_alltoall | OSU Micro-benchmarks for OpenMPI/CE (Point-to-Point and All-to-All) | [containers/container_engine](../checks/containers/container_engine/) |
| [CudaNBodyCheckCE](../checks/containers/container_engine/check_cuda_nbody.py) | Single-node N-Body test for GPUs using CE (from CUDA samples) | [containers/container_engine](../checks/containers/container_engine/) |
| [CUDA_MPS_CE](../checks/containers/container_engine/cuda_mps.py) | Check for CUDA MPS with CE | [containers/container_engine](../checks/containers/container_engine/) |
| [CPE_HDF5Test](../checks/libraries/io/hdf5.py)<br>• %lang=cpp | — | [libraries/io](../checks/libraries/io/) |
| [CPE_HDF5Test](../checks/libraries/io/hdf5.py)<br>• %lang=f90 | — | [libraries/io](../checks/libraries/io/) |