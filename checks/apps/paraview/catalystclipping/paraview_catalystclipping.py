# Copyright ETH Zurich/Swiss National Supercomputing Centre (CSCS)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class ParaviewCatalystClipping(rfm.RegressionTest):
    valid_systems = ['+uenv']
    valid_prog_environs = ['+paraview']

    build_system = 'CMake'
    build_locally = False

    num_tasks = 1
    num_tasks_per_node = 1
    time_limit = '3m'
    executable = 'build/bin/dummysph_catalystV2'

    maintainers = ['jfavre', 'albestro', 'biddisco', 'SSA']
    tags = {'production'}

    @run_before('compile')
    def prepare_build(self):
        self.prebuild_cmds = [
            'git clone --depth 1 --branch v0.1 https://github.com/jfavre/DummySPH dummy-sph.git',
        ]

        self.build_system.cc = "mpicc"
        self.build_system.cxx = "mpicxx"
        self.build_system.builddir = "build"
        self.build_system.configuredir = "dummy-sph.git/src"
        self.build_system.config_opts = ['-DINSITU=Catalyst']

    @run_before('run')
    def prepare_runtime(self):
        self.executable_opts = [
            '--catalyst',
            f'catalyst_clipping.py',
        ]
        self.postrun_cmds = [
            'head -1 datasets/dataset_000020/dataset_000020_0.vtp',
            'head -1 datasets/dataset_000020.vtpd',
            'file datasets/RenderView1_000020.png',
        ]

    @sanity_function
    def assert_runtime(self):
        regex_vtp = r'VTKFile type=\"PolyData\"'
        regex_vtpd = r'VTKFile type=\"vtkPartitionedDataSet\"'
        regex_png = r'PNG image data,'  # 1024 x 1024, 8-bit/color RGB

        return sn.all(
            [
                sn.assert_found(regex_vtp, self.stdout),
                sn.assert_found(regex_vtpd, self.stdout),
                sn.assert_found(regex_png, self.stdout),
            ]
        )
