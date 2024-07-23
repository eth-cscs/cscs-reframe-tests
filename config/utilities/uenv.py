import os
import pathlib
import yaml

import reframe.utility.osext as osext
from reframe.core.exceptions import ConfigError


_UENV_MOUNT_DEFAULT = '/user-environment'
_UENV_CLI = 'uenv'
_UENV_DELIMITER = ','
_UENV_MOUNT_DELIMITER = '@'


def _get_uenvs():
    uenv = os.environ.get('UENV', None)
    if uenv is None:
        return uenv

    help_cli = osext.run_command(f'{_UENV_CLI} --help', check=True, shell=True)
    uenv_environments = []
    uenv_list = uenv.split(_UENV_DELIMITER)

    for uenv in uenv_list:
        uenv_name, *image_mount = uenv.split(_UENV_MOUNT_DELIMITER)
        if len(image_mount) > 0:
            image_mount = image_mount[0]
        else:
            image_mount = _UENV_MOUNT_DEFAULT

        image_path = osext.run_command(
            f"{_UENV_CLI} image inspect {uenv_name} --format '{{sqfs}}'",
            shell=True
        ).stdout.strip()

        target_system = osext.run_command(
            f"{_UENV_CLI} image inspect {uenv_name} --format '{{system}}'",
            shell=True
        ).stdout.strip()

        image_path = pathlib.Path(image_path)

        try:
            print(f"image_path={image_path}")
            print(f"{image_path.parent} /// {image_path.stem}.yaml")
            rfm_meta = image_path.parent / f'{image_path.stem}.yaml'
            with open(rfm_meta) as image_envs:
                image_environments = yaml.load(
                    image_envs.read(), Loader=yaml.BaseLoader)
                print(f"# TO --- loading the metadata from '{rfm_meta}'")
        except OSError as err:
            msg = f"# TO --- problem loading the metadata from '{rfm_meta}'"
            # print(err)
            raise ConfigError(msg)

        for k, v in image_environments.items():
            env = {
                'target_systems': [target_system]
            }
            env.update(v)

            activation = v['activation']

            # FIXME: Assume that an activation script is given, to be sourced
            if isinstance(activation, str):
                if not activation.startswith(image_mount):
                    raise ConfigError(
                        f'activation script of {k!r} is not consistent '
                        f'with the mount point: {image_mount!r}'
                    )

                env['prepare_cmds'] = [f'source {activation}']
            elif isinstance(activation, list):
                env['prepare_cmds'] = activation
            else:
                raise ConfigError(
                    'activation has to be either a file to be sourced or a '
                    'list of commands to be executed to configure the '
                    'environment'
                )

            # Replace characters that create problems in environment names
            uenv_name_pretty = uenv_name.replace(":", "_").replace("/", "_")
            env['name'] = f'{uenv_name_pretty}_{k}'

            env['resources'] = {
                'uenv': {
                    'mount': image_mount,
                    'file': str(image_path),
                }
            }

            # Added as a prepare_cmd for the environment
            del env['activation']

            uenv_environments.append(env)

    return uenv_environments


UENV = _get_uenvs() or None
