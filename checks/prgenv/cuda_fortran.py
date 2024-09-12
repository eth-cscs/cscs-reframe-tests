# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


class CudaFortranBase(rfm.RegressionTest):
    build_locally = False
    build_system = 'SingleSource'
    sourcesdir = 'src/cuda-fortran'
    sourcepath = 'vecAdd_cuda.cuf'
    num_gpus_per_node = 1
    executable = 'vecAdd'

    @sanity_function
    def assert_correct_result(self):
        result = sn.extractsingle(r'final result:\s+(?P<result>\d+\.?\d*)',
                                  self.stdout, 'result', float)
        return sn.assert_reference(result, 1., -1e-5, 1e-5)


@rfm.simple_test
class CPE_CudaFortran(CudaFortranBase):
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['+cuda-fortran -uenv']
    tags = {'production', 'craype'}


@rfm.simple_test
class UENV_CudaFortran(CudaFortranBase):
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['+cuda-fortran +uenv']
    tags = {'production', 'uenv'}
