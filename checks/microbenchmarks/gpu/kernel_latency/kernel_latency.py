# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys

import reframe as rfm
from hpctestlib.microbenchmarks.gpu.kernel_latency import GpuKernelLatency

sys.path.append(os.path.abspath(os.path.join(__file__, '../../../..')))
import microbenchmarks.gpu.hooks as hooks


@rfm.simple_test
class gpu_kernel_latency_check(GpuKernelLatency):
    valid_systems = [
        'daint:gpu', 'dom:gpu', 'arolla:cn', 'tsa:cn', 'ault:amdv100',
        'ault:intelv100', 'ault:amda100', 'ault:amdvega'
    ]
    num_tasks = 0
    sys_reference = variable(dict, value={
        'sync': {
            'dom:gpu': {
                'latency': (6.6, None, 0.10, 'us')
            },
            'daint:gpu': {
                'latency': (6.6, None, 0.10, 'us')
            },
            'ault:intelv100': {
                'latency': (7.15, None, 0.10, 'us')
            },
            'ault:amdv100': {
                'latency': (7.15, None, 0.10, 'us')
            },
            'ault:amda100': {
                'latency': (9.65, None, 0.10, 'us')
            },
            'ault:amdvega': {
                'latency': (15.1, None, 0.10, 'us')
            },
        },
        'async': {
            'dom:gpu': {
                'latency': (2.2, None, 0.10, 'us')
            },
            'daint:gpu': {
                'latency': (2.2, None, 0.10, 'us')
            },
            'ault:intelv100': {
                'latency': (1.83, None, 0.10, 'us')
            },
            'ault:amdv100': {
                'latency': (1.83, None, 0.10, 'us')
            },
            'ault:amda100': {
                'latency': (2.7, None, 0.10, 'us')
            },
            'ault:amdvega': {
                'latency': (2.64, None, 0.10, 'us')
            },
        },
    })
    maintainers = ['@teojgo']
    tags = {'benchmark', 'diagnostic', 'craype', 'health'}

    @run_after('init')
    def set_valid_prog_environs(self):
        cs = self.current_system.name
        if cs in {'dom', 'daint'}:
            self.valid_prog_environs = ['PrgEnv-cray', 'PrgEnv-pgi',
                                        'PrgEnv-gnu', 'PrgEnv-nvidia']
        elif cs in {'arolla', 'tsa'}:
            self.valid_prog_environs = ['PrgEnv-pgi']
        elif cs in {'ault'}:
            self.valid_prog_environs = ['PrgEnv-gnu']
        else:
            self.valid_prog_environs = []

    # Inject external hooks
    @run_after('setup')
    def set_gpu_arch(self):
        hooks.set_gpu_arch(self)

    @run_before('run')
    def set_num_gpus_per_node(self):
        hooks.set_num_gpus_per_node(self)

    @run_before('performance')
    def set_references(self):
        '''Set the refences based on the ``launch_mode`` parameter.'''
        self.reference = self.sys_reference[self.launch_mode]
