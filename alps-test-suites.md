# Node validator test suite 

## Single-node checks be performed at boot time and upon node re-configuration

* Tag: vs-node-validator
  
| Category          | Description                                 | Duration | Test name               |
|:---               |:---                                         |   ----   |:---                     | 
| HW check          | Run dgemm on all GPUs and CPUs              | 30s      | [node-burn-ce.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py)         |
| UENV              | Check if uenv status runs                   | 5s       | [uenv_status.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/system/uenv/uenv_status.py)          | 
|                   | Build c++ hello world                       |          | TODO                    |
| Integration tests | Check for installed packages ([list](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/system/integration/constants.py))    | 5s       | [PackagePresentTest](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/system/integration/v-cluster_config.py)     | 
|                   | Check if mount points (main.tf) are present |          | [MountPointExistsTest](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/system/integration/v-cluster_config.py)    |
|                   | Check if environment vars are correctly set |          | [EnvVariableConfigTest](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/system/integration/v-cluster_config.py)   |
|                   | Check if proxy config is correctly set      |          | [ProxyConfigTest](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/system/integration/v-cluster_config.py)  |


	

## Appscheckout test suite 

Single and multi-node checks to be performed after node interventions (using a reservation)
* Tag: appscheckout

| Category          | Description                                 | Multi-node | Duration | Test name               |
|:---               |:---                                         |   ----     |   ----   |:---                     | 
| HW check          | Run dgemm on all GPUs and CPUs	          |    N       | 10min	  | [node-burn-ce.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) |     
|                   | Stream (memory bandwidth test)	          |    N       |  10s     | [node-burn-ce.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py) |  
| Network           | Simple MPI 	                          |    Y       |   5s     | [mpi_cpi.py](https://github.com/eth-cscs/cscs-reframe-tests/blob/main/checks/prgenv/mpi_cpi.py) | 
|                   | OSU all-to-all                              |    Y       |          | 	    | 
|                   | ....                                        |    Y       |          | 	    | 
	
	

## Maintenance test suite 

Single and multi-node checks to be performed before & after vCluster interventions (using a reservation)

* Tag: maintenance
  * See: [Test coverage](https://confluence.cscs.ch/spaces/reframe/pages/894965254/Test+coverage) 

| Category          | Description                                 | Test name               |
|:---               |:---                                         | :---                     | 
|                   | ....                                        | ??                    | 

## Production test suite 

Single and multi-node checks to be performed regularly in production using a subset of nodes

* Tag: production
  * See: [Test coverage](https://confluence.cscs.ch/spaces/reframe/pages/894965254/Test+coverage) 

| Category          | Description                                 | Test name               |
|:---               |:---                                         |:---                     | 
| Apps	            | CP2K 	                                      |                         | 
|                   | Gromacs	                                    |                         | 
|                   | LAMMPS                                      |                         | 
|                   | PyTorch	                                    |                         | 
|                   | QuantumEspresso	                            |                         | 
| Microbenchmarks   | Memory allocation speed	                    |                         | 
| Libraries	        | dlaf	                                      |                         | 
| Programming environment | Build Hello World (C/C++/F)	          |                         | 
|                         | Affinity	                            |                         | 
|                         | Test if multi-threaded MPI works	    | MpiInitTest             |
| System Components | Node availability	                          |                         |
|                   |  Check if Gres is properly configured on Slurm | SlurmGPUGres            |
| Containers        |  Test OSU benchmarsk with CE	              | OMB_MPICH_CE, OMB_OMPI_CE |
|                   |  Stream benchmark with ce	                  | RunNVGPUJobCE           |
|                   | Verify simple container runs	              |  RunJobCE               |
|                   | 	Test SSH to a container	                  |             | SSH_CE                  |
