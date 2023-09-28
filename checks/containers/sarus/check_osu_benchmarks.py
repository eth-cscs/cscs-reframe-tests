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


class BaseCheck(SarusExtraLauncherOptionsMixin, rfm.RunOnlyRegressionTest):
    valid_systems = ['+sarus']
    valid_prog_environs = ['builtin']
    container_platform = 'Sarus'
    sourcesdir = None
    num_tasks = 2
    num_tasks_per_node = 1
    num_gpus_per_node = 1

    @run_after('init')
    def set_descr(self):
        self.descr = f'{self.name} on {self.num_tasks} nodes(s)'

    @run_after('setup')
    def set_prerun_cmds(self):
        self.prerun_cmds += ['sarus --version', 'unset XDG_RUNTIME_DIR']

    @sanity_function
    def assert_sanity(self):
        # Only check for the last entry in the latency test,
        # if exists program completed successfully
        return sn.assert_found(r'4194304', self.stdout)


# note: the test images with Intel MPI are not used because we don't want
# to risk to run into licensing issues by publishing the images on Docker Hub
@rfm.simple_test
class SarusOSULatency(BaseCheck):
    sarus_image = parameter([f'ethcscs/osu-mb:5.3.2-{mpi_impl}'
                             for mpi_impl in ['mpich3.1.4', 'mvapich2.2']])
    reference = {
        'dom': {
            'latency_256': (1.15, None, 0.50, 'us'),
            'latency_4M':  (432., None, 0.15, 'us')
        },
        'daint': {
            'latency_256': (1.15, None, 0.50, 'us'),
            'latency_4M':  (432., None, 0.15, 'us')
        },
        '*': {
            'latency_256': (2.3, None, 0.50, 'us'),
            'latency_4M':  (180., None, 0.15, 'us')
        },
    }

    @run_after('setup')
    def setup_container_platform(self):
        self.container_platform.image = self.sarus_image
        self.container_platform.command = (
            '/usr/local/libexec/osu-micro-benchmarks/mpi/pt2pt/osu_latency'
        )
        self.container_platform.with_mpi = True

    @run_before('performance')
    def set_perf(self):
        # Check latency at two points, msg size 256 and the largest msg 4194304
        self.perf_patterns = {
            'latency_256': sn.extractsingle(r'256\s+(?P<latency_256>\S+)',
                                            self.stdout, 'latency_256', float),
            'latency_4M': sn.extractsingle(r'4194304\s+(?P<latency_4M>\S+)',
                                           self.stdout, 'latency_4M', float)
        }


@rfm.simple_test
class SarusOSULatencyWithSshLauncher(BaseCheck):
    sarus_image = parameter(
        [f'ethcscs/osu-mb:5.3.2-{mpi_impl}'
         for mpi_impl in ['mpich3.1.4', 'mvapich2.2ch3sock']]
    )

    @run_after('setup')
    def generate_ssh_keys(self):
        # Ensure ssh keys are generated before running the test
        self.prerun_cmds += ['sarus ssh-keygen']

    @run_after('setup')
    def setup_container_platform(self):
        self.container_platform.image = self.sarus_image
        self.container_platform.options = [
            '--mount=src=$SCRATCH,dst=$SCRATCH,type=bind',
            '--ssh'
        ]
        self.container_platform.command = (
            "bash -c 'syncfile=$SCRATCH/syncfile-$SLURM_JOB_ID;"
            "if [ $SLURM_PROCID = 0 ]; then"
            "   mpirun -launcher=ssh /usr/local/libexec/osu-micro-benchmarks/mpi/pt2pt/osu_latency;"  # noqa: E501
            "   touch $syncfile;"
            "else"
            "   while [ ! -e $syncfile ]; do"
            "      sleep 1;"
            "   done;"
            "   rm $syncfile;"
            "fi'"
        )


@rfm.simple_test
class SarusOSULatencyWithPMI2(BaseCheck):
    sarus_image = parameter(
        [f'ethcscs/osu-mb:5.3.2-{mpi_impl}'
         for mpi_impl in ['mpich3.1.4', 'mvapich2.2ch3sock']]
    )

    @run_after('setup')
    def set_launcher_options(self):
        self.job.launcher.options = ['--mpi=pmi2']

    @run_after('setup')
    def setup_container_platform(self):
        self.container_platform.image = self.sarus_image
        self.container_platform.command = (
            '/usr/local/libexec/osu-micro-benchmarks/mpi/pt2pt/osu_latency'
        )


@rfm.simple_test
class SarusOSUBandwidth(BaseCheck):
    sarus_image = parameter([f'ethcscs/osu-mb:5.3.2-{mpi_impl}'
                             for mpi_impl in ['mpich3.1.4', 'mvapich2.2']])
    reference = {
        'dom': {
            'bandwidth_256': (415., -0.20, None, 'MB/s'),
            'bandwidth_4M':  (9870., -0.20, None, 'MB/s')
        },
        'daint': {
            'bandwidth_256': (415., -0.50, None, 'MB/s'),
            'bandwidth_4M':  (9850., -0.20, None, 'MB/s')
        },
        '*': {
            'bandwidth_256': (600., -0.50, None, 'MB/s'),
            'bandwidth_4M':  (24000., -0.15, None, 'MB/s')
        },
    }

    @run_after('setup')
    def setup_container_platform(self):
        self.container_platform.image = self.sarus_image
        self.container_platform.command = (
            '/usr/local/libexec/osu-micro-benchmarks/mpi/pt2pt/osu_bw'
        )
        self.container_platform.with_mpi = True

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
