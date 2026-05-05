## Eligible ReFrame Tests on daint

- Filters:
  - system: `daint`
  - mode: `maintenance`
  - checks: `104`
- Generated: `2026-05-05 16:41:10 +0200`

| Test name | Description | Category |
|----------|-------------|----------|
| ../checks/system/gssr/dcgm_hook.py | Check DCGM executable and libraries are installed | ../checks/system/gssr/ |
| ../checks/system/gssr/dcgm_hook.py<br>• %pytorch_image_tag=25.01-py3_nvrtc-12.9 | Check DCGM CE hook is working with gssr | ../checks/system/gssr/ |
| ../checks/system/slurm/invalid_acc.py | Check if Slurm accepts job submission using an invalid account. Reframe should raise a failure if the job starts. | ../checks/system/slurm/ |
| ../checks/system/slurm/slurm.py | Check hostname pattern nidXXXXXX on the CN | ../checks/system/slurm/ |
| ../checks/system/slurm/slurm.py | Test if user env variables are propagated to CN | ../checks/system/slurm/ |
| ../checks/system/slurm/slurm.py | Nvidia-smi sanity check (output driver version) | ../checks/system/slurm/ |
| ../checks/system/slurm/slurm.py | Checks slurm config for 4-GPUs per node | ../checks/system/slurm/ |
| ../checks/system/slurm/slurm.py<br>• %hugepages_options=default | Check Slurm transparent hugepages configuration | ../checks/system/slurm/ |
| ../checks/system/slurm/slurm.py<br>• %hugepages_options=always | Check Slurm transparent hugepages configuration | ../checks/system/slurm/ |
| ../checks/system/slurm/slurm.py<br>• %hugepages_options=madvise | Check Slurm transparent hugepages configuration | ../checks/system/slurm/ |
| ../checks/system/slurm/slurm.py<br>• %hugepages_options=never | Check Slurm transparent hugepages configuration | ../checks/system/slurm/ |
| ../checks/system/slurm/slurm.py | Check that perf_event_paranoid enables per-process and system wideperformance monitoring | ../checks/system/slurm/ |
| ../checks/system/slurm/slurm.py | Check that isolcpus isn't enabled as it prevents threads from migrating between cores. This makes e.g. make jobs or OpenMPI threads all be stuck to one core. See e.g. | ../checks/system/slurm/ |
| ../checks/system/slurm/slurm.py | Allow access to the GPU Performance Counters for NVIDIA tools: | ../checks/system/slurm/ |
| ../checks/system/slurm/slurm.py | Check that uvm_perf_access_counter_mimc_migration_enable is set to 0 as it is buggy in older drivers. If the driver is at least version 565, the name of the option is different and should be set to the default (-1). | ../checks/system/slurm/ |
| ../checks/system/slurm/slurm.py | Ensure that the Slurm GRES (Generic REsource Scheduling) of the number of gpus is correctly set on all the nodes of each partition. For the current partition, the test performs the following steps: 1) count the number of nodes (node_count) 2) count the number of nodes having Gres=gpu:N (gres_count) where N=num_devices from the configuration 3) ensure that 1) and 2) match | ../checks/system/slurm/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/integration/daint.py | <none> | ../checks/system/integration/ |
| ../checks/system/io/fio.py | Make sure that we can compile fio. | ../checks/system/io/ |
| ../checks/system/io/dd_blk_size.py | dd write tests with different block sizes | ../checks/system/io/ |
| ../checks/system/ce/ce_import_run_image.py | <none> | ../checks/system/ce/ |
| ../checks/system/ce/ce_import_run_image.py | <none> | ../checks/system/ce/ |
| ../checks/microbenchmarks/xccl/xccl_tests.py<br>• %test_name=all_reduce<br>• %image_tag=cuda12.9.1-ubuntu24.04 | Point-to-Point and All-Reduce NCCL tests with CE | ../checks/microbenchmarks/xccl/ |
| ../checks/microbenchmarks/xccl/xccl_tests.py<br>• %test_name=sendrecv<br>• %image_tag=cuda12.9.1-ubuntu24.04 | Point-to-Point and All-Reduce NCCL tests with CE | ../checks/microbenchmarks/xccl/ |
| ../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py | GPU Node burn GEMM test for A100/GH200 using CE | ../checks/microbenchmarks/cpu_gpu/node_burn/ |
| ../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py | CPU Node burn GEMM test for A100/GH200-nodes using CE | ../checks/microbenchmarks/cpu_gpu/node_burn/ |
| ../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py | GPU Node burn Stream test for A100/GH200 using CE | ../checks/microbenchmarks/cpu_gpu/node_burn/ |
| ../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py | CPU Node burn Stream test for A100/GH200-nodes using CE | ../checks/microbenchmarks/cpu_gpu/node_burn/ |
| ../checks/apps/pytorch/pytorch_megatronlm.py<br>• %model=llama3-8b | <none> | ../checks/apps/pytorch/ |
| ../checks/apps/pytorch/pytorch_megatronlm.py<br>• %model=llama3-70b | <none> | ../checks/apps/pytorch/ |
| ../checks/apps/pytorch/pytorch_allreduce.py<br>• %image=nvcr.io#nvidia/pytorch:25.06-py3 | All-reduce PyTorch benchmark with CE (NCCL version) | ../checks/apps/pytorch/ |
| ../checks/apps/pytorch/pytorch_nvidia.py<br>• %num_nodes=1<br>• %aws_ofi_nccl=True<br>• %image=nvcr.io#nvidia/pytorch:25.06-py3 | Check the training throughput using the ContainerEngine and NVIDIA NGC | ../checks/apps/pytorch/ |
| ../checks/apps/pytorch/pytorch_nvidia.py<br>• %num_nodes=3<br>• %aws_ofi_nccl=True<br>• %image=nvcr.io#nvidia/pytorch:25.06-py3 | Check the training throughput using the ContainerEngine and NVIDIA NGC | ../checks/apps/pytorch/ |
| ../checks/apps/pytorch/pytorch_nvidia.py<br>• %num_nodes=8<br>• %aws_ofi_nccl=True<br>• %image=nvcr.io#nvidia/pytorch:25.06-py3 | Check the training throughput using the ContainerEngine and NVIDIA NGC | ../checks/apps/pytorch/ |
| ../checks/containers/container_engine/ssh.py | Checks if SSH is available with CE | ../checks/containers/container_engine/ |
| ../checks/containers/container_engine/omb.py<br>• %test_name=pt2pt/osu_bw | OSU Micro-benchmarks for MPICH/CE (Point-to-Point and All-to-All) | ../checks/containers/container_engine/ |
| ../checks/containers/container_engine/omb.py<br>• %test_name=collective/osu_alltoall | OSU Micro-benchmarks for MPICH/CE (Point-to-Point and All-to-All) | ../checks/containers/container_engine/ |
| ../checks/containers/container_engine/omb.py<br>• %test_name=pt2pt/osu_bw | OSU Micro-benchmarks for OpenMPI/CE (Point-to-Point and All-to-All) | ../checks/containers/container_engine/ |
| ../checks/containers/container_engine/omb.py<br>• %test_name=collective/osu_alltoall | OSU Micro-benchmarks for OpenMPI/CE (Point-to-Point and All-to-All) | ../checks/containers/container_engine/ |
| ../checks/containers/container_engine/check_cuda_nbody.py | Single-node N-Body test for GPUs using CE (from CUDA samples) | ../checks/containers/container_engine/ |
| ../checks/containers/container_engine/cuda_mps.py | Check for CUDA MPS with CE | ../checks/containers/container_engine/ |