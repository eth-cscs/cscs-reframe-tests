# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)


import os
import pathlib
import yaml

import reframe.utility.osext as osext
from reframe.core.exceptions import ConfigError

uenv = os.environ.get('UENV', None)

if uenv is None:
    raise ConfigError('UENV is not set')

uenv_environments = []
environ_names = []
uenv_list = uenv.split(',')

for uenv in uenv_list:
    uenv_file, *image_mount = uenv.split(':')

    if len(image_mount) > 0:
        image_mount = image_mount[0]
    else:
        image_mount = '/user-environment'

    image_path = pathlib.Path(uenv_file)
    if not image_path.exists():
        raise ConfigError(f"uenv image: '{image_path}' does not exist")

    image_name = str(image_path).replace('/', '_')

    try:
        rfm_meta = image_path.parent / f'{image_path.stem}.yaml'
        with open(rfm_meta) as image_envs:
            image_environments = yaml.load(
                image_envs.read(), Loader=yaml.BaseLoader)
            print(f"# --- loading the metadata from '{rfm_meta}'")
    except OSError as err:
        raise ConfigError(f"problem loading the metadata from '{rfm_meta}'")

    environs = image_environments.keys()
    environ_names.extend([f'{image_name}_{e}'for e in environs] or
                         [f'{image_name}_builtin'])

    for k, v in image_environments.items():
        env = {
            'target_systems': ['santis']
        }
        env.update(v)

        activation = v['activation']

        # FIXME: Assume that an activation script is given, to be sourced
        if isinstance(activation, str):
            if not activation.startswith(image_mount):
                raise ConfigError(
                        f'activation script of {k!r} is not consistent '
                        f'with the mount point: {image_mount!r}')

            env['prepare_cmds'] = [f'source {activation}']
        elif isinstance(activation, list):
            env['prepare_cmds'] = activation
        else:
           raise ConfigError(
               f'activation has to be either a string or list of strings'
            )

        env['name'] = f'{image_name}_{k}'
        env['resources'] = {
            'uenv': {
                'mount': image_mount,
                'file': uenv_file,
            }
        }

        # Added as a prepare_cmd for the environment
        del env['activation']

        uenv_environments.append(env)

site_configuration = {
    'systems': [
        {
            'name': 'santis',
            'descr': 'santis vcluster with uenv',
            'hostnames': ['santis'],
            'resourcesdir': '/apps/common/UES/reframe/resources/',
            'modules_system': 'nomod',
            'partitions': [
                {
                    'name': 'normal',
                    'scheduler': 'slurm',
                    'time_limit': '10m',
                    'environs': environ_names,
                    'max_jobs': 100,
                    'extras': {
                        'cn_memory': 500,
                    },
                    'access': [
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
                        {
                            'name': 'uenv',
                            'options': [
                                '--uenv={file}:{mount}',
                            ]
                        }
                    ],
                    'features': ['nvgpu', 'remote', 'scontrol', 'uenv'],
                    'devices': [
                        {
                            'type': 'gpu',
                            'arch': 'sm_90',
                            'num_devices': 4
                        }
                    ],
                    'launcher': 'srun'
                },
            ]
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
            'target_systems': ['santis'],
        }
    ],
    'environments': uenv_environments,
    'general': [
    ]
}
