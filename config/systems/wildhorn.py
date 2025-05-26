# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings
#

import reframe.utility.osext as osext
import copy


base_config = {
    'modules_system': 'lmod',
    'resourcesdir': '/capstor/apps/cscs/common/regression/resources',
    'partitions': [
        {
            'name': 'login',
            'scheduler': 'local',
            'time_limit': '10m',
            'environs': [
                'builtin',
            ],
            'descr': 'Login nodes',
            'max_jobs': 4,
            'launcher': 'local'
        },
        {
            'name': 'normal',
            'descr': 'Multicore nodes (AMD EPYC 7742, 256|512GB/cn)',
            'scheduler': 'slurm',
            'time_limit': '10m',
            'environs': [
                'builtin',
            ],
            'max_jobs': 100,
            'extras': {
                'cn_memory': 256,
            },
            'features': ['remote', 'ce'],
            'access': ['--mem=0', f'--account={osext.osgroup()}'],
            'resources': [
                {
                    'name': 'switches',
                    'options': ['--switches={num_switches}']
                },
                {
                    'name': 'memory',
                    'options': ['--mem={mem_per_node}']
                },
            ],
            'launcher': 'srun'
        },
    ]
}

wildhorn_sys = copy.deepcopy(base_config)
wildhorn_sys['name'] = 'wildhorn'
wildhorn_sys['descr'] = 'Alps Cray EX Supercomputer'
wildhorn_sys['hostnames'] = ['wildhorn']

site_configuration = {
    'systems': [
        wildhorn_sys
    ],
    'environments': [
     
    ],
}
