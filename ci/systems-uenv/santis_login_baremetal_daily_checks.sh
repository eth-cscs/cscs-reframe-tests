#!/bin/bash -x

rm -fr venv_reframe
python3 -m venv venv_reframe
source venv_reframe/bin/activate
pip install reframe-hpc

reframe -c config/cscs.py -c checks/prgenv/mpi.py --report-junit=$REPORT -r

deactivate

