# Copyright 2016 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))
from cuda_visible_devices_all import CudaVisibleDevicesAllMixin


class BuildDeviceCountBase(rfm.CompileOnlyRegressionTest):
    '''Fixture for building the device count binary'''
    build_locally = False
    build_system = 'SingleSource'
    sourcepath = 'deviceCount.cu'
    executable = 'deviceCount'
    num_tasks_per_node = 1

    @run_before('compile')
    def setup_compilers(self):
        self.build_system.ldflags = ['-lnvidia-ml']

    @sanity_function
    def validate_build(self):
        # If build fails, the test will fail before reaching this point.
        return True


class NvidiaDeviceCountBase(CudaVisibleDevicesAllMixin,
                            rfm.RunOnlyRegressionTest):
    '''Checks that the number of Nvidia gpu devices detected by NVML is the
       same with the one detected by Cuda.
       The test can easily run in multiple nodes by using the cli argument
       `-S '[CPE|UENV]_NvidiaDeviceCount.num_tasks=<num_nodes>'`.
       The above option can be combined with a particular nodelist to check
       the health of the nodes on demand.
    '''

    valid_systems = ['+nvgpu']
    num_tasks_per_node = 1
    num_tasks = 1

    @property
    @deferrable
    def num_tasks_assigned(self):
        return self.job.num_tasks

    @run_before('run')
    def set_executable(self):
        scheduler = self.device_count_bin.current_partition.scheduler.registered_name
        if scheduler != 'firecrest-slurm':
            remote_stagedir = self.device_count_bin.stagedir
        else:
            remote_stagedir = self.device_count_bin.build_job.remotedir

        self.executable = os.path.join(
            remote_stagedir, self.device_count_bin.executable
        )

    @sanity_function
    def validate_passed(self):
        healthy_node_match = (
            rf'\S+: NVML device count == Cuda device count == '
            rf'{self.num_gpus_per_node}'
        )
        return sn.assert_eq(
            sn.count(sn.findall(healthy_node_match, self.stdout)),
            self.num_tasks_assigned
        )


class CPE_BuildDeviceCount(BuildDeviceCountBase):
    valid_prog_environs = ['+cuda -uenv']

    # FIXME: version of clang compiler and default gcc not compatible
    # with the default cudatoolkit (11.6)
    @run_after('setup')
    def skip_incompatible_envs_cuda(self):
        if self.current_environ.name in {'PrgEnv-cray', 'PrgEnv-gnu'}:
            self.skip(
            f'environ {self.current_environ.name!r} incompatible with '
            f'default cudatoolkit')

    @run_before('compile')
    def setup_modules(self):
        sm = self.current_partition.select_devices('gpu')[0].arch[-2:]
        self.modules = ['cudatoolkit', f'craype-accel-nvidia{sm}']


class UENV_BuildDeviceCount(BuildDeviceCountBase):
    valid_prog_environs = ['+cuda +uenv']


@rfm.simple_test
class CPE_NvidiaDeviceCount(NvidiaDeviceCountBase):
    valid_prog_environs = ['+cuda -uenv']
    device_count_bin = fixture(CPE_BuildDeviceCount, scope='environment')
    tags = {'production'}

    @run_after('setup')
    def setup_modules(self):
        sm = self.current_partition.select_devices('gpu')[0].arch[-2:]
        self.modules = ['cudatoolkit', f'craype-accel-nvidia{sm}']


@rfm.simple_test
class UENV_NvidiaDeviceCount(NvidiaDeviceCountBase):
    valid_prog_environs = ['+cuda +uenv']
    device_count_bin = fixture(UENV_BuildDeviceCount, scope='environment')
    tags = {'production'}
