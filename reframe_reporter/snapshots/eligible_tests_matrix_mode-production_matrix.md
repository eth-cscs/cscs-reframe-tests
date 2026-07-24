## Test Coverage Matrix

- Generated: `2026-06-17 12:05:06 +0200`

### apps/ascent

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [uenv_ascent_cloverleaf3d](../checks/apps/ascent/ascent.py) | ✅ | ❌ | ❌ | ❌ | ✅ |
| [uenv_ascent_doublegyre_cpp](../checks/apps/ascent/ascent.py) | ✅ | ❌ | ❌ | ❌ | ✅ |
| [uenv_ascent_doublegyre_python](../checks/apps/ascent/ascent.py) | ✅ | ❌ | ❌ | ❌ | ✅ |
| [uenv_ascent_heatdiffusion_cpp](../checks/apps/ascent/ascent.py) | ✅ | ❌ | ❌ | ❌ | ✅ |
| [uenv_ascent_heatdiffusion_python](../checks/apps/ascent/ascent.py) | ✅ | ❌ | ❌ | ❌ | ✅ |
| [uenv_ascent_intro_cpp](../checks/apps/ascent/ascent.py)<br><details><summary>🔽 13 variants</summary><br>- %exe=ascent_binning_example1<br>- %exe=ascent_extract_example1<br>- %exe=ascent_extract_example2<br>- %exe=ascent_extract_example3<br>- %exe=ascent_extract_example4<br>- %exe=ascent_first_light_example<br>- %exe=ascent_pipeline_example1<br>- %exe=ascent_query_example1<br>- %exe=ascent_scene_example1<br>- %exe=ascent_scene_example2<br>- %exe=ascent_scene_example3<br>- %exe=ascent_scene_example4<br>- %exe=ascent_trigger_example1</details> | ✅ | ❌ | ❌ | ❌ | ✅ |
| [uenv_ascent_kripke](../checks/apps/ascent/ascent.py) | ✅ | ❌ | ❌ | ❌ | ✅ |
| [uenv_ascent_noise](../checks/apps/ascent/ascent.py) | ✅ | ❌ | ❌ | ❌ | ✅ |

### apps/cp2k

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [Cp2kCheckMD_UENVExec](../checks/apps/cp2k/cp2k_uenv.py) | ✅ | ❌ | ❌ | ❌ | ✅ |
| [Cp2kCheckMD_UENVExec_Workaround](../checks/apps/cp2k/cp2k_uenv.py) | ✅ | ❌ | ❌ | ❌ | ✅ |
| [Cp2kCheckPBE_UENVExec](../checks/apps/cp2k/cp2k_uenv.py) | ✅ | ❌ | ❌ | ❌ | ✅ |
| [Cp2kCheckPBE_UENVExec_Workaround](../checks/apps/cp2k/cp2k_uenv.py) | ✅ | ❌ | ❌ | ❌ | ✅ |

### apps/lammps

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [lammps_gpu_test](../checks/apps/lammps/lammps.py) | ✅ | ❌ | ❌ | ❌ | ✅ |
| [lammps_kokkos_test](../checks/apps/lammps/lammps.py) | ✅ | ❌ | ❌ | ❌ | ✅ |

### apps/namd

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [NamdCheckUENVExec](../checks/apps/namd/namd_check_uenv.py) | ✅ | ❌ | ❌ | ❌ | ✅ |

### apps/paraview

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [ParaView_catalystClipping](../checks/apps/paraview/paraview.py) | ✅ | ✅ | ✅ | ✅ | ✅ |
| [ParaView_coloredSphere](../checks/apps/paraview/paraview.py) | ✅ | ✅ | ✅ | ✅ | ✅ |

### apps/paraview/build-gadget-plugin

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [ParaviewBuildGadgetPlugin](../checks/apps/paraview/build-gadget-plugin/paraview_buildgadgetplugin.py) | ✅ | ✅ | ✅ | ❌ | ✅ |

### apps/paraview/catalystclipping

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [ParaviewCatalystClipping](../checks/apps/paraview/catalystclipping/paraview_catalystclipping.py) | ✅ | ✅ | ✅ | ❌ | ✅ |

### apps/paraview/coloredsphere

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [ParaviewColoredSphere](../checks/apps/paraview/coloredsphere/paraview_coloredsphere.py) | ✅ | ✅ | ✅ | ❌ | ✅ |

### apps/pytorch

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [PyTorchDdpCeNv](../checks/apps/pytorch/pytorch_nvidia.py) | ✅ | ❌ | ✅ | ✅ | ✅ |
| [PyTorchDdpCeNvlarge](../checks/apps/pytorch/pytorch_nvidia.py)<br><details><summary>🔽 2 variants</summary><br>- %aws_ofi_nccl=True<br>- %image=nvcr.io#nvidia/pytorch:25.06-py3<br>- %num_nodes=3<br>- %num_nodes=8</details> | ✅ | ❌ | ✅ | ✅ | ✅ |
| [PyTorchMegatronLM_CE](../checks/apps/pytorch/pytorch_megatronlm.py)<br><details><summary>🔽 2 variants</summary><br>- %model=llama3-70b<br>- %model=llama3-8b</details> | ✅ | ❌ | ✅ | ✅ | ✅ |
| [PyTorchMegatronLM_UENV](../checks/apps/pytorch/pytorch_megatronlm.py)<br><details><summary>🔽 2 variants</summary><br>- %model=llama3-70b<br>- %model=llama3-8b</details> | ✅ | ❌ | ✅ | ✅ | ✅ |
| [PyTorchNCCLAllReduce](../checks/apps/pytorch/pytorch_allreduce.py) | ✅ | ❌ | ✅ | ✅ | ✅ |
| [TorchHammerCEMultiGPU](../checks/apps/pytorch/torch_hammer_ce_checks.py) | ✅ | ❌ | ✅ | ✅ | ✅ |

### apps/q-e-sirius

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [QeSiriusCheckAuSurfUENVExec](../checks/apps/q-e-sirius/q-e-sirius_check_uenv.py) | ✅ | ❌ | ❌ | ❌ | ✅ |

### apps/quantumespresso

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [QeCheckAuSurfUENVExec](../checks/apps/quantumespresso/quantumespresso_check_uenv.py) | ✅ | ❌ | ✅ | ❌ | ✅ |

### apps/sphexa

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [SphExa](../checks/apps/sphexa/sphexa_uenv.py) | ✅ | ❌ | ✅ | ✅ | ✅ |

### apps/vasp

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [VaspCheckUENV](../checks/apps/vasp/vasp_check_uenv.py)<br><details><summary>🔽 2 variants</summary><br>- %num_nodes=1<br>- %num_nodes=2</details> | ✅ | ❌ | ❌ | ❌ | ✅ |

### containers/container_engine

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [CUDA_MPS_CE](../checks/containers/container_engine/cuda_mps.py) | ✅ | ❌ | ✅ | ✅ | ✅ |
| [OMB_MPICH_CE](../checks/containers/container_engine/omb.py) | ✅ | ❌ | ✅ | ✅ | ✅ |
| [OMB_OMPI_CE](../checks/containers/container_engine/omb.py) | ✅ | ❌ | ✅ | ✅ | ✅ |
| [PyFR_CE](../checks/containers/container_engine/pyfr.py) | ✅ | ❌ | ✅ | ✅ | ✅ |
| [SSH_CE](../checks/containers/container_engine/ssh.py) | ✅ | ✅ | ✅ | ✅ | ✅ |
| [SphExa_CE](../checks/containers/container_engine/sphexa.py) | ✅ | ❌ | ✅ | ✅ | ✅ |

### libraries/dlaf

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [dlaf_check_uenv](../checks/libraries/dlaf/dlaf.py)<br><details><summary>🔽 2 variants</summary><br>- %test_name=eigensolver<br>- %test_name=gen_eigensolver</details> | ✅ | ❌ | ❌ | ❌ | ✅ |
| [dlaf_check_uenv_cupointergetattribute_workaround](../checks/libraries/dlaf/dlaf.py)<br><details><summary>🔽 2 variants</summary><br>- %test_name=eigensolver<br>- %test_name=gen_eigensolver</details> | ✅ | ❌ | ❌ | ❌ | ✅ |

### libraries/io

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [HDF5Test](../checks/libraries/io/hdf5.py)<br><details><summary>🔽 2 variants</summary><br>- %lang=cpp<br>- %lang=f90</details> | ✅ | ✅ | ✅ | ✅ | ✅ |

### microbenchmarks/cpu/alloc_speed

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [AllocSpeedTest](../checks/microbenchmarks/cpu/alloc_speed/alloc_speed.py)<br><details><summary>🔽 2 variants</summary><br>- %hugepages=2M<br>- %hugepages=no</details> | ✅ | ✅ | ✅ | ✅ | ✅ |

### microbenchmarks/cpu_gpu/node_burn

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [CPUNodeBurnGemmCE](../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) | ✅ | ✅ | ✅ | ✅ | ✅ |
| [CPUNodeBurnStreamCE](../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) | ✅ | ✅ | ✅ | ✅ | ✅ |
| [CudaNodeBurnGemmCE](../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) | ✅ | ❌ | ✅ | ✅ | ✅ |
| [CudaNodeBurnStreamCE](../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) | ✅ | ❌ | ✅ | ✅ | ✅ |

### microbenchmarks/gpu/gpu_benchmarks

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [FFTBenchBuild](../checks/microbenchmarks/gpu/gpu_benchmarks/fft.py) | ✅ | ❌ | ✅ | ✅ | ✅ |
| [FFTCheck](../checks/microbenchmarks/gpu/gpu_benchmarks/fft.py)<br><details><summary>🔽 12 variants</summary><br>- %fft_dim=1D<br>- %fft_dim=2D<br>- %fft_dim=3D<br>- %fft_size=1024<br>- %fft_size=128<br>- %fft_size=256<br>- %fft_size=512</details> | ✅ | ❌ | ✅ | ✅ | ✅ |
| [ParallelAlgos](../checks/microbenchmarks/gpu/gpu_benchmarks/parallel_algos.py)<br><details><summary>🔽 9 variants</summary><br>- %_executable_opts=21<br>- %_executable_opts=24<br>- %_executable_opts=26<br>- %_executable_opts=27<br>- %_executable_opts=29<br>- %_executable_opts=30<br>- %_executable_opts=31<br>- %algo=radix-sort<br>- %algo=reduce<br>- %algo=scan</details> | ✅ | ❌ | ✅ | ✅ | ✅ |

### microbenchmarks/xccl

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [NCCLTestsCE](../checks/microbenchmarks/xccl/xccl_tests.py)<br><details><summary>🔽 2 variants</summary><br>- %test_name=all_reduce<br>- %test_name=sendrecv</details> | ✅ | ❌ | ✅ | ✅ | ✅ |
| [NCCLTestsUENV](../checks/microbenchmarks/xccl/xccl_tests.py)<br><details><summary>🔽 2 variants</summary><br>- %test_name=all_reduce<br>- %test_name=sendrecv</details> | ✅ | ❌ | ✅ | ✅ | ✅ |

### prgenv

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [HelloWorldTestMPI](../checks/prgenv/helloworld.py)<br><details><summary>🔽 3 variants</summary><br>- %lang=F90<br>- %lang=c<br>- %lang=cpp<br>- %linking=dynamic</details> | ✅ | ✅ | ✅ | ✅ | ✅ |
| [HelloWorldTestMPIOpenMP](../checks/prgenv/helloworld.py)<br><details><summary>🔽 3 variants</summary><br>- %lang=F90<br>- %lang=c<br>- %lang=cpp<br>- %linking=dynamic</details> | ✅ | ✅ | ✅ | ✅ | ✅ |
| [HelloWorldTestOpenMP](../checks/prgenv/helloworld.py)<br><details><summary>🔽 3 variants</summary><br>- %lang=F90<br>- %lang=c<br>- %lang=cpp<br>- %linking=dynamic</details> | ✅ | ✅ | ✅ | ✅ | ✅ |
| [HelloWorldTestSerial](../checks/prgenv/helloworld.py)<br><details><summary>🔽 3 variants</summary><br>- %lang=F90<br>- %lang=c<br>- %lang=cpp<br>- %linking=dynamic</details> | ✅ | ✅ | ✅ | ✅ | ✅ |
| [MpiGpuDirectOOM](../checks/prgenv/mpi.py)<br><details><summary>🔽 2 variants</summary><br>- %ipc=0<br>- %ipc=1</details> | ✅ | ❌ | ✅ | ✅ | ✅ |
| [MpiInitTest](../checks/prgenv/mpi.py) | ✅ | ✅ | ✅ | ✅ | ✅ |

### prgenv/cuda

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [UENV_CudaSamples](../checks/prgenv/cuda/cuda_samples.py)<br><details><summary>🔽 3 variants</summary><br>- %sample=conjugateGradient<br>- %sample=deviceQuery<br>- %sample=simpleCUBLAS</details> | ✅ | ❌ | ✅ | ✅ | ✅ |
| [UENV_NVML](../checks/prgenv/cuda/cuda_nvml.py) | ✅ | ❌ | ✅ | ✅ | ✅ |
| [cuda_aware_mpi_build](../checks/prgenv/cuda/cuda_aware_mpi.py) | ✅ | ❌ | ✅ | ✅ | ✅ |

### system/ce

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [RunJobCE](../checks/system/ce/ce_import_run_image.py) | ✅ | ✅ | ✅ | ✅ | ✅ |
| [RunNVGPUJobCE](../checks/system/ce/ce_import_run_image.py) | ✅ | ❌ | ✅ | ✅ | ✅ |

### system/integration

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [apps-path-check-eiger](../checks/system/integration/alps.py) | ❌ | ✅ | ❌ | ❌ | ❌ |
| [curl-external-access](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [df-command-timeout](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [dns-external-host](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [dns-internal-host](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [dns-invalid-hostname](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [env-apps-eiger](../checks/system/integration/alps.py) | ❌ | ✅ | ❌ | ❌ | ❌ |
| [env-home](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [env-project](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [env-scratch](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [env-store](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [env-tmp-not-set](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [fs-no-full](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [home-path-check](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [http-port-not-listening](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [ldap-getent-hosts](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [ldap-server-reachable](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [libfabric-1_22_0-installed](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [libfabric-host-directory](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [libfabric-installed](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [locale-check](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [mount-amd-eiger](../checks/system/integration/alps.py) | ❌ | ✅ | ❌ | ❌ | ❌ |
| [mount-cray-pe-eiger](../checks/system/integration/alps.py) | ❌ | ✅ | ❌ | ❌ | ❌ |
| [mount-intel-eiger](../checks/system/integration/alps.py) | ❌ | ✅ | ❌ | ❌ | ❌ |
| [mount-scratch-capstor](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ❌ | ❌ |
| [mount-scratch-iopsstor](../checks/system/integration/alps.py) | ❌ | ❌ | ❌ | ✅ | ❌ |
| [mount-store-capstor](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [mount-users-eiger](../checks/system/integration/alps.py) | ❌ | ✅ | ❌ | ❌ | ❌ |
| [netiface-hsn0-ip](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [netiface-hsn0-up](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [netiface-hsn1-ip](../checks/system/integration/alps.py) | ✅ | ❌ | ✅ | ✅ | ❌ |
| [netiface-hsn1-up](../checks/system/integration/alps.py) | ✅ | ❌ | ✅ | ✅ | ❌ |
| [netiface-hsn2-ip](../checks/system/integration/alps.py) | ✅ | ❌ | ✅ | ✅ | ❌ |
| [netiface-hsn2-up](../checks/system/integration/alps.py) | ✅ | ❌ | ✅ | ✅ | ❌ |
| [netiface-hsn3-ip](../checks/system/integration/alps.py) | ✅ | ❌ | ✅ | ✅ | ❌ |
| [netiface-hsn3-up](../checks/system/integration/alps.py) | ✅ | ❌ | ✅ | ✅ | ❌ |
| [netiface-nmn0-ip](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [netiface-nmn0-up](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [os-version-check-daint](../checks/system/integration/alps.py) | ✅ | ❌ | ✅ | ✅ | ❌ |
| [os-version-check-eiger](../checks/system/integration/alps.py) | ❌ | ✅ | ❌ | ❌ | ❌ |
| [ping-localhost](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [ping-remote-dns](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [ping-remote-http](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [project-path-check](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [ritom-mount-loopupcache](../checks/system/integration/alps.py) | ✅ | ❌ | ❌ | ✅ | ❌ |
| [ritom-mount-nconnect](../checks/system/integration/alps.py) | ✅ | ❌ | ❌ | ✅ | ❌ |
| [ritom-mount-noextend](../checks/system/integration/alps.py) | ✅ | ✅ | ❌ | ✅ | ❌ |
| [ritom-mount-nosuid](../checks/system/integration/alps.py) | ✅ | ✅ | ❌ | ✅ | ❌ |
| [ritom-mount-optlockflush](../checks/system/integration/alps.py) | ✅ | ✅ | ❌ | ✅ | ❌ |
| [ritom-mount-remoteports](../checks/system/integration/alps.py) | ✅ | ✅ | ❌ | ✅ | ❌ |
| [ritom-mount-spread_reads](../checks/system/integration/alps.py) | ✅ | ❌ | ❌ | ✅ | ❌ |
| [ritom-mount-spread_writes](../checks/system/integration/alps.py) | ✅ | ❌ | ❌ | ✅ | ❌ |
| [scratch-path-check-capstor](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ❌ | ❌ |
| [scratch-path-check-iopsstor](../checks/system/integration/alps.py) | ❌ | ❌ | ❌ | ✅ | ❌ |
| [slingshot-iommu-group](../checks/system/integration/alps.py) | ✅ | ❌ | ✅ | ✅ | ❌ |
| [slingshot-iommu-passthrough](../checks/system/integration/alps.py) | ❌ | ✅ | ❌ | ❌ | ❌ |
| [slurm-config-exists](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [slurm-munge-daemon](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [slurm-sinfo-tool](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [slurm-slurmctld-ping](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [ssh-port-listening](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [sshd-running](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [store-path-check](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [timeout-completes](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [timeout-signal-term](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [tool-emacs](../checks/system/integration/alps.py) | ❌ | ✅ | ❌ | ❌ | ❌ |
| [tool-gcc](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [tool-gcc-12](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [tool-jq](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [tool-vim](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [tool-zypper](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [vsbase-nomad](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [vservices-image-cp2k](../checks/system/integration/alps.py) | ✅ | ❌ | ❌ | ❌ | ❌ |
| [vservices-image-editors](../checks/system/integration/alps.py) | ✅ | ❌ | ✅ | ✅ | ❌ |
| [vservices-image-gromacs](../checks/system/integration/alps.py) | ✅ | ❌ | ❌ | ❌ | ❌ |
| [vservices-image-icon-wcp-not-available](../checks/system/integration/alps.py) | ✅ | ❌ | ❌ | ✅ | ❌ |
| [vservices-image-lammps](../checks/system/integration/alps.py) | ✅ | ❌ | ❌ | ❌ | ❌ |
| [vservices-image-linaro-forge](../checks/system/integration/alps.py) | ✅ | ❌ | ✅ | ✅ | ❌ |
| [vservices-image-namd](../checks/system/integration/alps.py) | ✅ | ❌ | ❌ | ❌ | ❌ |
| [vservices-image-netcdf-tools](../checks/system/integration/alps.py) | ✅ | ❌ | ✅ | ✅ | ❌ |
| [vservices-image-prgenv-gnu](../checks/system/integration/alps.py) | ✅ | ❌ | ✅ | ✅ | ❌ |
| [vservices-image-prgenv-nvidia-not-available](../checks/system/integration/alps.py) | ✅ | ❌ | ✅ | ✅ | ❌ |
| [vservices-image-pytorch](../checks/system/integration/alps.py) | ✅ | ❌ | ✅ | ✅ | ❌ |
| [vservices-image-quantumespresso](../checks/system/integration/alps.py) | ✅ | ❌ | ✅ | ❌ | ❌ |
| [vservices-image-vasp](../checks/system/integration/alps.py) | ✅ | ❌ | ❌ | ❌ | ❌ |
| [vservices-uenv-version](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |
| [workaround-cupointers](../checks/system/integration/alps.py) | ✅ | ✅ | ✅ | ✅ | ❌ |

### system/io

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [ddBlockSizeTest](../checks/system/io/dd_blk_size.py) | ✅ | ✅ | ✅ | ✅ | ✅ |

### system/nvidia

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [UENV_NvidiaDeviceCount](../checks/system/nvidia/nvidia_device_count.py) | ✅ | ❌ | ✅ | ✅ | ✅ |

### system/slurm

| Test name | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|-----------|-----------|-----------|-----------|-----------|-----------|
| [DefaultRequestGPUSetsGRES](../checks/system/slurm/slurm.py) | ✅ | ❌ | ✅ | ✅ | ✅ |
| [EnvironmentVariableCheck](../checks/system/slurm/slurm.py) | ✅ | ✅ | ✅ | ✅ | ✅ |
| [HostnameCheck](../checks/system/slurm/slurm.py) | ✅ | ✅ | ✅ | ✅ | ✅ |
| [InvalidAccount](../checks/system/slurm/invalid_acc.py) | ✅ | ✅ | ✅ | ✅ | ✅ |
| [MemoryOverconsumptionCheck](../checks/system/slurm/slurm.py) | ✅ | ✅ | ✅ | ✅ | ✅ |
| [MemoryOverconsumptionCheckMPI](../checks/system/slurm/slurm.py) | ✅ | ✅ | ✅ | ✅ | ✅ |
| [NVreg_RestrictProfilingToAdminUsers](../checks/system/slurm/slurm.py) | ✅ | ❌ | ✅ | ✅ | ✅ |
| [NvidiaSmiDriverVersion](../checks/system/slurm/slurm.py) | ✅ | ❌ | ✅ | ✅ | ✅ |
| [SlurmGPUGresTest](../checks/system/slurm/slurm.py) | ✅ | ❌ | ✅ | ✅ | ✅ |
| [SlurmNoIsolCpus](../checks/system/slurm/slurm.py) | ✅ | ✅ | ✅ | ✅ | ✅ |
| [SlurmParanoidCheck](../checks/system/slurm/slurm.py) | ✅ | ✅ | ✅ | ✅ | ✅ |
| [SlurmTransparentHugepagesCheck](../checks/system/slurm/slurm.py)<br><details><summary>🔽 4 variants</summary><br>- %hugepages_options=always<br>- %hugepages_options=default<br>- %hugepages_options=madvise<br>- %hugepages_options=never</details> | ✅ | ❌ | ✅ | ✅ | ✅ |
| [SlurmUvmPerfAccessCounterMigration](../checks/system/slurm/slurm.py) | ✅ | ❌ | ✅ | ✅ | ✅ |

### Summary

| Metric | daint-prod | eiger-prod | santis-prod | clariden-prod | starlex-prod |
|--------|--------|--------|--------|--------|--------|
| TOTAL (visible grouped rows) | 151 | 84 | 118 | 122 | 75 |
| TOTAL (raw ReFrame-selected tests) | 206 | 94 | 158 | 162 | 130 |