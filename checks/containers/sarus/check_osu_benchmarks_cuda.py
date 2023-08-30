# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))

from sarus_extra_launcher_options import SarusExtraLauncherOptionsMixin  # noqa: E402


class SarusOSUCudaCheck(SarusExtraLauncherOptionsMixin,
                        rfm.RunOnlyRegressionTest):
    image = 'quay.io/ethcscs/osu-mb:5.9-mpich3.4.1-cuda11.7.0-ubuntu22.04'
    valid_systems = ['+sarus +nvgpu']
    valid_prog_environs = ['builtin']
    container_platform = 'Sarus'
    sourcesdir = None
    num_tasks = 2
    num_tasks_per_node = 1
    num_gpus_per_node = 1
    env_vars = {
        # Enable GPU support for cray-mpich
        'MPICH_GPU_SUPPORT_ENABLED': 1,

        # Use only the first CUDA GPU
        'CUDA_VISIBLE_DEVICES': 0,
    }

    @run_after('setup')
    def set_prerun_cmds(self):
        self.prerun_cmds += ['sarus --version', 'unset XDG_RUNTIME_DIR']

    @run_after('setup')
    def setup_container_platform(self):
        self.container_platform.image = self.image
        self.container_platform.command = (
            # The libmpi_gtl_cuda.so is needed by cray-mpich injected by
            # the Sarus mpi hook
            f"bash -c 'LD_PRELOAD=/usr/lib/libmpi_gtl_cuda.so "
            f"/usr/local/libexec/osu-micro-benchmarks/mpi/pt2pt/"
            f"{self.executable} -d cuda D D'"
        )
        self.container_platform.with_mpi = True

    @sanity_function
    def assert_sanity(self):
        # Only check for the last entry in the latency/bandwidth tests,
        # if exists program completed successfully
        return sn.assert_found(r'4194304', self.stdout)


@rfm.simple_test
class SarusOSUCudaBandwidthCheck(SarusOSUCudaCheck):
    executable = 'osu_bw'
    reference = {
        '*': {
            'bandwidth_256': (200., -0.15, None, 'MB/s'),
            'bandwidth_4M':  (24000., -0.15, None, 'MB/s')
        },
    }

    @run_before('performance')
    def set_perf(self):
        # For performance we only evaluate two points of output
        self.perf_patterns = {
            'bandwidth_256':
                sn.extractsingle(r'256\s+(?P<bandwidth_256>\S+)', self.stdout,
                                 'bandwidth_256', float),
            'bandwidth_4M':
                sn.extractsingle(r'4194304\s+(?P<bandwidth_4M>\S+)',
                                 self.stdout, 'bandwidth_4M', float)
        }


@rfm.simple_test
class SarusOSUCudaLatencyCheck(SarusOSUCudaCheck):
    executable = 'osu_latency'
    reference = {
        '*': {
            'latency_256': (3.75, None, 0.15, 'us'),
            'latency_4M':  (180., None, 0.15, 'us')
        },
    }

    @run_before('performance')
    def set_perf(self):
        self.perf_patterns = {
            'latency_256': sn.extractsingle(r'256\s+(?P<latency_256>\S+)',
                                            self.stdout, 'latency_256', float),
            'latency_4M': sn.extractsingle(r'4194304\s+(?P<latency_4M>\S+)',
                                           self.stdout, 'latency_4M', float)
        }
