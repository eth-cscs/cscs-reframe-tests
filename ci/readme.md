# vcue.yml

- showing tests to be updated --> see gitlab ci

## tests not included in ci yet

### gpu tests

- prgenv/cuda/cuda_aware_mpi.py
- prgenv/cuda/cuda_memtest_check.py
- prgenv/cuda_fortran.py
- prgenv/cuda_nvml.py
- prgenv/cuda_samples.py
- prgenv/hip/build_hip.py
- prgenv/openacc.py
- prgenv/opencl.py
- microbenchmarks/gpu/dgemm/dgemm.py
- microbenchmarks/gpu/gpu_burn/gpu_burn_test.py
- microbenchmarks/gpu/kernel_latency/kernel_latency.py
- microbenchmarks/gpu/memory_bandwidth/memory_bandwidth.py
- microbenchmarks/gpu/pointer_chase/pointer_chase.py
- microbenchmarks/gpu/roofline/berkeley-ert-gpu.py
- microbenchmarks/gpu/shmem/shmem.py
- libraries/cray-libsci/libsci_acc.py
- compile/libsci_acc_symlink.py

#### mch tests to drop

- microbenchmarks/mpi/halo_exchange/halo_cell_exchange.py
- mch/automatic_arrays_acc.py
- mch/collectives_halo.py
- mch/cuda_stress_test.py
- mch/gpu_direct_acc.py
- mch/gpu_direct_cuda.py
- mch/multi_device_openacc.py
- mch/openacc_cuda_mpi_cppstd.py
- libraries/gridtools/gridtools_tests.py

### supported application tests

> https://confluence.cscs.ch/display/SRM/Automation+rules

- cp2k: ./apps/cp2k/cp2k_check.py
- cpmd: ./apps/cpmd/cpmd_check.py
- gromacs: ./apps/gromacs/gromacs_check.py
- lammps: ./apps/lammps/lammps_check.py
- icon: ./apps/icon/rrtmgp_check.py
- namd: ./apps/namd/namd_check.py
- quantum espresso: 
    - ./apps/quantumespresso/quantumespresso_check.py
    - ./apps/sirius/sirius_check.py
- vasp: ./apps/vasp/vasp_check.py
- paraview: ./apps/paraview/paraview_check.py
- amber (deprecated): ./apps/amber/amber_check.py

## ML tests

- apps/pytorch/pytorch_distr_check.py
- apps/pytorch/pytorch_horovod_check.py
- apps/spark/spark_check.py
- apps/tensorflow/tf2_horovod_check.py

### spci tests

- apps/greasy/greasy_check.py
- apps/jupyter/check_ipcmagic.py
- apps/python/numpy_check.py
- system/io/ior_check.py
- system/jobreport/gpu_report.py
- system/nvidia/nvidia_smi_check.py
- system/openstack/s3_check.py
- system/openstack/src/s3_create_bucket.py
- system/openstack/src/s3_create_small_object.py
- system/openstack/src/s3_delete.py
- system/openstack/src/s3_download_large_object.py
- system/openstack/src/s3_upload_large_object.py
- system/openstack/src/tools.py
- system/slurm/cscs_usertools.py
- system/slurm/gres_gpu.py
- system/slurm/gres.py
- system/slurm/hetjob.py
- system/slurm/slurm.py
- tools/jupyter/jupyter_tests.py

### container tests

- containers/buildah/buildah_check.py
- containers/sarus/check_cuda_nbody.py
- containers/sarus/check_gpu_ids.py
- containers/sarus/check_horovod.py
- containers/sarus/check_osu_benchmarks_cuda.py
- containers/sarus/check_osu_benchmarks.py
- containers/sarus/check_pull_command.py
- containers/sarus/check_pyfr.py
- containers/sarus/check_root_squash_bind_mount.py

### perf. tools tests

- ...
