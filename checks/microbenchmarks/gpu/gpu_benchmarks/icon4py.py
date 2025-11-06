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
    ]
    time_limit = '20m'
    build_locally = False
    tags = {'production', 'uenv'}
    executable = 'pytest'
    executable_opts = [
        "-v",
        "-m continuous_benchmarking",
        "--benchmark-only",
        "--benchmark-warmup=on",
        "--benchmark-warmup-iterations=30",
        "--benchmark-json=TESTING.json",
        "--backend=dace_gpu --grid=icon_benchmark_regional",
        "model/atmosphere/diffusion/tests/diffusion/integration_tests/test_benchmark_diffusion.py::test_diffusion_benchmark",
        "model/atmosphere/dycore/tests/dycore/integration_tests/test_benchmark_solve_nonhydro.py::test_benchmark_solve_nonhydro[True-False]",
    ]

    @run_before('run')
    def prepare_run(self):
        if 'rocm' in self.current_environ.features:
            self.prerun_cmds +=[
                'rm uv.lock',
                'export CC=$(which gcc) MPICH_CC=$(which gcc) CXX=$(which g++) MPICH_CXX=$(which g++)',
                'uv sync --extra all --python $(which python) --active',
                'uv pip uninstall mpi4py && uv pip install --no-binary mpi4py mpi4py',
                'export CUPY_INSTALL_USE_HIP=1 HCC_AMDGPU_TARGET=gfx942 ROCM_HOME=/user-environment/env/default',
                'uv pip install git+https://github.com/cupy/cupy.git',
            ]
        else:
            self.prerun_cmds +=[
                'uv sync --extra all --extra cuda12 --python $(which python) --active',
            ]

    @sanity_function
    def validate_test(self):
        return sn.assert_found(r'PASSED', self.stdout)
