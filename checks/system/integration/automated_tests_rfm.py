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
# --------------------------------------------------------------------------- #

def read_config_yaml(file_path):

    with open(file_path, 'r') as config_yaml:

        config = yaml.safe_load(config_yaml)

        return config

# Look recursively for yaml files in the dummy directory
for file_i in glob.glob(yaml_files_path+"*", recursive=True):
    if file_i.endswith("yml"):  
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
    mount_tag  = "sysint-found"
    test_info.update({MOUNT_VARS : mount_info})
except:
    mount_info = [None]
    mount_tag  = "not_found"

# Check for pkg installations to be checked
try:
    tools_info = config_yaml_data[TOOLS_VARS]
    tools_tag  = "sysint-found"
    test_info.update({TOOLS_VARS : tools_info})
except:
    tools_info = [None]
    tools_tag  = "not_found"

# Check for environment variables to be checked
try:
    envs_info = config_yaml_data[ENV_VARS]
    envs_tag  = "sysint-found"
    test_info.update({ENV_VARS : envs_info})
except:
    envs_info = [None]
    envs_tag  = "not_found"

# Save the extracted info to a json file
with open(yaml_files_path+'test_data.json', 'w') as json_file:
    json.dump(test_info, json_file, indent=4)

# with open(yaml_files_path+'test_data.json', 'r') as json_file:
#     config_yaml_data = json.load(json_file)

# --------------------------------------------------------------------------- #
#                PERFORM INTEGRATION CHECKS
# --------------------------------------------------------------------------- #

class IntegrationTest(rfm.RunOnlyRegressionTest):

    def __init__(self):
        # Common configuration for all integration tests
        self.valid_prog_environs = ['builtin']
        self.time_limit = '2m'
        self.not_expected = None
        self.expected = None
        self.check_class = 'NOCLASS'
        
    @sanity_function
    def validate(self):
        a, b = True, True

        if self.expected is not None:
            a = sn.assert_found(
                self.expected,
                self.stdout,
                msg=f"Expected '{self.expected}' running " +
                    f"'{self.executable}'")

        if self.not_expected is not None:
            b = sn.assert_not_found(
                self.not_expected,
                self.stdout,
                msg=f"Did not expect '{self.not_expected}' " +
                    f"running '{self.executable}'")
            
        return (a and b)
    
@rfm.simple_test
class MountTest(IntegrationTest):

    mount_info_par = []
    for mount_i in mount_info:
        mount_info_par.append((mount_i["mount_point"], mount_i["fstype"]))
    mount_info = parameter(mount_info_par)
    
    def __init__(self):
        super().__init__()
        # Configuration for grep /proc/mount info test
        self.check_class = "MOUNT"
        self.descr = 'Test mount points in the system'
        self.not_expected = "FAILED"
        # self.valid_systems = ["*"]
        # For now
        self.valid_systems = ["-remote"]
        self.tags = {mount_tag}

    @run_after('setup')
    def set_executable(self):
        self.executable = f'grep -q "{self.mount_info[0]} {self.mount_info[1]}" /proc/mounts || echo FAILED'

@rfm.simple_test
class ToolsTest(IntegrationTest):

    tools_info = parameter(tools_info)
    
    def __init__(self):
        super().__init__()
        # Configuration for grep /proc/mount info test
        self.check_class = "TOOLS"
        self.descr = 'Test pkgs installation in the system'
        self.not_expected = "FAILED"
        # self.valid_systems = ["*"]
        # For now
        self.valid_systems = ["-remote"]
        self.tags = {tools_tag}

    @run_after('setup')
    def set_executable(self):
        self.executable = f'which {pkg_names[self.tools_info]} || echo FAILED'

@rfm.simple_test
class EnvTest(IntegrationTest):

    envs_info = parameter(envs_info)
    
    def __init__(self):
        super().__init__()
        # Configuration for grep /proc/mount info test
        self.check_class = "ENV"
        self.descr = 'Test environment variables of the system'
        self.expected = self.envs_info[1]
        # self.valid_systems = ["*"]
        # For now
        self.valid_systems = ["-remote"]
        self.tags = {envs_tag}

    @run_after('setup')
    def set_executable(self):
        self.executable = f'printenv {self.envs_info[0]}'
