# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn


# {{{ uenv_ascent_intro_cpp
ascent_intro_cpp_d = {
    'ascent_first_light_example': 'out_first_light_render_3d.png',
    #
    'ascent_scene_example1': 'ascent_output_render_var2_000000.png',
    'ascent_scene_example2': 'out_scene_ex2_render_two_plots_000000.png',
    'ascent_scene_example3': 'out_scene_ex3_view2.png',
    'ascent_scene_example4': 'out_scene_ex4_render_inferno.png',
    #
    'ascent_pipeline_example1': 'out_pipeline_ex1_contour.png',
    #
    'ascent_extract_example1': 'out_export_braid_all_fields.cycle_000100.root',
    'ascent_extract_example2': 'out_export_braid_one_field.cycle_000100.root',
    'ascent_extract_example3': 'out_extract_braid_contour.cycle_000100.root',
    'ascent_extract_example4': '108.0_144.0_out_extract_cinema_contour.png',
    #
    'ascent_query_example1': 'out_gyre_0009.png',
    #
    'ascent_trigger_example1': 'entropy_trigger_out_000200.png',
    'ascent_binning_example1': 'binning.png'
}


class uenv_ascent_intro_cpp_build(rfm.CompileOnlyRegressionTest):
    descr = "Build Ascent intro (C++)"
    sourcesdir = None
    ascent_v = variable(str, value='0.9.5')
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
            f'ascent-{self.ascent_v}/src/examples/tutorial/ascent_intro/cpp'
        self.prebuild_cmds += [
            f'tar xf {ascent_src} {self.build_system.srcdir}',
            f'tar xf {ascent_src} '
            f'{self.build_system.srcdir.replace("cpp", "notebooks")}',
            f'ls -l {src}', f'unzip -q {src}',
        ]
        self.build_system.options = [
            f'-C {self.build_system.srcdir}',
            f'ASCENT_DIR=/user-tools/env/default',
            r'ascent_first_light_example',
            #
            r'ascent_scene_examples',
            r'ascent_pipeline_example1',
            r'ascent_extract_examples',
            #
            r'ascent_query_example1',
            r'ascent_trigger_example1',
            r'ascent_binning_example1'
        ]


@rfm.simple_test
class uenv_ascent_intro_cpp(rfm.RunOnlyRegressionTest):
    descr = "Build Ascent intro (C++)"
    maintainers = ['SSA']
    tags = {'uenv', 'production'}
    valid_systems = ['+uenv']
    valid_prog_environs = ['+uenv +ascent -cpe']
    sourcesdir = None
    ascent_v = variable(str, value='0.9.5')
    time_limit = '2m'
    build_dir = fixture(uenv_ascent_intro_cpp_build, scope='environment')
    exe = parameter([
        'ascent_first_light_example',
        #
        'ascent_scene_example1', 'ascent_scene_example2',
        'ascent_scene_example3', 'ascent_scene_example4',
        #
        'ascent_pipeline_example1',
        #
        'ascent_extract_example1', 'ascent_extract_example2',
        'ascent_extract_example3', 'ascent_extract_example4',
        #
        'ascent_query_example1',
        'ascent_trigger_example1',
        'ascent_binning_example1'
    ])

    @run_after('setup')
    def set_executable(self):
        ascent_dir = os.path.join(
            self.build_dir.stagedir,
            f'ascent-{self.ascent_v}/src/examples/tutorial/ascent_intro/cpp')
        self.executable = os.path.join(ascent_dir, self.exe)
        self.prerun_cmds = [f'ln -fs {self.executable} .']
        if self.exe == 'ascent_trigger_example1':
            self.prerun_cmds += [
                f'cp {ascent_dir}/../notebooks/entropy_trigger_actions.yaml .',
                f'cp {ascent_dir}/../notebooks/cycle_trigger_actions.yaml .',
            ]

        self.png = ascent_intro_cpp_d[self.exe]
        ref_dir = os.path.join(self.current_system.resourcesdir,
                               'ascent/reference/intro_cpp')

        if self.exe == 'ascent_extract_example4':
            self.postrun_cmds = [
                f'ln -s cinema_databases/out_extract_cinema_contour/0.0/'
                f'{self.png}']
        elif self.exe == 'ascent_binning_example1':
            # TODO: add pyyaml to uenv
            self.postrun_cmds += [
                # plot (1D,2D,3D) data from ascent_session.yaml
                f'# ln -s {ascent_dir}/plot_binning*.py .',
                f'# sed -i "s@yaml.load@yaml.safe_load@" plot_binning*.py',
                f'# pip install --user pyyaml',
                f'# python3 plot_binning_1d.py',
                f'# python3 plot_binning_2d.py',
                f'# python3 plot_binning_3d.py',
                f'touch binning.png'
            ]

        self.postrun_cmds += [f'file {self.png}',
                              f'diff -s {self.png} {ref_dir}/{self.png}']

    @sanity_function
    def validate_test(self):
        if self.exe in ['ascent_scene_example4',
                        'ascent_pipeline_example1',
                        'ascent_query_example1']:
            regex = 'PNG image data'
        elif self.exe in ['ascent_extract_example1',
                          'ascent_extract_example2',
                          'ascent_extract_example3']:
            regex = 'Hierarchical Data Format'
        else:
            regex = f'{self.png} are identical'

        return sn.assert_found(regex, self.stdout)
# }}}


# {{{ uenv_ascent_doublegyre_python
@rfm.simple_test
class uenv_ascent_doublegyre_python(rfm.RunOnlyRegressionTest):
    descr = "Run Ascent test: DoubleGyre (Python)"
    maintainers = ['SSA']
    tags = {'uenv', 'production'}
    valid_systems = ['+uenv']
    valid_prog_environs = ['+uenv +ascent -cpe']
    sourcesdir = None
    png1 = 'velocity_magnitude.00100.png'
    png2 = 'vorticity_magnitude.00100.png'
    png3 = 'Velocity.100.png'
    png4 = 'Vy-iso-contours.100.png'
    root = 'mesh.cycle_000100.root'
    time_limit = '2m'

    @run_before('run')
    def set_code(self):
        src = os.path.join(self.current_system.resourcesdir,
                           f'github/InSitu-Vis-Tutorial/main.zip')
        self.prerun_cmds += [f'ls -l {src}', f'unzip -q {src}']

    @run_before('run')
    def set_run(self):
        self.num_tasks = 1
        self.num_tasks_per_node = self.num_tasks
        self.executable = 'python'
        self.rundir = 'InSitu-Vis-Tutorial-main/Examples/DoubleGyre/Python'
        self.serfile = 'double_gyre_ascent.py'
        self.prerun_cmds += [f'ln -s {self.rundir}/save_images_actions.yaml .']
        self.executable_opts = [f'{self.rundir}/{self.serfile}']
        ref_dir = os.path.join(self.current_system.resourcesdir,
                               'ascent/reference/doublegyre_python')
        self.postrun_cmds = [
            f'file datasets/{self.root}',
            f'diff -s datasets/{self.png1} {ref_dir}/{self.png1}',
            f'diff -s datasets/{self.png2} {ref_dir}/{self.png2}',
            f'diff -s {self.png3} {ref_dir}/{self.png3}',
            f'diff -s {self.png4} {ref_dir}/{self.png4}'
        ]

    @sanity_function
    def validate_test(self):
        assert_list = []
        regexes = [
            f'DoubleGyre Mesh verify success',
            f'{self.root}: Hierarchical Data Format',
            f'{self.png1} are identical',
            f'{self.png2} are identical',
            f'{self.png3} are identical',
            f'{self.png4} are identical',
        ]
        for regex in regexes:
            assert_list.append(
                sn.assert_found(regex, self.stdout, msg=f'found "{regex}"'))

        return sn.all(assert_list)
# }}}


# {{{ uenv_ascent_doublegyre_cpp
@rfm.simple_test
class uenv_ascent_doublegyre_cpp(rfm.RegressionTest):
    descr = "Build and Run Ascent test: DoubleGyre (C++)"
    maintainers = ['SSA']
    tags = {'uenv', 'production'}
    valid_systems = ['+uenv']
    valid_prog_environs = ['+uenv +ascent -cpe']
    sourcesdir = None
    srcdir = 'InSitu-Vis-Tutorial-main/Examples/DoubleGyre/C++'
    png1 = 'velocity_magnitude.00100.png'
    png2 = 'vorticity_magnitude.00100.png'
    build_system = 'CMake'
    build_locally = False
    time_limit = '2m'

    @run_before('compile')
    def set_build(self):
        src = os.path.join(self.current_system.resourcesdir,
                           f'github/InSitu-Vis-Tutorial/main.zip')
        self.build_system.max_concurrency = 5
        self.build_system.srcdir = (
                'InSitu-Vis-Tutorial-main/Examples/DoubleGyre/C++')
        self.prebuild_cmds += [f'ls -l {src}', f'unzip -q {src}']
        self.build_system.config_opts = [
            f'-S {self.srcdir}',
            f'-DCMAKE_BUILD_TYPE=Debug',  # Release
            f'-DINSITU=Ascent',
            f'-DAscent_DIR=$(find /user-tools/ -name ascent |grep ascent- |grep cmake)',  # noqa: E501
            f'-DCMAKE_CUDA_ARCHITECTURES='
            f'{self.current_partition.devices[0].arch[-2:]}',
            f'-DCMAKE_CUDA_HOST_COMPILER=mpicxx'
        ]

    @run_before('run')
    def set_run(self):
        self.num_tasks = 1
        self.num_tasks_per_node = self.num_tasks
        self.executable = './bin/double_gyre_ascent'
        self.executable_opts = ['128', '64', '100', '10', '2>&1']
        ref_dir = os.path.join(self.current_system.resourcesdir,
                               'ascent/reference/doublegyre_cpp')
        self.prerun_cmds += [
            f'ln -s {self.srcdir}/save_images_actions.yaml .']
        self.postrun_cmds = [
            f'diff -s datasets/{self.png1} {ref_dir}/{self.png1}',
            f'diff -s datasets/{self.png2} {ref_dir}/{self.png2}',
        ]

    @sanity_function
    def validate_test(self):
        regexes = [
            f'DoubleGyre Mesh verify success',
            f'{self.png1} are identical',
            f'{self.png2} are identical',
        ]
        assert_list = []
        for regex in regexes:
            assert_list.append(
                sn.assert_found(regex, self.stdout, msg=f'found "{regex}"'))

        return sn.all(assert_list)
# }}}


# {{{ uenv_ascent_heatdiffusion_python
@rfm.simple_test
class uenv_ascent_heatdiffusion_python(rfm.RunOnlyRegressionTest):
    descr = "Run Ascent test: HeatDiffusion (Python, serial and parallel)"
    maintainers = ['SSA']
    tags = {'uenv', 'production'}
    valid_systems = ['+uenv']
    valid_prog_environs = ['+uenv +ascent -cpe']
    sourcesdir = None
    par_png1 = 'temperature-par.1000.png'
    ser_png1 = 'temperature-ser.0500.png'
    ser_png2 = 'Temperature-iso-contours.0500.png'
    # TODO: _root = 'Jmesh.cycle_000500.root'
    time_limit = '2m'

    @run_before('run')
    def set_code(self):
        src = os.path.join(self.current_system.resourcesdir,
                           f'github/InSitu-Vis-Tutorial/main.zip')
        self.prerun_cmds += [f'ls -l {src}', f'unzip -q {src}']

    @run_before('run')
    def set_run(self):
        self.num_tasks = 4
        self.num_tasks_per_node = self.num_tasks
        self.executable = 'python'
        self.rundir = 'InSitu-Vis-Tutorial-main/Examples/HeatDiffusion/Python'
        self.parfile = 'heat_diffusion_insitu_parallel_Ascent.py'
        self.serfile = 'heat_diffusion_insitu_Ascent.py'
        self.executable_opts = [
            f'{self.rundir}/{self.parfile}', '--mesh=uniform',
            '--res=64', '--timesteps 1000', '--frequency 100', '--verbose'
        ]
        ref_dir = os.path.join(self.current_system.resourcesdir,
                               'ascent/reference/heatdiffusion_py')
        self.postrun_cmds = [
            f'{self.executable} {self.rundir}/{self.serfile} &> ser.rpt',
            f'diff -s {self.par_png1} {ref_dir}/{self.par_png1}',
            f'diff -s {self.ser_png1} {ref_dir}/{self.ser_png1}',
            f'diff -s {self.ser_png2} {ref_dir}/{self.ser_png2}',
        ]

    @sanity_function
    def validate_test(self):
        assert_list = []
        regex = r'^Rank\s+(\d+)'
        num_tasks_found = sn.count(sn.extractall(regex, self.stdout, 1, int))
        assert_list.append(sn.assert_eq(num_tasks_found, self.num_tasks))

        regexes = [
            f'{self.par_png1} are identical',
            f'{self.ser_png1} are identical',
            f'{self.ser_png2} are identical',
        ]
        for regex in regexes:
            assert_list.append(
                sn.assert_found(regex, self.stdout, msg=f'found "{regex}"'))

        return sn.all(assert_list)
# }}}


# {{{ uenv_ascent_heatdiffusion_cpp
@rfm.simple_test
class uenv_ascent_heatdiffusion_cpp(rfm.RegressionTest):
    descr = "Build and Run Ascent test: HeatDiffusion (C++)"
    maintainers = ['SSA']
    tags = {'uenv', 'production'}
    valid_systems = ['+uenv']
    valid_prog_environs = ['+uenv +ascent -cpe']
    sourcesdir = None
    srcdir = 'InSitu-Vis-Tutorial-main/Examples/HeatDiffusion/C++'
    png1 = 'ascent_temperature_isolines-010000.png'
    build_system = 'CMake'
    build_locally = False
    time_limit = '2m'

    @run_before('compile')
    def set_build(self):
        src = os.path.join(self.current_system.resourcesdir,
                           f'github/InSitu-Vis-Tutorial/main.zip')
        self.build_system.max_concurrency = 5
        self.prebuild_cmds += [f'ls -l {src}', f'unzip -q {src}']
        self.build_system.config_opts = [
            f'-S {self.srcdir}',
            f'-DCMAKE_BUILD_TYPE=Debug',  # Release
            f'-DINSITU=Ascent',
            f'-DAscent_DIR=$(find /user-tools/ -name ascent |grep ascent- |grep cmake)',  # noqa: E501
            f'-DCMAKE_CUDA_ARCHITECTURES='
            f'{self.current_partition.devices[0].arch[-2:]}',
            f'-DCMAKE_CUDA_HOST_COMPILER=mpicxx'
        ]

    @run_before('run')
    def set_run(self):
        self.num_tasks = 4
        self.num_tasks_per_node = self.num_tasks
        self.executable = './bin/heat_diffusion'
        self.executable_opts = ['--mesh=uniform', '--res=64']
        ref_dir = os.path.join(self.current_system.resourcesdir,
                               'ascent/reference/heatdiffusion_cpp')
        self.postrun_cmds = [
            f'cat Heat.bov',
            f'diff -s datasets/{self.png1} {ref_dir}/{self.png1}',
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
            f'-DAscent_DIR=$(find /user-tools/ -name ascent |grep ascent- |grep cmake)',  # noqa: E501
            f'-DCMAKE_CUDA_ARCHITECTURES='
            f'{self.current_partition.devices[0].arch[-2:]}',
            f'-DCMAKE_CUDA_HOST_COMPILER=mpicxx'
    ]

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
            f'-DAscent_DIR=$(find /user-tools/ -name ascent |grep ascent- |grep cmake)',  # noqa: E501
            f'-DCMAKE_CUDA_ARCHITECTURES='
            f'{self.current_partition.devices[0].arch[-2:]}',
            f'-DCMAKE_CUDA_HOST_COMPILER=mpicxx'
        ]

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
        # ref_dir = os.path.join(self.current_system.resourcesdir,
        #                        'ascent/reference/kripke')
        self.postrun_cmds = [
            f'file {self.png1}',
            # .png may vary between identical jobs, can't use 'diff -s' here
        ]

    @sanity_function
    def validate_test(self):
        regexes = [
            r'blueprint verify succeeded',
            r'iter 9: particle count=',
            r'PNG image data, 1024 x 1024',
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
    descr = "Build and Run Ascent test: CloverLeaf3D (F90)"
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
            r'This test is considered NOT PASSED',  # ok as long as .png exist
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
