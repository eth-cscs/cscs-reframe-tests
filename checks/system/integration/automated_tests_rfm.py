# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import yaml
from utils import *
from constants import *
import os
import reframe as rfm
import reframe.utility.sanity as sn
import glob
import json

# --------------------------------------------------------------------------- #
#                READ THE CONFIGURATION FROM THE YAML FILES
#                This part should be modified for the final 
#                structure of the V-Clusters config files
# --------------------------------------------------------------------------- #

# Reading from yaml files inside a directory recursively

# def read_config_yaml(file_path):

#     with open(file_path, 'r') as config_yaml:
#         config = yaml.safe_load(config_yaml)

#         return config

# # Look recursively for yaml files in the dummy directory
# for file_i in glob.glob(yaml_files_path+"*", recursive=True):
#     if file_i.endswith("yml"):  
#         try:
#             config_yaml_data
#         except:
#             config_yaml_data = read_config_yaml(file_i)
#         else:
#             config_yaml_data.update(read_config_yaml(file_i))

# Save the extracted info to a json file
# with open(yaml_files_path+'test_data.json', 'w') as json_file:
#     json.dump(test_info, json_file, indent=4)

# Read the extracted info from the json file
with open(yaml_files_path+'test_data.json', 'r') as json_file:
    config_yaml_data = json.load(json_file)

cluster_name = config_yaml_data[MOUNT_VARS]

test_info = {}
# Check for mount points to be checked
try:
    mount_info = config_yaml_data[MOUNT_VARS]
    test_info.update({MOUNT_VARS : mount_info})
except:
    mount_info = [None]

# Check for pkg installations to be checked
try:
    tools_info = config_yaml_data[TOOLS_VARS]
    test_info.update({TOOLS_VARS : tools_info})
except:
    tools_info = [None]

# Check for environment variables to be checked
try:
    envs_info = config_yaml_data[ENV_VARS]
    test_info.update({ENV_VARS : envs_info})
except:
    envs_info = [None]

# --------------------------------------------------------------------------- #
#                PERFORM INTEGRATION CHECKS
# --------------------------------------------------------------------------- #

@rfm.simple_test
class MountTest(rfm.RunOnlyRegressionTest):

    if mount_info[0] is not None:
        mount_info_par = []
        for mount_i in mount_info:
            mount_info_par.append((mount_i["mount_point"], mount_i["fstype"]))
        mount_info = parameter(mount_info_par)
    
    descr = 'Test mount points in the system'
    # For now
    valid_systems = ["-remote"]
    valid_prog_environs = ['builtin']
    time_limit = '2m'
    tags = {"MOUNT"}

    @run_after('init')
    def skip_notfound(self):
        self.skip_if(mount_info[0]==None, msg='No mount points found')

    @run_after('setup')
    def set_executable(self):
        self.executable = f'grep -q "{self.mount_info[0]} {self.mount_info[1]}" /proc/mounts || echo FAILED'

    @sanity_function
    def validate(self):
        return sn.assert_not_found("FAILED", self.stdout, 
                msg=f"Mount point '{self.mount_info[0]} {self.mount_info[1]}' not found in /proc/mounts")


@rfm.simple_test
class ToolsTest(rfm.RunOnlyRegressionTest):

    tools_info = parameter(tools_info)
    descr = 'Test pkgs installation in the system'
    # For now
    valid_systems = ["-remote"]
    valid_prog_environs = ['builtin']
    time_limit = '2m'
    tags = {"TOOLS"}

    @run_after('init')
    def skip_notfound(self):
        self.skip_if(tools_info[0]==None, msg='No required packages found')

    @run_after('setup')
    def set_executable(self):
        self.executable = f'which {pkg_names[self.tools_info]} || echo FAILED'

    @sanity_function
    def validate(self):
        return sn.assert_not_found("FAILED", self.stdout, 
                msg=f"Did not find an installation for {self.tools_info}")

@rfm.simple_test
class EnvTest(rfm.RunOnlyRegressionTest):

    if envs_info[0] is not None:
        envs_info_par = []
        for envs_i in envs_info:
            envs_info_par.append((envs_i["env_var"], envs_i["env_value"]))
        envs_info = parameter(envs_info_par)
    # Configuration for grep /proc/mount info test
    descr = 'Test environment variables of the system'
    # For now
    valid_systems = ["-remote"]
    valid_prog_environs = ['builtin']
    time_limit = '2m'
    tags = {"ENV"}

    @run_after('init')
    def skip_notfound(self):
        self.skip_if(envs_info[0]==None, msg='No extra environment variables to check')

    @run_after('setup')
    def set_executable(self):
        self.executable = f'printenv {self.envs_info[0]}'

    @sanity_function
    def validate(self):
        return sn.assert_found(self.envs_info[1], self.stdout, 
                msg=f"Environment variable {self.envs_info[0]} is not set up correctly")
