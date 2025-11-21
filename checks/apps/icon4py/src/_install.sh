#!/bin/bash

py_version=$(python3 --version 2>&1 |awk '{print $2}')
minor_version=$(echo "$py_version" |cut -d \. -f2)
# echo "$py_version $minor_version"

if [ "$minor_version" -gt "13" ] ;then export RFM_ICON4PY_STOP='Y' ; else export RFM_ICON4PY_STOP='N' ; fi

if [ "$RFM_ICON4PY_STOP" == "Y" ] ;then
    echo "# INFO: $0: python/$py_version is incompatible with this test (try python/3.13), exiting..."
    exit 0

else

    date
    echo "# SLURM_JOBID=$SLURM_JOBID"

    git clone https://github.com/C2SM/icon4py.git
    cd icon4py
    git checkout 5485bcacb1dbc7688b1e7d276d4e2e28362c5444  # Commit: Update to GT4Py v1.1.0 (#933)
    rm uv.lock

    python -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install uv

    uv sync --extra all --python $(which python) --active

    uv pip uninstall mpi4py && uv pip install --no-binary mpi4py mpi4py
    uv pip install git+https://github.com/cupy/cupy.git

    echo "# install done"
    date

fi
