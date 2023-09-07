# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm


class UenvSetup(rfm.RegressionMixin):
    @run_after('setup')
    def set_build_locally(self):
        curr_part = self.current_partition
        if 'uenv' in curr_part.features:
            self.build_locally = False
