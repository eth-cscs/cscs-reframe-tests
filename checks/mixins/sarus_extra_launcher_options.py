# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm


class SarusExtraLauncherOptionsMixin(rfm.RegressionMixin):
    @run_before('run')
    def set_launcher_options(self):
        if self.current_system.name in {'hohgant'}:
            self.job.launcher.options = ['--mpi=pmi2']
