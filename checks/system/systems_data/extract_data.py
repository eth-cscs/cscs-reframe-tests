# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import sys
sys.path.append("../integration")

import yaml
import os
import hcl2
import json
from constants import (MOUNT_VARS, TOOLS_VARS,
                       ENV_VARS, PROXY_VARS,
                       json_file_path, VSERVICES_DICT,
                       pkg_names)


def main(config_dir, system_name):

    def read_config_yaml(file_path):
        """Read a YAML configuration file and return its content."""
        with open(file_path, 'r') as config_yaml:
            config = yaml.safe_load(config_yaml)

            return config

    def read_config_tf(file_path):
        """Read a terraform configuration file and return its content."""
        with open(file_path, 'r') as config_tf:
            config = hcl2.load(config_tf)

            return config

    # Look recursively for yaml / tf files in the config directory
    config_yaml_data = {}
    config_tf_data = {}

    def normalize_tf_module_name(name):
        return str(name).strip().strip('"').strip("'")

    def normalize_tf_string(value):
        if isinstance(value, str):
            return value.strip().strip('"').strip("'")
        return value

    for root, _, files in os.walk(config_dir):
        for file_i in files:
            if os.path.splitext(file_i)[1] == ".yml":
                print(f'Extracting data from {file_i}...')
                file_data = read_config_yaml(os.path.join(root, file_i))
                if isinstance(file_data, dict):
                    config_yaml_data.update(file_data)
            elif os.path.splitext(file_i)[1] == ".tf":
                print(f"Extracting data from {file_i}...")
                file_data = read_config_tf(os.path.join(root, file_i))
                if isinstance(file_data, dict):
                    for key, value in file_data.items():
                        if key == 'module' and isinstance(value, list):
                            config_tf_data.setdefault('module', []).extend(value)
                        else:
                            config_tf_data[key] = value

    # Let's extract here the names of the v-services and the associated dict
    v_services = {}
    print(f'Detected the following v-services in the v-cluster {system_name}:')
    for v_serv in config_tf_data.get('module', []):
        module_name = normalize_tf_module_name(list(v_serv.keys())[0])
        v_services[module_name] = v_serv[list(v_serv.keys())[0]]
        print(f'-   {module_name}')

    # We proceed to extract the relevant information for the tests
    test_info = {}

    # ---------------------- MOUNT POINTS -------------------------
    mount_info = []
    # Extract the mount points from the storage vservice
    storage_vservice = v_services.get(VSERVICES_DICT['storage'])
    if storage_vservice:
        for field, value in storage_vservice.items():
            if value == 'mounted':
                if 'vast_users_cscs_state' in field:
                    mounted_path = '/users'
                    fstype = 'nfs'
                else:
                    mounted_path = field.replace("_state", "").replace('_', '/')
                    fstype = 'lustre'
                mount_info.append({'mount_point': mounted_path,
                                   'fstype': fstype})
    else:
        print(f'\033[33mThe "{VSERVICES_DICT["storage"]}" '
              'vservice was not found\033[0m')

    # Extract the mount points from the cscs-config vservice vars.yml if present
    if config_yaml_data.get(MOUNT_VARS[0]):
        for m in config_yaml_data.get(MOUNT_VARS[0], []):
            if m.get('state') != 'mounted':
                continue
            mount_info.append({
                'mount_point': m.get('mount_point'),
                'fstype': m.get('fstype'),
            })

    for mount_var in MOUNT_VARS[1::]:
        if config_yaml_data.get(mount_var):
            mounted_path = mount_var.replace("_path", "").replace('_', '/')
            for i, mount_point in enumerate(mount_info):
                if mount_point["mount_point"] == mounted_path:
                    mount_info[i]["mount_point"] = config_yaml_data.get(
                        mount_var
                    )

    vcluster_vservice = v_services.get(VSERVICES_DICT['v-cluster'])
    if vcluster_vservice:
        shared_scratch = normalize_tf_string(vcluster_vservice.get('shared_scratch'))
        if shared_scratch:
            mount_info.append({'mount_point': shared_scratch})
    else:
        print(f'\033[31mThe "{VSERVICES_DICT["v-cluster"]}" '
              'vservice was not found\033[0m')

    if mount_info:
        # Remove duplicates while preserving order
        seen = set()
        unique_mounts = []
        for mount in mount_info:
            key = (mount.get('mount_point'), mount.get('fstype'))
            if key not in seen:
                seen.add(key)
                unique_mounts.append(mount)

        test_info.update({MOUNT_VARS[0]: unique_mounts})
    else:
        print('\033[33mNo mount points could be extracted\033[0m')

    # ------------------ INSTALLED PACKAGES ---------------------
    # Check for pkg installations to be checked
    if isinstance(TOOLS_VARS, list):
        test_info["pkgs"] = set()
        for tool_var in TOOLS_VARS:
            if config_yaml_data.get(tool_var):
                for pkg in config_yaml_data.get(tool_var):
                    if pkg in pkg_names:
                        test_info["pkgs"].add(pkg)
        # Make package list deterministic
        test_info["pkgs"] = sorted(list(test_info["pkgs"]))
    else:
        if config_yaml_data.get(TOOLS_VARS):
            test_info.update({TOOLS_VARS: config_yaml_data.get(TOOLS_VARS)})

    # ----------------- ENVIRONMENT VARIABLES --------------------
    # Check for environment variables to be checked
    env_list = config_yaml_data.get(ENV_VARS) or []
    if not isinstance(env_list, list):
        env_list = []

    # Ensure SCRATCH env var present: fallback to `cscs_scratch_basedir`
    if not any((isinstance(e, dict) and e.get('env_var') == 'SCRATCH') for e in env_list):
        scratch = config_yaml_data.get('cscs_scratch_basedir')
        if scratch:
            env_list.append({'env_var': 'SCRATCH', 'env_value': scratch})

    if env_list:
        test_info.update({ENV_VARS: env_list})

    # ------------------ PROXY CONFIGURATION ---------------------
    # Check for proxy configuration
    for proxy_v in PROXY_VARS:
        if config_yaml_data.get(proxy_v):
            test_info.update({proxy_v: config_yaml_data.get(proxy_v)})

    # Save the extracted info to a json file
    with open(os.path.join(json_file_path, system_name+"_data.json"), 'w') \
            as json_file:
        json.dump(test_info, json_file, indent=4)
        json_file.write('\n')


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print('Usage: python extract_data.py'
              'path/to/your/yaml/config/dir system_name')
        sys.exit(1)
    else:
        yaml_config = sys.argv[1]
        system_name = sys.argv[2]

    if os.path.isdir(yaml_config):
        main(yaml_config, system_name)
    else:
        print(f"The directory '{yaml_config}' is not valid.")
        sys.exit(1)
