# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings
#

base_config = {
    'modules_system': 'nomod',
    'resourcesdir': '/capstor/store/cscs/cscs/public/reframe/resources',
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
            'name': 'mi300',
            'descr': 'MI300',
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
            'features': ['ce', 'gpu', 'amdgpu', 'remote', 'scontrol', 'uenv'],
            'access': ['-pmi300'],
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
                    'arch': 'gfx942',
                    'num_devices': 4
                }
                ],
            'launcher': 'srun',
        },
        {
            'name': 'mi200',
            'descr': 'MI200',
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
            'features': ['ce', 'gpu', 'amdgpu', 'remote', 'scontrol', 'uenv'],
            'access': ['-pmi200'],
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
                    'arch': 'gfx90a',
                    'num_devices': 8
                }
            ],
            'launcher': 'srun',
        },

    ]
}

base_config['name'] = 'beverin'
base_config['descr'] = 'Beverin VCluster'
base_config['hostnames'] = ['beverin']

site_configuration = {
    'systems': [
        base_config,
    ],
    'environments': [
    ],
}
