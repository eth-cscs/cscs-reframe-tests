# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm


class CudaVisibleDevicesAllMixin(rfm.RegressionTestPlugin):
    @run_after('setup')
    def set_cuda_visible_devices(self):
        curr_part = self.current_partition
        if curr_part.select_devices('gpu'):
            gpu_count = curr_part.select_devices('gpu')[0].num_devices
            cuda_visible_devices = ','.join(f'{i}' for i in range(gpu_count))
            self.env_vars['CUDA_VISIBLE_DEVICES'] = cuda_visible_devices
            self.num_gpus_per_node = gpu_count
