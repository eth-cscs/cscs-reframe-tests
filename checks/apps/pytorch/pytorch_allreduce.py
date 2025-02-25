# Copyright 2025 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib
import re
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))

from container_engine import ContainerEngineMixin  # noqa: E402

sys.path.append(
    str(pathlib.Path(__file__).parent.parent.parent.parent / 'utility')
)
from nvcr import nvidia_image_tags


@rfm.simple_test
class PyTorchNCCLAllReduce(rfm.RunOnlyRegressionTest, ContainerEngineMixin):
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['builtin']
    num_nodes = variable(int, value=8)
    sourcesdir = None
    curated_images = ['nvcr.io#nvidia/pytorch:24.12-py3']

    # NOTE: only the "-py3" image is supported by the test
    supported_flavors = ["-py3"]

    pytorch_tags = nvidia_image_tags('pytorch')
    latest_tags = []

    for flavor in supported_flavors:
        versions = []
        for tag in pytorch_tags:
            if re.match(rf'^\d+\.\d+{flavor}$', tag):
                versions.append(tag[:-len(flavor)])
        if versions:
            latest_version = max(versions)
            latest_tags += [f'{latest_version+flavor}']

    latest_images = [f'nvcr.io#nvidia/pytorch:{tag}' for tag in latest_tags]
    image = parameter(curated_images + latest_images)
    executable = 'torchrun'
    num_tasks_per_node = 1
    env_vars = {
        'NCCL_DEBUG': 'Info',
    }
    reference = {
        '*': {'bandwidth': (91.04, -0.05, None, 'GB/s')}
    }
    tags = {'ml'}

    @run_after('init')
    def set_image(self):
        self.container_image = self.image
        self.container_env_table = {
            'annotations.com.hooks': {
                    'aws_ofi_nccl.enabled': 'true',
                    'aws_ofi_nccl.variant': 'cuda12',
            },
       }

    @run_after('setup')
    def setup_test(self):
        curr_part = self.current_partition
        self.num_gpus_per_node = curr_part.select_devices('gpu')[0].num_devices
        self.num_tasks = self.num_nodes
        self.job.options = [f'--gpus-per-task={self.num_gpus_per_node}']
        self.num_cpus_per_task = curr_part.processor.num_cpus
        self.env_vars['OMP_NUM_THREADS'] = (self.num_cpus_per_task //
                                            self.num_gpus_per_node)

    @run_after('setup')
    def set_executable_opts(self):
        self.prerun_cmds = ['wget https://jfrog.svc.cscs.ch/artifactory/cscs-reframe-tests/PyTorch/all_reduce_bench.py'] # noqa: E501
        headnode_cmd = (
            '$(scontrol show hostnames $SLURM_JOB_NODELIST | head -n 1)'
        )
        self.executable_opts = [
            f'--nproc_per_node={self.num_gpus_per_node}',
            f'--nnodes={self.num_nodes}',
            f'--rdzv_endpoint {headnode_cmd}:6000',
            f'--rdzv_backend c10d',
            f'all_reduce_bench.py',
        ]

    @sanity_function
    def assert_sanity(self):
        return sn.assert_found(
            r'The average bandwidth of all_reduce', self.stdout
        )

    @performance_function('GB/s')
    def bandwidth(self):
        return sn.extractsingle(r'\|\s*16GiB\s*\|\s*(?P<busbw>\S+)GBps\s*\|',
                                self.stdout, tag='busbw', conv=float
        )
