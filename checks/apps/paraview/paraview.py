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


@rfm.simple_test
class ParaView_catalystClipping(rfm.RegressionTest):
    # TODO: fix mpicc on eiger ?
    valid_systems = ['+uenv +remote']
    valid_prog_environs = ['+paraview-python']
    git_tag = variable(str, value='0.1')
    sourcesdir = None
    build_system = 'CMake'
    build_locally = False
    num_tasks = 1
    num_tasks_per_node = 1
    time_limit = '3m'
    executable = './bin/dummysph_catalystV2'
    env_vars = {
        'CATALYST_IMPLEMENTATION_NAME': 'paraview',
        'CATALYST_IMPLEMENTATION_PATHS':
        '/user-environment/ParaView-5.13/lib64/catalyst',
        'CATALYST_DATA_DUMP_DIRECTORY': '$PWD/dataset',
    }
    maintainers = ['SSA']
    tags = {'production'}

    @run_before('compile')
    def prepare_build(self):
        tgz = f'v{self.git_tag}.tar.gz'
        self.prebuild_cmds = [
            f'# tested with paraview/5.13.2:v2 -v paraview-python',
            f'wget -q https://github.com/jfavre/DummySPH/archive/refs/tags/'
            f'{tgz} && tar xf {tgz} && rm -f {tgz}',
        ]
        self.build_system.config_opts = [
            f'-S DummySPH-{self.git_tag}/src',
            '-DINSITU=Catalyst'
        ]

    @run_before('run')
    def prepare_runtime(self):
        self.executable_opts = [
            '--catalyst',
            f'DummySPH-{self.git_tag}/ParaView_scripts/catalyst_clipping.py']
        self.postrun_cmds = [
            'head -1 datasets/dataset_000020/dataset_000020_0.vtp',
            'head -1 datasets/dataset_000020.vtpd',
            'file datasets/RenderView1_000020.png'
        ]

    @sanity_function
    def assert_runtime(self):
        regex_vtp = r'VTKFile type=\"PolyData\"'
        regex_vtpd = r'VTKFile type=\"vtkPartitionedDataSet\"'
        regex_png = r'PNG image data,'  # 1024 x 1024, 8-bit/color RGB

        return sn.all([
            sn.assert_found(regex_vtp, self.stdout),
            sn.assert_found(regex_vtpd, self.stdout),
            sn.assert_found(regex_png, self.stdout),
        ])
