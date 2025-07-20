# Node validator test suite 

## Single-node checks be performed at boot time and upon node re-configuration

* Tag: vs-node-validator
  
| Category          | Description                                 | Duration | Test name               |
|:---               |:---                                         |   ----   |:---                     | 
| ~HW check~        |~Run dgemm on all GPUs and CPUs~  (*)        | ~30s~   | ~[node-burn-ce.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py)~ |
| UENV              | Check if uenv status runs                   | 5s       | [uenv_status.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/system/uenv/uenv_status.py)          | 
|                   | Build c++ hello world                       |          | TODO                    |
| Integration tests | Check for installed packages ([list](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/system/integration/constants.py))    | 5s       | [PackagePresentTest](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/system/integration/v-cluster_config.py)     | 
|                   | Check if mount points (main.tf) are present |          | [MountPointExistsTest](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/system/integration/v-cluster_config.py)    |
|                   | Check if environment vars are correctly set |          | [EnvVariableConfigTest](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/system/integration/v-cluster_config.py)   |
|                   | Check if proxy config is correctly set      |          | [ProxyConfigTest](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/system/integration/v-cluster_config.py)  |
| Slurm             | Selected Epilog and Prolog tests            | 5s       | 002-slowlink, 006-bugs.sh, 020-gpumem.sh    | 

- **Remark:** (*) running tests such as node burn locally (without slurm) would require to maintain the same test twice and, therefore for the moment being, it was agreed that we should find an alternative solution for these tests.  

## Node vetting / Appscheckout test suite 

* Single and multi-node checks to be performed after interventions 
  * To be executed against all nodes in a reservation (such as appscheckout or maintenance)
  * Tag: appscheckout

| Category          | Description                                 | All-nodes  | Duration | Test name               |
|:---               |:---                                         |   ----     |   ----   |:---                     | 
| HW check          | Run dgemm on all GPUs and CPUs	          |    Y       |  1min    | [node-burn-ce.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) |     
|                   | Stream (memory bandwidth test)	          |    Y       |  1min    | [node-burn-ce.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) |  
| Network           | Simple MPI (CPI)	                          |    Y       |   5s     | [mpi_cpi.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/prgenv/mpi_cpi.py) | 
|                   | OSU all-to-all                              |    Y       |   1min?  |  TODO  | 
|                   | NCCL allreduce (2min)                       |    Y       |   2 min  |  [pytorch_allreduce.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/apps/pytorch/pytorch_allreduce.py#L24) | 
|                   | Network bandwidth between gpus (per node)   |    Y       |   1min   |  [cxi_gpu_loopback_bw.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/system/network/cxi_gpu_loopback_bw.py) | 
	

  
## Production test suite 

Single and multi-node checks to be performed regularly (nightly) in production using a subset of nodes

* Tag: production
  * See: [Test coverage](https://confluence.cscs.ch/spaces/reframe/pages/894965254/Test+coverage) 

| Category          | Description                                   | Test name               |
|:---               |:---                                           |:---                     | 
| Apps	            | CP2K 	                                    | [cp2k_uenv.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/apps/cp2k/cp2k_uenv.py)  | 
|                   | Gromacs	                                    | [gromacs_check.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/apps/gromacs/gromacs_check.py) | 
|                   | LAMMPS                                        | [lammps.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/apps/lammps/lammps.py) | 
|                   | PyTorch	                                    | [pytorch_allreduce.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/apps/pytorch/pytorch_allreduce.py), [pytorch_nvidia.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/apps/pytorch/pytorch_nvidia.py) | 
|                   | QuantumEspresso	                            | [quantumespresso_check_uenv.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/apps/quantumespresso/quantumespresso_check_uenv.py) | 
| Microbenchmarks   | Memory allocation speed	                    | [alloc_speed.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/microbenchmarks/cpu/alloc_speed/alloc_speed.py) | 
| Libraries	        | dlaf	                                    | [dlaf.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/libraries/dlaf/dlaf.py)| 
| Programming environment | Build Hello World (C/C++/F)	            | [helloworld.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/prgenv/helloworld.py) | 
|                         | CUDA Samples (?)                        | [cuda_samples.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/prgenv/cuda_samples.py) |
|                         | Checks that nvml can report GPU informations | [cuda_nvml.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/prgenv/cuda_nvml.py) |
|                         | Affinity	                            | [affinity_check.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/prgenv/affinity_check.py) | 
|                         | Test if multi-threaded MPI works	    | [mpi.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/prgenv/mpi.py)  |
| Config/Integration| Slurm:  | [slurm.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/system/slurm/slurm.py) | 
|                   | Slurm: partitions correspond to TF definition | TODO                    | 
|                   | Slurm: Slurm Transparent Hugepages            | [slurm.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/system/slurm/slurm.py#L448) | 
|                   | Slurm: number of nodes available per partition | [SlurmQueueStatusCheck](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/system/slurm/slurm.py#L285) | 
|                   | Slurm: Check if Gres is properly configured on Slurm | [SlurmGPUGres](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/system/slurm/gres_gpu.py#L11)     |
|                   | Slurm: new features                           | TODO                    |
| Containers        |  Test OSU benchmarsk with CE	            | [OMB_MPICH_CE](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/containers/container_engine/omb.py#L77), [OMB_OMPI_CE](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/containers/container_engine/omb.py#L101) |
|                   |  Stream benchmark with ce	                    | RunNVGPUJobCE - [ce_import_run_image.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/system/ce/ce_import_run_image.py#L64)  |
|                   | Verify simple container runs	            | RunJobCE - [ce_import_run_image.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/system/ce/ce_import_run_image.py#L44)  |
|                   | 	Test SSH to a container	                    |  [ssh.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/containers/container_engine/ssh.py) |
|                   | 	CUDA nbody with CE                          |  [check_cuda_nbody.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/containers/container_engine/check_cuda_nbody.py) |




## Maintenance test suite 

Single and multi-node checks to be performed  before & after vCluster interventions (using a reservation)

* Tags: appscheckout + production
  * See: [Test coverage](https://confluence.cscs.ch/spaces/reframe/pages/894965254/Test+coverage) 

- **Remark:** Application checks can be the same as Production, but ideally they should be using more nodes
