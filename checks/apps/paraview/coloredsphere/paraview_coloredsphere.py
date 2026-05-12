# Copyright ETH Zurich/Swiss National Supercomputing Centre (CSCS)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class ParaviewColoredSphere(rfm.RunOnlyRegressionTest):
    valid_systems = ['+uenv']
    valid_prog_environs = ['+paraview']
    time_limit = '3m'
    maintainers = ['jfavre', 'albestro', 'SSA']
    tags = {'production'}

    @run_before('run')
    def setup_mpi(self):
        def get_num_gpus(partition):
            gpus = partition.select_devices("gpu")
            if len(gpus) == 0:
                return 0
            return gpus[0].num_devices

        self.num_gpus_per_node = get_num_gpus(self.current_partition)

        if self.num_gpus_per_node > 0:
            self.num_tasks_per_node = self.num_gpus_per_node
            self.job.options = ['--gpus-per-task=1']
        else:
            self.num_tasks_per_node = 2

        self.num_tasks = 2 * self.num_tasks_per_node

    @run_before('run')
    def setup_execution(self):
        cli_exec = ["pvbatch", "coloredSphere.py"]
        if self.num_gpus_per_node > 0:
            self.prerun_cmds += [
                'cp /user-environment/helpers/bind-gpu-vtk-egl .',
            ]
            cli_exec.insert(0, "bind-gpu-vtk-egl")
        self.executable = cli_exec[0]
        self.executable_opts = cli_exec[1:]

    @run_before('run')
    def extract_info(self):
        self.postrun_cmds = [
            'file *.png',
            (
                'magick *.png -format "%c" histogram:info:'
                '| tr -d :'
                '| awk \'$1 > 1000 { count++ }; END { print "unique colors: " count }\''
            ),
        ]

    @sanity_function
    def verify_info(self):
        regex_vendor = {
            'zen2': 'Mesa',
            'neoverse_v2': 'NVIDIA Corporation',
        }
        regex_render = {
            'zen2': 'Renderer: (softpipe|llvmpipe)',
            'neoverse_v2': 'Renderer: NVIDIA GH200',
        }
        regex_png = 'PNG image data, 1024 x 1024, 8-bit/color RGB, non-interlaced'

        arch = self.current_partition.processor.arch
        ncolors = sn.extractsingle(r"unique colors: (\d+)", self.stdout, 1, int)

        return sn.all(
            [
                sn.assert_found(regex_vendor[arch], self.stdout),
                sn.assert_found(regex_render[arch], self.stdout),
                sn.assert_found(regex_png, self.stdout),
                sn.assert_eq(ncolors, self.num_tasks + 1),
            ]
        )
