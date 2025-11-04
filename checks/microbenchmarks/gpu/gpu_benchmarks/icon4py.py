# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
from uenv import uarch


@rfm.simple_test
class ICON4PyBenchmarks(rfm.RunOnlyRegressionTest):
    descr = 'ICON4Py GPU benchmarks'
    maintainers = ['SSA']
    valid_systems = ['+uenv +amdgpu', '+uenv +nvgpu']
    valid_prog_environs = ['+uenv +prgenv +rocm', '+uenv +prgenv +cuda']
    sourcesdir = None
    prerun_cmds = [
        'python -m venv .venv',
        'source .venv/bin/activate',
        'git clone --depth 1 -b main https://github.com/C2SM/icon4py.git',
        'cd icon4py',
        'pip install --upgrade pip',
        'pip install uv',
        'rm uv.lock',
        'export CC=$(which gcc) MPICH_CC=$(which gcc) CXX=$(which g++) MPICH_CXX=$(which g++)',
        'uv sync --extra all --python $(which python) --active',
        'uv pip uninstall mpi4py && uv pip install --no-binary mpi4py mpi4py',
        'export CUPY_INSTALL_USE_HIP=1 HCC_AMDGPU_TARGET=gfx942 ROCM_HOME=/user-environment/env/default',
        'uv pip install git+https://github.com/cupy/cupy.git',
    ]
    time_limit = '20m'
    build_locally = False
    tags = {'production', 'uenv'}
    executable = 'pytest'
    executable_opts = [
        "-v -m continuous_benchmarking "
        "--benchmark-only "
        "--benchmark-json=TESTING.json "
        "--backend=gtfn_gpu --grid=icon_benchmark "
        "model/atmosphere/diffusion/tests/diffusion/integration_tests/test_benchmark_diffusion.py::test_run_diffusion_benchmark[grid0]" 
    ]
