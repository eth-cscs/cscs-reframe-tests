# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import sys
import pathlib

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))
from container_engine import ContainerEngineMixin  # noqa: E402


class MLperfStorageBase(rfm.RunOnlyRegressionTest):
    image = 'jfrog.svc.cscs.ch/reframe-oci/mlperf-storage:v1.0-mpi'
    valid_prog_environs = ['builtin']
    num_nodes = parameter([1, 2])
    time_limit = '20m'
    accelerator_type = 'h100'
    workload = 'unet3d'
    tags = {'production'}
    env_vars = {
        'LC_ALL': 'C',
        'HYDRA_FULL_ERROR': '1',
        'RDMAV_FORK_SAFE': '1',
    }
    
    @run_after('setup')
    def setup_test(self):
        curr_part = self.current_partition
        self.num_gpus_per_node = curr_part.select_devices('gpu')[0].num_devices
        self.num_tasks_per_node = self.num_gpus_per_node
        self.num_tasks = self.num_nodes * self.num_tasks_per_node
        self.num_files = 512 * self.num_tasks
       
        self.executable = rf""" bash -c '
            set -xe;

            ./benchmark.sh datagen --workload {self.workload} \
                --accelerator-type {self.accelerator_type} \
                --num-parallel {self.num_tasks} \
                --param dataset.num_files_train={self.num_files} \
                --param dataset.data_folder=/rfm_workdir/unet3d_data;

            ./benchmark.sh run --workload {self.workload} \
                --accelerator-type {self.accelerator_type} \
                --num-accelerators {self.num_tasks} \
                --results-dir resultsdir \
                --param dataset.num_files_train={self.num_files} \
                --param dataset.data_folder=/rfm_workdir/unet3d_data;
        ' """
        # clean up data
        self.postrun_cmds = ['rm -rf /rfm_workdir/unet3d_data']

        self.reference = {
            '*': {
                'mb_per_sec_total': (8000, -0.1, None, 'MB/second'),
            }
        }
        self.job.launcher.options += ['-l']

    @sanity_function
    def assert_job_is_complete(self):
        return sn.assert_found(r'.*train_au_meet_expectation.*', self.stderr)

    @performance_function('MB/second')
    def mb_per_sec_total(self):
        return sn.avg(sn.extractall(
            r'Training I/O Throughput \(MB/second\): (?P<mbs_total>\S+)',
            self.stderr, 'mbs_total', float
        ))



@rfm.simple_test
class MLperfStorageBaseCEtest(MLperfStorageBase, ContainerEngineMixin):
    descr = ('Check the training throughput using the ContainerEngine and '
             'NVIDIA NGC')
    valid_systems = ['+ce']
    tags = {'production', 'ce'}
    sourcesdir = 'src'
    
    @run_before('run')
    def set_container_variables(self):
        self.container_image = self.image


@rfm.simple_test
class MLperfStorageBaseSarusTest(MLperfStorageBase):
    descr = 'Check the training throughput using Sarus and NVIDIA NGC'
    valid_systems = ['+nvgpu +sarus']
    platform = 'Sarus'

    @run_before('run')
    def set_container_variables(self):
        self.container_platform = self.platform
        self.container_platform.command = self.executable
        self.container_platform.image = self.image
        self.container_platform.workdir = None
        self.container_platform.with_mpi = True


@rfm.simple_test
class MLperfStorageBaseDockerTest(MLperfStorageBase):
    descr = 'Check the training throughput using Docker and NVIDIA NGC'
    valid_systems = ['+docker']
    platform = 'Docker'
    num_nodes = parameter([1])
    num_files = 16

    @run_before('run')
    def set_container_variables(self):
        self.container_platform = self.platform
        self.container_platform.command = self.executable
        self.container_platform.image = self.image
        self.container_platform.workdir = None
        self.container_platform.options = ['-e RDMAV_FORK_SAFE=1']
