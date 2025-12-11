# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))

from container_engine import ContainerEngineMixin  # noqa: E402


class enroot_import_image(rfm.RunOnlyRegressionTest):
    archive_name = 'test_image.sqsh'
    executable = 'enroot'
    valid_systems = ['+ce']
    valid_prog_environs = ['builtin']
    maintainers = ['amadonna', 'VCUE']

    @run_before('run')
    def set_executable_opts(self):
        self.executable_opts = ['import', '-o', self.archive_name, self.image]

    @sanity_function
    def assert_image_imported(self):
        return sn.path_exists(os.path.join(self.stagedir, self.archive_name))


class enroot_import_image_dockerhub(enroot_import_image):
    image = variable(str, value='docker://index.docker.io#library/ubuntu:latest')


class enroot_import_image_ngc(enroot_import_image):
    image = variable(
        str, value='docker://nvcr.io#nvidia/hpc-benchmarks:24.03'
    )


@rfm.simple_test
class RunJobCE(rfm.RunOnlyRegressionTest, ContainerEngineMixin):
    descr = 'CE check with Dockerhub import and simple image run (ubuntu)'
    valid_systems = ['+ce']
    valid_prog_environs = ['builtin']
    container_image = ''  # Defined after setup
    enroot_image = fixture(enroot_import_image_dockerhub, scope='session')
    executable = 'cat'
    executable_opts = ['/etc/os-release']
    tags = {'production', 'ce', 'maintenance'}

    @run_after('setup')
    def set_image_path(self):
        self.container_image = os.path.join(self.enroot_image.stagedir,
                                            self.enroot_image.archive_name)

    @sanity_function
    def assert_found_found_ubuntu(self):
        return sn.assert_found(r'^NAME="Ubuntu"', self.stdout)


@rfm.simple_test
class RunNVGPUJobCE(rfm.RunOnlyRegressionTest, ContainerEngineMixin):
    descr = 'CE check with NGC import and Stream job on GPU'
    valid_systems = ['+ce +nvgpu']
    valid_prog_environs = ['builtin']
    container_image = ''  # Defined after setup
    enroot_image = fixture(enroot_import_image_ngc, scope='session')
    stream_array_size = variable(int, value=100000000)
    executable = '/workspace/stream-gpu-linux-$(uname -m)/stream_test'
    reference = {
        '*': {
            'MB/s': (3705000., -0.05, None, 'MB/s')
        }
    }
    tags = {'production', 'ce', 'maintenance'}

    @run_before('run')
    def set_num_gpus(self):
        gpu_devices = self.current_partition.select_devices('gpu')
        if not gpu_devices:
            self.skip('The test is not supported in partitions without gpus')

        self.num_gpus_per_node = gpu_devices[0].num_devices

    @run_after('setup')
    def set_image_path(self):
        self.container_image = os.path.join(self.enroot_image.stagedir,
                                            self.enroot_image.archive_name)

    @run_before('run')
    def set_executable_opts(self):
        self.executable_opts = [
            f'-d0', f'-n{self.stream_array_size}',
        ]

    @sanity_function
    def assert_sanity(self):
        return sn.assert_found(r'^Triad:\s+\S+', self.stdout)

    @performance_function('MB/s')
    def bandwidth(self):
        return sn.extractsingle(
            r'^Triad:\s+(?P<mbs>\S+)', self.stdout, 'mbs', float)
