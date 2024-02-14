#!/bin/bash -x

rm -fr venv_reframe
python3 -m venv venv_reframe
source venv_reframe/bin/activate
pip install reframe-hpc

CHECKS="\
-c config/cscs.py
-c checks/prgenv/cuda_nvml.py
-c checks/prgenv/cuda_fortran.py
-c checks/prgenv/mpi.py
-c checks/prgenv/openacc.py
-c checks/prgenv/helloworld.py
-c checks/libraries/io/hdf5.py
-c checks/libraries/io/netcdf.py
-c checks/libraries/io/pnetcdf.py
-c checks/microbenchmarks/cpu/alloc_speed/alloc_speed.py 
"

reframe $(xargs <<< ${CHECKS}) --report-junit=$REPORT -r

deactivate

