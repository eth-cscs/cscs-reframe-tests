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
# --------------------------------------------------------------------------- 

# Read the extracted info from the json file
with open(os.path.join(json_file_path,'test_data.json'), 'r') as json_file:
    config_yaml_data = json.load(json_file)

# Check for mount points to be checked
mount_info = config_yaml_data.get(MOUNT_VARS)

# Check for pkg installations to be checked
tools_info = config_yaml_data.get(TOOLS_VARS)

# Check for environment variables to be checked
envs_info = config_yaml_data.get(ENV_VARS)

# --------------------------------------------------------------------------- #
#                PERFORM INTEGRATION CHECKS
# --------------------------------------------------------------------------- #

@rfm.simple_test
class MountTest(rfm.RunOnlyRegressionTest):

    if mount_info:
        mount_info_par = []
        for mount_i in mount_info:
            mount_info_par.append((mount_i['mount_point'], mount_i['fstype']))
        mount_info = parameter(mount_info_par)
        # For now
        valid_systems = ['-remote']
    else:
        valid_systems = []
    descr = 'Test mount points in the system'
    valid_prog_environs = ['builtin']
    time_limit = '2m'
    tags = {'MOUNT'}

    @run_after('setup')
    def set_executable(self):
        self.executable = f'grep -q "{self.mount_info[0]} {self.mount_info[1]}" /proc/mounts || echo FAILED'

    @sanity_function
    def validate(self):
        return sn.assert_not_found('FAILED', self.stdout, 
                msg=f'Mount point "{self.mount_info[0]} {self.mount_info[1]}" not found in /proc/mounts')


@rfm.simple_test
class ToolsTest(rfm.RunOnlyRegressionTest):

    if tools_info:
        tools_info = parameter(tools_info)
        # For now
        valid_systems = ['-remote']
    else:
        valid_systems = []
    descr = 'Test pkgs installation in the system'
    valid_prog_environs = ['builtin']
    time_limit = '2m'
    tags = {'TOOLS'}

    @run_after('setup')
    def set_executable(self):
        self.executable = f'which {pkg_names[self.tools_info]} || echo FAILED'

    @sanity_function
    def validate(self):
        return sn.assert_not_found('FAILED', self.stdout, 
                msg=f'Did not find an installation for {self.tools_info}')

@rfm.simple_test
class EnvTest(rfm.RunOnlyRegressionTest):

    if envs_info:
        envs_info_par = []
        for envs_i in envs_info:
            envs_info_par.append((envs_i['env_var'], envs_i['env_value']))
        envs_info = parameter(envs_info_par)
        # For now
        valid_systems = ['-remote']
    else:
        valid_systems = []
    descr = 'Test environment variables of the system'
    valid_prog_environs = ['builtin']
    time_limit = '2m'
    tags = {'ENV'}

    @run_after('setup')
    def set_executable(self):
        self.executable = f'printenv {self.envs_info[0]}'

    @sanity_function
    def validate(self):
        return sn.assert_found(self.envs_info[1], self.stdout, 
                msg=f'Environment variable {self.envs_info[0]} is not set up correctly')
