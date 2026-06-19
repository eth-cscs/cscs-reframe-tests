# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os

import reframe as rfm
import reframe.utility.sanity as sn

from packaging.specifiers import SpecifierSet


@rfm.simple_test
class ParaviewGadgetPlugin(rfm.RegressionTest):
    valid_systems = ['+uenv']
    valid_prog_environs = ['+paraview']

    build_system = 'CMake'
    build_locally = False
    repo = variable(str,
                    value='https://github.com/jfavre/ParaViewGadgetPlugin.git')
    commit = variable(str, value='da0e244a23adeb3d38c87d0ac2479c38a9c83c90')
    executable = 'echo'

    num_tasks = 1
    num_tasks_per_node = 1
    time_limit = '3m'

    maintainers = ['jfavre', 'albestro', 'SSA']
    tags = {'production'}

    uenv_version = variable(tuple, value=(None, None))

    @run_before('compile')
    def set_version(self):
        self.uenv_version = self.current_environ.extras['version']

    @run_before('compile')
    def prepare_build(self):
        self.prebuild_cmds = [
            f'mkdir gadget-plugin.git', 'cd gadget-plugin.git',
            f'git init', f'git remote add origin {self.repo}',
            f'git fetch --depth 1 origin {self.commit}',
            f'git reset --hard FETCH_HEAD', 'cd ..'
        ]

        fix_actions = need_fix_hdf5vtk(self)
        if fix_actions is not None:
            self.prebuild_cmds.extend(fix_actions)

        self.build_system.cc = 'gcc'
        self.build_system.cxx = 'g++'
        self.build_system.builddir = 'build'
        self.build_system.configuredir = 'gadget-plugin.git'

    @run_before('run')
    def prepare_postproc(self):
        _vv = '_venv'
        test_file = f'{self.build_system.configuredir}/src/Testing/Python/pvReadIsothermalCollapse.py'  # noqa: E501
        self.postrun_cmds = [
            f'pvpython -m venv {_vv}',
            f'{_vv}/bin/pip install requests',
            f'ln -s {test_file}',
            f'pvbatch --venv {_vv} {test_file}'
        ]

        self.env_vars.update({
            'PV_PLUGIN_PATH': f'{self.build_system.builddir}/lib64/paraview/plugins',  # noqa: E501
        })

    @sanity_function
    def validate_test(self):

        return sn.all(
            [
                sn.assert_eq(
                    sn.count(sn.glob(r'**/libGadgetReader.so', recursive=True)),  # noqa: E501
                    1,
                ),
                sn.assert_eq(
                    sn.count(sn.glob(r'**/pvGadgetReader.so', recursive=True)),
                    1,
                ),
                os.path.isfile('screenshot.png'),
            ]
        )


def need_fix_hdf5vtk(test):
    """Patch code according to ParaView version"""
    version, _ = test.uenv_version

    if version is None or version in SpecifierSet('~=6.1'):
        _patch_cmd = [
            'patch -p 1 -d gadget-plugin.git -i ../fix_reader_v61.patch']
    elif version in SpecifierSet('~=6.0'):
        _patch_cmd = [
            'patch -p 1 -d gadget-plugin.git -i ../fix_reader_v60.patch']
    else:
        _patch_cmd = None

    return _patch_cmd
