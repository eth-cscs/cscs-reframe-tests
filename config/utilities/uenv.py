import os
import pathlib
import yaml

import reframe.utility.osext as osext
from reframe.core.exceptions import ConfigError
from packaging.version import Version


_UENV_MOUNT_DEFAULT = '/user-environment'
_UENV_CLI = 'uenv'
_UENV_DELIMITER = ','
_UENV_MOUNT_DELIMITER = '@'
_RFM_META = pathlib.Path('extra') / 'reframe.yaml'


def _get_uenvs():
    uenv = os.environ.get('UENV', None)
    if uenv is None:
        return uenv

    uenv_environments = []
    uenv_list = uenv.split(_UENV_DELIMITER)
    uenv_version = osext.run_command(
        f'{_UENV_CLI} --version', shell=True
    ).stdout.strip()

    for uenv in uenv_list:
        uenv_name, *image_mount = uenv.split(_UENV_MOUNT_DELIMITER)
        if len(image_mount) > 0:
            image_mount = image_mount[0]
        else:
            image_mount = _UENV_MOUNT_DEFAULT

        inspect_cmd = f'{_UENV_CLI} image inspect {uenv_name} --format'

        image_path = osext.run_command(
            f"{inspect_cmd} '{{sqfs}}'", shell=True).stdout.strip()
        target_system = osext.run_command(
            f"{inspect_cmd} '{{system}}'", shell=True).stdout.strip()

        image_path = pathlib.Path(image_path)

        # FIXME temporary workaround for older uenv versions
        if Version(uenv_version) >= Version('5.1.0-dev'):
            meta_path = osext.run_command(
                f"{inspect_cmd} '{{meta}}'", shell=True
            ).stdout.strip()
            rfm_meta = pathlib.Path(meta_path) / _RFM_META
        else:
            rfm_meta = image_path.parent / 'store.yaml'

        try:
            with open(rfm_meta) as image_envs:
                image_environments = yaml.load(
                    image_envs.read(), Loader=yaml.BaseLoader)
                # print(f"# --- loading the metadata from '{rfm_meta}'")
        except OSError as err:
            raise ConfigError(
                f"problem loading the metadata from '{rfm_meta}'"
            )

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
            env['features'] += ['uenv']

            # Added as a prepare_cmd for the environment
            del env['activation']

            uenv_environments.append(env)

    return uenv_environments


UENV = _get_uenvs() or None
