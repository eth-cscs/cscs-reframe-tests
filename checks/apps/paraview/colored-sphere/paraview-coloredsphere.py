# Copyright 2016 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class paraview_coloredsphere(rfm.RunOnlyRegressionTest):
    valid_systems = ['+uenv']
    valid_prog_environs = ['+paraview']
    num_tasks = 12
    num_tasks_per_node = 4
    time_limit = '3m'
    maintainers = ['jfavre', 'albestro', 'biddisco', 'SSA']
    tags = {'production'}

    @run_before('run')
    def output_file_info(self):
        self.job.options = ['--gpus-per-task=1']

        self.prerun_cmds = [
            'cp /user-environment/helpers/bind-gpu-vtk-egl .',
        ]
        self.executable = 'bind-gpu-vtk-egl'
        self.executable_opts = ['pvbatch', 'coloredSphere.py']

        self.postrun_cmds = [
            'file *.png',
            (
                'magick *.png -format "%c" histogram:info:'
                '| tr -d :'
                '| awk \'$1 > 1000 { count++ }; END { print "unique colors: " count }\''
            ),
        ]

    @sanity_function
    def assert_vendor_renderer(self):
        arch = self.current_partition.processor.arch
        regex_vendor = {
            'zen2': 'Mesa',
            'neoverse_v2': 'NVIDIA Corporation',
        }
        regex_render = {
            'zen2': 'Renderer: (softpipe|llvmpipe)',
            'neoverse_v2': 'Renderer: NVIDIA GH200',
        }
        regex_png = 'PNG image data, 1024 x 1024, 8-bit/color RGB, non-interlaced'

        ncolors = sn.extractsingle(r"unique colors: (\d+)", self.stdout, 1, int)

        return sn.all(
            [
                sn.assert_found(regex_vendor[arch], self.stdout),
                sn.assert_found(regex_render[arch], self.stdout),
                sn.assert_found(regex_png, self.stdout),
                sn.assert_eq(ncolors, self.num_tasks + 1),
            ]
        )
