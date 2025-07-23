# Copyright 2025 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
import os

import reframe as rfm
import reframe.utility.sanity as sn
import uenv


@rfm.simple_test
class DummySPH_Uenv_Ascent_Single(rfm.RegressionTest):
    descr = "Build and Run Ascent tests with DummySPH"
    valid_systems = ['+remote']
    valid_prog_environs = ['+uenv +cuda']
    ascentdir = variable(
        str,
        value=('/capstor/store/cscs/cscs/csstaff/jfavre/ascent/0.9.4/lib/'
               'cmake/ascent')
    )
    # TODO: deploy a uenv with ascent,
    #       until then using (local install + prgenv-gnu/24.11:v2)
    sourcesdir = 'https://github.com/jfavre/DummySPH.git'
    tag = variable(str, value='92a06a1')  # v0.1
    aos = parameter(['OFF'])  # STRIDED_SCALARS:
    # ON = struct tipsy (AOS) / OFF = std::vector (SOA)
    fp64 = parameter(['OFF', 'ON'])  # OFF=<float>, ON=<double>
    input_dir = variable(
        str, value='/capstor/store/cscs/cscs/csstaff/jfavre/ascent')
    tipsy = parameter(['OFF', 'ON'])
    tipsy_file = variable(str, value='hr8799_bol_bd1.017300')
    # https://jfrog.svc.cscs.ch/artifactory/cscs-reframe-tests/dummysph/
    # -> hr8799_bol_bd1.017300.gz (1.06G) will take ~33 s (39.0MB/s)
    h5part = parameter(['OFF', 'ON'])
    h5part_file = variable(str, value='dump_wind-shock.h5')
    test = parameter(['rendering', 'thresholding', 'compositing',
                      'histsampling', 'binning'])
    datadump = variable(str, value='OFF')
    num_gpus = variable(int, value=4)
    build_system = 'CMake'
    build_locally = False
    executable = './src/bin/dummysph_ascent'
    time_limit = '4m'

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

    @run_before('compile')
    def set_build_system(self):
        self.build_system.max_concurrency = 6
        self.build_system.srcdir = 'src'
        self.prebuild_cmds += [
            f"git checkout {self.tag}",
            f"git switch -c {self.tag}",
            f"touch _{self.aos}_{self.fp64}_{self.tipsy}_{self.h5part}",
            f"cd src"
        ]
        self.build_system.config_opts = [
            # '-DCMAKE_C_COMPILER=mpicc',
            # '-DCMAKE_CXX_COMPILER=mpicxx',
            '-DCMAKE_BUILD_TYPE=Debug',  # Release
            f'-DSTRIDED_SCALARS={self.aos}',
            f'-DSPH_DOUBLE={self.fp64}',
            f'-DCAN_LOAD_TIPSY={self.tipsy}',
            f'-DCAN_LOAD_H5Part={self.h5part}',
            # f'-DCAN_DATADUMP={self.datadump}',
            '-DINSITU=Ascent',
            f'-DAscent_DIR={self.ascentdir}',
        ]
        if uenv.uarch(self.current_partition) == 'gh200':
            cmake_arch = '-DCMAKE_CUDA_ARCHITECTURES=90'
            self.build_system.config_opts.append(cmake_arch)

    @run_before('run')
    def set_executable_tests(self):
        self.job.options = [f'--nodes=1']
        self.rpt = 'rpt'
        infile = ''
        if self.h5part == "ON":
            infile = f'--h5part {self.input_dir}/{self.h5part_file}'
        elif self.tipsy == "ON":
            infile = f'--h5part {self.input_dir}/{self.h5part_file}'

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
