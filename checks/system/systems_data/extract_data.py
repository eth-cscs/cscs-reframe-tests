# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import yaml
import sys
import os
sys.path.append("../integration")
from constants import *
import sys
import glob
import json
 

def main(yaml_config):

    def read_config_yaml(file_path):
        """Read a YAML configuration file and return its content."""
        with open(file_path, 'r') as config_yaml:
            config = yaml.safe_load(config_yaml)

            return config

    # Look recursively for yaml files in the config directory
    for file_i in glob.glob(yaml_config+"/*", recursive=True):
        if file_i.endswith("yml"):  
            print(f"Extracting data from {file_i}...")
            try:
                config_yaml_data
            except:
                config_yaml_data = read_config_yaml(file_i)
            else:
                config_yaml_data.update(read_config_yaml(file_i))

    test_info = {}
    # Check for mount points to be checked
    try:
        mount_info = config_yaml_data[MOUNT_VARS]
        for i in range(len(mount_info)):
            del mount_info[i]['src']
            del mount_info[i]['opts']
        test_info.update({MOUNT_VARS : mount_info})
    except:
        pass

    # Check for pkg installations to be checked
    try:
        test_info.update({TOOLS_VARS : config_yaml_data[TOOLS_VARS]})
    except:
        pass

    # Check for environment variables to be checked
    try:
        test_info.update({ENV_VARS : config_yaml_data[ENV_VARS]})
    except:
        pass
        
    def read_config_yaml(file_path):

        with open(file_path, 'r') as config_yaml:
            config = yaml.safe_load(config_yaml)

            return config

    # Save the extracted info to a json file
    with open(json_file_path+'test_data.json', 'w') as json_file:
        json.dump(test_info, json_file, indent=4)


if __name__ == "__main__":
    
    try:
        yaml_config = sys.argv[1]
    except:
        main(yaml_config)
        print("The directory where the configuration is stored must be provided.")
        print("Usage: python your_script_name.py path/to/your/config.yaml")
        sys.exit(1)

    if os.path.isdir(yaml_config):
        main(yaml_config)
    else:
        print(f"The directory '{yaml_config}' is not valid.")
        sys.exit(1)
