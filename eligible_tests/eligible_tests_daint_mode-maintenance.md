## Eligible ReFrame Tests on daint

- Filters:
  - system: `daint`
  - mode: `maintenance`
  - checks: `103`
- Generated: `2026-05-13 15:43:39 +0200`

| Test name | Description | Category |
|----------|-------------|----------|
| [PyTorchNCCLAllReduce](../checks/apps/pytorch/pytorch_allreduce.py)<br>• %image=nvcr.io#nvidia/pytorch:25.06-py3 | All-reduce PyTorch benchmark with CE (NCCL version) | [apps/pytorch](../checks/apps/pytorch/) |
| [PyTorchMegatronLM_CE](../checks/apps/pytorch/pytorch_megatronlm.py)<br>• %model=llama3-8b | <none> | [apps/pytorch](../checks/apps/pytorch/) |
| [PyTorchMegatronLM_CE](../checks/apps/pytorch/pytorch_megatronlm.py)<br>• %model=llama3-70b | <none> | [apps/pytorch](../checks/apps/pytorch/) |
| [PyTorchDdpCeNv](../checks/apps/pytorch/pytorch_nvidia.py)<br>• %num_nodes=1<br>• %aws_ofi_nccl=True<br>• %image=nvcr.io#nvidia/pytorch:25.06-py3 | Check the training throughput using the ContainerEngine and NVIDIA NGC | [apps/pytorch](../checks/apps/pytorch/) |
| [PyTorchDdpCeNvlarge](../checks/apps/pytorch/pytorch_nvidia.py)<br>• %num_nodes=3<br>• %aws_ofi_nccl=True<br>• %image=nvcr.io#nvidia/pytorch:25.06-py3 | Check the training throughput using the ContainerEngine and NVIDIA NGC | [apps/pytorch](../checks/apps/pytorch/) |
| [PyTorchDdpCeNvlarge](../checks/apps/pytorch/pytorch_nvidia.py)<br>• %num_nodes=8<br>• %aws_ofi_nccl=True<br>• %image=nvcr.io#nvidia/pytorch:25.06-py3 | Check the training throughput using the ContainerEngine and NVIDIA NGC | [apps/pytorch](../checks/apps/pytorch/) |
| [CudaNBodyCheckCE](../checks/containers/container_engine/check_cuda_nbody.py) | Single-node N-Body test for GPUs using CE (from CUDA samples) | [containers/container_engine](../checks/containers/container_engine/) |
| [CUDA_MPS_CE](../checks/containers/container_engine/cuda_mps.py) | Check for CUDA MPS with CE | [containers/container_engine](../checks/containers/container_engine/) |
| [OMB_MPICH_CE](../checks/containers/container_engine/omb.py)<br>• %test_name=pt2pt/osu_bw | OSU Micro-benchmarks for MPICH/CE (Point-to-Point and All-to-All) | [containers/container_engine](../checks/containers/container_engine/) |
| [OMB_MPICH_CE](../checks/containers/container_engine/omb.py)<br>• %test_name=collective/osu_alltoall | OSU Micro-benchmarks for MPICH/CE (Point-to-Point and All-to-All) | [containers/container_engine](../checks/containers/container_engine/) |
| [OMB_OMPI_CE](../checks/containers/container_engine/omb.py)<br>• %test_name=pt2pt/osu_bw | OSU Micro-benchmarks for OpenMPI/CE (Point-to-Point and All-to-All) | [containers/container_engine](../checks/containers/container_engine/) |
| [OMB_OMPI_CE](../checks/containers/container_engine/omb.py)<br>• %test_name=collective/osu_alltoall | OSU Micro-benchmarks for OpenMPI/CE (Point-to-Point and All-to-All) | [containers/container_engine](../checks/containers/container_engine/) |
| [SSH_CE](../checks/containers/container_engine/ssh.py) | Checks if SSH is available with CE | [containers/container_engine](../checks/containers/container_engine/) |
| [CudaNodeBurnGemmCE](../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) | GPU Node burn GEMM test for A100/GH200 using CE | [microbenchmarks/cpu_gpu/node_burn](../checks/microbenchmarks/cpu_gpu/node_burn/) |
| [CPUNodeBurnGemmCE](../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) | CPU Node burn GEMM test for A100/GH200-nodes using CE | [microbenchmarks/cpu_gpu/node_burn](../checks/microbenchmarks/cpu_gpu/node_burn/) |
| [CudaNodeBurnStreamCE](../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) | GPU Node burn Stream test for A100/GH200 using CE | [microbenchmarks/cpu_gpu/node_burn](../checks/microbenchmarks/cpu_gpu/node_burn/) |
| [CPUNodeBurnStreamCE](../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) | CPU Node burn Stream test for A100/GH200-nodes using CE | [microbenchmarks/cpu_gpu/node_burn](../checks/microbenchmarks/cpu_gpu/node_burn/) |
| [NCCLTestsCE](../checks/microbenchmarks/xccl/xccl_tests.py)<br>• %test_name=all_reduce<br>• %image_tag=cuda12.9.1-ubuntu24.04 | Point-to-Point and All-Reduce NCCL tests with CE | [microbenchmarks/xccl](../checks/microbenchmarks/xccl/) |
| [NCCLTestsCE](../checks/microbenchmarks/xccl/xccl_tests.py)<br>• %test_name=sendrecv<br>• %image_tag=cuda12.9.1-ubuntu24.04 | Point-to-Point and All-Reduce NCCL tests with CE | [microbenchmarks/xccl](../checks/microbenchmarks/xccl/) |
| [RunJobCE](../checks/system/ce/ce_import_run_image.py) | <none> | [system/ce](../checks/system/ce/) |
| [RunNVGPUJobCE](../checks/system/ce/ce_import_run_image.py) | <none> | [system/ce](../checks/system/ce/) |
| [DcgmRpmCheck](../checks/system/gssr/dcgm_hook.py) | Check DCGM executable and libraries are installed | [system/gssr](../checks/system/gssr/) |
| [GssrCeHookCheck](../checks/system/gssr/dcgm_hook.py)<br>• %pytorch_image_tag=25.01-py3_nvrtc-12.9 | Check DCGM CE hook is working with gssr | [system/gssr](../checks/system/gssr/) |
| [timeout-completes](../checks/system/integration/alps.py) | Verify timeout completes successfully | [system/integration](../checks/system/integration/) |
| [timeout-signal-term](../checks/system/integration/alps.py) | Verify timeout delivers TERM after expiry | [system/integration](../checks/system/integration/) |
| [df-command-timeout](../checks/system/integration/alps.py) | Verify df command completes without timeout | [system/integration](../checks/system/integration/) |
| [fs-no-full](../checks/system/integration/alps.py) | Verify filesystem is not at 100% capacity | [system/integration](../checks/system/integration/) |
| [ping-localhost](../checks/system/integration/alps.py) | Verify localhost ping is successful | [system/integration](../checks/system/integration/) |
| [ping-remote-dns](../checks/system/integration/alps.py) | Verify remote internet ping routing via DNS | [system/integration](../checks/system/integration/) |
| [ping-remote-http](../checks/system/integration/alps.py) | Verify remote HTTP hostname resolves and responds to ping | [system/integration](../checks/system/integration/) |
| [curl-external-access](../checks/system/integration/alps.py) | Verify external internet connectivity via curl | [system/integration](../checks/system/integration/) |
| [dns-invalid-hostname](../checks/system/integration/alps.py) | Verify DNS lookup fails for invalid hostname | [system/integration](../checks/system/integration/) |
| [dns-internal-host](../checks/system/integration/alps.py) | Verify DNS resolution for internal CSCS host | [system/integration](../checks/system/integration/) |
| [dns-external-host](../checks/system/integration/alps.py) | Verify DNS resolution for external internet host | [system/integration](../checks/system/integration/) |
| [netiface-nmn0-up](../checks/system/integration/alps.py) | Verify nmn0 network interface is up | [system/integration](../checks/system/integration/) |
| [netiface-nmn0-ip](../checks/system/integration/alps.py) | Verify nmn0 has expected IP address range | [system/integration](../checks/system/integration/) |
| [netiface-hsn0-up](../checks/system/integration/alps.py) | Verify hsn0 network interface is up | [system/integration](../checks/system/integration/) |
| [netiface-hsn0-ip](../checks/system/integration/alps.py) | Verify hsn0 has expected IP address range | [system/integration](../checks/system/integration/) |
| [netiface-hsn1-up](../checks/system/integration/alps.py) | Verify hsn1 network interface is up (Daint only) | [system/integration](../checks/system/integration/) |
| [netiface-hsn1-ip](../checks/system/integration/alps.py) | Verify hsn1 has expected IP address range (Daint only) | [system/integration](../checks/system/integration/) |
| [netiface-hsn2-up](../checks/system/integration/alps.py) | Verify hsn2 network interface is up (Daint only) | [system/integration](../checks/system/integration/) |
| [netiface-hsn2-ip](../checks/system/integration/alps.py) | Verify hsn2 has expected IP address range (Daint only) | [system/integration](../checks/system/integration/) |
| [netiface-hsn3-up](../checks/system/integration/alps.py) | Verify hsn3 network interface is up (Daint only) | [system/integration](../checks/system/integration/) |
| [netiface-hsn3-ip](../checks/system/integration/alps.py) | Verify hsn3 has expected IP address range (Daint only) | [system/integration](../checks/system/integration/) |
| [ldap-server-reachable](../checks/system/integration/alps.py) | Verify LDAP server is reachable | [system/integration](../checks/system/integration/) |
| [ldap-getent-hosts](../checks/system/integration/alps.py) | Verify getent hosts command works for LDAP | [system/integration](../checks/system/integration/) |
| [os-version-check-daint](../checks/system/integration/alps.py) | Verify SUSE Linux Enterprise Server 15 SP6 is installed (Daint) | [system/integration](../checks/system/integration/) |
| [locale-check](../checks/system/integration/alps.py) | Verify locale is set to en_US.UTF-8 | [system/integration](../checks/system/integration/) |
| [sshd-running](../checks/system/integration/alps.py) | Verify SSH daemon is running | [system/integration](../checks/system/integration/) |
| [ssh-port-listening](../checks/system/integration/alps.py) | Verify SSH port is listening | [system/integration](../checks/system/integration/) |
| [http-port-not-listening](../checks/system/integration/alps.py) | Verify HTTP port is not listening | [system/integration](../checks/system/integration/) |
| [tool-zypper](../checks/system/integration/alps.py) | Verify zypper package manager is available | [system/integration](../checks/system/integration/) |
| [tool-vim](../checks/system/integration/alps.py) | Verify vim editor is available | [system/integration](../checks/system/integration/) |
| [tool-gcc](../checks/system/integration/alps.py) | Verify gcc compiler is available | [system/integration](../checks/system/integration/) |
| [tool-gcc-12](../checks/system/integration/alps.py) | Verify gcc-12 compiler is available | [system/integration](../checks/system/integration/) |
| [tool-jq](../checks/system/integration/alps.py) | Verify jq JSON processor is available | [system/integration](../checks/system/integration/) |
| [mount-scratch-capstor](../checks/system/integration/alps.py) | Verify scratch filesystem is mounted | [system/integration](../checks/system/integration/) |
| [mount-store-capstor](../checks/system/integration/alps.py) | Verify store filesystem is mounted (capstor) | [system/integration](../checks/system/integration/) |
| [env-scratch](../checks/system/integration/alps.py) | Verify SCRATCH environment variable is set | [system/integration](../checks/system/integration/) |
| [env-project](../checks/system/integration/alps.py) | Verify PROJECT environment variable is set | [system/integration](../checks/system/integration/) |
| [env-store](../checks/system/integration/alps.py) | Verify STORE environment variable is set | [system/integration](../checks/system/integration/) |
| [env-home](../checks/system/integration/alps.py) | Verify HOME environment variable is set | [system/integration](../checks/system/integration/) |
| [scratch-path-check-capstor](../checks/system/integration/alps.py) | Verify SCRATCH path is under /capstor/scratch/cscs | [system/integration](../checks/system/integration/) |
| [project-path-check](../checks/system/integration/alps.py) | Verify PROJECT path is under /capstor/store/cscs (Daint) | [system/integration](../checks/system/integration/) |
| [store-path-check](../checks/system/integration/alps.py) | Verify STORE path is under /capstor/store/cscs (Daint) | [system/integration](../checks/system/integration/) |
| [home-path-check](../checks/system/integration/alps.py) | Verify HOME path is under /users | [system/integration](../checks/system/integration/) |
| [env-tmp-not-set](../checks/system/integration/alps.py) | Verify TMP environment variable is not set | [system/integration](../checks/system/integration/) |
| [slurm-config-exists](../checks/system/integration/alps.py) | Verify Slurm configuration file exists | [system/integration](../checks/system/integration/) |
| [slurm-sinfo-tool](../checks/system/integration/alps.py) | Verify Slurm sinfo tool is available | [system/integration](../checks/system/integration/) |
| [slurm-munge-daemon](../checks/system/integration/alps.py) | Verify Munge daemon is running | [system/integration](../checks/system/integration/) |
| [slurm-slurmctld-ping](../checks/system/integration/alps.py) | Verify Slurm controller is responsive | [system/integration](../checks/system/integration/) |
| [vsbase-nomad](../checks/system/integration/alps.py) | Verify Nomad orchestrator is available | [system/integration](../checks/system/integration/) |
| [vservices-uenv-version](../checks/system/integration/alps.py) | Verify uenv command is available and works | [system/integration](../checks/system/integration/) |
| [vservices-image-cp2k](../checks/system/integration/alps.py) | Verify CP2K image available for GH200 | [system/integration](../checks/system/integration/) |
| [vservices-image-gromacs](../checks/system/integration/alps.py) | Verify GROMACS image available for GH200 | [system/integration](../checks/system/integration/) |
| [vservices-image-lammps](../checks/system/integration/alps.py) | Verify LAMMPS image available for GH200 | [system/integration](../checks/system/integration/) |
| [vservices-image-namd](../checks/system/integration/alps.py) | Verify NAMD image available for GH200 | [system/integration](../checks/system/integration/) |
| [vservices-image-quantumespresso](../checks/system/integration/alps.py) | Verify QuantumESPRESSO image available for GH200 | [system/integration](../checks/system/integration/) |
| [vservices-image-vasp](../checks/system/integration/alps.py) | Verify VASP image available for GH200 | [system/integration](../checks/system/integration/) |
| [vservices-image-linaro-forge](../checks/system/integration/alps.py) | Verify Linaro Forge image available for GH200 | [system/integration](../checks/system/integration/) |
| [vservices-image-pytorch](../checks/system/integration/alps.py) | Verify PyTorch image available for GH200 | [system/integration](../checks/system/integration/) |
| [vservices-image-icon-wcp-not-available](../checks/system/integration/alps.py) | Verify ICON-WCP image is not available for GH200 | [system/integration](../checks/system/integration/) |
| [vservices-image-prgenv-nvidia-not-available](../checks/system/integration/alps.py) | Verify PrgEnv-nvidia image is not available for GH200 | [system/integration](../checks/system/integration/) |
| [vservices-image-prgenv-gnu](../checks/system/integration/alps.py) | Verify PrgEnv-gnu image available for GH200 | [system/integration](../checks/system/integration/) |
| [vservices-image-netcdf-tools](../checks/system/integration/alps.py) | Verify NetCDF tools image available for GH200 | [system/integration](../checks/system/integration/) |
| [vservices-image-editors](../checks/system/integration/alps.py) | Verify editors image available for GH200 | [system/integration](../checks/system/integration/) |
| [ddBlockSizeTest](../checks/system/io/dd_blk_size.py) | dd write tests with different block sizes | [system/io](../checks/system/io/) |
| [stuck_gpu_mem_test](../checks/system/io/fio.py) | Make sure that we can compile fio. | [system/io](../checks/system/io/) |
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