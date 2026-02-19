# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings
#

import reframe.utility.osext as osext


base_config = {
    'modules_system': 'nomod',
    'resourcesdir': '/vast/scratch/firecr02/reframe/resources',
    'partitions': [        
        {
            'name': 'normal',
            'descr': 'GH200',
            'scheduler': 'slurm',
            'time_limit': '10m',
            'container_platforms': [
            ],
            'environs': [
                'builtin',
            ],
            'max_jobs': 900,
            'extras': {
                'cn_memory': 825,
            },
            'features': ['ce', 'gpu', 'nvgpu', 'remote', 'scontrol', 'uenv', 'hugepages_slurm'],
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
                    'arch': 'sm_90',
                    'num_devices': 4
                }
                ],
            'launcher': 'srun',
        },
    ]
}

base_config['name'] = 'lys'
base_config['descr'] = 'Lys vcluster'
base_config['hostnames'] = ['lys']

site_configuration = {
    'systems': [
        base_config,
    ],
    'environments': [
    ],
}
