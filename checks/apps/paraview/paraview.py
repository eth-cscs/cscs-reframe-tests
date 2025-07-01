# Copyright 2016 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class ParaView_coloredSphere(rfm.RunOnlyRegressionTest):
    """
    daint:
    ParaView Version  (5, 13, 2)
    rank= 0 / 12
    Vendor:   NVIDIA Corporation
    Version:  4.6.0 NVIDIA 550.54.15
    Renderer: NVIDIA GH200 120GB/PCIe
    writing  coloredSphere_v5.13.2.EGL.png

    eiger:
    ParaView Version  (5, 13, 2)
    rank= 0 / 12
    Vendor:   Mesa
    Version:  3.3 (Core Profile) Mesa 23.3.6
    Renderer: softpipe
    writing  coloredSphere_v5.13.2.OSMESA.png
    """
    valid_systems = ['+uenv']
    valid_prog_environs = ['+paraview-python']
    num_tasks = 12
    num_tasks_per_node = 4
    time_limit = '3m'
    executable = '/user-environment/ParaView-5.13/bin/pvbatch'
    executable_opts = ['-- coloredSphere.py']
    maintainers = ['SSA']
    tags = {'production', 'maintenance'}

    @run_before('run')
    def output_file_info(self):
        self.postrun_cmds = ['file *.png']

    @sanity_function
    def assert_vendor_renderer(self):
        arch = self.current_partition.processor.arch
        regex_vendor = {'zen2': 'Mesa', 'neoverse_v2': 'NVIDIA Corporation'}
        regex_render = {
            'zen2': 'Renderer: softpipe',
            'neoverse_v2': 'Renderer: NVIDIA GH200'
        }
        regex_png = 'PNG image data,'  # 1024 x 1024, 8-bit/color RGB

        return sn.all([
            sn.assert_found(regex_vendor[arch], self.stdout),
            sn.assert_found(regex_render[arch], self.stdout),
            sn.assert_found(regex_png, self.stdout),
        ])
