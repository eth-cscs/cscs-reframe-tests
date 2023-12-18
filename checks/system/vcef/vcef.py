# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os

import reframe as rfm
import reframe.utility.sanity as sn


class enroot_import_image(rfm.RunOnlyRegressionTest):
    archive_name = 'test_image.sqsh' 
    executable = 'enroot'
    valid_systems = ['+enroot']
    valid_prog_environs= ['builtin']

    @run_before('run')
    def set_executable_opts(self):
        self.executable_opts = ['import', '-o', self.archive_name, self.image]

    @sanity_function
    def assert_image_imported(self): 
        return sn.path_exists(os.path.join(self.stagedir, self.archive_name))


@rfm.simple_test
class enroot_import_image_dockerhub(enroot_import_image):
    image = variable(str, value='docker://index.docker.io#ubuntu:latest')


class enroot_import_image_ngc(enroot_import_image):
    image = 'docker://nvcr.io#nvidia/k8s/cuda-sample:nbody'


@rfm.simple_test
class VcefRunJob(rfm.RunOnlyRegressionTest):
    valid_systems = ['+pyxis']
    valid_prog_environs = ['builtin']
    enroot_image = fixture(enroot_import_image_dockerhub, scope='session')
    executable = 'cat'
    executable_opts = ['/etc/os-release']

    @run_before('run')
    def set_image_path(self):
        self.image = os.path.join(self.enroot_image.stagedir,
                                  self.enroot_image.archive_name)

    @run_before('run')
    def set_launcher_options(self):
        self.job.launcher.options = [f'--container-image={self.image}']

    @sanity_function
    def assert_found_found_ubuntu(self): 
        return sn.assert_found(r'^NAME="Ubuntu"', self.stdout)


@rfm.simple_test
class VcefRunGPUJob(rfm.RunOnlyRegressionTest):
    valid_systems = ['+pyxis']
    valid_prog_environs = ['builtin']
    enroot_image = fixture(enroot_import_image_ngc, scope='session')
    executable = '/cuda-samples/nbody'
    num_bodies_per_gpu = variable(int, value=200000)
    reference = {
        '*': {
            'gflops': (27200., -0.05, None, 'Gflop/s')
        }
    }

    @run_before('run')
    def set_num_gpus(self):
        gpu_devices = self.current_partition.select_devices('gpu')
        if not gpu_devices:
            self.skip('The test is not supported in partitions without gpus')

        self.num_gpus_per_node = gpu_devices[0].num_devices

    @run_before('run')
    def set_image_path(self):
        self.image = os.path.join(self.enroot_image.stagedir,
                                  self.enroot_image.archive_name)

    @run_before('run')
    def set_launcher_options(self):
        self.job.launcher.options = [f'--container-image={self.image}']


    @run_before('run')
    def set_executable_opts(self):
        self.executable_opts = [
            '-benchmark', '-fp64',
            f'-numbodies={self.num_bodies_per_gpu * self.num_gpus_per_node}',
            f'-numdevices={self.num_gpus_per_node}'
        ] 

    @sanity_function
    def assert_sanity(self):
        return sn.assert_found(r'.+double-precision GFLOP/s.+', self.stdout)

    @performance_function('Gflop/s')
    def gflops(self):
        return sn.extractsingle(
            r'= (?P<gflops>\S+)\sdouble-precision GFLOP/s.+',
            self.stdout, 'gflops', float)
