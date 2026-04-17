# Copyright ETH Zurich/Swiss National Supercomputing Centre (CSCS)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn

from textwrap import dedent


@rfm.simple_test
class ParaviewBuildGadgetPlugin(rfm.CompileOnlyRegressionTest):
    valid_systems = ['+uenv']
    valid_prog_environs = ['+paraview']

    build_system = 'CMake'
    build_locally = False

    num_tasks = 1
    num_tasks_per_node = 1
    time_limit = '3m'

    maintainers = ['jfavre', 'albestro', 'SSA']
    tags = {'production'}

    @run_before('compile')
    def prepare_build(self):
        self.prebuild_cmds = [
            'git clone --depth 1 --branch master https://github.com/jfavre/ParaViewGadgetPlugin gadget-plugin.git',
            dedent(
                """
                patch -p 1 -d gadget-plugin.git <<-'EOF'
                    diff --git a/src/Reader/vtk.module b/src/Reader/vtk.module
                    index 46b504d..ed640bc 100644
                    --- a/src/Reader/vtk.module
                    +++ b/src/Reader/vtk.module
                    @@ -12,4 +12,4 @@ DEPENDS
                     PRIVATE_DEPENDS
                       VTK::vtksys
                       VTK::mpi
                    -  VTK::hdf5
                    +  VTK::hdf5vtk
                EOF
                """
            ),
        ]

        self.build_system.cc = "gcc"
        self.build_system.cxx = "g++"
        self.build_system.builddir = "build"
        self.build_system.configuredir = "gadget-plugin.git"

    @sanity_function
    def validate_build(self):
        return sn.all(
            [
                sn.assert_eq(
                    sn.count(sn.glob(r'**/libGadgetReader.so', recursive=True)),
                    1,
                ),
                sn.assert_eq(
                    sn.count(sn.glob(r'**/pvGadgetReader.so', recursive=True)),
                    1,
                ),
            ]
        )
