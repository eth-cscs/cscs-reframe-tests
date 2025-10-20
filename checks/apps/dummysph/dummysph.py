# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
import uenv


@rfm.simple_test
class dummysph_uenv_ascent_single(rfm.RegressionTest):
    descr = "Build and Run Ascent tests with DummySPH"
    maintainers = ['SSA']
    valid_systems = ['+uenv']
    valid_prog_environs = ['+ascent +uenv -cpe']
    sourcesdir = 'https://github.com/jfavre/DummySPH.git'
    commit = variable(str, value='92a06a1')  # v0.1
    #
    aos = parameter(['OFF'])  # ON=struct tipsy (AOS) / OFF = std::vector (SOA)
    fp64 = parameter(['OFF', 'ON'])  # OFF=<float>, ON=<double>
    tipsy = parameter(['OFF', 'ON'])
    h5part = parameter(['OFF', 'ON'])
    test = parameter(['rendering', 'thresholding', 'compositing', 'binning',
                      'histsampling'])

    # --- input data:
    # In https://jfrog.svc.cscs.ch/artifactory/cscs-reframe-tests/dummysph/
    # but loading ~1G (hr8799_bol_bd1.017300.gz) will take ~33 s (40 MB/s)
    # -> using CSCS resourcesdir instead
    # -> or /capstor/store/cscs/cscs/csstaff/jfavre/ascent
    tipsy_file = variable(str, value='hr8799_bol_bd1.017300')
    h5part_file = variable(str, value='dump_wind-shock.h5')

    datadump = variable(str, value='OFF')
    build_system = 'CMake'
    build_locally = False
    executable = './src/bin/dummysph_ascent'
    time_limit = '4m'

    # {{{ skip unsupported tests
    @run_after('init')
    def skip_test(self):
        """
        Unsupported:
STRIDED_SCALARS=ON  SPH_DOUBLE=ON  CAN_LOAD_TIPSY=ON  CAN_LOAD_H5Part=ON
STRIDED_SCALARS=ON  SPH_DOUBLE=ON  CAN_LOAD_TIPSY=ON  CAN_LOAD_H5Part=OFF
STRIDED_SCALARS=ON  SPH_DOUBLE=ON  CAN_LOAD_TIPSY=OFF CAN_LOAD_H5Part=ON
STRIDED_SCALARS=ON  SPH_DOUBLE=OFF CAN_LOAD_TIPSY=ON  CAN_LOAD_H5Part=ON
STRIDED_SCALARS=ON  SPH_DOUBLE=OFF CAN_LOAD_TIPSY=OFF CAN_LOAD_H5Part=ON
STRIDED_SCALARS=OFF SPH_DOUBLE=ON  CAN_LOAD_TIPSY=ON  CAN_LOAD_H5Part=ON
STRIDED_SCALARS=OFF SPH_DOUBLE=ON  CAN_LOAD_TIPSY=ON  CAN_LOAD_H5Part=OFF
STRIDED_SCALARS=OFF SPH_DOUBLE=OFF CAN_LOAD_TIPSY=ON  CAN_LOAD_H5Part=ON
STRIDED_SCALARS=OFF SPH_DOUBLE=OFF CAN_LOAD_TIPSY=ON  CAN_LOAD_H5Part=OFF
        """
        skip = (
            (self.tipsy == "ON" and self.h5part == "ON") or
            (self.aos == "ON" and self.h5part == "ON") or
            (self.aos == "OFF" and self.tipsy == "ON") or
            (self.fp64 == "ON" and self.tipsy == "ON")
        )
        self.skip_if(skip, 'skipping unsupported test')
        # manage expected failures:
        skip = (
            # "Field type unsupported for conversion to blueprint":
            (self.aos == "OFF"
             and (self.fp64 == "OFF" or self.fp64 == "ON")
             # intentionally redundant
             and self.tipsy == "OFF"
             and self.h5part == "OFF"
             and self.test == "compositing") or
            # vtkm: Cast failed: vtkm::cont::ArrayHandle":
            (self.aos == "OFF"
             and self.fp64 == "OFF"
             and self.tipsy == "OFF"
             and (self.h5part == "OFF" or self.h5part == "ON")
             and self.test == "histsampling")
        )
        self.skip_if(skip, 'skipping expected failures')
    # }}}

    @run_before('compile')
    def set_input_dir(self):
        self.input_dir = os.path.join(self.current_system.resourcesdir,
                                      'ascent', 'inputs')

    @run_before('compile')
    def set_build_system(self):
        self.build_system.max_concurrency = 6
        self.build_system.srcdir = 'src'
        self.prebuild_cmds += [
            # https://github.com/jfavre/DummySPH/releases/
            f"git checkout {self.commit}",
            f"git switch -c {self.commit}",
            f"touch _{self.aos}_{self.fp64}_{self.tipsy}_{self.h5part}",
            f"cd src",
            # temporary workaround until new release of DummySPH:
            f'cp {self.input_dir}/../CMakeLists.txt .',
            f'sed -i "s-CAMP_HAVE_CUDA)-CAMP_HAVE_CUDA) || '
            f'defined (ASCENT_CUDA_ENABLED)-" cuda_helpers.cpp',
        ]
        self.build_system.config_opts = [
            # f'-DCAN_DATADUMP={self.datadump}',
            # '-DCMAKE_C_COMPILER=mpicc',
            # '-DCMAKE_CXX_COMPILER=mpicxx',
            f'-DCMAKE_BUILD_TYPE=Debug',  # Release
            f'-DCMAKE_CUDA_HOST_COMPILER=mpicxx',
            f'-DSTRIDED_SCALARS={self.aos}',
            f'-DSPH_DOUBLE={self.fp64}',
            f'-DCAN_LOAD_TIPSY={self.tipsy}',
            f'-DCAN_LOAD_H5Part={self.h5part}',
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
    def set_executable_tests(self):
        self.job.options = [f'--nodes=1']
        infile = ''
        if self.h5part == "ON":
            infile = f'--h5part {self.input_dir}/{self.h5part_file}'
        elif self.tipsy == "ON":
            infile = f'--tipsy {self.input_dir}/{self.tipsy_file}'

        if self.test == 'binning':
            self.executable_opts = [f'--{self.test}', 'rho', infile, '2>&1']
        else:
            self.executable_opts = [f'--{self.test}', 'out', infile, '2>&1']

    @sanity_function
    def validate_test(self):
        regexes = [
            'Could not find appropriate cast for array in CastAndCall',
            'Field type unsupported for conversion to blueprint',
            'Execution failed with vtkm: Cast failed: vtkm::cont::ArrayHandle',
            'Segmentation fault (core dumped)',
            'Field: dataset does not contain field',
        ]
        assert_list = []
        for regex in regexes:
            assert_list.append(
                sn.assert_not_found(
                    regex, self.stdout, msg=f'found "{regex}"'))

        return sn.all(assert_list)
