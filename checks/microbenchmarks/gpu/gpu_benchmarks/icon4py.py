# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class ICON4PyBenchmarks(rfm.RunOnlyRegressionTest):
    descr = 'ICON4Py GPU benchmarks -Diffusion & DyCore Granules-'
    maintainers = ['SSA']
    valid_systems = ['+uenv +amdgpu', '+uenv +nvgpu']
    valid_prog_environs = ['+uenv +prgenv +rocm', '+uenv +prgenv +cuda']
    tags = {'production', 'uenv'}
    time_limit = '60m'
    sourcesdir = None
    build_locally = False
    prerun_cmds = [
        'python -m venv .venv',
        'source .venv/bin/activate',
        'git clone --depth 1 -b main https://github.com/C2SM/icon4py.git',
        'cd icon4py',
        'pip install --upgrade pip',
        'pip install uv',
        'rm uv.lock',
        'export CC=$(which gcc) MPICH_CC=$(which gcc)',
        'export CXX=$(which g++) MPICH_CXX=$(which g++)',
    ]
    executable = 'pytest'
    executable_opts = [
        '-v',
        '-m continuous_benchmarking',
        '--benchmark-only',
        '--benchmark-warmup=on',
        '--benchmark-warmup-iterations=30',
        '--benchmark-json=icon4py_benchmarks.json',
        '--backend=dace_gpu --grid=icon_benchmark_regional',
        ('model/atmosphere/diffusion/tests/diffusion/integration_tests'
         '/test_benchmark_diffusion.py'
         '::test_diffusion_benchmark'
         ),
        ('model/atmosphere/dycore/tests/dycore/integration_tests/'
         'test_benchmark_solve_nonhydro.py'
         '::test_benchmark_solve_nonhydro[True-False]'
         ),
    ]

    @run_before('run')
    def prepare_run(self):
        if 'rocm' in self.current_environ.features:
            self.prerun_cmds += [
                'uv sync --extra all --python $(which python) --active',
                ('uv pip uninstall mpi4py && '
                 'uv pip install --no-binary mpi4py mpi4py'
                 ),
                ('export CUPY_INSTALL_USE_HIP=1 '
                 'HCC_AMDGPU_TARGET=gfx942 '
                 'ROCM_HOME=/user-environment/env/default'
                 ),
                'uv pip install git+https://github.com/cupy/cupy.git',
            ]
        else:
            self.prerun_cmds += [
                ('uv sync --extra all '
                 '--extra cuda12 --python $(which python) --active'
                 ),
                ('uv pip uninstall mpi4py && '
                 'uv pip install --no-binary mpi4py mpi4py'
                 ),
            ]

    @sanity_function
    def validate_test(self):
        diffusion_granule = sn.assert_found(
            (r'^\s*model/atmosphere/diffusion/tests/'
             r'diffusion/integration_tests/'
             r'test_benchmark_diffusion\.py'
             r'::test_diffusion_benchmark\s*PASSED'
             ),
            self.stdout)
        dycore_granule = sn.assert_found(
            (r'^\s*model/atmosphere/dycore/tests/'
             r'dycore/integration_tests/test_benchmark_solve_nonhydro\.py'
             r'::test_benchmark_solve_nonhydro\[True-False\]\s*PASSED'),
            self.stdout)
        return diffusion_granule and dycore_granule

    @run_before('performance')
    def set_perf_vars(self):
        diffusion_regex = (
            r'^\s*test_diffusion_benchmark\s+'
            r'(?P<min>\d+(?:\.\d+)?)'            # Min
            r'(?:\s+\([^)]+\))?\s+'              # optional '(...)'
            r'(?P<max>\d+(?:\.\d+)?)'            # Max
            r'(?:\s+\([^)]+\))?\s+'              # optional '(...)'
            r'(?P<mean>\d+(?:\.\d+)?)'           # Mean
        )
        diffusion_granule_mean = sn.extractsingle(
            diffusion_regex, self.stdout, 'mean', float)

        dycore_regex = (
            r'^\s*test_benchmark_solve_nonhydro\[True-False\]\s+'
            r'(?P<min>\d+(?:\.\d+)?)'            # Min
            r'(?:\s+\([^)]+\))?\s+'              # optional '(...)'
            r'(?P<max>\d+(?:\.\d+)?)'            # Max
            r'(?:\s+\([^)]+\))?\s+'              # optional '(...)'
            r'(?P<mean>\d+(?:\.\d+)?)'           # Mean
        )
        dycore_granule_mean = sn.extractsingle(
            dycore_regex, self.stdout, 'mean', float)

        self.perf_variables = {
            'diffusion_granule':
                sn.make_performance_function(diffusion_granule_mean, 'ms'),
            #
            'dycore_granule':
                sn.make_performance_function(dycore_granule_mean, 'ms'),
        }
