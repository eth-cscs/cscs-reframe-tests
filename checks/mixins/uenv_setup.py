# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm


class UenvSetup(rfm.RegressionMixin):
    @run_after('setup')
    def setup_uenv(self):
        pass
