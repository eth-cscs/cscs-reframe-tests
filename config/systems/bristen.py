# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings
#

import reframe.utility.osext as osext


base_config = {
    'modules_system': 'nomod',
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
            'descr': 'A100',
            'scheduler': 'slurm',
            'time_limit': '10m',
            'container_platforms': [
            ],
            'environs': [
                'builtin',
            ],
            'max_jobs': 100,
            'extras': {
                'cn_memory': 500,
            },
            'features': ['ce', 'gpu', 'nvgpu', 'remote', 'scontrol', 'uenv'],
            'access': [f'--account=a-{osext.osgroup()}'],
            'resources': [
                {
                    'name': 'switches',
                    'options': ['--switches={num_switches}']
                },
                {
                    'name': 'gres',
                    'options': ['--gres={gres}']
                },
                {
                    'name': 'memory',
                    'options': ['--mem={mem_per_node}']
                },
            ],
            'devices': [
                {
                    'type': 'gpu',
                    'arch': 'sm_80',
                    'num_devices': 4
                }
                ],
            'launcher': 'srun',
        },
    ]
}

base_config['name'] = 'bristen'
base_config['descr'] = 'Bristen vcluster'
base_config['hostnames'] = ['bristen']

site_configuration = {
    'systems': [
        base_config,
    ],
    'environments': [
    ],
}
