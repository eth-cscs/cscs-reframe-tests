# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))


@rfm.simple_test
class DCGM_NATIVE_AVAIL(rfm.RunOnlyRegressionTest):
    descr = 'Check DGCM is installed on system by default'
    valid_prog_environs = ['builtin']
    valid_systems = ['+nvgpu']
    test_name= r'is_dcgm_avail'
    executable = r'which dcgmi'

    @sanity_function
    def assert_sanity(self):
        return sn.assert_found(rf'/usr/bin/dcgmi', self.stdout)
    
@rfm.simple_test
class DCGM_LIBS_AVAIL(rfm.RunOnlyRegressionTest):
    descr = 'Check DGCM libraries are installed on expected system paths by default'
    valid_prog_environs = ['builtin']
    valid_systems = ['+nvgpu']
    test_name= r'dcgm_libs'
    executable = r'ls /usr/lib64/*dcgm* | wc -l'

    @sanity_function
    def assert_sanity(self):
        #31 libraries are found (32 lines in hook shell script due on /usr/lib64 as one line)
        return sn.assert_found(rf'31', self.stdout)

@rfm.simple_test
class DCGM_HOOK_CE(rfm.RunOnlyRegressionTest, ContainerEngineMixin):
    descr = 'Check DGCM hook is working with gssr'
    valid_prog_environs = ['builtin']
    valid_systems = ['+ce +nvgpu']
    test_name = r'dcgm_hook'
    num_nodes = variable(int, value=1)
    container_image = 'nvcr.io/nvidia/pytorch:25.08-py3'
    container_env_table = {
        'annotations.com.hooks': {
             'dcgm.enabled' = 'true',
         }
    }
    @run_after('setup')
    def config_container_platform(self):
        self.container_platform = self.platform
        self.container_platform.command = f"pip install gssr && x=`gssr -h | grep usage | wc -l` &&  if ((x > 0 )); then echo true; fi"


    @sanity_function
    def assert_dcgm_hook_ok(self):
        return sn.assert_found(r'true', self.stdout)
    
    tags = {'production', 'ce', 'maintenance'}
