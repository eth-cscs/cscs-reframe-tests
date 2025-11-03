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


class XCCLTestsBase(rfm.RunOnlyRegressionTest):
    valid_prog_environs = ['builtin']
    maintainers = ['amadonna', 'msimberg', 'VCUE', 'SSA']
    sourcesdir = None
    test_name = parameter(['all_reduce', 'sendrecv'])
    num_nodes = variable(int, value=2)
    min_bytes = variable(str, value='1024M')
    max_bytes = variable(str, value='1024M')
    tags = {'production', 'maintenance'}
    env_vars = {
        'NCCL_DEBUG': 'Info',
        'FI_LOG_LEVEL': 'Info',
    }

    reference_per_test = {
        'sendrecv': {
            '*': {
                'GB/s': (24.0, -0.05, 0.05, 'GB/s')
            }
         },
        'all_reduce': {
            '*': {
                'GB/s': (150.0, -0.10, 0.10, 'GB/s')
            }
        }
    }

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
            f'--minbytes {self.min_bytes}', f'--maxbytes {self.max_bytes}',
            '--ngpus 1'
        ]

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


class XCCLTestsBaseCE(XCCLTestsBase, ContainerEngineMixin):
    container_env_table = {
        'annotations.com.hooks': {
            'aws_ofi_nccl.enabled': 'true'
        }
    }

    @run_before('run')
    def set_pmix(self):
        self.job.launcher.options += ['--mpi=pmix']

        # Disable MCA components to avoid warnings
        self.env_vars.update(
            {
                'PMIX_MCA_psec': '^munge',
                'PMIX_MCA_gds': '^shmem2'
            }
        )


class XCCLTestsBaseUENV(XCCLTestsBase):
    @run_before('run')
    def set_pmix(self):
        # Some clusters, like clariden, don't use cray_shasta as default.
        # cray_shasta is required for cray-mpich, which most uenvs use.  This
        # will need to be updated when uenvs can have OpenMPI in them.
        self.job.launcher.options += ['--mpi=cray_shasta']


def _set_xccl_uenv_env_vars(env_vars):
    env_vars.update(
        {
            # These variables are documented on
            # https://docs.cscs.ch/software/communication/nccl/#using-nccl
            'NCCL_CROSS_NIC': '1',
            'NCCL_NET': '\'AWS Libfabric\'',
            'NCCL_NET_GDR_LEVEL': 'PHB',
            'NCCL_PROTO': '^LL128',
            'FI_CXI_DEFAULT_CQ_SIZE': '131072',
            'FI_CXI_DEFAULT_TX_SIZE': '32768',
            'FI_CXI_DISABLE_HOST_REGISTER': '1',
            'FI_CXI_RX_MATCH_MODE': 'software',
            'FI_MR_CACHE_MONITOR': 'userfaultfd',
            # The following have been found to help avoid hangs, but are not yet
            # documented elsewhere
            'FI_CXI_RDZV_EAGER_SIZE': '0',
            'FI_CXI_RDZV_GET_MIN': '0',
            'FI_CXI_RDZV_THRESHOLD': '0',
        }
    )


@rfm.simple_test
class NCCLTestsCE(XCCLTestsBaseCE):
    descr = 'Point-to-Point and All-Reduce NCCL tests with CE'
    valid_systems = ['+ce +nvgpu']
    image_tag = parameter(['cuda12.9.1'])

    # Disable Nvidia Driver requirement
    env_vars['NVIDIA_DISABLE_REQUIRE'] = 1

    @run_after('init')
    def setup_ce(self):
        cuda_major = self.image_tag.split('.')[0]
        self.container_image = (f'jfrog.svc.cscs.ch#reframe-oci/nccl-tests:'
                                f'{self.image_tag}')
        self.container_env_table['annotations.com.hooks'].update({
            'aws_ofi_nccl.variant': cuda_major
        })


@rfm.simple_test
class NCCLTestsUENV(XCCLTestsBaseUENV):
    descr = 'Point-to-Point and All-Reduce NCCL tests with uenv'
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['+uenv +prgenv +nccl-tests']

    @run_after('setup')
    def set_env_vars(self):
        _set_xccl_uenv_env_vars(self.env_vars)


def _set_rccl_min_nchannels(gpu_devices, env_vars):
    # https://rocm.docs.amd.com/projects/rccl/en/latest/how-to/rccl-usage-tips.html#improving-performance-on-the-mi300x-accelerator-when-using-fewer-than-8-gpus # noqa: E501
    if gpu_devices.num_devices < 8 and gpu_devices.arch == 'gfx942':
        env_vars['NCCL_MIN_NCHANNELS'] = 32


@rfm.simple_test
class RCCLTestsCE(XCCLTestsBaseCE):
    descr = 'Point-to-Point and All-Reduce RCCL tests with CE'
    valid_systems = ['+ce +amdgpu']
    image_tag = parameter(['rocm6.3.4'])

    @run_after('init')
    def setup_ce(self):
        rocm_major = self.image_tag.split('.')[0]
        self.container_image = (f'jfrog.svc.cscs.ch#reframe-oci/rccl-tests:'
                                f'{self.image_tag}')
        self.container_env_table['annotations.com.hooks'].update({
            'aws_ofi_nccl.variant': rocm_major
        })

    @run_after('setup')
    def set_env_vars(self):
        _set_rccl_min_nchannels(
            self.current_partition.select_devices('gpu')[0], self.env_vars)


def _set_rccl_uenv_env_vars(env_vars):
    env_vars.update(
        {
            'NCCL_GDRCOPY_ENABLE': '1',
            'NCCL_NET_FORCE_FLUSH': '1',
            'FI_CXI_DISABLE_NON_INJECT_MSG_IDC': '1',
        }
    )


@rfm.simple_test
class RCCLTestsUENV(XCCLTestsBaseUENV):
    descr = 'Point-to-Point and All-Reduce RCCL tests with uenv'
    valid_systems = ['+amdgpu']
    valid_prog_environs = ['+uenv +prgenv +rccl-tests']

    @run_after('setup')
    def set_env_vars(self):
        _set_rccl_min_nchannels(
            self.current_partition.select_devices('gpu')[0], self.env_vars)
        _set_xccl_uenv_env_vars(self.env_vars)
        _set_rccl_uenv_env_vars(self.env_vars)
