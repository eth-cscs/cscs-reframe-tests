# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class HPLCheck(rfm.RunOnlyRegressionTest):
    nnodes = parameter([9, 16, 5292])
    num_tasks_per_node = 1
    valid_prog_environs = ['PrgEnv-intel']
    modules = ['craype-accel-nvidia60', 'craype-hugepages8M']
    executable = 'xhpl'
    env_vars = {
        'CPU_CORES_PER_RANK': '11',
        'CUDA_COPY_SPLIT_THRESHOLD_MB': '1',
        'MONITOR_GPU': '1',
        'GPU_TEMP_WARNING': '75',
        'GPU_CLOCK_WARNING': '1230',
        'GPU_POWER_WARNING': '270',
        'GPU_DGEMM_SPLIT': '0.983',
        'GPU_DGEMM_SPLIT2': '0.995',
        'OMP_NUM_THREADS': '$CPU_CORES_PER_RANK',
        'MKL_NUM_THREADS': '$CPU_CORES_PER_RANK',
        'CUDA_DEVICE_MAX_CONNECTIONS': '12',
        'CUDA_AUTO_BOOST': '0',
        'MPICH_GNI_NDREG_MAXSIZE': '32M',
        'HUGETLB_VERBOSE': '0',
        'HUGETLB_DEFAULT_PAGE_SIZE': '8M',
    }

    @run_after('init')
    def set_descr(self):
        self.descr = f'HPL {self.nnodes} nodes check'

    @run_after('init')
    def set_valid_systems(self):
        if self.nnodes <= 16:
            self.valid_systems = ['daint:gpu', 'dom:gpu']
        else:
            self.valid_systems = ['daint:gpu']

    @run_after('setup')
    def set_sourcesdir(self):
        self.sourcesdir = os.path.join(
            self.current_system.resourcesdir, 'HPL', self.current_system.name,
            str(self.nnodes)
        )

    @run_before('run')
    def set_num_tasks(self):
        self.num_tasks = self.nnodes

    @run_before('run')
    def setjobopts(self):
        self.job.options += ['--cpu-freq=2601000']
        self.job.options += ['--ntasks-per-core=2']

    @run_before('run')
    def set_trsm_cutoff(self):
        if self.nnodes <= 16:
            self.env_vars['TRSM_CUTOFF'] = '35000'
        else:
            self.env_vars['TRSM_CUTOFF'] = '30000'

    @sanity_function
    def assert_end_of_tests(self):
        return sn.assert_found(r'End of Tests', self.stdout)

    @run_before('performance')
    def set_perf_reference(self):
        if self.nnodes == 9:
            self.reference = {
                'dom:gpu': {
                    'perf': (1.728e+04, -0.10, None, 'Gflop/s')
                },
                'daint:gpu': {
                    'perf': (1.641e+04, -0.10, None, 'Gflop/s')
                }
            }
        elif self.nnodes == 16:
            self.reference = {
                'dom:gpu': {
                    'perf': (2.5004e+04, -0.10, None, 'Gflop/s')
                },
                'daint:gpu': {
                    'perf': (2.504e+04, -0.10, None, 'Gflop/s')
                }
            }
        else:
            self.reference = {
                'daint:gpu': {
                    'perf': (1.959e+07, -0.05, None, 'Gflop/s')
                }
            }

    @performance_function('Gflop/s')
    def perf(self):
        return sn.extractsingle(r'WR05L2L8(\s+\d+(.\d+)?){5}\s+(?P<perf>\S+)',
                                self.stdout, 'perf', float, item=1)
