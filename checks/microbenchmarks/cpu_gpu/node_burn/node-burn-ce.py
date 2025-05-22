# Copyright 2025 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn
import uenv

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.parent /
                    'mixins'))

from container_engine import ContainerEngineMixin  # noqa: E402


class NodeBurnCE(rfm.RunOnlyRegressionTest, ContainerEngineMixin):
    '''The base class os the node burn test using the Container Engine.

       Every clild class of `NodeBurnCE` can be made flexible on demand by
       using the `-S flexible=True` cli option of ReFrame and further control
       of the flexible node allocation can be achieved using the
       `--flex-alloc-nodes` option.
    '''

    valid_prog_environs = ['builtin']
    nb_duration = variable(int, value=20)
    nb_matrix_size = variable(int, value=40000)
    executable = 'burn-f64'
    flexible = variable(bool, value=False)
    container_image = 'jfrog.svc.cscs.ch#reframe-oci/node-burn:cuda-12.4'
    tags = {'production', 'maintenance', 'appscheckout'}

    def set_num_tasks(self):
        if self.flexible:
            self.num_tasks = 0
        else:
            self.num_tasks = self.num_tasks_per_node

    @run_before('performance')
    def validate_perf(self):
        self.uarch = uenv.uarch(self.current_partition)
        if (
            self.uarch is not None and
            self.uarch in self.ref_nb_gflops
        ):
            self.reference = {
                self.current_partition.fullname: self.ref_nb_gflops[self.uarch]
            }

    @sanity_function
    def validate_test(self):
        regex = rf'nid\d+:{self.test_hw}.*\s+(\d+\.\d+)\s+GFlops,'
        num_res = sn.count(sn.extractall(regex, self.stdout, 1, float))
        return sn.assert_eq(self.num_tasks_assigned, num_res)

    @performance_function('GFlops')
    def nb_gflops(self):
        regex = rf'nid\d+:{self.test_hw}.*\s+(\d+\.\d+)\s+GFlops,'
        return sn.min(sn.extractall(regex, self.stdout, 1, float))

    @property
    @deferrable
    def num_tasks_assigned(self):
        return self.job.num_tasks


@rfm.simple_test
class CudaNodeBurnGemmCE(NodeBurnCE):
    ref_nb_gflops = {
        'a100': {'nb_gflops': (9746*2*0.85, -0.1, None, 'GFlops')},
        'gh200': {'nb_gflops': (42700, -0.1, None, 'GFlops')},
    }
    valid_systems = ['+ce +nvgpu']
    test_hw = 'gpu'

    @run_before('run')
    def setup_job(self):
        self.skip_if_no_procinfo()
        self.job.options = [f'--gpus-per-task=1']
        self.num_gpus = self.current_partition.devices[0].num_devices
        self.num_tasks_per_node = self.num_gpus
        self.set_num_tasks()
        self.extra_resources = {
            'gres': {'gres': f'gpu:{self.num_tasks}'}
        }
        self.executable_opts = [
            f'-ggemm,{self.nb_matrix_size}',
            f'-d{self.nb_duration}', '--batch'
        ]


@rfm.simple_test
class CPUNodeBurnGemmCE(NodeBurnCE):
    ref_nb_gflops = {
        'gh200': {'nb_gflops': (2500, -0.1, None, 'GFlops')},
    }
    test_hw = 'cpu'
    valid_systems = ['+ce']
    env_vars.update({
        # Disable the nvidia-container-cli to run on systems without
        # Nvidia Gpus
        'NVIDIA_VISIBLE_DEVICES': '"void"',
        'NVIDIA_DISABLE_REQUIRE': 1,
        'OMP_PROC_BIND': 'true',
    })

    @run_before('run')
    def setup_job(self):
        self.skip_if_no_procinfo()
        proc = self.current_partition.processor
        self.num_sockets = int(proc.num_sockets)
        self.cpus_per_socket = int(proc.num_cpus_per_socket)

        # On GH200 use 1 task per GH module
        if proc.arch == 'neoverse_v2':
            self.num_tasks_per_node = self.num_sockets
            self.num_cpus_per_task = self.cpus_per_socket
        else:
            self.num_tasks_per_node = 1
            self.num_cpus_per_task = self.cpus_per_socket * self.num_sockets

        self.set_num_tasks()
        self.executable_opts = [
            f'-cgemm,{self.nb_matrix_size}',
            f'-d{self.nb_duration}', '--batch'
        ]
