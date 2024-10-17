# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import json
import glob
import sys
sys.path.append("../integration")
from constants import *
import yaml
import sys
import os


def main(yaml_config, system_name):

    def read_config_yaml(file_path):
        """Read a YAML configuration file and return its content."""
        with open(file_path, 'r') as config_yaml:
            config = yaml.safe_load(config_yaml)

            return config

    # Look recursively for yaml files in the config directory
    for root, _, files in os.walk(yaml_config):
        for file_i in files:
            if os.path.splitext(file_i)[1] == ".yml":
                print(f"Extracting data from {file_i}...")
                try:
                    config_yaml_data
                except:
                    config_yaml_data = read_config_yaml(
                        os.path.join(root, file_i))
                else:
                    config_yaml_data.update(
                        read_config_yaml(os.path.join(root, file_i)))

    test_info = {}
    # Check for mount points to be checked
    mount_info = config_yaml_data.get(MOUNT_VARS)
    if mount_info:
        for m in mount_info:
            del m['src']
            del m['opts']
        test_info.update({MOUNT_VARS: mount_info})

    # Check for pkg installations to be checked
    if config_yaml_data.get(TOOLS_VARS):
        test_info.update({TOOLS_VARS: config_yaml_data.get(TOOLS_VARS)})

    # Check for environment variables to be checked
    if config_yaml_data.get(ENV_VARS):
        test_info.update({ENV_VARS: config_yaml_data.get(ENV_VARS)})

    # Check for proxy configuration
    for proxy_v in PROXY_VARS:
        if config_yaml_data.get(proxy_v):
            test_info.update({proxy_v: config_yaml_data.get(proxy_v)})

    # Save the extracted info to a json file
    with open(os.path.join(json_file_path, system_name+"_data.json"), 'w') as json_file:
        json.dump(test_info, json_file, indent=4)
        json_file.write('\n')


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: python extract_data.py path/to/your/yaml/config/dir system_name")
        sys.exit(1)
    else:
        yaml_config = sys.argv[1]
        system_name = sys.argv[2]

    if os.path.isdir(yaml_config):
        main(yaml_config, system_name)
    else:
        print(f"The directory '{yaml_config}' is not valid.")
        sys.exit(1)
