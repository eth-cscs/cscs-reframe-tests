# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class paraview_colored_sphere(rfm.RunOnlyRegressionTest):
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
    descr = 'ParaView pvbatch coloredSphere.py test'
    valid_systems = ['+uenv +nvgpu', '+uenv -nvgpu -amdgpu']
    valid_prog_environs = ['+uenv +paraview-python']
    num_tasks = 12
    num_tasks_per_node = 6
    time_limit = '3m'
    executable = 'pvbatch'
    executable_opts = ['-- coloredSphere.py']
    maintainers = ['jfavre', 'biddisco', 'albestro', 'SSA']
    tags = {'production'}

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
class paraview_catalyst_clipping(rfm.RegressionTest):
    descr = 'ParaView Catalyst DummySPH test'
    valid_systems = ['+uenv +nvgpu', '+uenv -nvgpu -amdgpu']
    valid_prog_environs = ['+uenv +paraview-python']
    sourcesdir = 'https://github.com/jfavre/DummySPH.git'
    build_system = 'CMake'
    build_locally = False
    num_tasks = 1
    num_tasks_per_node = 1
    time_limit = '3m'
    executable = './bin/dummysph_catalystV2'
    env_vars = {
        'CATALYST_IMPLEMENTATION_NAME': 'paraview',
        'CATALYST_IMPLEMENTATION_PATHS':
            '/user-environment/paraview/lib64/catalyst',
        'CATALYST_DATA_DUMP_DIRECTORY': 'dataset',
        'VTK_SILENCE_GET_VOID_POINTER_WARNINGS': '1'
    }
    maintainers = ['jfavre', 'biddisco', 'albestro', 'SSA']
    tags = {'production'}

    @run_before('compile')
    def prepare_build(self):
        self.build_system.config_opts = ['-S src', '-DINSITU=Catalyst']

    @run_before('run')
    def prepare_job(self):
        self.executable_opts = [
            f'--catalyst',
            f'ParaView_scripts/catalyst_clipping.py'
        ]
        self.prerun_cmds = ['']
        self.postrun_cmds = [
            '',
            'head -1 datasets/dataset_000001.vtpd',
            'head -1 head datasets/dataset_000001/dataset_000001_0.vtp',
            'file datasets/RenderView1_000001.png'
        ]

    @sanity_function
    def assert_runtime(self):
        regex_1 = r'VTKFile type=\"vtkPartitionedDataSet\"'
        regex_2 = r'VTKFile type=\"PolyData\"'
        regex_3 = r'PNG image data,'  # 1024 x 1024, 8-bit/color RGB

        return sn.all([
            sn.assert_found(regex_1, self.stdout),
            sn.assert_found(regex_2, self.stdout),
            sn.assert_found(regex_3, self.stdout),
        ])


@rfm.simple_test
class paraview_catalyst_double_gyre(rfm.RegressionTest):
    descr = 'ParaView Catalyst Double Gyre test'
    valid_systems = ['+uenv +nvgpu', '+uenv -nvgpu -amdgpu']
    valid_prog_environs = ['+uenv +paraview-python']
    sourcesdir = 'https://github.com/jfavre/InSitu-Vis-Tutorial.git'
    build_system = 'CMake'
    build_locally = False
    num_tasks = 1
    num_tasks_per_node = 1
    time_limit = '3m'
    executable = 'bin/double_gyre_catalyst'
    env_vars = {
        'CATALYST_IMPLEMENTATION_NAME': 'paraview',
        'CATALYST_IMPLEMENTATION_PATHS':
            '/user-environment/paraview/lib64/catalyst',
        'CATALYST_DATA_DUMP_DIRECTORY': 'dataset',
        'VTK_SILENCE_GET_VOID_POINTER_WARNINGS': '1'
    }
    maintainers = ['jfavre', 'biddisco', 'albestro', 'SSA']
    tags = {'production'}

    @run_before('compile')
    def prepare_build(self):
        # on eiger, mpicxx/mpicc were broken (g++: No such file),
        # keeping for reference:
        # self.build_system.cc = 'gcc'
        # self.build_system.cxx = 'g++'
        self.build_system.config_opts = [
            '-S Examples/DoubleGyre/C++', '-DINSITU=Catalyst']

    @run_before('run')
    def prepare_job(self):
        self.executable_opts = [
            '128 64 10', './Examples/DoubleGyre/Python/pvDoubleGyre.py'
        ]
        self.prerun_cmds = ['']
        self.postrun_cmds = [
            '',
            'head -1 datasets/doublegyre_000010.vtpd',
            'head -1 datasets/doublegyre_000010/doublegyre_000010_0.vti',
            'file datasets/RenderView1_000010.png'
        ]

    @sanity_function
    def assert_runtime(self):
        regex_1 = r'VTKFile type=\"vtkPartitionedDataSet\"'
        regex_2 = r'VTKFile type=\"ImageData\"'
        regex_3 = r'PNG image data,'  # 1280 x 768, 8-bit/color RGB

        return sn.all([
            sn.assert_found(regex_1, self.stdout),
            sn.assert_found(regex_2, self.stdout),
            sn.assert_found(regex_3, self.stdout)
        ])
