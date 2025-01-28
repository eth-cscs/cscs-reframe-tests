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

import firecrest_slurm
import uenv
import cpe_ce


def is_var_true(var):
    if var is None:
        return False

    return var.lower() in ['true', 'yes', '1']


firecrest = os.environ.get('RFM_FIRECREST', None)
systems_path = 'systems-firecrest' if is_var_true(firecrest) else 'systems'

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

# {{{ UENV
# If a system partition has the 'uenv' feature, replace the environment'
# names valid for that system with the ones from uenv
# del print(f'site_configuration={site_configuration}')
# del print(f'uenv_environs={uenv_environs}')
uenv_environs = uenv.UENV

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
                # Replace the partition environs with the uenv ones
                partition['environs'] = valid_system_uenv_names
                # Add the corresponding resources for uenv
                resources = partition.get('resources', [])
                resources.append( { 'name': 'uenv', 'options': ['--uenv={file}:{mount}'] })
                resources.append( { 'name': 'uenv_views', 'options': ['--view={views}'] })
                partition['resources'] = resources
                print(f'\n# FINAL: partition={partition}\n')
                # FINAL: partition={'name': 'normal', 'descr': 'GH200', 'scheduler': 'slurm', 'launcher': 'srun', 'time_limit': '10m', 'sched_options': {'use_nodes_option': True}, 'environs': ['_capstor_scratch_cscs_piccinal_daint_rfm_CPE_cpe-gnu.sqsh_default'], 'max_jobs': 100, 'container_platforms': [], 'extras': {'cn_memory': 825}, 'features': ['uenv', 'remote', 'cpe_ce'], 'resources': [{'name': 'uenv', 'options': ['--uenv={file}:{mount}']}, {'name': 'uenv_views', 'options': ['--view={views}']}], 'devices': [{'type': 'gpu', 'arch': 'sm_90', 'num_devices': 4}]}
# }}}

# {{{ CPE
cpe_environs = cpe_ce.CPE
print(f'cpe_environs2={cpe_environs}')
# cpe_environs=[{'name': '_capstor_scratch_cscs_anfink_cpe_cpe-gnu.sqsh',
#   'target_systems': ['*'], 'resources': {'cpe': {'file':
#   '/users/piccinal/.edf/cpe-gnu.toml'}}, 'features': ['cpe_ce']}]

if site_configuration and cpe_environs:
    #yes print('+L98')
    site_configuration['environments'] += cpe_environs

    for system in site_configuration['systems']:
        print(f'\nsystem={system}')
        # system={'modules_system': 'lmod', 'partitions': [{'name': 'normal', 'descr': 'GH200', 'scheduler': 'slurm', 'launcher': 'srun', 'time_limit': '10m', 'sched_options': {'use_nodes_option': True}, 'environs': ['builtin', 'PrgEnv-gnu'], 'max_jobs': 100, 'container_platforms': [], 'extras': {'cn_memory': 825}, 'features': ['uenv', 'remote', 'cpe_ce'], 'resources': [{'name': 'switches', 'options': ['--switches={num_switches}']}, {'name': 'gres', 'options': ['--gres={gres}']}, {'name': 'memory', 'options': ['--mem={mem_per_node}']}, {'name': 'cpe', 'options': ['--environment={cpe_sqfs}']}], 'devices': [{'type': 'gpu', 'arch': 'sm_90', 'num_devices': 4}]}], 'name': 'daint', 'descr': 'Piz daint vcluster', 'hostnames': ['daint']}

        valid_system_uenv_names = [
            u['name'] for u in cpe_environs
            if (system['name'] in u['target_systems'] or
                u['target_systems'] == ['*'])
        ]

        for partition in system['partitions']:
            print(f'\npartition={partition}')
            # partition={'name': 'normal', 'descr': 'GH200', 'scheduler': 'slurm', 'launcher': 'srun', 'time_limit': '10m', 'sched_options': {'use_nodes_option': True}, 'environs': ['builtin', 'PrgEnv-gnu'], 'max_jobs': 100, 'container_platforms': [], 'extras': {'cn_memory': 825}, 'features': ['uenv', 'remote', 'cpe_ce'], 'resources': [{'name': 'switches', 'options': ['--switches={num_switches}']}, {'name': 'gres', 'options': ['--gres={gres}']}, {'name': 'memory', 'options': ['--mem={mem_per_node}']}, {'name': 'cpe', 'options': ['--environment={cpe_sqfs}']}], 'devices': [{'type': 'gpu', 'arch': 'sm_90', 'num_devices': 4}]}

            if partition.get('features', None) and ('cpe_ce' in partition['features']):
                # Replace the partition environs with the uenv ones
                partition['environs'] = valid_system_uenv_names
                # Add the corresponding resources for uenv
                resources = partition.get('resources', [])
                # resources.append({'name': 'uenv', 'options': ['--uenv={file}:{mount}'] })
                # resources.append({'name': 'uenv_views', 'options': ['--view={views}'] })
                # --environment=cpe-gnu
                # resources.append({'name': 'cpe', 'options': [f'--environment={cpe_environs[0]["resources"]["cpe"]["file"]}']})
                resources.append({'name': 'cpe', 'options': ['--environment={file}']})
                partition['resources'] = resources
                print(f'\n# FINAL: partition={partition}\n')
                # FINAL: partition={'name': 'normal', 'descr': 'GH200', 'scheduler': 'slurm', 'launcher': 'srun', 'time_limit': '10m', 'sched_options': {'use_nodes_option': True}, 'environs': ['builtin', 'PrgEnv-gnu'], 'max_jobs': 100, 'container_platforms': [], 'extras': {'cn_memory': 825}, 'features': ['uenv', 'remote', 'cpe_ce'], 'resources': [{'name': 'cpe', 'options': ['--environment=/users/piccinal/.edf/cpe-gnu.toml']}], 'devices': [{'type': 'gpu', 'arch': 'sm_90', 'num_devices': 4}]}
# }}}
