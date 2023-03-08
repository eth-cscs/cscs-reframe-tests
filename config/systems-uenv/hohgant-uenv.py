# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings
#

import os

uenv_file = os.environ.get('UENV_FILE', None)
uenv_mount = os.environ.get('UENV_MOUNT', '/user-environment')

uenv_access = [] 
uenv_modules_path = [] 

if uenv_file is not None:
    uenv_access = [
        f'--uenv-file={uenv_file}',
        f'--uenv-mount={uenv_mount}',
    ]
    uenv_modules_path = [f'module use {uenv_mount}/modules']

site_configuration = {
    'systems': [
        {
            'name': 'hohgant-uenv',
            'descr': 'Hohgant vcluster with uenv',
            'hostnames': ['hohgant'],
            'modules_system': 'lmod',
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
                    'name': 'nvgpu',
                    'scheduler': 'slurm',
                    'time_limit': '10m',
                    'environs': [
                        'builtin',
                    ],
                    'container_platforms': [
                        {
                            'type': 'Sarus',
                        },
                        {
                            'type': 'Singularity',
                        }
                    ],
                    'max_jobs': 100,
                    'extras': {
                        'cn_memory': 500,
                    },
                    'access': ['-pnvgpu'] + uenv_access,
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
                    'features': ['gpu', 'nvgpu', 'remote', 'uenv'],
                    'devices': [
                        {
                            'type': 'gpu',
                            'arch': 'sm_80',
                            'num_devices': 4
                        }
                    ],
                    'prepare_cmds': uenv_modules_path,
                    'launcher': 'srun'
                },
                {
                    'name': 'amdgpu',
                    'scheduler': 'slurm',
                    'time_limit': '10m',
                    'environs': [
                        'builtin',
                    ],
                    'max_jobs': 100,
                    'extras': {
                        'cn_memory': 500,
                    },
                    'access': ['-pamdgpu'] + uenv_access,
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
                    'features': ['gpu', 'amdgpu', 'remote', 'uenv'],
                    'prepare_cmds': uenv_modules_path,
                    'launcher': 'srun'
                },
                {
                    'name': 'cpu',
                    'scheduler': 'slurm',
                    'time_limit': '10m',
                    'environs': [
                        'builtin',
                    ],
                    'max_jobs': 100,
                    'extras': {
                        'cn_memory': 500,
                    },
                    'access': ['-pcpu'] + uenv_access ,
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
                    'features': ['remote', 'uenv'],
                    'prepare_cmds': uenv_modules_path,
                    'launcher': 'srun'
                }
            ]
        },
    ],
    'modes': [
        {
            'name': 'production',
            'options': [
                '--unload-module=reframe',
                '--exec-policy=async',
                '-Sstrict_check=1',
                '--prefix=$SCRATCH/$USER/regression/production',
                '--report-file=$SCRATCH/$USER/regression/production/reports/prod_report_{sessionid}.json',
                '--save-log-files',
                '--tag=production',
                '--timestamp=%F_%H-%M-%S'
            ],
            'target_systems': ['hohgant-uenv'],
        }
    ],
    'general': [
        {
             'resolve_module_conflicts': False,
             'target_systems': ['hohgant-uenv']
        }
    ]
}
