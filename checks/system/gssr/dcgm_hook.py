# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import sys
import pathlib

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))
from container_engine import ContainerEngineMixin  # noqa: E402


@rfm.simple_test
class dcgmi_rpm_bin_and_lib_installed(rfm.RunOnlyRegressionTest):
    descr = 'Check DCGM executable and libraries are installed'
    maintainers = ['VCUE', 'PA']
    tags = {'maintenance', 'vs-node-validator'}
    sourcesdir = 'src/rpm'
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['builtin']
    executable = './dcgm_rpm.sh'
    time_limit = '1m'

    @sanity_function
    def assert_sanity(self):
        return sn.all([
            sn.assert_found('/usr/bin/dcgmi', self.stdout),
            sn.assert_found('^Files \\S+ and \\S+ are identical', self.stdout),
        ])


@rfm.simple_test
class gssr_ce_hook_avail(rfm.RunOnlyRegressionTest, ContainerEngineMixin):
    descr = 'Check DCGM CE hook is working with gssr'
    maintainers = ['VCUE', 'PA']
    tags = {'ce', 'maintenance', 'vs-node-validator'}
    sourcesdir = 'src/hook'
    valid_systems = ['+ce +nvgpu']
    valid_prog_environs = ['builtin']
    num_nodes = variable(int, value=1)
    pytorch_image_tag = parameter(['25.01-py3_nvrtc-12.9'])
    container_env_table = {'annotations.com.hooks': {'dcgm.enabled': 'true'}}
    executable = './dcgm_hook.sh'
    time_limit = '5m'

    @run_after('init')
    def setup_ce(self):
        self.container_image = (f'jfrog.svc.cscs.ch#reframe-oci/pytorch:'
                                f'{self.pytorch_image_tag}')

    @sanity_function
    def assert_dcgm_hook(self):
        return sn.assert_found(
            'Monitor and analyze resource usage of a workload with GSSR',
            self.stdout)
