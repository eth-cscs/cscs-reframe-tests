#!/bin/bash

date
echo "# SLURM_JOBID=$SLURM_JOBID"

git clone https://github.com/C2SM/icon4py.git && cd icon4py
git checkout 5485bcacb1dbc7688b1e7d276d4e2e28362c5444
rm uv.lock

curl -LsSf https://astral.sh/uv/install.sh | UV_INSTALL_DIR="$PWD/bin" sh
export PATH="$PWD/bin:$PATH"
export UV_NO_CACHE=1

HOME="$PWD/_home" uv python install $ICON4PY_PYTHON_VERSION

uv sync --no-cache --extra all --python $PWD/_home/.local/bin/python$ICON4PY_PYTHON_VERSION
source .venv/bin/activate

uv --no-cache pip uninstall mpi4py && \
uv --no-cache pip install --no-binary mpi4py mpi4py && \
uv --no-cache pip install git+https://github.com/cupy/cupy.git

echo "# install done"
date
