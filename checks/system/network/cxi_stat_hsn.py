# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent /
                    'mixins'))

from container_engine import ContainerEngineMixin  # noqa: E402

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class CXIStatHSN(rfm.RunOnlyRegressionTest):
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['builtin']
    cxi_device_count = variable(int, value=4)
    flexible = variable(bool, value=False)
    sourcesdir = None
    num_tasks_per_node = 1
    executable = 'bash'
    executable_opts = ["-c", "'cxi_stat > $(hostname).out'"]
    tags = {'appscheckout', 'production', 'maintenance'}

    @run_before('run')
    def set_num_tasks(self):
        if self.flexible:
            self.num_tasks = 0
        else:
            self.num_tasks = self.num_tasks_per_node

    @property
    @deferrable
    def num_tasks_assigned(self):
        return self.job.num_tasks

    @sanity_function
    def assert_hsn_count(self):
        expected_devices = {f'hsn{i}' for i in range(self.cxi_device_count)}
        total_matches = 0
        nodeset = set(self.job.nodelist)
        healthy_nodes = set()
        for nid_path in pathlib.Path.cwd().glob('nid*.out'):
            nodename = nid_path.stem
            network_devices = sn.extractall(
                rf'Network device:\s*(?P<name>\S+)', nid_path, 'name'
            )
            if sn.assert_eq(expected_devices, set(network_devices)):
                total_matches += 1
                healthy_nodes.add(nodename)

        problematic_nodes = nodeset.difference(healthy_nodes)
        msg = (f'nodes with fewer than expected healthy cxi devices: '
               f'{",".join(problematic_nodes)!r}')
        return sn.assert_eq(total_matches, self.num_tasks, msg=msg)


@rfm.simple_test
class CXIStatHSNCE(CXIStatHSN, ContainerEngineMixin):
    valid_systems = ['+ce +nvgpu']
    image_repository = 'teojgo/cxi-utils'
    image_tag = 'shs-12.0.1'
    container_image = f'{image_repository}:{image_tag}'
