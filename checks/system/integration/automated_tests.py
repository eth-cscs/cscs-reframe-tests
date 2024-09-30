# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import yaml
from utils import *
from constants import *

# --------------------------------------------------------------------------- #
#                READ THE CONFIGURATION FROM THE YAML FILES
# --------------------------------------------------------------------------- #

file_path_config = []
file_path_config.append( r"/users/bfuentes/sandbox/filesystems.yml")
file_path_config.append( r"/users/bfuentes/sandbox/cscs-config.yml")

check = Check()

check.SYSTEM = "daint" 

def read_config_yaml(file_path):

    with open(file_path, 'r') as config_yaml:

        config = yaml.safe_load(config_yaml)

        return config
 
if __name__ == '__main__':
    check.DEBUG = True
else:
    import reframe as rfm
    check.MODULE_NAME = __name__

config_yaml_data = read_config_yaml(file_path_config[0])

for file_i in range(len(file_path_config)-1):
    config_yaml_data.update(read_config_yaml(file_path_config[file_i+1]))

checks_class = []
config_list = {}
check_format = {}

if list(config_yaml_data.keys())[0] == "filesystems":
    checks_class.append("MOUNTS")
    config_list["MOUNTS"] = config_yaml_data["filesystems"]
    check_format["MOUNTS"] = mount_check
if "cscs_cluster_extra_pkgs" in list(config_yaml_data.keys()):
    checks_class.append("TOOLS")
    config_list["TOOLS"] = config_yaml_data["cscs_cluster_extra_pkgs"]
    print(config_list["TOOLS"])
    check_format["TOOLS"] = tools_check 

for check_type in checks_class:
    check.CLASS = check_type
    check_format[check_type](check, config_list[check_type])