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
|                   | OSU all-to-all                              |    Y       |   1min?  |  ?  | 
|                   | NCCL allreduce (2min)                       |    Y       |   2 min  |  ?  | 
|                   | Network bandwidth between gpus (per node)   |    Y       |   1min   |  cxi bandwidth | 
	

  
## Production test suite 

Single and multi-node checks to be performed regularly (nightly) in production using a subset of nodes

* Tag: production
  * See: [Test coverage](https://confluence.cscs.ch/spaces/reframe/pages/894965254/Test+coverage) 

| Category          | Description                                   | Test name               |
|:---               |:---                                           |:---                     | 
| Apps	            | CP2K 	                                    |                         | 
|                   | Gromacs	                                    |                         | 
|                   | LAMMPS                                        |                         | 
|                   | PyTorch	                                    |                         | 
|                   | QuantumEspresso	                            |                         | 
| Microbenchmarks   | Memory allocation speed	                    |                         | 
| Libraries	        | dlaf	                                    |                         | 
| Programming environment | Build Hello World (C/C++/F)	            |                         | 
|                         | Affinity	                            |                         | 
|                         | Test if multi-threaded MPI works	    | MpiInitTest             |
| System Components | Node availability	                             |                        |
|                   |  Check if Gres is properly configured on Slurm | SlurmGPUGres           |
| Config/Integration| Slurm: partitions                             | TODO                    | 
|                   | Slurm: number of nodes available              | TODO                    | 
|                   | Slurm: Check if Gres is properly configured on Slurm | SlurmGPUGres     |
|                   | Slurm: new features                           | TODO                    |
| Containers        |  Test OSU benchmarsk with CE	            | OMB_MPICH_CE, OMB_OMPI_CE |
|                   |  Stream benchmark with ce	                    | RunNVGPUJobCE           |
|                   | Verify simple container runs	            |  RunJobCE               |
|                   | 	Test SSH to a container	                    |  SSH_CE                 |


## Maintenance test suite 

Single and multi-node checks to be performed  before & after vCluster interventions (using a reservation)

* Tags: appscheckout + production
  * See: [Test coverage](https://confluence.cscs.ch/spaces/reframe/pages/894965254/Test+coverage) 

- **Remark:** Application checks can be the same as Production, but ideally they should be using more nodes
