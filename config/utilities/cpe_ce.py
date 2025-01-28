import os
import pathlib
import toml
# pip install toml
# import yaml
# import reframe.utility.osext as osext

from reframe.core.exceptions import ConfigError
#del from packaging.version import Version
#del
#del
#del _UENV_MOUNT_DEFAULT = '/user-environment'
#del _UENV_CLI = 'uenv'
#del _UENV_DELIMITER = ','
#del _UENV_MOUNT_DELIMITER = '@'
#del _RFM_META = pathlib.Path('extra') / 'reframe.yaml'
#del _RFM_META_DIR = pathlib.Path('meta')


def _get_cpe_ce():
    """
    Example: CPE=~/.edf/cpe-gnu.toml
    """
    cpe_toml = os.environ.get('CPE', None)
    if cpe_toml is None:
        print('# cpe_ce.py: CPE env var not set')
        return None

    cpe_toml_path = pathlib.Path(cpe_toml)
    cpe_environments = []
    # check toml file
    if cpe_toml_path.is_file():
        try:
            cpe_toml_image = pathlib.Path(toml.load(cpe_toml_path)['image'])
        except OSError as err:
            raise ConfigError(
                f"issue reading the toml file '{cpe_toml_path}'"
            )

    # check sqfs file
    if not cpe_toml_image.is_file():
        raise ConfigError(
            f"issue reading the image '{cpe_toml_image}' "
            f"from toml file '{cpe_toml_path}'"
        )


    # Replace characters that create problems in environment names
    uenv_name_pretty = str(cpe_toml_image).replace(":", "_").replace("/", "_")
    env = {}
    env['name'] = f'{uenv_name_pretty}'
    target_system = '*'
    env['target_systems'] = [target_system]
    env['resources'] = {
        'cpe': {
            'file': str(cpe_toml),
        }
    }
    # 'resources': [
    #     {
    #         'name': 'cpe',
    #         'options': ['--environment={str(cpe_toml)}']
    #     }
    # ],

    # env['features'] = ['cpe_ce']
    env['features'] = ['cuda', 'mpi', 'openmp', 'serial', 'uenv']
    env['cc'] = 'cc'
    env['cxx'] = 'CC'
    env['ftn'] = 'ftn'
    # env['prepare_cmds'] = ['module list']
    cpe_environments.append(env)
    print(f'# RETURN cpe_environments1={cpe_environments}')
    # RETURN cpe_environments1=[{'name': '_capstor_scratch_cscs_anfink_cpe_cpe-gnu.sqsh', 'target_systems': ['*'], 'resources': {'cpe': {'file': '/users/piccinal/.edf/cpe-gnu.toml'}}, 'features': ['cuda', 'mpi', 'openmp', 'serial', 'uenv']}]
    return cpe_environments


# UENV = _get_uenvs() or None
# str(cpe_toml)
CPE = _get_cpe_ce() or None
