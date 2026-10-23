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
    'resourcesdir': '/capstor/store/cscs/cscs/public/reframe/resources',
    'max_local_jobs': 20,
    'partitions': [
        {
            'name': 'login',
            'descr': 'Login nodes',
            'scheduler': 'local',
            'time_limit': '10m',
            'environs': [
                'builtin',
            ],
            'max_jobs': 20,
            'launcher': 'local'
        },
        {
            'name': 'normal',
            'descr': 'NVIDIA A100',
            'scheduler': 'slurm',
            'time_limit': '10m',
#             'container_platforms': [
#                 {
#                      'type': 'Sarus',
#                 },
#             ],
            'environs': [
                'builtin',
            ],
            'max_jobs': 1000,
            'extras': {
                'cn_memory': 456704,
            },
            'features': [
                'sarus', 'gpu', 'nvgpu', 'remote', 'scontrol', 'uenv'
            ],
            'access': [
                f'--partition=normal',
                f'--account={osext.osgroup()}',
                f'--gpus-per-node=4'
            ],
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
        {
            'name': 'cpu',
            'descr': 'AMD_EPYC_7713',
            'scheduler': 'slurm',
            'time_limit': '10m',
            'container_platforms': [
                {
                     'type': 'Sarus',
                },
            ],
            'environs': [
                'builtin',
            ],
            'max_jobs': 1000,
            'extras': {
                'cn_memory': 456704,
            },
            'features': [
                'sarus', 'remote', 'scontrol', 'uenv'
            ],
            'access': [
                f'--partition=postproc',
                f'--account={osext.osgroup()}'
            ],
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
            'launcher': 'srun',
        },
    ]
}

base_config['name'] = 'linard'
base_config['descr'] = 'Linard vcluster'
base_config['hostnames'] = ['linard']

site_configuration = {
    'systems': [
        base_config,
    ],
    'environments': [
    ],
}
