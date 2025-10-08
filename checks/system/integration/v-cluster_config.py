# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

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

system_data_file = "cluster_data.json"

# Read the extracted info from the json file
with open(os.path.join(json_file_path, system_data_file), 'r') as json_file:
    config_yaml_data = json.load(json_file)

# Check for mount points to be checked
mount_info = config_yaml_data.get(MOUNT_VARS[0])

# Check for pkg installations to be checked
tools_info = config_yaml_data.get("pkgs")

# Check for environment variables to be checked
envs_info = config_yaml_data.get(ENV_VARS)

# Check the proxy configuration
proxy_info = {}
if config_yaml_data.get(PROXY_VARS['proxy_server']) and config_yaml_data.get(PROXY_VARS['proxy_port']):
    proxy_info.update({"http_proxy": f"{config_yaml_data.get(PROXY_VARS['proxy_server'])}" +
                       f":{config_yaml_data.get(PROXY_VARS['proxy_port'])}",
                       "https_proxy": f"{config_yaml_data.get(PROXY_VARS['proxy_server'])}" +
                       f":{config_yaml_data.get(PROXY_VARS['proxy_port'])}"})
if config_yaml_data.get(PROXY_VARS['no_proxy']):
    proxy_info.update({"no_proxy":   ", ".join(
        config_yaml_data.get(PROXY_VARS['no_proxy']))})

# --------------------------------------------------------------------------- #
#                PERFORM INTEGRATION CHECKS
# --------------------------------------------------------------------------- #

@rfm.simple_test
class MountPointExistsTest(rfm.RunOnlyRegressionTest):

    if mount_info:
        mount_info_par = []
        for mount_i in mount_info:
            if mount_i.get('fstype'):
                mount_info_par.append(
                    (mount_i['mount_point'],
                     mount_i['fstype'])
                )
            else:
                mount_info_par.append(
                    (mount_i['mount_point'],
                     None)
                )
        mount_info = parameter(mount_info_par)
        # For now
        valid_systems = ['-remote']
    else:
        valid_systems = []
    descr = 'Test mount points in the system'
    valid_prog_environs = ['builtin']
    maintainers = ['VCUE', 'PA']
    time_limit = '2m'
    tags = {'mount', 'vs-node-validator'}

    @run_after('setup')
    def set_executable(self):
        if self.mount_info[1]:
            self.executable = f'grep -q "{self.mount_info[0]} {self.mount_info[1]}" /proc/mounts || echo FAILED'
        else:
            self.executable = f'ls {self.mount_info[0]} || echo FAILED'

    @sanity_function
    def validate(self):

        return sn.assert_not_found('FAILED', self.stdout,
                                   msg=f'Mount point "{self.mount_info[0]} {self.mount_info[1]}" not found in /proc/mounts')


@rfm.simple_test
class PackagePresentTest(rfm.RunOnlyRegressionTest):

    if tools_info:
        tools_info = parameter(tools_info)
        # For now
        valid_systems = ['-remote']
    else:
        valid_systems = []
    descr = 'Test pkgs installation in the system'
    valid_prog_environs = ['builtin']
    maintainers = ['VCUE', 'PA']
    time_limit = '2m'
    tags = {'tools', 'vs-node-validator'}

    @run_after('setup')
    def set_executable(self):
        self.executable = ''
        for pkg in pkg_names[self.tools_info]:
            if not self.executable:
                self.executable += f'(which {pkg}'
            else:
                self.executable += f' && which {pkg}'
        self.executable += ') || echo FAILED'

    @sanity_function
    def validate(self):
        return sn.assert_not_found('FAILED', self.stdout,
                                   msg=f'Did not find an installation for {self.tools_info}')


@rfm.simple_test
class EnvVariableConfigTest(rfm.RunOnlyRegressionTest):

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
    maintainers = ['VCUE', 'PA']
    time_limit = '2m'
    tags = {'env_var', 'vs-node-validator'}

    @run_after('setup')
    def set_executable(self):
        self.executable = f'printenv {self.envs_info[0]}'

    @sanity_function
    def validate(self):
        return sn.assert_found(self.envs_info[1], self.stdout,
                               msg=f'Environment variable {self.envs_info[0]} is not set up correctly')


@rfm.simple_test
class ProxyConfigTest(rfm.RunOnlyRegressionTest):

    proxy_info_par = [(k, v)
                      for k, v in proxy_info.items() if v and "None" not in v]
    if proxy_info_par:
        proxy_info = parameter(proxy_info_par)
        valid_systems = ['+remote']
    else:
        valid_systems = []
    descr = 'Test proxy configuration of the system'
    valid_prog_environs = ['builtin']
    time_limit = '2m'
    tags = {'proxy', 'vs-node-validator'}

    @run_after('setup')
    def set_executable(self):
        self.executable = f'printenv {self.proxy_info[0]}'

    @sanity_function
    def validate(self):
        return sn.assert_found(self.proxy_info[1], self.stdout,
                               msg=f'Proxy configuration {self.proxy_info[0]} is not set up correctly')
