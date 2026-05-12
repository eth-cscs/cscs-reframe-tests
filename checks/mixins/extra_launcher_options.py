# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm


class ExtraLauncherOptionsMixin(rfm.RegressionTestPlugin):
    @run_before('run')
    def set_launcher_options(self):
        self.job.launcher.options += (
            # get launcher_options from config if it exists else ''
            self.current_environ.extras.get('launcher_options', [])
        )

