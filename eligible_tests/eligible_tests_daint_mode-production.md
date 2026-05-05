## Eligible ReFrame Tests on daint

- Filters:
  - system: `daint`
  - mode: `production`
  - checks: `100`
- Generated: `2026-05-05 17:20:21 +0200`

| Test name | Description | Category |
|----------|-------------|----------|
| [InvalidAccount](../checks/system/slurm/invalid_acc.py) | Check if Slurm accepts job submission using an invalid account. Reframe should raise a failure if the job starts. | [system/slurm](../checks/system/slurm/) |
| [HostnameCheck](../checks/system/slurm/slurm.py) | Check hostname pattern nidXXXXXX on the CN | [system/slurm](../checks/system/slurm/) |
| [EnvironmentVariableCheck](../checks/system/slurm/slurm.py) | Test if user env variables are propagated to CN | [system/slurm](../checks/system/slurm/) |
| [NvidiaSmiDriverVersion](../checks/system/slurm/slurm.py) | Nvidia-smi sanity check (output driver version) | [system/slurm](../checks/system/slurm/) |
| [DefaultRequestGPUSetsGRES](../checks/system/slurm/slurm.py) | Checks slurm config for 4-GPUs per node | [system/slurm](../checks/system/slurm/) |
| [SlurmTransparentHugepagesCheck](../checks/system/slurm/slurm.py)<br>• %hugepages_options=default | Check Slurm transparent hugepages configuration | [system/slurm](../checks/system/slurm/) |
| [SlurmTransparentHugepagesCheck](../checks/system/slurm/slurm.py)<br>• %hugepages_options=always | Check Slurm transparent hugepages configuration | [system/slurm](../checks/system/slurm/) |
| [SlurmTransparentHugepagesCheck](../checks/system/slurm/slurm.py)<br>• %hugepages_options=madvise | Check Slurm transparent hugepages configuration | [system/slurm](../checks/system/slurm/) |
| [SlurmTransparentHugepagesCheck](../checks/system/slurm/slurm.py)<br>• %hugepages_options=never | Check Slurm transparent hugepages configuration | [system/slurm](../checks/system/slurm/) |
| [SlurmParanoidCheck](../checks/system/slurm/slurm.py) | Check that perf_event_paranoid enables per-process and system wideperformance monitoring | [system/slurm](../checks/system/slurm/) |
| [SlurmNoIsolCpus](../checks/system/slurm/slurm.py) | Check that isolcpus isn't enabled as it prevents threads from migrating between cores. This makes e.g. make jobs or OpenMPI threads all be stuck to one core. See e.g. | [system/slurm](../checks/system/slurm/) |
| [NVreg_RestrictProfilingToAdminUsers](../checks/system/slurm/slurm.py) | Allow access to the GPU Performance Counters for NVIDIA tools: | [system/slurm](../checks/system/slurm/) |
| [SlurmUvmPerfAccessCounterMigration](../checks/system/slurm/slurm.py) | Check that uvm_perf_access_counter_mimc_migration_enable is set to 0 as it is buggy in older drivers. If the driver is at least version 565, the name of the option is different and should be set to the default (-1). | [system/slurm](../checks/system/slurm/) |
| [SlurmGPUGresTest](../checks/system/slurm/slurm.py) | Ensure that the Slurm GRES (Generic REsource Scheduling) of the number of gpus is correctly set on all the nodes of each partition. For the current partition, the test performs the following steps: 1) count the number of nodes (node_count) 2) count the number of nodes having Gres=gpu:N (gres_count) where N=num_devices from the configuration 3) ensure that 1) and 2) match | [system/slurm](../checks/system/slurm/) |
| [Check_0001_SLEEP](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0002_SLEEP](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0003_FS](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0004_FS](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0005_PING](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0006_PING](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0007_PING](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0008_PROXY](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0009_DNS](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0010_DNS](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0011_DNS](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0012_NETIFACE](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0013_NETIFACE](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0014_NETIFACE](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0015_NETIFACE](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0016_NETIFACE](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0017_NETIFACE](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0018_NETIFACE](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0019_NETIFACE](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0020_NETIFACE](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0021_NETIFACE](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0022_LDAP](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0023_LDAP](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0024_OSINSTALL](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0025_OSINSTALL](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0026_OSSERVICE](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0027_OSSERVICE](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0028_OSSERVICE](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0029_TOOLS](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0030_TOOLS](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0031_TOOLS](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0032_TOOLS](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0033_TOOLS](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0034_MOUNTS](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0035_MOUNTS](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0036_MOUNTS](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0037_MOUNTS](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0038_MOUNTS](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0039_MOUNTS](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0040_MOUNTS](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0041_MOUNTS](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0042_MOUNTS](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0043_MOUNTS](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0044_MOUNTS](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0045_MOUNTS](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0046_SLURM](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0047_SLURM](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0048_SLURM](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0049_SLURM](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0050_VSBASE](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0051_VSERVICES](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0052_VSERVICES](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0053_VSERVICES](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0054_VSERVICES](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0055_VSERVICES](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0056_VSERVICES](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0057_VSERVICES](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0058_VSERVICES](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0059_VSERVICES](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0060_VSERVICES](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0061_VSERVICES](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0062_VSERVICES](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0063_VSERVICES](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [Check_0064_VSERVICES](../checks/system/integration/daint.py) | <none> | [system/integration](../checks/system/integration/) |
| [ddBlockSizeTest](../checks/system/io/dd_blk_size.py) | dd write tests with different block sizes | [system/io](../checks/system/io/) |
| [RunJobCE](../checks/system/ce/ce_import_run_image.py) | <none> | [system/ce](../checks/system/ce/) |
| [RunNVGPUJobCE](../checks/system/ce/ce_import_run_image.py) | <none> | [system/ce](../checks/system/ce/) |
| [NCCLTestsCE](../checks/microbenchmarks/xccl/xccl_tests.py)<br>• %test_name=all_reduce<br>• %image_tag=cuda12.9.1-ubuntu24.04 | Point-to-Point and All-Reduce NCCL tests with CE | [microbenchmarks/xccl](../checks/microbenchmarks/xccl/) |
| [NCCLTestsCE](../checks/microbenchmarks/xccl/xccl_tests.py)<br>• %test_name=sendrecv<br>• %image_tag=cuda12.9.1-ubuntu24.04 | Point-to-Point and All-Reduce NCCL tests with CE | [microbenchmarks/xccl](../checks/microbenchmarks/xccl/) |
| [CudaNodeBurnGemmCE](../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) | GPU Node burn GEMM test for A100/GH200 using CE | [microbenchmarks/cpu_gpu/node_burn](../checks/microbenchmarks/cpu_gpu/node_burn/) |
| [CPUNodeBurnGemmCE](../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) | CPU Node burn GEMM test for A100/GH200-nodes using CE | [microbenchmarks/cpu_gpu/node_burn](../checks/microbenchmarks/cpu_gpu/node_burn/) |
| [CudaNodeBurnStreamCE](../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) | GPU Node burn Stream test for A100/GH200 using CE | [microbenchmarks/cpu_gpu/node_burn](../checks/microbenchmarks/cpu_gpu/node_burn/) |
| [CPUNodeBurnStreamCE](../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) | CPU Node burn Stream test for A100/GH200-nodes using CE | [microbenchmarks/cpu_gpu/node_burn](../checks/microbenchmarks/cpu_gpu/node_burn/) |
| [PyTorchMegatronLM_CE](../checks/apps/pytorch/pytorch_megatronlm.py)<br>• %model=llama3-8b | <none> | [apps/pytorch](../checks/apps/pytorch/) |
| [PyTorchMegatronLM_CE](../checks/apps/pytorch/pytorch_megatronlm.py)<br>• %model=llama3-70b | <none> | [apps/pytorch](../checks/apps/pytorch/) |
| [PyTorchNCCLAllReduce](../checks/apps/pytorch/pytorch_allreduce.py)<br>• %image=nvcr.io#nvidia/pytorch:25.06-py3 | All-reduce PyTorch benchmark with CE (NCCL version) | [apps/pytorch](../checks/apps/pytorch/) |
| [PyTorchDdpCeNv](../checks/apps/pytorch/pytorch_nvidia.py)<br>• %num_nodes=1<br>• %aws_ofi_nccl=True<br>• %image=nvcr.io#nvidia/pytorch:25.06-py3 | Check the training throughput using the ContainerEngine and NVIDIA NGC | [apps/pytorch](../checks/apps/pytorch/) |
| [PyTorchDdpCeNvlarge](../checks/apps/pytorch/pytorch_nvidia.py)<br>• %num_nodes=3<br>• %aws_ofi_nccl=True<br>• %image=nvcr.io#nvidia/pytorch:25.06-py3 | Check the training throughput using the ContainerEngine and NVIDIA NGC | [apps/pytorch](../checks/apps/pytorch/) |
| [PyTorchDdpCeNvlarge](../checks/apps/pytorch/pytorch_nvidia.py)<br>• %num_nodes=8<br>• %aws_ofi_nccl=True<br>• %image=nvcr.io#nvidia/pytorch:25.06-py3 | Check the training throughput using the ContainerEngine and NVIDIA NGC | [apps/pytorch](../checks/apps/pytorch/) |
| [SSH_CE](../checks/containers/container_engine/ssh.py) | Checks if SSH is available with CE | [containers/container_engine](../checks/containers/container_engine/) |
| [OMB_MPICH_CE](../checks/containers/container_engine/omb.py)<br>• %test_name=pt2pt/osu_bw | OSU Micro-benchmarks for MPICH/CE (Point-to-Point and All-to-All) | [containers/container_engine](../checks/containers/container_engine/) |
| [OMB_MPICH_CE](../checks/containers/container_engine/omb.py)<br>• %test_name=collective/osu_alltoall | OSU Micro-benchmarks for MPICH/CE (Point-to-Point and All-to-All) | [containers/container_engine](../checks/containers/container_engine/) |
| [OMB_OMPI_CE](../checks/containers/container_engine/omb.py)<br>• %test_name=pt2pt/osu_bw | OSU Micro-benchmarks for OpenMPI/CE (Point-to-Point and All-to-All) | [containers/container_engine](../checks/containers/container_engine/) |
| [OMB_OMPI_CE](../checks/containers/container_engine/omb.py)<br>• %test_name=collective/osu_alltoall | OSU Micro-benchmarks for OpenMPI/CE (Point-to-Point and All-to-All) | [containers/container_engine](../checks/containers/container_engine/) |
| [CudaNBodyCheckCE](../checks/containers/container_engine/check_cuda_nbody.py) | Single-node N-Body test for GPUs using CE (from CUDA samples) | [containers/container_engine](../checks/containers/container_engine/) |
| [CUDA_MPS_CE](../checks/containers/container_engine/cuda_mps.py) | Check for CUDA MPS with CE | [containers/container_engine](../checks/containers/container_engine/) |