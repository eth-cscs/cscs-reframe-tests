# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))

from container_engine import ContainerEngineMixin  # noqa: E402


class XCCLTestBase(rfm.RunOnlyRegressionTest, ContainerEngineMixin):
    valid_prog_environs = ['builtin']
    maintainers = ['amadonna', 'VCUE']
    sourcesdir = None
    test_name = parameter(['all_reduce', 'sendrecv'])
    num_nodes = variable(int, value=2)
    min_bytes = variable(str, value='1024M')
    max_bytes = variable(str, value='1024M')
    container_env_table = {
        'annotations.com.hooks': {
            'aws_ofi_nccl.enabled': 'true'
        }
    }
    env_vars = {
        'NCCL_DEBUG': 'Info',

        # Disable MCA components to avoid warnings
        'PMIX_MCA_psec': '^munge',
        'PMIX_MCA_gds': '^shmem2'
    }
    tags = {'production', 'ce', 'maintenance'}

    @run_after('setup')
    def set_executable(self):
        self.executable = f'{self.test_name}_perf'

    @run_after('setup')
    def set_num_gpus_per_node(self):
        curr_part = self.current_partition
        self.num_gpus_per_node = curr_part.select_devices('gpu')[0].num_devices
        self.num_tasks_per_node = self.num_gpus_per_node
        self.num_tasks = self.num_nodes * self.num_gpus_per_node

    @run_after('setup')
    def set_nchannels_per_net_peer(self):
        # The following boosts performance for sendrecv in multiple nodes
        # See https://github.com/NVIDIA/nccl/issues/1272
        if self.test_name == 'sendrecv':
            self.env_vars['NCCL_NCHANNELS_PER_NET_PEER'] = 4

    @run_after('setup')
    def set_executable_opts(self):
        self.executable_opts = [
            f'-b {self.min_bytes}', f'-e {self.max_bytes}', f'-g 1'
        ]

    @run_before('run')
    def set_pmix(self):
        self.job.launcher.options += ['--mpi=pmix']

    @sanity_function
    def assert_sanity(self):
        return sn.all([
            sn.assert_found(r'Out of bounds values\s*:\s*0\s*OK', self.stdout),
            sn.assert_found(
                r'NCCL INFO NET/OFI Selected [pP]rovider is cxi', self.stdout
            )
         ])

    @run_before('performance')
    def set_reference(self):
        self.reference = self.reference_per_test[self.test_name]

    @run_before('performance')
    def set_perf(self):
        self.perf_patterns = {
            'GB/s': sn.extractsingle(
                r'Avg bus bandwidth\s*:\s*(?P<gbs>\S+)',
                self.stdout, 'gbs', float)
        }


@rfm.simple_test
class NCCLTestsCE(XCCLTestBase):
    descr = 'Point-to-Point and All-Reduce NCCL tests with CE'
    valid_systems = ['+ce +nvgpu']
    image_tag = parameter(['cuda12.9.1'])

    # Disable Nvidia Driver requirement
    env_vars['NVIDIA_DISABLE_REQUIRE'] = 1

    # Disable MCA components to avoid warnings
    env_vars.update(
        {
            'PMIX_MCA_psec': '^munge',
            'PMIX_MCA_gds': '^shmem2'
        }
    )

    reference_per_test = {
        'sendrecv': {
            '*': {
                'GB/s': (24.0, -0.05, None, 'GB/s')
            }
         },
        'all_reduce': {
            '*': {
                'GB/s': (75.0, -0.05, None, 'GB/s')
            }
        }
    }

    @run_after('init')
    def setup_ce(self):
        cuda_major = self.image_tag.split('.')[0]
        self.container_image = (f'jfrog.svc.cscs.ch#reframe-oci/nccl-tests:'
                                f'{self.image_tag}')
        self.container_env_table['annotations.com.hooks'].update({
            'aws_ofi_nccl.variant': cuda_major
        })


@rfm.simple_test
class RCCLTestCE(XCCLTestBase):
    descr = 'Point-to-Point and All-Reduce RCCL tests with CE'
    valid_systems = ['+ce +amdgpu']
    image_tag = parameter(['rocm6.3.4'])
    min_bytes = '4096M'
    max_bytes = '4096M'
    reference_per_test = {
        'sendrecv': {
            '*': {

                # TODO: revisit the performance limits based on more data
                'GB/s': (24.0, -0.40, None, 'GB/s')
            }
         },
        'all_reduce': {
            '*': {
                'GB/s': (90.0, -0.05, None, 'GB/s')
            }
        }
    }

    @run_after('init')
    def setup_ce(self):
        rocm_major = self.image_tag.split('.')[0]
        self.container_image = (f'jfrog.svc.cscs.ch#reframe-oci/rccl-tests:'
                                f'{self.image_tag}')
        self.container_env_table['annotations.com.hooks'].update({
            'aws_ofi_nccl.variant': rocm_major
        })

    @run_after('setup')
    def set_nccl_min_nchannels(self):
        gpu_devices = self.current_partition.select_devices('gpu')[0]

        # https://rocm.docs.amd.com/projects/rccl/en/latest/how-to/rccl-usage-tips.html#improving-performance-on-the-mi300x-accelerator-when-using-fewer-than-8-gpus # noqa: E501
        if gpu_devices.num_devices < 8 and gpu_devices.arch == 'gfx942':
            self.env_vars['NCCL_MIN_NCHANNELS'] = 32
