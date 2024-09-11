# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class H5PyTest(rfm.RunOnlyRegressionTest):
    descr = 'Test that h5py can write a HDF5 file in parallel'
    valid_systems = ['+remote']
    valid_prog_environs = ['+h5py +mpi +uenv']
    num_tasks = 4
    executable = 'python'
    executable_opts = ['h5py_mpi.py']  # from src/
    prerun_cmds = ['python --version']
    postrun_cmds = ['h5dump parallel_test.hdf5']
    tags = {'health', 'production', 'uenv'}

    @sanity_function
    def assert_success(self):
        expected_dataset = ', '.join(str(i) for i in range(self.num_tasks))
        return sn.assert_found(
            rf'.*DATA\s+{{\s+\(0\): {expected_dataset}\s*}}',
            self.stdout
        )
