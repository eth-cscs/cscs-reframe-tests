# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class SlurmGPUGresTest(rfm.RunOnlyRegressionTest):
    descr = '''Ensure that the Slurm GRES (Gereric REsource Scheduling) of the number
       of gpus is correctly set on all the nodes of each partition.

       For the current partition, the test performs the following steps:
       1) count the number of nodes (node_count)
       2) count the number of nodes having Gres=gpu:N (gres_count) where
          N=num_devices from the configuration
       3) ensure that 1) and 2) match
    '''

    valid_systems = ['+scontrol +gpu']
    valid_prog_environs = ['builtin']
    sourcesdir = None
    num_tasks_per_node = 1
    executable = 'scontrol'
    executable_opts = ['show', 'nodes', '--oneliner']
    tags = {'production', 'maintenance'}

    @sanity_function
    def assert_gres_valid(self):
        partition_name = self.current_partition.name
        gpu_count = self.current_partition.select_devices('gpu')[0].num_devices
        gres_gpu = f'gpu:{gpu_count}'
        part_re = rf'Partitions=\S*{partition_name}'
        gres_re = rf'Gres=\S*{gres_gpu}'
        node_count = sn.count(sn.extractall(part_re, self.stdout))
        gres_count = sn.count(
            sn.extractall(rf'{gres_re}.*{part_re}', self.stdout))
        return sn.assert_eq(
            node_count, gres_count,
            f'{gres_count}/{node_count} of '
            f'{partition_name} nodes satisfy Gres={gres_gpu}'
        )
