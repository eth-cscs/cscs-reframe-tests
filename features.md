# Features and extras in valid systems and programming environment

In order for tests to be as generic as possible we define the `valid_systems` and `valid_prog_environs` with features that should be included in the configuration.
More information [here](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.valid_systems).

## Features for partitions

| Feature | Description | Notes |
| --- | --- | --- |
| gpu | The partitions has a GPU | |
| nvgpu | The partitions has an NVIDIA GPU | Typically used with an environment with `cuda` feature |
| amdgpu | The partitions has an AMD GPU | | |
| remote | The partitions has a remote scheduler (set when you want to test the compute nodes of a cluster) | | |
| login | This partitios includes login nodes | | |
| sarus | Sarus is available in this partition | | |
| singularity | Singularity is available in this partition | | |
| uenv | Supports mounting and using user environments | |

## Features for environments

| Feature | Description | Notes |
| --- | --- | --- |
| cpe | This a CRAY based environment | |
| cuda | The environment has a CUDA compiler | |
| compiler | The environment provides a typical compiler | |
| openmp | The compiler of the environment supports openmp |
| mpi | The compiler of the environment supports openmp | |
| gromacs | GROMACS is avaliable in this environment | |
| netcdf-hdf5parallel | | |
| pnetcdf | | |
| alloc_speed | | |
| cuda-fortran | | |
| openacc | | |

## How to use the value of `extras` in a test

...

## How to use the processor/device specs in a test

...

## Extras for partitions

| Extras | Description | Type | Example value |
| --- | --- | --- | --- |
| cn_memory | Compute node memory | integer | 500 |
| launcher_options | | list[string] | ['--mpi=pmi2']

## Extras for environments

| Extras | Description | Type | Example value |
| --- | --- | --- | --- |
| openmp_flags | | list[string] | |
| launcher_options | | list[string] | ['--mpi=pmi2']

## Continuous Integration

Testing of CPE and UENV software stacks is automated using CSCS CI. A list of the current ReFrame tests integrated in the CI can be found here:
- CPE: https://gitlab.com/cscs-ci/ci-testing/webhook-ci/mirrors/6557018579987861/835515875116200/-/pipelines
- UENV: https://gitlab.com/cscs-ci/ci-testing/webhook-ci/mirrors/551234120955960/1440398897047549/-/pipelines

## How to test containers
