# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
import uenv


# {{{ uenv_ascent_heatdiffusion_cpp
@rfm.simple_test
class uenv_ascent_heatdiffusion_cpp(rfm.RegressionTest):
    descr = "Build and Run Ascent test: HeatDiffusion (C++)"
    maintainers = ['SSA']
    tags = {'uenv', 'production'}
    valid_systems = ['+uenv']
    valid_prog_environs = ['+uenv +ascent -cpe']
    sourcesdir = None
    png1 = 'ascent_temperature_isolines-010000.png'
    build_system = 'CMake'
    build_locally = False
    time_limit = '2m'

    @run_before('compile')
    def set_build(self):
        src = os.path.join(self.current_system.resourcesdir,
                           f'github/InSitu-Vis-Tutorial/main.zip')
        self.build_system.max_concurrency = 5
        self.build_system.srcdir = (
                'InSitu-Vis-Tutorial-main/Examples/HeatDiffusion/C++')
        self.prebuild_cmds += [f'ls -l {src}', f'unzip -q {src}']
        self.build_system.config_opts = [
            f'-S {self.build_system.srcdir}',
            f'-DCMAKE_BUILD_TYPE=Debug',  # Release
            f'-DINSITU=Ascent',
            f'-DAscent_DIR=`find /user-tools/ -name ascent |grep ascent- |grep cmake`'  # noqa: E402
        ]
        cmake_arch = ''
        if uenv.uarch(self.current_partition) == 'gh200':
            cmake_arch = (
                '-DCMAKE_CUDA_ARCHITECTURES=90 '
                '-DCMAKE_CUDA_HOST_COMPILER=mpicxx')
        elif uenv.uarch(self.current_partition) == 'a100':
            cmake_arch = (
                '-DCMAKE_CUDA_ARCHITECTURES=80 '
                '-DCMAKE_CUDA_HOST_COMPILER=mpicxx')

        self.build_system.config_opts.append(cmake_arch)

    @run_before('run')
    def set_run(self):
        self.num_tasks = 4
        self.num_tasks_per_node = self.num_tasks
        self.executable = './bin/heat_diffusion'
        self.executable_opts = ['--mesh=uniform', '--res=64']
        ref_dir = os.path.join(self.current_system.resourcesdir,
                               'ascent/reference/heatdiffusion_cpp')
        self.postrun_cmds = [
            f'diff -s datasets/{self.png1} {ref_dir}/{self.png1}',
            f'cat Heat.bov',
        ]

    @sanity_function
    def validate_test(self):
        regexes = [
            r'^AscentInitialize',
            r'Stopped at iteration \d+.*Maximum error =',
            r'^AscentFinalize',
            f'{self.png1} are identical',
            r'DATA_FILE: ./Heat.bin',
            r'DATA_SIZE: 66 66 1',
            r'DATA_FORMAT: DOUBLE',
            r'VARIABLE: temperature'
        ]
        assert_list = []
        for regex in regexes:
            assert_list.append(
                sn.assert_found(regex, self.stdout, msg=f'found "{regex}"'))

        return sn.all(assert_list)
# }}}


# {{{ uenv_ascent_noise
@rfm.simple_test
class uenv_ascent_noise(rfm.RegressionTest):
    descr = "Build and Run Ascent test: noise (C++)"
    maintainers = ['SSA']
    tags = {'uenv', 'production'}
    valid_systems = ['+uenv']
    valid_prog_environs = ['+uenv +ascent -cpe']
    sourcesdir = None
    ascent_v = variable(str, value='0.9.5')
    png1 = 's1_0_000005.png'
    build_system = 'CMake'
    build_locally = False
    time_limit = '2m'

    @run_before('compile')
    def set_build(self):
        src = os.path.join(self.current_system.resourcesdir,
                           'github/InSitu-Vis-Tutorial/main.zip')
        ascent_src = os.path.join(self.current_system.resourcesdir,
                                  f'github/ascent/v{self.ascent_v}.tar.gz')
        self.build_system.max_concurrency = 5
        self.build_system.srcdir = \
            f'ascent-{self.ascent_v}/src/examples/synthetic/noise'
        self.prebuild_cmds += [
            f'tar xf {ascent_src} {self.build_system.srcdir}',
            f'ls -l {src}', f'unzip -q {src}',
            f'cp InSitu-Vis-Tutorial-main/Examples/noise/CMakeLists.txt'
            f' {self.build_system.srcdir}'
        ]
        self.build_system.config_opts = [
            f'-S {self.build_system.srcdir}',
            f'-DCMAKE_BUILD_TYPE=Debug',  # Release
            f'-DINSITU=Ascent',
            f'-DAscent_DIR=`find /user-tools/ -name ascent |grep ascent- |grep cmake`'  # noqa: E402
        ]
        cmake_arch = ''
        if uenv.uarch(self.current_partition) == 'gh200':
            cmake_arch = (
                '-DCMAKE_CUDA_ARCHITECTURES=90 '
                '-DCMAKE_CUDA_HOST_COMPILER=mpicxx')
        elif uenv.uarch(self.current_partition) == 'a100':
            cmake_arch = (
                '-DCMAKE_CUDA_ARCHITECTURES=80 '
                '-DCMAKE_CUDA_HOST_COMPILER=mpicxx')

        self.build_system.config_opts.append(cmake_arch)

    @run_before('run')
    def set_run(self):
        self.num_tasks = 8
        self.num_tasks_per_node = self.num_tasks
        self.executable = './noise'
        self.executable_opts = ['--dims=32,32,32', '--time_steps=5',
                                '--time_delta=.5']
        self.prerun_cmds = [
            f'cp ascent-{self.ascent_v}/src/examples/synthetic/noise/'
            f'example_actions.yaml ascent_actions.yaml']
        self.env_vars['OMP_NUM_THREADS'] = '16'
        ref_dir = os.path.join(self.current_system.resourcesdir,
                               'ascent/reference/noise')
        self.postrun_cmds = [f'diff -s {self.png1} {ref_dir}/{self.png1}']

    @sanity_function
    def validate_test(self):
        regexes = [
            r'^dims\s+: \(32, 32, 32\)',
            r'^time steps : \d+',
            f'{self.png1} are identical',
        ]
        assert_list = []
        for regex in regexes:
            assert_list.append(
                sn.assert_found(regex, self.stdout, msg=f'found "{regex}"'))

        return sn.all(assert_list)
# }}}


# {{{ uenv_ascent_kripke
@rfm.simple_test
class uenv_ascent_kripke(rfm.RegressionTest):
    descr = "Build and Run Ascent test: kripke (C++)"
    maintainers = ['SSA']
    tags = {'uenv', 'production'}
    valid_systems = ['+uenv']
    valid_prog_environs = ['+uenv +ascent -cpe']
    sourcesdir = None
    ascent_v = variable(str, value='0.9.5')
    png1 = 's1_0_000009.png'
    build_system = 'CMake'
    build_locally = False
    time_limit = '2m'

    @run_before('compile')
    def set_build(self):
        src = os.path.join(self.current_system.resourcesdir,
                           'github/InSitu-Vis-Tutorial/main.zip')
        ascent_src = os.path.join(self.current_system.resourcesdir,
                                  f'github/ascent/v{self.ascent_v}.tar.gz')
        self.build_system.max_concurrency = 5
        self.build_system.srcdir = \
            f'ascent-{self.ascent_v}/src/examples/proxies/kripke'
        self.prebuild_cmds += [
            f'tar xf {ascent_src} {self.build_system.srcdir}',
            f'ls -l {src}', f'unzip -q {src}',
            f'cp InSitu-Vis-Tutorial-main/Examples/kripke/CMakeLists.txt'
            f' {self.build_system.srcdir}'
        ]
        self.build_system.config_opts = [
            f'-S {self.build_system.srcdir}',
            f'-DCMAKE_BUILD_TYPE=Debug',  # Release
            f'-DINSITU=Ascent',
            f'-DAscent_DIR=`find /user-tools/ -name ascent |grep ascent- |grep cmake`'  # noqa: E402
        ]
        cmake_arch = ''
        if uenv.uarch(self.current_partition) == 'gh200':
            cmake_arch = (
                '-DCMAKE_CUDA_ARCHITECTURES=90 '
                '-DCMAKE_CUDA_HOST_COMPILER=mpicxx')
        elif uenv.uarch(self.current_partition) == 'a100':
            cmake_arch = (
                '-DCMAKE_CUDA_ARCHITECTURES=80 '
                '-DCMAKE_CUDA_HOST_COMPILER=mpicxx')

        self.build_system.config_opts.append(cmake_arch)

    @run_before('run')
    def set_run(self):
        self.num_tasks = 8
        self.num_tasks_per_node = self.num_tasks
        self.executable = './Kripke'
        self.executable_opts = [
            '--procs 2,2,2', '--zones 32,32,32', '--niter 10', '--dir 1:2',
            '--grp 1:1', '--legendre 4', '--quad 4:4']
        build_system_srcdir = \
            f'ascent-{self.ascent_v}/src/examples/proxies/kripke'
        self.prerun_cmds = [
            f'ln -fs {build_system_srcdir}/ascent_options.json .',
            f'ln -fs {build_system_srcdir}/ascent_actions.json .',
            f'ln -fs {build_system_srcdir}/run_kripke_simple_example.sh .',
        ]
        self.env_vars['OMP_NUM_THREADS'] = '16'
        ref_dir = os.path.join(self.current_system.resourcesdir,
                               'ascent/reference/kripke')
        self.postrun_cmds = [
            f'file {self.png1}',
            # TODO: f'diff -s {self.png1} {ref_dir}/{self.png1}'
        ]

    @sanity_function
    def validate_test(self):
        regexes = [
            r'blueprint verify succeeded',
            r'iter 9: particle count=',
            r'PNG image data, 1024 x 1024',
            # TODO: f'{self.png1} are identical',
        ]
        assert_list = []
        for regex in regexes:
            assert_list.append(
                sn.assert_found(regex, self.stdout, msg=f'found "{regex}"'))

        return sn.all(assert_list)
# }}}


# {{{ uenv_ascent_cloverleaf3d
@rfm.simple_test
class uenv_ascent_cloverleaf3d(rfm.RegressionTest):
    descr = "Build and Run Ascent test: CloverLeaf3D ()"
    maintainers = ['SSA']
    tags = {'uenv', 'production'}
    valid_systems = ['+uenv']
    valid_prog_environs = ['+uenv +ascent -cpe']
    sourcesdir = None
    ascent_v = variable(str, value='0.9.5')
    png1 = 'contour_tree_0200.png'
    png2 = 'levels_0200.png'
    png3 = 's1_0_000200.png'
    build_system = 'Make'
    build_locally = False
    time_limit = '2m'

    @run_before('compile')
    def set_build(self):
        src = os.path.join(self.current_system.resourcesdir,
                           'github/InSitu-Vis-Tutorial/main.zip')
        ascent_src = os.path.join(self.current_system.resourcesdir,
                                  f'github/ascent/v{self.ascent_v}.tar.gz')
        self.build_system.max_concurrency = 5
        self.build_system.srcdir = \
            f'ascent-{self.ascent_v}/src/examples/proxies/cloverleaf3d-ref'
        self.prebuild_cmds += [
            f'tar xf {ascent_src} {self.build_system.srcdir}',
            f'ls -l {src}', f'unzip -q {src}',
            f'cp InSitu-Vis-Tutorial-main/Examples/cloverleaf3d/Makefile'
            f' {self.build_system.srcdir}'
        ]
        self.build_system.options = [
            f'ASCENT_DIR=/user-tools/env/default/',
            f'-C {self.build_system.srcdir}'
        ]

    @run_before('run')
    def set_run(self):
        self.num_tasks = 8
        self.num_tasks_per_node = self.num_tasks
        build_system_srcdir = \
            f'ascent-{self.ascent_v}/src/examples/proxies/cloverleaf3d-ref'
        self.executable = f'{build_system_srcdir}/cloverleaf3d.exe'
        self.prerun_cmds = [
            f'ln -fs {build_system_srcdir}/clover.in .',
            f'ln -fs {build_system_srcdir}/ascent_options.json .',
            f'ln -fs {build_system_srcdir}/'
            f'ascent_actions_contour_tree_energy.json ascent_actions.json',
        ]
        self.env_vars['OMP_NUM_THREADS'] = '16'
        ref_dir = os.path.join(self.current_system.resourcesdir,
                               'ascent/reference/cloverleaf3d')
        self.postrun_cmds = [
            f'diff -s {self.png1} {ref_dir}/{self.png1}',
            f'diff -s {self.png2} {ref_dir}/{self.png2}',
            f'diff -s {self.png3} {ref_dir}/{self.png3}',
        ]

    @sanity_function
    def validate_test(self):
        regexes = [
            r'This test is considered NOT PASSED',
            f'{self.png1} are identical',
            f'{self.png2} are identical',
            f'{self.png3} are identical',
        ]
        assert_list = []
        for regex in regexes:
            assert_list.append(
                sn.assert_found(regex, self.stdout, msg=f'found "{regex}"'))

        return sn.all(assert_list)
# }}}
