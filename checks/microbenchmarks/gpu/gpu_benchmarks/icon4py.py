# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class ICON4PyBenchmarks(rfm.RunOnlyRegressionTest):
    descr = 'ICON4Py GPU benchmarks -Diffusion & DyCore Granules-'
    maintainers = ['SSA']
    valid_systems = ['+uenv +amdgpu', '+uenv +nvgpu']
    valid_prog_environs = ['+uenv +prgenv +rocm', '+uenv +prgenv +cuda']
    tags = {'production', 'uenv'}
    time_limit = '20m'
    # sourcesdir = None
    build_locally = False
    env_vars = {
        'UV_CACHE_DIR': '$SCRATCH/.cache/uv',
        'CC': '$(which gcc)',
        'MPICH_CC': '$(which gcc)',
        'CXX': '$(which g++)',
        'MPICH_CXX': '$(which g++)',
        # GT4Py cache does not work properly for dace backend yet
        # 'GT4PY_BUILD_CACHE_LIFETIME': 'persistent',
        # 'GT4PY_BUILD_CACHE_DIR': '...',
    }
    executable = './_run.sh'
    executable_opts = ['2>&1']
#del     executable = 'pytest'
#del     executable_opts = [
#del         '-v',
#del         '-m continuous_benchmarking',
#del         '--benchmark-only',
#del         '--benchmark-warmup=on',
#del         '--benchmark-warmup-iterations=30',
#del         '--benchmark-json=icon4py_benchmarks.json',
#del         '--backend=dace_gpu --grid=icon_benchmark_regional',
#del         ('model/atmosphere/diffusion/tests/diffusion/integration_tests'
#del          '/test_benchmark_diffusion.py'
#del          '::test_diffusion_benchmark'
#del          ),
#del         # ('model/atmosphere/dycore/tests/dycore/integration_tests/'
#del         #  'test_benchmark_solve_nonhydro.py'
#del         #  '::test_benchmark_solve_nonhydro[True-False]'
#del         #  ),
#del     ]

#del     # @run_after('init')
#del     @run_before('run')
#del     def check_python_version(self):
#del         # sys.version_info(major=3, minor=11, micro=10, releaselevel='final', serial=0)
#del         hh = os.getenv('HOME') ;print(hh)
#del         print(sys.version_info)
#del         self.skip_if(sys.version_info.minor >= 14,
#del                      f'incompatible python version ({sys.version_info.minor})')

    @run_before('run')
    def install_deps(self):
        self.prerun_cmds = ['./_install.sh &> _install.sh.log 2>&1']
#del         self.prerun_cmds = [
#del             'echo "# SLURM_JOBID=$SLURM_JOBID"', 'date',
#del             'python -m venv .venv',
#del             'source .venv/bin/activate',
#del             'git clone https://github.com/C2SM/icon4py.git',
#del             'cd icon4py',
#del             # Commit: Update to GT4Py v1.1.0 (#933)
#del             'git checkout 5485bcacb1dbc7688b1e7d276d4e2e28362c5444',
#del             'pip install --upgrade pip',
#del             'pip install uv',
#del             'rm uv.lock',
#del             'uv sync --extra all --python $(which python) --active',
#del             ('uv pip uninstall mpi4py && '
#del              'uv pip install --no-binary mpi4py mpi4py && '
#del              'uv pip install git+https://github.com/cupy/cupy.git'),
#del             'date', '',
#del         ]
#del         self.postrun_cmds = ['', 'date']

    @run_before('run')
    def prepare_run(self):
        if 'rocm' in self.current_environ.features:
            gpu_arch = self.current_partition.select_devices('gpu')[0].arch
            self.env_vars['CUPY_INSTALL_USE_HIP'] = '1'
            self.env_vars['HCC_AMDGPU_TARGET'] = gpu_arch
            self.env_vars['ROCM_HOME'] = '/user-environment/env/default'

    @sanity_function
    def validate_test(self):
        rfm_stop = os.getenv('RFM_ICON4PY_STOP')
        if rfm_stop == 'Y':
            diffusion_granule = sn.assert_found('# INFO:', self.stdout)
        else:
            diffusion_granule = sn.assert_found(
                (r'^\s*model/atmosphere/diffusion/tests/'
                 r'diffusion/integration_tests/'
                 r'test_benchmark_diffusion\.py'
                 r'::test_diffusion_benchmark\s*PASSED'
                 ), self.stdout)
        # dycore_granule = sn.assert_found(
        #     (r'^\s*model/atmosphere/dycore/tests/'
        #      r'dycore/integration_tests/test_benchmark_solve_nonhydro\.py'
        #      r'::test_benchmark_solve_nonhydro\[True-False\]\s*PASSED'),
        #     self.stdout)

        return diffusion_granule  # and dycore_granule

#del Legend:
#del   Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd Quartile.
#del   OPS: Operations Per Second, computed as 1 / Mean
#del ================== 1 passed, 62 warnings in 494.14s (0:08:14) ==================

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

        # dycore_regex = (
        #     r'^\s*test_benchmark_solve_nonhydro\[True-False\]\s+'
        #     r'(?P<min>\d+(?:\.\d+)?)'            # Min
        #     r'(?:\s+\([^)]+\))?\s+'              # optional '(...)'
        #     r'(?P<max>\d+(?:\.\d+)?)'            # Max
        #     r'(?:\s+\([^)]+\))?\s+'              # optional '(...)'
        #     r'(?P<mean>\d+(?:\.\d+)?)'           # Mean
        # )
        # dycore_granule_mean = sn.extractsingle(
        #     dycore_regex, self.stdout, 'mean', float)

        self.perf_variables = {
            'diffusion_granule':
                sn.make_performance_function(diffusion_granule_mean, 'ms'),
            #
            # 'dycore_granule':
            #     sn.make_performance_function(dycore_granule_mean, 'ms'),
        }

    # TODO: add ref. (https://github.com/eth-cscs/cscs-reframe-tests/pull/440)
