# Copyright ETH Zurich/Swiss National Supercomputing Centre (CSCS)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn

from textwrap import dedent

from packaging.version import Version
from packaging.specifiers import SpecifierSet


_UENV_CLI = 'uenv'


def uenv_metadata():
    import os
    import json
    from reframe.utility import osext

    uenv_label = os.environ['UENV']
    _uenv_version = osext.run_command(f'{_UENV_CLI} --version').stdout.strip()

    if Version(_uenv_version) >= Version('9.2.0'):
        _cmd = f"{_UENV_CLI} image inspect --json {uenv_label}"
        metadata = json.loads(osext.run_command(_cmd, shell=True).stdout)
        return Version(metadata["version"]), Version(metadata["tag"])
    else:
        _cmd = f"{_UENV_CLI} image inspect --format=\'{{version}} {{tag}}\' {uenv_label}"  # noqa E501
        _version_tag = osext.run_command(_cmd, shell=True).stdout
        return str(_version_tag.split(" ")[0]), \
            str(_version_tag.split(" ")[1])


@rfm.simple_test
class ParaviewBuildGadgetPlugin(rfm.CompileOnlyRegressionTest):
    valid_systems = ['+uenv']
    valid_prog_environs = ['+paraview']

    build_system = 'CMake'
    build_locally = False
    repo = variable(str,
                    value='https://github.com/jfavre/ParaViewGadgetPlugin.git')
    commit = variable(str, value='d9d12bde19454199b733b4e1285be3dcd1ac5595')

    num_tasks = 1
    num_tasks_per_node = 1
    time_limit = '3m'

    maintainers = ['jfavre', 'albestro', 'SSA']
    tags = {'production'}

    uenv_version = variable(tuple, value=(None, None))

    @run_before("compile")
    def set_version(self):
        self.uenv_version = uenv_metadata()

    @run_before('compile')
    def prepare_build(self):
        self.prebuild_cmds = [
            f"mkdir gadget-plugin.git", "cd gadget-plugin.git",
            f"git init", f"git remote add origin {self.repo}",
            f"git fetch --depth 1 origin {self.commit}",
            f"git reset --hard FETCH_HEAD", "cd .."
        ]

        if (fix_actions := need_fix_hdf5vtk(self)) is not None:
            self.prebuild_cmds.extend(fix_actions)

        self.build_system.cc = "gcc"
        self.build_system.cxx = "g++"
        self.build_system.builddir = "build"
        self.build_system.configuredir = "gadget-plugin.git"
        self.env_vars["Python3_ROOT_DIR"] = \
            '$(dirname $(which python3) |xargs dirname)'

    @sanity_function
    def validate_build(self):
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
            ]
        )


def need_fix_hdf5vtk(test):
    """
    Patch fix code according to ParaView version
    """
    version, _ = test.uenv_version

    if version in SpecifierSet("~=6.1"):
        _patch_cmd = [
            'patch -p 1 -d gadget-plugin.git -i ../fix_reader_v61.patch'
        ]
    elif version in SpecifierSet("~=6.0"):
        _patch_cmd = [
            'patch -p 1 -d gadget-plugin.git -i ../fix_reader_v60.patch'
        ]
    else:
        _patch_cmd = None

    return _patch_cmd
