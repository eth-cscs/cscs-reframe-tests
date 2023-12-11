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

uenv = os.environ.get('UENV', None)

if uenv is None:
    raise ConfigError('UENV is not set')

# FIXME: Only the first image:mount pair is currenty used
uenv_list = uenv.split(',')
uenv_first = uenv_list[0]

uenv_file, *image_mount = uenv_first.split(':')
if len(image_mount) > 0:
    image_mount = image_mount[0]
else:
    image_mount = '/user-environment'

image_path = pathlib.Path(uenv_file)
if not image_path.exists():
    raise ConfigError(f"uenv image: '{image_path}' does not exist")

image_name = image_path.stem

# Options for the Slurm plugin to mount the Squashfs uenv image
uenv_access = [f'--uenv-file={uenv_file} --uenv-mount={image_mount}']

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
        'name': 'nvgpu',
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
        'name': 'amdgpu',
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
]

if image_environments:
    actual_environs = []

for k, v in image_environments.items():
    env = {
        'target_systems': ['clariden']
    }
    env.update(v)
    activation_script = v['activation']

    # FIXME: Handle the activation script based on the image mount point
    if not activation_script.startswith(image_mount):
        raise ConfigError(
                f'activation script of {k!r} is not consistent '
                f'with the mount point: {image_mount!r}')

    env['prepare_cmds'] = [f'source {activation_script}']
    env['name'] = f'{image_name}_{k}'
    del env['activation']
    actual_environs.append(env)

site_configuration = {
    'systems': [
        {
            'name': 'clariden',
            'descr': 'clariden vcluster with uenv',
            'hostnames': ['clariden'],
            'resourcesdir': '/apps/common/UES/reframe/resources/',
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
            'target_systems': ['clariden'],
        }
    ],
    'environments': actual_environs,
    'general': [
        {
             # 'resolve_module_conflicts': False,
             'target_systems': ['clariden']
        }
    ]
}
