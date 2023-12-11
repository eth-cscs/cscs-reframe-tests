# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class SlurmGresTest(rfm.RunOnlyRegressionTest):
    valid_systems = ['+scontrol']
    valid_prog_environs = ['builtin']
    num_tasks_per_node = 1
    partition = variable(str, value='nvgpu')
    gres = variable(str, value='gpu:4')
    executable = 'scontrol'
    executable_opts = ['show', 'nodes', '-o']

    @sanity_function
    def assert_gres_valid(self):
        part_re = rf'Partitions=\S*{self.partition}'
        gres_re = rf'Gres=\S*{self.gres}'
        node_count = sn.count(sn.extractall(part_re, self.stdout))
        gres_count = sn.count(sn.extractall(
            rf'{part_re}.*{gres_re}|{gres_re}.*{part_re}', self.stdout))
        return sn.assert_eq(node_count, gres_count,
            f'{gres_count}/{node_count} of '
            f'{self.partition} nodes satisfy Gres={self.gres}'
        )
