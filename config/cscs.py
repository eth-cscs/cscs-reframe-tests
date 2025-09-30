# Copyright 2016 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings

import glob
import os
import sys
from reframe.utility import import_module_from_file

base_dir = os.path.dirname(os.path.abspath(__file__))
utilities_path = os.path.join(base_dir, 'utilities')
sys.path.append(utilities_path)

import uenv


def is_var_true(var):
    if var is None:
        return False

    return var.lower() in ['true', 'yes', '1']


systems_path = 'systems'

system_conf_files = glob.glob(
    os.path.join(os.path.dirname(__file__), systems_path, '*.py')
)
config_files = [
    os.path.join(os.path.dirname(__file__), 'common.py')
]
# Filter out the links
config_files += [s for s in system_conf_files if not os.path.islink(s)]
system_configs = [
    import_module_from_file(f).site_configuration for f in config_files
]

# Build the configuration dictionary from all the systems/*.py config files
site_configuration = {}
for c in system_configs:
    for key, val in c.items():
        site_configuration.setdefault(key, [])
        site_configuration[key] += val

uenv_environs = uenv.UENV

# If a system partition has the 'uenv' feature, replace the environment'
# names valid for that system with the ones from uenv
if site_configuration and uenv_environs:
    site_configuration['environments'] += uenv_environs
    for system in site_configuration['systems']:
        valid_system_uenv_names = [
            u['name'] for u in uenv_environs
            if (system['name'] in u['target_systems'] or
                u['target_systems'] == ['*'])
        ]
        for partition in system['partitions']:
            if partition.get('features', None) and ('uenv' in partition['features']):
                # Add the uenvs in the relevant partitions
                partition['environs'] += valid_system_uenv_names

                # Add the corresponding resources for uenv
                resources = partition.get('resources', [])
                resources.append(
                    {
                        'name': 'uenv',
                        'options': ['--uenv={file}:{mount}']
                    }
                )
                resources.append(
                    {
                        'name': 'uenv_views',
                        'options': ['--view={views}']
                    }
                )
                partition['resources'] = resources
