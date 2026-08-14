## Test Coverage Matrix

- Generated: `2026-06-22 20:10:16 +0200`

### apps/pytorch

| Test name | prod | maint |
|-----------|-----------|-----------|
| [PyTorchDdpCeNv](../checks/apps/pytorch/pytorch_nvidia.py) | ✅ | ✅ |
| [PyTorchDdpCeNvlarge](../checks/apps/pytorch/pytorch_nvidia.py)<br><details><summary>🔽 2 variants</summary><br>- %aws_ofi_nccl=True<br>- %image=nvcr.io#nvidia/pytorch:25.06-py3<br>- %num_nodes=3<br>- %num_nodes=8</details> | ✅ | ✅ |
| [PyTorchMegatronLM_CE](../checks/apps/pytorch/pytorch_megatronlm.py)<br><details><summary>🔽 2 variants</summary><br>- %model=llama3-70b<br>- %model=llama3-8b</details> | ✅ | ✅ |
| [PyTorchNCCLAllReduce](../checks/apps/pytorch/pytorch_allreduce.py) | ✅ | ✅ |
| [TorchHammerCEMultiGPU](../checks/apps/pytorch/torch_hammer_ce_checks.py) | ✅ | ✅ |

### containers/container_engine

| Test name | prod | maint |
|-----------|-----------|-----------|
| [CUDA_MPS_CE](../checks/containers/container_engine/cuda_mps.py) | ✅ | ✅ |
| [OMB_MPICH_CE](../checks/containers/container_engine/omb.py) | ✅ | ✅ |
| [OMB_MPICH_CE_Host](../checks/containers/container_engine/omb.py) | ✅ | ✅ |
| [OMB_OMPI_CE](../checks/containers/container_engine/omb.py) | ✅ | ✅ |
| [OMB_OMPI_CE_Host](../checks/containers/container_engine/omb.py) | ✅ | ✅ |
| [PyFR_CE](../checks/containers/container_engine/pyfr.py) | ✅ | ✅ |
| [SSH_CE](../checks/containers/container_engine/ssh.py) | ✅ | ✅ |
| [SphExa_CE](../checks/containers/container_engine/sphexa.py) | ✅ | ✅ |

### microbenchmarks/cpu_gpu/node_burn

| Test name | prod | maint |
|-----------|-----------|-----------|
| [CPUNodeBurnGemmCE](../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) | ✅ | ✅ |
| [CPUNodeBurnStreamCE](../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) | ✅ | ✅ |
| [CudaNodeBurnGemmCE](../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) | ✅ | ✅ |
| [CudaNodeBurnStreamCE](../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) | ✅ | ✅ |

### microbenchmarks/xccl

| Test name | prod | maint |
|-----------|-----------|-----------|
| [NCCLTestsCE](../checks/microbenchmarks/xccl/xccl_tests.py)<br><details><summary>🔽 2 variants</summary><br>- %test_name=all_reduce<br>- %test_name=sendrecv</details> | ✅ | ✅ |
| [NCCLTestsCEHost](../checks/microbenchmarks/xccl/xccl_tests.py)<br><details><summary>🔽 2 variants</summary><br>- %test_name=all_reduce<br>- %test_name=sendrecv</details> | ✅ | ✅ |

### system/ce

| Test name | prod | maint |
|-----------|-----------|-----------|
| [RunJobCE](../checks/system/ce/ce_import_run_image.py) | ✅ | ✅ |
| [RunNVGPUJobCE](../checks/system/ce/ce_import_run_image.py) | ✅ | ✅ |

### system/gssr

| Test name | prod | maint |
|-----------|-----------|-----------|
| [DcgmRpmCheck](../checks/system/gssr/dcgm_hook.py) | ❌ | ✅ |
| [GssrCeHookCheck](../checks/system/gssr/dcgm_hook.py) | ❌ | ✅ |

### system/integration

| Test name | prod | maint |
|-----------|-----------|-----------|
| [curl-external-access](../checks/system/integration/alps.py) | ✅ | ✅ |
| [df-command-timeout](../checks/system/integration/alps.py) | ✅ | ✅ |
| [dns-external-host](../checks/system/integration/alps.py) | ✅ | ✅ |
| [dns-internal-host](../checks/system/integration/alps.py) | ✅ | ✅ |
| [dns-invalid-hostname](../checks/system/integration/alps.py) | ✅ | ✅ |
| [env-home](../checks/system/integration/alps.py) | ✅ | ✅ |
| [env-project](../checks/system/integration/alps.py) | ✅ | ✅ |
| [env-scratch](../checks/system/integration/alps.py) | ✅ | ✅ |
| [env-store](../checks/system/integration/alps.py) | ✅ | ✅ |
| [env-tmp-not-set](../checks/system/integration/alps.py) | ✅ | ✅ |
| [fs-no-full](../checks/system/integration/alps.py) | ✅ | ✅ |
| [home-path-check](../checks/system/integration/alps.py) | ✅ | ✅ |
| [http-port-not-listening](../checks/system/integration/alps.py) | ✅ | ✅ |
| [ldap-getent-hosts](../checks/system/integration/alps.py) | ✅ | ✅ |
| [ldap-server-reachable](../checks/system/integration/alps.py) | ✅ | ✅ |
| [libfabric-1_22_0-installed](../checks/system/integration/alps.py) | ✅ | ✅ |
| [libfabric-host-directory](../checks/system/integration/alps.py) | ✅ | ✅ |
| [libfabric-installed](../checks/system/integration/alps.py) | ✅ | ✅ |
| [locale-check](../checks/system/integration/alps.py) | ✅ | ✅ |
| [mount-scratch-capstor](../checks/system/integration/alps.py) | ✅ | ✅ |
| [mount-store-capstor](../checks/system/integration/alps.py) | ✅ | ✅ |
| [netiface-hsn0-ip](../checks/system/integration/alps.py) | ✅ | ✅ |
| [netiface-hsn0-up](../checks/system/integration/alps.py) | ✅ | ✅ |
| [netiface-hsn1-ip](../checks/system/integration/alps.py) | ✅ | ✅ |
| [netiface-hsn1-up](../checks/system/integration/alps.py) | ✅ | ✅ |
| [netiface-hsn2-ip](../checks/system/integration/alps.py) | ✅ | ✅ |
| [netiface-hsn2-up](../checks/system/integration/alps.py) | ✅ | ✅ |
| [netiface-hsn3-ip](../checks/system/integration/alps.py) | ✅ | ✅ |
| [netiface-hsn3-up](../checks/system/integration/alps.py) | ✅ | ✅ |
| [netiface-nmn0-ip](../checks/system/integration/alps.py) | ✅ | ✅ |
| [netiface-nmn0-up](../checks/system/integration/alps.py) | ✅ | ✅ |
| [os-version-check-daint](../checks/system/integration/alps.py) | ✅ | ✅ |
| [ping-localhost](../checks/system/integration/alps.py) | ✅ | ✅ |
| [ping-remote-dns](../checks/system/integration/alps.py) | ✅ | ✅ |
| [ping-remote-http](../checks/system/integration/alps.py) | ✅ | ✅ |
| [project-path-check](../checks/system/integration/alps.py) | ✅ | ✅ |
| [ritom-mount-loopupcache](../checks/system/integration/alps.py) | ✅ | ✅ |
| [ritom-mount-nconnect](../checks/system/integration/alps.py) | ✅ | ✅ |
| [ritom-mount-noextend](../checks/system/integration/alps.py) | ✅ | ✅ |
| [ritom-mount-nosuid](../checks/system/integration/alps.py) | ✅ | ✅ |
| [ritom-mount-optlockflush](../checks/system/integration/alps.py) | ✅ | ✅ |
| [ritom-mount-remoteports](../checks/system/integration/alps.py) | ✅ | ✅ |
| [ritom-mount-spread_reads](../checks/system/integration/alps.py) | ✅ | ✅ |
| [ritom-mount-spread_writes](../checks/system/integration/alps.py) | ✅ | ✅ |
| [scratch-path-check-capstor](../checks/system/integration/alps.py) | ✅ | ✅ |
| [slingshot-iommu-group](../checks/system/integration/alps.py) | ✅ | ✅ |
| [slurm-config-exists](../checks/system/integration/alps.py) | ✅ | ✅ |
| [slurm-munge-daemon](../checks/system/integration/alps.py) | ✅ | ✅ |
| [slurm-sinfo-tool](../checks/system/integration/alps.py) | ✅ | ✅ |
| [slurm-slurmctld-ping](../checks/system/integration/alps.py) | ✅ | ✅ |
| [ssh-port-listening](../checks/system/integration/alps.py) | ✅ | ✅ |
| [sshd-running](../checks/system/integration/alps.py) | ✅ | ✅ |
| [store-path-check](../checks/system/integration/alps.py) | ✅ | ✅ |
| [timeout-completes](../checks/system/integration/alps.py) | ✅ | ✅ |
| [timeout-signal-term](../checks/system/integration/alps.py) | ✅ | ✅ |
| [tool-gcc](../checks/system/integration/alps.py) | ✅ | ✅ |
| [tool-gcc-12](../checks/system/integration/alps.py) | ✅ | ✅ |
| [tool-jq](../checks/system/integration/alps.py) | ✅ | ✅ |
| [tool-vim](../checks/system/integration/alps.py) | ✅ | ✅ |
| [tool-zypper](../checks/system/integration/alps.py) | ✅ | ✅ |
| [vsbase-nomad](../checks/system/integration/alps.py) | ✅ | ✅ |
| [vservices-image-cp2k](../checks/system/integration/alps.py) | ✅ | ✅ |
| [vservices-image-editors](../checks/system/integration/alps.py) | ✅ | ✅ |
| [vservices-image-gromacs](../checks/system/integration/alps.py) | ✅ | ✅ |
| [vservices-image-icon-wcp-not-available](../checks/system/integration/alps.py) | ✅ | ✅ |
| [vservices-image-lammps](../checks/system/integration/alps.py) | ✅ | ✅ |
| [vservices-image-linaro-forge](../checks/system/integration/alps.py) | ✅ | ✅ |
| [vservices-image-namd](../checks/system/integration/alps.py) | ✅ | ✅ |
| [vservices-image-netcdf-tools](../checks/system/integration/alps.py) | ✅ | ✅ |
| [vservices-image-prgenv-gnu](../checks/system/integration/alps.py) | ✅ | ✅ |
| [vservices-image-prgenv-nvidia-not-available](../checks/system/integration/alps.py) | ✅ | ✅ |
| [vservices-image-pytorch](../checks/system/integration/alps.py) | ✅ | ✅ |
| [vservices-image-quantumespresso](../checks/system/integration/alps.py) | ✅ | ✅ |
| [vservices-image-vasp](../checks/system/integration/alps.py) | ✅ | ✅ |
| [vservices-uenv-version](../checks/system/integration/alps.py) | ✅ | ✅ |
| [workaround-cupointers](../checks/system/integration/alps.py) | ✅ | ✅ |

### system/io

| Test name | prod | maint |
|-----------|-----------|-----------|
| [ddBlockSizeTest](../checks/system/io/dd_blk_size.py) | ✅ | ✅ |
| [fio_compile_test](../checks/system/io/fio.py) | ❌ | ✅ |
| [stuck_gpu_mem_test](../checks/system/io/fio.py) | ❌ | ✅ |

### system/slurm

| Test name | prod | maint |
|-----------|-----------|-----------|
| [DefaultRequestGPUSetsGRES](../checks/system/slurm/slurm.py) | ✅ | ✅ |
| [EnvironmentVariableCheck](../checks/system/slurm/slurm.py) | ✅ | ✅ |
| [HostnameCheck](../checks/system/slurm/slurm.py) | ✅ | ✅ |
| [InvalidAccount](../checks/system/slurm/invalid_acc.py) | ✅ | ✅ |
| [NVreg_RestrictProfilingToAdminUsers](../checks/system/slurm/slurm.py) | ✅ | ✅ |
| [NvidiaSmiDriverVersion](../checks/system/slurm/slurm.py) | ✅ | ✅ |
| [SlurmGPUGresTest](../checks/system/slurm/slurm.py) | ✅ | ✅ |
| [SlurmNoIsolCpus](../checks/system/slurm/slurm.py) | ✅ | ✅ |
| [SlurmParanoidCheck](../checks/system/slurm/slurm.py) | ✅ | ✅ |
| [SlurmTransparentHugepagesCheck](../checks/system/slurm/slurm.py)<br><details><summary>🔽 4 variants</summary><br>- %hugepages_options=always<br>- %hugepages_options=default<br>- %hugepages_options=madvise<br>- %hugepages_options=never</details> | ✅ | ✅ |
| [SlurmUvmPerfAccessCounterMigration](../checks/system/slurm/slurm.py) | ✅ | ✅ |

### Summary

| Metric | prod | maint |
|--------|--------|--------|
| TOTAL (visible grouped rows) | 109 | 113 |
| TOTAL (raw ReFrame-selected tests) | 116 | 120 |