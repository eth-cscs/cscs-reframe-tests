# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import re
import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class ICON4PyBenchmarks(rfm.RunOnlyRegressionTest):
    descr = 'ICON4Py Check -Diffusion & DyCore Granules-'
    maintainers = ['SSA']
    valid_systems = ['+uenv +amdgpu', '+uenv +nvgpu']
    valid_prog_environs = ['+uenv +rocm', '+uenv +cuda']
    tags = {'uenv', 'bencher'}
    time_limit = '60m'
    build_locally = False
    env_vars = {
        'ICON4PY_PYTHON_VERSION': '3.11',
        'UV_NO_CACHE': '1',
        'UV_CACHE_DIR': '$SCRATCH/.cache/uv',
        'CC': '$(which gcc)',
        'MPICH_CC': '$(which gcc)',
        'CXX': '$(which g++)',
        'MPICH_CXX': '$(which g++)',
        'HUGETLB_ELFMAP': 'no',
        'HUGETLB_MORECORE': 'no',
        'GT4PY_UNSTRUCTURED_HORIZONTAL_HAS_UNIT_STRIDE': '1',
        'PYTHONOPTIMIZE': '2',
        'GT4PY_BUILD_CACHE_LIFETIME': 'persistent',
    }
    executable = './_run.sh'
    executable_opts = ['2>&1']

    @run_before('run')
    def prepare_env(self):
        gpu_arch = self.current_partition.select_devices('gpu')[0].arch

        cache_folder = (
            f"{os.environ.get('SCRATCH')}/"
            f".cache/reframe_bencher_icon4py/"
        )
        sub_folder = (
            f"{self.current_system.name}="
            f"{gpu_arch}="
            f"{self.current_environ}"
        )
        sub_folder = re.sub(r'[^a-zA-Z0-9=]', '', sub_folder)
        cache_folder = os.path.join(cache_folder, sub_folder)
        self.env_vars['GT4PY_BUILD_CACHE_DIR'] = cache_folder

        if 'gfx' in gpu_arch:  # AMD GPU
            self.env_vars['CUPY_INSTALL_USE_HIP'] = '1'
            self.env_vars['HCC_AMDGPU_TARGET'] = gpu_arch
            self.env_vars['ROCM_HOME'] = '/user-environment/env/default'
        # elif 'sm_' in gpu_arch:  # CUDA GPU

    @run_before('run')
    def install_deps(self):
        self.prerun_cmds = ['./_install.sh &> _install.sh.log 2>&1']

    @sanity_function
    def validate_test(self):
        diffusion_granule = sn.assert_found(
            (r'^\s*model/atmosphere/diffusion/tests/'
             r'diffusion/integration_tests/'
             r'test_benchmark_diffusion\.py'
             r'::test_diffusion_benchmark[\s\S]*?PASSED'
             ), self.stdout)
        dycore_granule = sn.assert_found(
            (r'^\s*model/atmosphere/dycore/tests/'
             r'dycore/integration_tests/test_benchmark_solve_nonhydro\.py'
             r'::test_benchmark_solve_nonhydro\[True-False\][\s\S]*?PASSED'
             ), self.stdout)

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

    # TODO: add ref. (https://github.com/eth-cscs/cscs-reframe-tests/pull/440)
