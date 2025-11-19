# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm


class UenvSlurmMpiOptionsMixin(rfm.RegressionMixin):
    """
    Set slurm --mpi flags based on uenv features.

    For uenvs that announce that they use OpenMPI, --mpi=pmix needs to be used.
    For uenvs that advertise Cray MPICH, or uenvs that don't specify, we assume
    that --mpi=cray_shasta is required.

    Additionally for OpenMPI we silence some warnings.
    """

    @run_after('setup')
    def set_uenv_slurm_mpi_options(self):
        features = self.current_environ.features
        if "openmpi" in features:
            self.job.launcher.options += ['--mpi=pmix']

            # Disable MCA components to avoid warnings
            self.env_vars.update(
                {
                    'PMIX_MCA_psec': 'native',
                    'PMIX_MCA_gds': '^shmem2'
                }
            )
        elif "cray-mpich" in features:
            self.job.launcher.options += ['--mpi=cray_shasta']
        else:
            # Assume cray-mpich is used if nothing is specified.
            self.job.launcher.options += ['--mpi=cray_shasta']
