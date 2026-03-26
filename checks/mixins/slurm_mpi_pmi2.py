# Copyright 2016-2026 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm


class SlurmMpiPmi2Mixin(rfm.RegressionTestPlugin):
    """
    Set slurm --mpi=pmi2 flag for jobs that require PMI-2.
    """

    @run_after('setup')
    def set_slurm_mpi_pmix(self):
        self.job.launcher.options += ['--mpi=pmi2']
