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
_RFM_META_DIR = pathlib.Path('meta')


def uarch(partition):
    """
    Return the uenv uarch tag of the nodes in a reframe partition description.

    partition: reframe partition information
    returns:
       'a100', 'gh200', 'mi200', 'mi300', 'zen2' or 'zen3'
       None -> unable to identify uarch
    """
    gpus = partition.devices
    if gpus:
        device = gpus[0]
        if device.arch == 'sm_90':
            return 'gh200'
        if device.arch == 'sm_80':
            return 'a100'
        if device.arch == 'gfx90a':
            return 'mi200'
        if device.arch == 'gfx942':
            return 'mi300'
        return None

    cpus = partition.processor
    if cpus.arch == 'zen2':
        return 'zen2'
    if cpus.arch == 'zen3':
        return 'zen3'

    return None


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
            image_mount = None

        # Check if given uenv_name is a path to a squashfs archive
        uenv_path = pathlib.Path(uenv_name)
        if uenv_path.is_file():
            # We cannot inspect for target systems
            target_system = '*'
            image_path = uenv_path
            rfm_meta = image_path.parent / _RFM_META_DIR / _RFM_META
        else:
            inspect_cmd = f'{_UENV_CLI} image inspect {uenv_name} --format'

            image_path = osext.run_command(
                f"{inspect_cmd}='{{sqfs}}'", shell=True).stdout.strip()
            target_system = osext.run_command(
                f"{inspect_cmd}='{{system}}'", shell=True).stdout.strip()

            image_path = pathlib.Path(image_path)
            # Check that uenv was pulled
            if not image_path.is_file():
                raise ConfigError(f"{uenv_name} is missing, "
                    f"try pulling it with: uenv image pull {uenv_name}")
            try:
                if image_path.stat().st_size == 0:
                    raise ConfigError(f"{uenv_name} is empty, "
                        f"try pulling it with: uenv image pull {uenv_name}")
            except FileNotFoundError:
                raise ConfigError(f"{uenv_name} was not found")

            # FIXME temporary workaround for older uenv versions
            if Version(uenv_version) >= Version('5.1.0-dev'):
                meta_path = osext.run_command(
                    f"{inspect_cmd}='{{meta}}'", shell=True
                ).stdout.strip()
                rfm_meta = pathlib.Path(meta_path) / _RFM_META
            else:
                rfm_meta = image_path.parent / 'store.yaml'

        try:
            with open(rfm_meta) as image_envs:
                image_environments = yaml.load(
                    image_envs.read(), Loader=yaml.BaseLoader)
        except OSError as err:
            print(f'Skipping uenv `{uenv}`, there was an error '
                  f'reading the metadata: {err}')

            continue

        for k, v in image_environments.items():
            # strip out the fields that are not to be part reframe environment
            activation = v.pop('activation', [])
            views = v.pop('views', [])

            env = {
                'target_systems': [target_system]
            }
            env.update(v)

            if isinstance(activation, list):
                env['prepare_cmds'] = activation
            # FIXME: this is deprecated and should be removed
            elif isinstance(activation, str):
                env['prepare_cmds'] = [f'source {activation}']
            else:
                raise ConfigError(
                    'activation has to be a list of commands to be '
                    'executed to configure the environment'
                )

            # Replace characters that create problems in environment names
            uenv_name_pretty = uenv_name.replace(":", "_").replace("/", "_")
            env['name'] = f'{uenv_name_pretty}_{k}'
            env['resources'] = {
                'uenv': {
                    'file': str(image_path),
                    'mount': image_mount,
                    'uenv': f'{image_path}:{image_mount}' if image_mount else str(image_path)
                }
            }
            if len(views) > 0:
                env['resources']['uenv_views'] = {'views': ','.join(views)}
            env['features'] += ['uenv']
            if env['name'].startswith('prgenv'):
                env['features'] += ['prgenv']

            uenv_environments.append(env)

    return uenv_environments


UENV = _get_uenvs() or None
