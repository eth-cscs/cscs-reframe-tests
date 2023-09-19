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

from reframe.core.exceptions import ConfigError

uenv_file = os.environ.get('UENV_FILE', None)
uenv_mount = os.environ.get('UENV_MOUNT', '/user-environment')

if uenv_file is None:
    raise ConfigError('UENV_FILE is not set')

image_path = pathlib.Path(uenv_file)
if not image_path.exists():
    raise ConfigError(f"uenv image: '{image_path}' does not exist")

image_name = image_path.stem

# Options for the Slurm plugin to mount the Squashfs uenv image
uenv_access = [f'--uenv-file={uenv_file}', f'--uenv-mount={uenv_mount}']

try:
    rfm_meta = image_path.parent / f'{image_name}.yaml'
    with open(rfm_meta) as image_envs:
        image_environments = yaml.load(
            image_envs.read(), Loader=yaml.BaseLoader)
except OSError as err:
    raise ConfigError(f"problem loading the metadata from '{rfm_meta}'")


environs = image_environments.keys()
environ_names =  ([f'{image_name}_{e}'for e in environs] or
                  [f'{image_name}_builtin'])

partitions = [
    {
        'name': f'nvgpu',
        'scheduler': 'slurm',
        'time_limit': '10m',
        'environs': environ_names,
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
        'launcher': 'srun'
    },
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
        'features': ['gpu', 'amdgpu', 'remote', 'uenv'],
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
        'features': ['remote', 'uenv'],
        'launcher': 'srun'
    }
]

if image_environments:
    actual_environs = []

for k, v in image_environments.items():
    env = {
        'target_systems': ['hohgant']
    }
    env.update(v)

    env['prepare_cmds'] = [f'source {v["activation"]}']
    env['name'] = f'{image_name}_{k}'
    del env['activation']
    actual_environs.append(env)

site_configuration = {
    'systems': [
        {
            'name': 'hohgant',
            'descr': 'Hohgant vcluster with uenv',
            'hostnames': ['hohgant'],
            'resourcesdir': '/users/manitart/reframe/resources',
            'modules_system': 'nomod',
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
            'target_systems': ['hohgant'],
        }
    ],
    'environments': actual_environs,
    'general': [
        {
             'resolve_module_conflicts': False,
             'target_systems': ['hohgant']
        }
    ]
}
