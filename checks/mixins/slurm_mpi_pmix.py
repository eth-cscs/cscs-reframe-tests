# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm


class SlurmMpiPmixMixin(rfm.RegressionMixin):
    """
    Set slurm --mpi flags for containers that require PMIx.

    Containers that use OpenMPI require the --mpi=pmix flag.

    Additionally silence some warnings triggered by OpenMPI.
    """

    @run_after('setup')
    def set_slurm_mpi_pmix(self):
        self.job.launcher.options += ['--mpi=pmix']

        # Disable MCA components to avoid warnings
        self.env_vars.update(
            {
                'PMIX_MCA_psec': 'native',
                'PMIX_MCA_gds': '^shmem2'
            }
        )
