import json
import os
import pathlib
import yaml

from typing import List, Optional, Tuple

import reframe.utility.osext as osext
from reframe.core.exceptions import ConfigError
from packaging.version import Version


_UENV_MOUNT_DEFAULT = '/user-environment'
_UENV_CLI = 'uenv'
_UENV_DELIMITER = ','
_UENV_MOUNT_DELIMITER = '@'
_UENV_LABEL_DELIMITER = '^'
_UENV_RFM_SYSTEM_DELIMITER = '+'
_UENV_CLI_SYSTEM_DELIMITER = '@'
_RFM_META = pathlib.Path('extra') / 'reframe.yaml'
_RFM_META_DIR = pathlib.Path('meta')
UENV_RECIPES_ENVVAR = 'CSCS_RFM_UENV_RECIPES_DIR'
UENV_IMAGE_INVENTORY_ENVVAR = 'CSCS_RFM_UENV_IMAGE_INVENTORY'
UENV_TARGET_SYSTEMS_ENVVAR = 'CSCS_RFM_UENV_TARGET_SYSTEMS'

# Environment variable used to explicitly request UENV image inventory
# queries for one or more target systems. This avoids relying on the
# CLI's implicit default filtering behavior.

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


def _uenv_version_and_tag_from_label(
    uenv_label: Optional[str],
) -> Tuple[Optional[str], Optional[str]]:
    """
    Given a uenv label "{name}/{ver}:{tag} it returns the tuple (ver, tag).

    Values are returned as str and any semantic is left to the user.
    The only required component is the name; if any (or both) of the two is missing,
    the related tuple component is considered not specified and set to None.
    """

    if uenv_label is None or ("/" not in uenv_label and ":" not in uenv_label):
        return (None, None)

    if "/" not in uenv_label:
        ver = None
        rem = uenv_label
    else:
        _, rem = uenv_label.split("/")

    if ":" not in rem:
        ver = rem
        tag = None
    else:
        ver, tag = rem.split(":")

    return ver, tag


def _parse_uenv_identifier(
    uenv_identifier: str,
) -> Tuple[Optional[str], Optional[pathlib.Path]]:
    """
    return: (name, path)
    """

    # uenv identifier can be either:
    # - squashfs_path^uenv_label (see _UENV_LABEL_DELIMITER)
    # - squashfs_path
    # - uenv_label
    if _UENV_LABEL_DELIMITER in uenv_identifier:
        uenv_path, uenv_name = uenv_identifier.split(_UENV_LABEL_DELIMITER)
        uenv_path = pathlib.Path(uenv_path)
    elif pathlib.Path(uenv_identifier).is_file():
        uenv_path = pathlib.Path(uenv_identifier)
        uenv_name = None
    else:
        uenv_name = uenv_identifier
        uenv_path = None

    return (uenv_name, uenv_path)

def _load_uenv_image_inventory(path: str | None = None) -> list[dict]:
    # Load UENV inventory from a provided JSON file or from the UENV CLI.
    # When no inventory file is configured, prefer explicit per-system
    # queries with '@<system>' rather than relying on the default CLI
    # filtering or config.yaml mappings, which are not reliable.
    if path:
        inventory_file = pathlib.Path(path).expanduser().resolve()
        if not inventory_file.is_file():
            raise ConfigError(
                f"{UENV_IMAGE_INVENTORY_ENVVAR} path is not a file: "
                f"{path}"
            )
        try:
            with open(inventory_file, encoding='utf-8') as f:
                inventory = json.load(f)
        except OSError as err:
            raise ConfigError(
                f"Cannot read inventory file {inventory_file}: {err}"
            )
        except json.JSONDecodeError as err:
            raise ConfigError(
                f"Cannot parse inventory file {inventory_file}: {err}"
            )
    else:
        # If the caller set a target-systems envvar, query uenv per-system
        # using the '@system' syntax to avoid the CLI default filtering.
        # This is the preferred path for multi-system availability checks.
        target_systems = os.environ.get(UENV_TARGET_SYSTEMS_ENVVAR)
        if target_systems:
            records: list[dict] = []
            seen: set[str] = set()
            for sys in [s.strip() for s in target_systems.split(',') if s.strip()]:
                cmd = f"{_UENV_CLI} image find --json @{sys}"
                output = osext.run_command(cmd, shell=True).stdout
                try:
                    inv = json.loads(output)
                except json.JSONDecodeError as err:
                    raise ConfigError(
                        f"Cannot parse JSON from '{cmd}': {err}"
                    )
                recs = inv.get('records') if isinstance(inv, dict) else None
                if isinstance(recs, list):
                    for r in recs:
                        if not isinstance(r, dict):
                            continue
                        record_key = json.dumps(r, sort_keys=True)
                        if record_key in seen:
                            continue
                        seen.add(record_key)
                        records.append(r)
            inventory = {'records': records}
        else:
            cluster_name = os.environ.get('CLUSTER_NAME')
            if cluster_name:
                cmd = f"{_UENV_CLI} image find --json @{cluster_name}"
            else:
                cmd = f"{_UENV_CLI} image find --json"
            output = osext.run_command(cmd, shell=True).stdout
            try:
                inventory = json.loads(output)
            except json.JSONDecodeError as err:
                raise ConfigError(
                    f"Cannot parse JSON from '{cmd}': {err}"
                )

    if not isinstance(inventory, dict):
        raise ConfigError(
            f"Invalid UENV inventory JSON: expected object, got {type(inventory).__name__}"
        )

    records = inventory.get('records')
    if not isinstance(records, list):
        raise ConfigError(
            "Invalid UENV inventory JSON: missing 'records' list"
        )

    return [r for r in records if isinstance(r, dict)]


def _recipe_target_systems(
    recipe_root: pathlib.Path,
    recipe_dir_path: pathlib.Path,
    inventory_records: list[dict],
) -> list[str]:
    relative_recipe_path = recipe_root.relative_to(recipe_dir_path).as_posix()
    parts = relative_recipe_path.split('/')

    if len(parts) < 2:
        return []

    recipe_name = parts[0]
    recipe_version = parts[1]
    recipe_uarch = parts[2] if len(parts) > 2 else None

    systems: set[str] = set()
    for record in inventory_records:
        if record.get('name') != recipe_name:
            continue
        if recipe_version and record.get('version') != recipe_version:
            continue
        if recipe_uarch and record.get('uarch') != recipe_uarch:
            continue

        system = record.get('system')
        if isinstance(system, str) and system:
            systems.add(system)

    return sorted(systems)


def _load_uenvs_from_recipes(recipe_dir: str) -> list[dict]:
    recipe_dir_path = pathlib.Path(recipe_dir).expanduser().resolve()
    if not recipe_dir_path.is_dir():
        raise ConfigError(
            f"{UENV_RECIPES_ENVVAR} path is not a directory: "
            f"{recipe_dir}"
        )

    inventory_path = os.environ.get(UENV_IMAGE_INVENTORY_ENVVAR)
    inventory_records = _load_uenv_image_inventory(inventory_path)
    uenv_environments = []

    for rfm_meta in recipe_dir_path.rglob('extra/reframe.yaml'):
        recipe_root = rfm_meta.parent.parent
        uenv_name = recipe_root.relative_to(recipe_dir_path).as_posix()
        uenv_name_pretty = uenv_name.replace('/', '_').replace(':', '_')

        try:
            with open(rfm_meta, encoding='utf-8') as image_envs:
                image_environments = yaml.load(
                    image_envs.read(), Loader=yaml.BaseLoader)
        except OSError as err:
            print(
                f'Skipping local uenv recipe `{rfm_meta}`, there was an error '
                f'reading the metadata: {err}'
            )
            continue

        if not isinstance(image_environments, dict):
            continue

        target_systems = _recipe_target_systems(
            recipe_root, recipe_dir_path, inventory_records
        )
        if not target_systems:
            continue

        for k, v in image_environments.items():
            if not isinstance(v, dict):
                continue

            env = {'target_systems': target_systems}
            env.update(v)

            activation = env.pop('activation', [])
            views = env.pop('views', [])

            if isinstance(activation, list):
                env['prepare_cmds'] = activation
            elif isinstance(activation, str):
                env['prepare_cmds'] = [f'source {activation}']
            else:
                raise ConfigError(
                    'activation has to be a list of commands to be '
                    'executed to configure the environment'
                )

            features = env.get('features', [])
            if isinstance(features, str):
                features = [features]
            env['features'] = list(features) + ['uenv']

            env['name'] = f'{uenv_name_pretty}_{k}'
            env['resources'] = {
                'uenv': {
                    'file': str(recipe_root),
                    'mount': None,
                    'uenv': str(recipe_root),
                }
            }
            if views:
                env['resources']['uenv_views'] = {
                    'views': ','.join(views)
                }

            uenv_environments.append(env)

    return uenv_environments

def _get_uenvs() -> Optional[List]:
    recipes_dir = os.environ.get(UENV_RECIPES_ENVVAR, None)
    if recipes_dir:
        return _load_uenvs_from_recipes(recipes_dir)

    uenv = os.environ.get('CSCS_RFM_UENV', None)
    if uenv is None:
        return uenv

    uenv_environments = []
    uenv_list = uenv.split(_UENV_DELIMITER)
    uenv_version = osext.run_command(
        f'{_UENV_CLI} --version', shell=True
    ).stdout.strip()

    for uenv in uenv_list:
        uenv_identifier, *uenv_mountpoint = uenv.split(_UENV_MOUNT_DELIMITER)
        uenv_identifier = uenv_identifier.replace(_UENV_RFM_SYSTEM_DELIMITER, _UENV_CLI_SYSTEM_DELIMITER)
        uenv_name, uenv_path = _parse_uenv_identifier(uenv_identifier)

        if len(uenv_mountpoint) > 0:
            uenv_mountpoint = uenv_mountpoint[0]
        else:
            uenv_mountpoint = None

        # Check if given uenv_name is a path to a squashfs archive
        if uenv_path:
            if not uenv_path.is_file():
                raise ConfigError(f"{uenv_name} is not a valid path to a squashfs uenv image")

            # We cannot inspect for target systems
            target_system = '*'
            image_path = uenv_path
            rfm_meta = image_path.parent / _RFM_META_DIR / _RFM_META
        else:
            inspect_cmd = f'{_UENV_CLI} image inspect {uenv_name} --format'

            image_path = osext.run_command(
                f"{inspect_cmd}='{{sqfs}}'", shell=True).stdout.strip()
            target_system = '*'

            image_path = pathlib.Path(image_path)
            # Check that uenv was pulled
            if not image_path.is_file():
                raise ConfigError(
                    f"{uenv_name} is missing, "
                    f"try pulling it with: uenv image pull {uenv_name}")
            try:
                if image_path.stat().st_size == 0:
                    raise ConfigError(
                        f"{uenv_name} is empty, "
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
            uenv_name_pretty = (
                (uenv_name if uenv_name else str(uenv_path))
                .replace(":", "_")
                .replace("/", "_")
                .replace("%", "_")
            )
            env['name'] = f'{uenv_name_pretty}_{k}'

            if not env.get('extras', {}).get('version'):
                env.setdefault("extras", {})["version"] = _uenv_version_and_tag_from_label(uenv_name)

            env['resources'] = {
                'uenv': {
                    'file': str(image_path),
                    'mount': uenv_mountpoint,
                    'uenv': (
                        f'{str(image_path):{uenv_mountpoint}}' if uenv_mountpoint else str(image_path)
                    ),
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
