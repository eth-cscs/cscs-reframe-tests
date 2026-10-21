## Eligible ReFrame Tests on daint

- Filters:
  - system: `daint`
  - mode: `production`
  - checks: `189`
- Generated: `2026-06-10 18:42:56 +0200`

| Test name | Description | Category |
|----------|-------------|----------|
| [Uenv_HDF5Test](../checks/libraries/io/hdf5.py)<br>• %lang=cpp | — | [libraries/io](../checks/libraries/io/) |
| [Uenv_HDF5Test](../checks/libraries/io/hdf5.py)<br>• %lang=f90 | — | [libraries/io](../checks/libraries/io/) |
| [dlaf_check_uenv](../checks/libraries/dlaf/dlaf.py)<br>• %test_name=gen_eigensolver | — | [libraries/dlaf](../checks/libraries/dlaf/) |
| [dlaf_check_uenv](../checks/libraries/dlaf/dlaf.py)<br>• %test_name=eigensolver | — | [libraries/dlaf](../checks/libraries/dlaf/) |
| [dlaf_check_uenv_cupointergetattribute_workaround](../checks/libraries/dlaf/dlaf.py)<br>• %test_name=gen_eigensolver | — | [libraries/dlaf](../checks/libraries/dlaf/) |
| [dlaf_check_uenv_cupointergetattribute_workaround](../checks/libraries/dlaf/dlaf.py)<br>• %test_name=eigensolver | — | [libraries/dlaf](../checks/libraries/dlaf/) |
| [HostnameCheck](../checks/system/slurm/slurm.py) | Check hostname pattern nidXXXXXX on the CN | [system/slurm](../checks/system/slurm/) |
| [EnvironmentVariableCheck](../checks/system/slurm/slurm.py) | Test if user env variables are propagated to CN | [system/slurm](../checks/system/slurm/) |
| [NvidiaSmiDriverVersion](../checks/system/slurm/slurm.py) | Nvidia-smi sanity check (output driver version) | [system/slurm](../checks/system/slurm/) |
| [DefaultRequestGPUSetsGRES](../checks/system/slurm/slurm.py) | Checks slurm config for 4-GPUs per node | [system/slurm](../checks/system/slurm/) |
| [MemoryOverconsumptionCheck](../checks/system/slurm/slurm.py) | Tests if requested memory limit works | [system/slurm](../checks/system/slurm/) |
| [MemoryOverconsumptionCheckMPI](../checks/system/slurm/slurm.py) | Testing max "allocatable" memory | [system/slurm](../checks/system/slurm/) |
| [SlurmTransparentHugepagesCheck](../checks/system/slurm/slurm.py)<br>• %hugepages_options=default | Check Slurm transparent hugepages configuration | [system/slurm](../checks/system/slurm/) |
| [SlurmTransparentHugepagesCheck](../checks/system/slurm/slurm.py)<br>• %hugepages_options=always | Check Slurm transparent hugepages configuration | [system/slurm](../checks/system/slurm/) |
| [SlurmTransparentHugepagesCheck](../checks/system/slurm/slurm.py)<br>• %hugepages_options=madvise | Check Slurm transparent hugepages configuration | [system/slurm](../checks/system/slurm/) |
| [SlurmTransparentHugepagesCheck](../checks/system/slurm/slurm.py)<br>• %hugepages_options=never | Check Slurm transparent hugepages configuration | [system/slurm](../checks/system/slurm/) |
| [SlurmParanoidCheck](../checks/system/slurm/slurm.py) | Check that perf_event_paranoid enables per-process and system wideperformance monitoring | [system/slurm](../checks/system/slurm/) |
| [SlurmNoIsolCpus](../checks/system/slurm/slurm.py) | <br>    Check that isolcpus isn't enabled as it prevents threads from migrating<br>    between cores. This makes e.g. make jobs or OpenMPI threads all be stuck to<br>    one core. See e.g.<br>    https://www.kernel.org/doc/html/latest/admin-guide/kernel-parameters.html<br>    and https://access.redhat.com/solutions/480473 for more details.<br>     | [system/slurm](../checks/system/slurm/) |
| [NVreg_RestrictProfilingToAdminUsers](../checks/system/slurm/slurm.py) | <br>    Allow access to the GPU Performance Counters for NVIDIA tools:<br>    https://developer.nvidia.com/nvidia-development-tools-solutions-err_nvgpuctrperm-permission-issue-performance-counters<br>     | [system/slurm](../checks/system/slurm/) |
| [SlurmUvmPerfAccessCounterMigration](../checks/system/slurm/slurm.py) | <br>    Check that uvm_perf_access_counter_mimc_migration_enable is set to 0<br>    as it is buggy in older drivers. If the driver is at least version 565, the<br>    name of the option is different and should be set to the default (-1).<br>     | [system/slurm](../checks/system/slurm/) |
| [SlurmGPUGresTest](../checks/system/slurm/slurm.py) | <br>       Ensure that the Slurm GRES (Generic REsource Scheduling) of the<br>       number of gpus is correctly set on all the nodes of each partition.<br><br>       For the current partition, the test performs the following steps:<br>        1) count the number of nodes (node_count)<br>        2) count the number of nodes having Gres=gpu:N (gres_count) where<br>           N=num_devices from the configuration<br>        3) ensure that 1) and 2) match<br>     | [system/slurm](../checks/system/slurm/) |
| [InvalidAccount](../checks/system/slurm/invalid_acc.py) | Check if Slurm accepts job submission using an invalid<br>        account. Reframe should raise a failure if the job starts. | [system/slurm](../checks/system/slurm/) |
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
| [UENV_NvidiaDeviceCount](../checks/system/nvidia/nvidia_device_count.py) | — | [system/nvidia](../checks/system/nvidia/) |
| [RunJobCE](../checks/system/ce/ce_import_run_image.py) | CE check with Dockerhub import and simple image run (ubuntu) | [system/ce](../checks/system/ce/) |
| [RunNVGPUJobCE](../checks/system/ce/ce_import_run_image.py) | CE check with NGC import and Stream job on GPU | [system/ce](../checks/system/ce/) |
| [cuda_aware_mpi_build](../checks/prgenv/cuda/cuda_aware_mpi.py) | Cuda-aware MPI test from NVIDIA code-samples.git | [prgenv/cuda](../checks/prgenv/cuda/) |
| [UENV_NVML](../checks/prgenv/cuda/cuda_nvml.py) | Checks that nvml can report GPU informations | [prgenv/cuda](../checks/prgenv/cuda/) |
| [UENV_CudaSamples](../checks/prgenv/cuda/cuda_samples.py)<br>• %sample=deviceQuery | CUDA deviceQuery test | [prgenv/cuda](../checks/prgenv/cuda/) |
| [UENV_CudaSamples](../checks/prgenv/cuda/cuda_samples.py)<br>• %sample=simpleCUBLAS | CUDA simpleCUBLAS test | [prgenv/cuda](../checks/prgenv/cuda/) |
| [UENV_CudaSamples](../checks/prgenv/cuda/cuda_samples.py)<br>• %sample=conjugateGradient | CUDA conjugateGradient test | [prgenv/cuda](../checks/prgenv/cuda/) |
| [MpiInitTest](../checks/prgenv/mpi.py) | — | [prgenv](../checks/prgenv/) |
| [MpiGpuDirectOOM](../checks/prgenv/mpi.py)<br>• %ipc=0 | — | [prgenv](../checks/prgenv/) |
| [MpiGpuDirectOOM](../checks/prgenv/mpi.py)<br>• %ipc=1 | — | [prgenv](../checks/prgenv/) |
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
| [SphExa_CE](../checks/containers/container_engine/sphexa.py)<br>• %sph_infile=/sphexa/50c.h5<br>• %num_gpus=8<br>• %sph_testcase=evrard<br>• %sph_steps=10<br>• %sph_size=200 | SPH-EXA for CE | [containers/container_engine](../checks/containers/container_engine/) |
| [PyFR_CE](../checks/containers/container_engine/pyfr.py)<br>• %backend=cuda<br>• %test_name=3d-taylor-green-ci | PyFR for CE | [containers/container_engine](../checks/containers/container_engine/) |
| [CUDA_MPS_CE](../checks/containers/container_engine/cuda_mps.py) | Check for CUDA MPS with CE | [containers/container_engine](../checks/containers/container_engine/) |
| [SSH_CE](../checks/containers/container_engine/ssh.py) | Checks if SSH is available with CE | [containers/container_engine](../checks/containers/container_engine/) |
| [OMB_MPICH_CE](../checks/containers/container_engine/omb.py)<br>• %test_name=pt2pt/osu_bw | OSU Micro-benchmarks for MPICH/CE (Point2Point and All2All) | [containers/container_engine](../checks/containers/container_engine/) |
| [OMB_OMPI_CE](../checks/containers/container_engine/omb.py)<br>• %test_name=pt2pt/osu_bw | OSU Micro-benchmarks for OpenMPI/CE (Point2Point and All2All) | [containers/container_engine](../checks/containers/container_engine/) |
| [FFTBenchBuild](../checks/microbenchmarks/gpu/gpu_benchmarks/fft.py) | Build FFT benchmark | [microbenchmarks/gpu/gpu_benchmarks](../checks/microbenchmarks/gpu/gpu_benchmarks/) |
| [FFTCheck](../checks/microbenchmarks/gpu/gpu_benchmarks/fft.py)<br>• %fft_dim=1D<br>• %fft_size=128 | — | [microbenchmarks/gpu/gpu_benchmarks](../checks/microbenchmarks/gpu/gpu_benchmarks/) |
| [FFTCheck](../checks/microbenchmarks/gpu/gpu_benchmarks/fft.py)<br>• %fft_dim=1D<br>• %fft_size=256 | — | [microbenchmarks/gpu/gpu_benchmarks](../checks/microbenchmarks/gpu/gpu_benchmarks/) |
| [FFTCheck](../checks/microbenchmarks/gpu/gpu_benchmarks/fft.py)<br>• %fft_dim=1D<br>• %fft_size=512 | — | [microbenchmarks/gpu/gpu_benchmarks](../checks/microbenchmarks/gpu/gpu_benchmarks/) |
| [FFTCheck](../checks/microbenchmarks/gpu/gpu_benchmarks/fft.py)<br>• %fft_dim=1D<br>• %fft_size=1024 | — | [microbenchmarks/gpu/gpu_benchmarks](../checks/microbenchmarks/gpu/gpu_benchmarks/) |
| [FFTCheck](../checks/microbenchmarks/gpu/gpu_benchmarks/fft.py)<br>• %fft_dim=2D<br>• %fft_size=128 | — | [microbenchmarks/gpu/gpu_benchmarks](../checks/microbenchmarks/gpu/gpu_benchmarks/) |
| [FFTCheck](../checks/microbenchmarks/gpu/gpu_benchmarks/fft.py)<br>• %fft_dim=2D<br>• %fft_size=256 | — | [microbenchmarks/gpu/gpu_benchmarks](../checks/microbenchmarks/gpu/gpu_benchmarks/) |
| [FFTCheck](../checks/microbenchmarks/gpu/gpu_benchmarks/fft.py)<br>• %fft_dim=2D<br>• %fft_size=512 | — | [microbenchmarks/gpu/gpu_benchmarks](../checks/microbenchmarks/gpu/gpu_benchmarks/) |
| [FFTCheck](../checks/microbenchmarks/gpu/gpu_benchmarks/fft.py)<br>• %fft_dim=2D<br>• %fft_size=1024 | — | [microbenchmarks/gpu/gpu_benchmarks](../checks/microbenchmarks/gpu/gpu_benchmarks/) |
| [FFTCheck](../checks/microbenchmarks/gpu/gpu_benchmarks/fft.py)<br>• %fft_dim=3D<br>• %fft_size=128 | — | [microbenchmarks/gpu/gpu_benchmarks](../checks/microbenchmarks/gpu/gpu_benchmarks/) |
| [FFTCheck](../checks/microbenchmarks/gpu/gpu_benchmarks/fft.py)<br>• %fft_dim=3D<br>• %fft_size=256 | — | [microbenchmarks/gpu/gpu_benchmarks](../checks/microbenchmarks/gpu/gpu_benchmarks/) |
| [FFTCheck](../checks/microbenchmarks/gpu/gpu_benchmarks/fft.py)<br>• %fft_dim=3D<br>• %fft_size=512 | — | [microbenchmarks/gpu/gpu_benchmarks](../checks/microbenchmarks/gpu/gpu_benchmarks/) |
| [FFTCheck](../checks/microbenchmarks/gpu/gpu_benchmarks/fft.py)<br>• %fft_dim=3D<br>• %fft_size=1024 | — | [microbenchmarks/gpu/gpu_benchmarks](../checks/microbenchmarks/gpu/gpu_benchmarks/) |
| [ParallelAlgos](../checks/microbenchmarks/gpu/gpu_benchmarks/parallel_algos.py)<br>• %algo=radix-sort<br>• %_executable_opts=21 | — | [microbenchmarks/gpu/gpu_benchmarks](../checks/microbenchmarks/gpu/gpu_benchmarks/) |
| [ParallelAlgos](../checks/microbenchmarks/gpu/gpu_benchmarks/parallel_algos.py)<br>• %algo=radix-sort<br>• %_executable_opts=27 | — | [microbenchmarks/gpu/gpu_benchmarks](../checks/microbenchmarks/gpu/gpu_benchmarks/) |
| [ParallelAlgos](../checks/microbenchmarks/gpu/gpu_benchmarks/parallel_algos.py)<br>• %algo=radix-sort<br>• %_executable_opts=30 | — | [microbenchmarks/gpu/gpu_benchmarks](../checks/microbenchmarks/gpu/gpu_benchmarks/) |
| [ParallelAlgos](../checks/microbenchmarks/gpu/gpu_benchmarks/parallel_algos.py)<br>• %algo=scan<br>• %_executable_opts=24 | — | [microbenchmarks/gpu/gpu_benchmarks](../checks/microbenchmarks/gpu/gpu_benchmarks/) |
| [ParallelAlgos](../checks/microbenchmarks/gpu/gpu_benchmarks/parallel_algos.py)<br>• %algo=scan<br>• %_executable_opts=26 | — | [microbenchmarks/gpu/gpu_benchmarks](../checks/microbenchmarks/gpu/gpu_benchmarks/) |
| [ParallelAlgos](../checks/microbenchmarks/gpu/gpu_benchmarks/parallel_algos.py)<br>• %algo=scan<br>• %_executable_opts=29 | — | [microbenchmarks/gpu/gpu_benchmarks](../checks/microbenchmarks/gpu/gpu_benchmarks/) |
| [ParallelAlgos](../checks/microbenchmarks/gpu/gpu_benchmarks/parallel_algos.py)<br>• %algo=reduce<br>• %_executable_opts=26 | — | [microbenchmarks/gpu/gpu_benchmarks](../checks/microbenchmarks/gpu/gpu_benchmarks/) |
| [ParallelAlgos](../checks/microbenchmarks/gpu/gpu_benchmarks/parallel_algos.py)<br>• %algo=reduce<br>• %_executable_opts=29 | — | [microbenchmarks/gpu/gpu_benchmarks](../checks/microbenchmarks/gpu/gpu_benchmarks/) |
| [ParallelAlgos](../checks/microbenchmarks/gpu/gpu_benchmarks/parallel_algos.py)<br>• %algo=reduce<br>• %_executable_opts=31 | — | [microbenchmarks/gpu/gpu_benchmarks](../checks/microbenchmarks/gpu/gpu_benchmarks/) |
| [NCCLTestsCE](../checks/microbenchmarks/xccl/xccl_tests.py)<br>• %test_name=all_reduce<br>• %image_tag=cuda12.9.1-ubuntu24.04 | Point-to-Point and All-Reduce NCCL tests with CE | [microbenchmarks/xccl](../checks/microbenchmarks/xccl/) |
| [NCCLTestsCE](../checks/microbenchmarks/xccl/xccl_tests.py)<br>• %test_name=sendrecv<br>• %image_tag=cuda12.9.1-ubuntu24.04 | Point-to-Point and All-Reduce NCCL tests with CE | [microbenchmarks/xccl](../checks/microbenchmarks/xccl/) |
| [NCCLTestsUENV](../checks/microbenchmarks/xccl/xccl_tests.py)<br>• %test_name=all_reduce | Point-to-Point and All-Reduce NCCL tests with uenv | [microbenchmarks/xccl](../checks/microbenchmarks/xccl/) |
| [NCCLTestsUENV](../checks/microbenchmarks/xccl/xccl_tests.py)<br>• %test_name=sendrecv | Point-to-Point and All-Reduce NCCL tests with uenv | [microbenchmarks/xccl](../checks/microbenchmarks/xccl/) |
| [CudaNodeBurnGemmCE](../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) | GPU Node burn GEMM test for A100/GH200 using CE | [microbenchmarks/cpu_gpu/node_burn](../checks/microbenchmarks/cpu_gpu/node_burn/) |
| [CPUNodeBurnGemmCE](../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) | CPU Node burn GEMM test for A100/GH200-nodes using CE | [microbenchmarks/cpu_gpu/node_burn](../checks/microbenchmarks/cpu_gpu/node_burn/) |
| [CudaNodeBurnStreamCE](../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) | GPU Node burn Stream test for A100/GH200 using CE | [microbenchmarks/cpu_gpu/node_burn](../checks/microbenchmarks/cpu_gpu/node_burn/) |
| [CPUNodeBurnStreamCE](../checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) | CPU Node burn Stream test for A100/GH200-nodes using CE | [microbenchmarks/cpu_gpu/node_burn](../checks/microbenchmarks/cpu_gpu/node_burn/) |
| [ParaviewBuildGadgetPlugin](../checks/apps/paraview/build-gadget-plugin/paraview_buildgadgetplugin.py) | — | [apps/paraview/build-gadget-plugin](../checks/apps/paraview/build-gadget-plugin/) |
| [ParaviewCatalystClipping](../checks/apps/paraview/catalystclipping/paraview_catalystclipping.py) | — | [apps/paraview/catalystclipping](../checks/apps/paraview/catalystclipping/) |
| [ParaView_coloredSphere](../checks/apps/paraview/paraview.py) | — | [apps/paraview](../checks/apps/paraview/) |
| [ParaView_catalystClipping](../checks/apps/paraview/paraview.py) | — | [apps/paraview](../checks/apps/paraview/) |
| [ParaviewColoredSphere](../checks/apps/paraview/coloredsphere/paraview_coloredsphere.py) | — | [apps/paraview/coloredsphere](../checks/apps/paraview/coloredsphere/) |
| [Cp2kCheckMD_UENVExec](../checks/apps/cp2k/cp2k_uenv.py) | — | [apps/cp2k](../checks/apps/cp2k/) |
| [Cp2kCheckPBE_UENVExec](../checks/apps/cp2k/cp2k_uenv.py) | — | [apps/cp2k](../checks/apps/cp2k/) |
| [VaspCheckUENV](../checks/apps/vasp/vasp_check_uenv.py)<br>• %num_nodes=1 | — | [apps/vasp](../checks/apps/vasp/) |
| [VaspCheckUENV](../checks/apps/vasp/vasp_check_uenv.py)<br>• %num_nodes=2 | — | [apps/vasp](../checks/apps/vasp/) |
| [QeSiriusCheckAuSurfUENVExec](../checks/apps/q-e-sirius/q-e-sirius_check_uenv.py) | — | [apps/q-e-sirius](../checks/apps/q-e-sirius/) |
| [uenv_ascent_intro_cpp](../checks/apps/ascent/ascent.py)<br>• %exe=ascent_first_light_example | Build Ascent intro (C++) | [apps/ascent](../checks/apps/ascent/) |
| [uenv_ascent_intro_cpp](../checks/apps/ascent/ascent.py)<br>• %exe=ascent_scene_example1 | Build Ascent intro (C++) | [apps/ascent](../checks/apps/ascent/) |
| [uenv_ascent_intro_cpp](../checks/apps/ascent/ascent.py)<br>• %exe=ascent_scene_example2 | Build Ascent intro (C++) | [apps/ascent](../checks/apps/ascent/) |
| [uenv_ascent_intro_cpp](../checks/apps/ascent/ascent.py)<br>• %exe=ascent_scene_example3 | Build Ascent intro (C++) | [apps/ascent](../checks/apps/ascent/) |
| [uenv_ascent_intro_cpp](../checks/apps/ascent/ascent.py)<br>• %exe=ascent_scene_example4 | Build Ascent intro (C++) | [apps/ascent](../checks/apps/ascent/) |
| [uenv_ascent_intro_cpp](../checks/apps/ascent/ascent.py)<br>• %exe=ascent_pipeline_example1 | Build Ascent intro (C++) | [apps/ascent](../checks/apps/ascent/) |
| [uenv_ascent_intro_cpp](../checks/apps/ascent/ascent.py)<br>• %exe=ascent_extract_example1 | Build Ascent intro (C++) | [apps/ascent](../checks/apps/ascent/) |
| [uenv_ascent_intro_cpp](../checks/apps/ascent/ascent.py)<br>• %exe=ascent_extract_example2 | Build Ascent intro (C++) | [apps/ascent](../checks/apps/ascent/) |
| [uenv_ascent_intro_cpp](../checks/apps/ascent/ascent.py)<br>• %exe=ascent_extract_example3 | Build Ascent intro (C++) | [apps/ascent](../checks/apps/ascent/) |
| [uenv_ascent_intro_cpp](../checks/apps/ascent/ascent.py)<br>• %exe=ascent_extract_example4 | Build Ascent intro (C++) | [apps/ascent](../checks/apps/ascent/) |
| [uenv_ascent_intro_cpp](../checks/apps/ascent/ascent.py)<br>• %exe=ascent_query_example1 | Build Ascent intro (C++) | [apps/ascent](../checks/apps/ascent/) |
| [uenv_ascent_intro_cpp](../checks/apps/ascent/ascent.py)<br>• %exe=ascent_trigger_example1 | Build Ascent intro (C++) | [apps/ascent](../checks/apps/ascent/) |
| [uenv_ascent_intro_cpp](../checks/apps/ascent/ascent.py)<br>• %exe=ascent_binning_example1 | Build Ascent intro (C++) | [apps/ascent](../checks/apps/ascent/) |
| [uenv_ascent_doublegyre_python](../checks/apps/ascent/ascent.py) | Run Ascent test: DoubleGyre (Python) | [apps/ascent](../checks/apps/ascent/) |
| [uenv_ascent_doublegyre_cpp](../checks/apps/ascent/ascent.py) | Build and Run Ascent test: DoubleGyre (C++) | [apps/ascent](../checks/apps/ascent/) |
| [uenv_ascent_heatdiffusion_python](../checks/apps/ascent/ascent.py) | Run Ascent test: HeatDiffusion (Python, serial and parallel) | [apps/ascent](../checks/apps/ascent/) |
| [uenv_ascent_heatdiffusion_cpp](../checks/apps/ascent/ascent.py) | Build and Run Ascent test: HeatDiffusion (C++) | [apps/ascent](../checks/apps/ascent/) |
| [uenv_ascent_noise](../checks/apps/ascent/ascent.py) | Build and Run Ascent test: noise (C++) | [apps/ascent](../checks/apps/ascent/) |
| [uenv_ascent_kripke](../checks/apps/ascent/ascent.py) | Build and Run Ascent test: kripke (C++) | [apps/ascent](../checks/apps/ascent/) |
| [uenv_ascent_cloverleaf3d](../checks/apps/ascent/ascent.py) | Build and Run Ascent test: CloverLeaf3D (F90) | [apps/ascent](../checks/apps/ascent/) |
| [NamdCheckUENVExec](../checks/apps/namd/namd_check_uenv.py) | NAMD STMV Benchmark | [apps/namd](../checks/apps/namd/) |
| [lammps_gpu_test](../checks/apps/lammps/lammps.py) | — | [apps/lammps](../checks/apps/lammps/) |
| [lammps_kokkos_test](../checks/apps/lammps/lammps.py) | — | [apps/lammps](../checks/apps/lammps/) |
| [PyTorchMegatronLM_CE](../checks/apps/pytorch/pytorch_megatronlm.py)<br>• %model=llama3-8b | — | [apps/pytorch](../checks/apps/pytorch/) |
| [PyTorchMegatronLM_CE](../checks/apps/pytorch/pytorch_megatronlm.py)<br>• %model=llama3-70b | — | [apps/pytorch](../checks/apps/pytorch/) |
| [PyTorchMegatronLM_UENV](../checks/apps/pytorch/pytorch_megatronlm.py)<br>• %model=llama3-8b | — | [apps/pytorch](../checks/apps/pytorch/) |
| [PyTorchMegatronLM_UENV](../checks/apps/pytorch/pytorch_megatronlm.py)<br>• %model=llama3-70b | — | [apps/pytorch](../checks/apps/pytorch/) |
| [TorchHammerCEMultiGPU](../checks/apps/pytorch/torch_hammer_ce_checks.py) | Torch Hammer CE Multi-GPU Benchmark | [apps/pytorch](../checks/apps/pytorch/) |
| [PyTorchNCCLAllReduce](../checks/apps/pytorch/pytorch_allreduce.py)<br>• %image=nvcr.io#nvidia/pytorch:25.06-py3 | All-reduce PyTorch benchmark with CE (NCCL version) | [apps/pytorch](../checks/apps/pytorch/) |
| [PyTorchDdpCeNv](../checks/apps/pytorch/pytorch_nvidia.py)<br>• %num_nodes=1<br>• %aws_ofi_nccl=True<br>• %image=nvcr.io#nvidia/pytorch:25.06-py3 | Check the training throughput using the ContainerEngine and NVIDIA NGC | [apps/pytorch](../checks/apps/pytorch/) |
| [PyTorchDdpCeNvlarge](../checks/apps/pytorch/pytorch_nvidia.py)<br>• %num_nodes=3<br>• %aws_ofi_nccl=True<br>• %image=nvcr.io#nvidia/pytorch:25.06-py3 | Check the training throughput using the ContainerEngine and NVIDIA NGC | [apps/pytorch](../checks/apps/pytorch/) |
| [PyTorchDdpCeNvlarge](../checks/apps/pytorch/pytorch_nvidia.py)<br>• %num_nodes=8<br>• %aws_ofi_nccl=True<br>• %image=nvcr.io#nvidia/pytorch:25.06-py3 | Check the training throughput using the ContainerEngine and NVIDIA NGC | [apps/pytorch](../checks/apps/pytorch/) |
| [SphExa](../checks/apps/sphexa/sphexa_uenv.py)<br>• %sph_build_type=Release<br>• %sph_infile=50c.h5<br>• %num_gpus=4<br>• %sph_testcase=evrard<br>• %sph_steps=2<br>• %sph_side=150 | SphExa test | [apps/sphexa](../checks/apps/sphexa/) |
| [QeCheckAuSurfUENVExec](../checks/apps/quantumespresso/quantumespresso_check_uenv.py) | — | [apps/quantumespresso](../checks/apps/quantumespresso/) |