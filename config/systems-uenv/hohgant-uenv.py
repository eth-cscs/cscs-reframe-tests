# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings
#

import os
import pathlib
import yaml

uenv_file = os.environ.get('UENV_FILE', None)
uenv_mount = os.environ.get('UENV_MOUNT', '/user-environment')

uenv_access = [] 
uenv_modules_path = [] 
image_name = None 
partitions = []
features = []

if uenv_file is not None:
    uenv_access = [
        f'--uenv-file={uenv_file}',
        f'--uenv-mount={uenv_mount}',
    ]
    uenv_modules_path = [f'module use {uenv_mount}/modules']
    image_path = pathlib.Path(uenv_file)
    image_name = image_path.stem

with open(image_path.parent / f'{image_name}.yaml') as image_envs:
    image_environments = yaml.load(image_envs.read(), Loader=yaml.BaseLoader)


if image_name is not None:
    environs = image_environments['environments'] 
    environ_names =  ([f'{image_name}_{e["name"]}'for e in environs] or 
                      [f'{image_name}_builtin'])

    partitions = [
#        {
#            'name': f'nvgpu',
#            'scheduler': 'slurm',
#            'time_limit': '10m',
#            'environs': environ_names,
#            'container_platforms': [
#                {
#                    'type': 'Sarus',
#                },
#                {
#                    'type': 'Singularity',
#                }
#            ],
#            'max_jobs': 100,
#            'extras': {
#                'cn_memory': 500,
#            },
#            'access': ['-pnvgpu'] + uenv_access,
#            'resources': [
#                {
#                    'name': 'switches',
#                    'options': ['--switches={num_switches}']
#                },
#                {
#                    'name': 'memory',
#                    'options': ['--mem={mem_per_node}']
#                },
#            ],
#            'features': ['gpu', 'nvgpu', 'remote', 'uenv'] + features,
#            'devices': [
#                {
#                    'type': 'gpu',
#                    'arch': 'sm_80',
#                    'num_devices': 4
#                }
#            ],
#            'prepare_cmds': uenv_modules_path,
#            'launcher': 'srun'
#        },
        {
            'name': f'amdgpu',
            'scheduler': 'slurm',
            'time_limit': '10m',
            'environs': environ_names,
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
            'features': ['gpu', 'amdgpu', 'remote', 'uenv'] + features,
            'prepare_cmds': uenv_modules_path,
            'launcher': 'srun'
        },
        {
            'name': f'cpu',
            'scheduler': 'slurm',
            'time_limit': '10m',
            'environs': environ_names,
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
            'features': ['remote', 'uenv'] + features,
            'prepare_cmds': uenv_modules_path,
            'launcher': 'srun'
        }
    ]


environs = image_environments['environments'] 

if environs:
    actual_environs = []

for e in environs: 
    env = {
        'target_systems': ['hohgant-uenv']
    }
    env.update(e)
    env['name'] = f'{image_name}_{e["name"]}'
    actual_environs.append(env)

site_configuration = {
    'systems': [
        {
            'name': 'hohgant-uenv',
            'descr': 'Hohgant vcluster with uenv',
            'hostnames': ['hohgant'],
            'resourcesdir': '/users/manitart/reframe/resources',
            'modules_system': 'lmod',
            'partitions': partitions
        }
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
    'environments': actual_environs,
    'general': [
        {
             'resolve_module_conflicts': False,
             'target_systems': ['hohgant-uenv']
        }
    ]
}
