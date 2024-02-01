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
    sourcesdir = None
    num_tasks = 2 
    num_tasks_per_node = 1
    test_name = parameter(['all_reduce', 'sendrecv'])
    env_vars = {
        'NCCL_DEBUG': 'Info',
        'ENROOT_SLURM_HOOK': 1,
        'ENROOT_CXI_HOOK': 1,
        'NCCL_NET_PLUGIN': 'ofi',
        'CXI_FORK_SAFE': 1,
        'CXI_FORK_SAFE_HP': 1,
        'FI_CXI_DISABLE_CQ_HUGETLB': 1,
        'NCCL_CROSS_NIC': 1,
        'NCCL_NET_GDR_LEVEL': 'PHB',
        'FI_CXI_DISABLE_HOST_REGISTER': 1,
        'FI_MR_CACHE_MONITOR': 'userfaultfd',
    }

    @run_after('setup')
    def set_executable(self):
        self.executable = f'{self.test_name}_perf'

    @run_after('setup')
    def set_num_gpus_per_node(self):
        curr_part = self.current_partition
        self.num_gpus_per_node = curr_part.select_devices('gpu')[0].num_devices

    @run_after('setup')
    def set_executable_opts(self):
        self.executable_opts = [
            f'-w 10', '-n 20', f'-b 1024', f'-e 1024M',
            f'-g {self.num_gpus_per_node}' 
        ] 

    @run_before('run')
    def set_pmi2(self):
        self.job.launcher.options += ['--mpi=pmi2']

    @sanity_function
    def assert_sanity(self):
        return sn.all([
            sn.assert_found(r'Out of bounds values\s*:\s*0\s*OK', self.stdout),
            sn.assert_found(
                r'NCCL INFO NET/OFI Selected Provider is cxi', self.stdout
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
    valid_systems = ['+ce +nvgpu']
    image_tag = parameter(['cuda11.8', 'cuda12.3'])

    # Disable Nvidia Driver requirement
    env_vars['NVIDIA_DISABLE_REQUIRE'] = 1

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
        self.container_image = f'teojgo/nccl-tests:{self.image_tag}'
        self.container_mounts = [ 
            f'/opt/cscs/aws-ofi-ccl-plugin/{cuda_major}/libnccl-net.so:'
            f'/usr/lib/libnccl-net-ofi.so'
        ] 


@rfm.simple_test
class RCCLTestCE(XCCLTestBase):
    valid_systems = ['+ce +amdgpu']
    image_tag = parameter(['rocm57', 'rocm60'])
    reference_per_test = {
        'sendrecv': {
            '*': {
                'GB/s': (7.4, -0.05, None, 'GB/s')
            }
         },
        'all_reduce': {
            '*': {
                'GB/s': (105.0, -0.05, None, 'GB/s')
            }
        }
    }

    @run_after('init')
    def setup_ce(self):
        rocm_major = self.image_tag[:-1]
        self.container_image = f'teojgo/rccl-tests:{self.image_tag}'
        self.container_mounts = [
            f'/opt/cscs/aws-ofi-ccl-plugin/{rocm_major}/librccl-net.so:'
            f'/usr/lib/librccl-net-ofi.so'
        ]
