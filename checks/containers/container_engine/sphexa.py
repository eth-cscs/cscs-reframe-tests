# Copyright 2026 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import sys
import pathlib
import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.parent / 'config' / 'utilities'))

from uenv import uarch
from container_engine import ContainerEngineMixin  # noqa: E402
from slurm_mpi_pmi2 import SlurmMpiPmi2Mixin


@rfm.simple_test
class SphExa_CE(rfm.RunOnlyRegressionTest, ContainerEngineMixin, SlurmMpiPmi2Mixin):
    descr = 'SPH-EXA for CE'
    valid_systems = ['+ce +nvgpu']
    valid_prog_environs = ['builtin']
    maintainers = ['VCUE']
    tags = {'ce_dev'}

    container_image = 'jfrog.svc.cscs.ch/ghcr/sarus-suite/containerfiles-ci/sphexa:0.95-mpich4.3.2-ofi1.22-cuda12.8.1'
    sph_infile = parameter(['/sphexa/50c.h5'])
    num_gpus = parameter([8])
    sph_testcase = parameter(['evrard'])
    sph_steps = parameter([10])
    sph_size = parameter([200])
    ntasks_per_node = variable(int, value=4)
    time_limit = '3m'
    regex_elapsed = (
        r'Total execution time of (?P<steps>\d+) iterations of \S+ '
        r'up to t = \S+: (?P<sec>\S+)s$')

    @run_before('run')
    def set_executable(self):
        self.executable = f'/sphexa/wrapper.sh sphexa-cuda'
        self.executable_opts = [
            f'--init {self.sph_testcase}',
            f'--glass {self.sph_infile}',
            f'-n {self.sph_size}',
            f'-s {self.sph_steps}',
        ]
        self.num_tasks = self.num_gpus
        self.num_tasks_per_node = self.ntasks_per_node
        self.num_cpus_per_task = 30
        # self.skip_if_no_procinfo()
        # self.num_cpus_per_task = (
        #     self.current_partition.processor.info["num_cpus"]
        #     // self.current_partition.processor.info["num_cpus_per_core"]
        #     // self.num_tasks_per_node
        # )
        self.job.options = [
            f'--nodes={int(self.num_gpus / self.num_tasks_per_node)}'
            if self.num_tasks > self.num_tasks_per_node else '--nodes=1',
        ]
        self.env_vars = {'OMP_NUM_THREADS': '$SLURM_CPUS_PER_TASK'}

    @sanity_function
    def assert_results(self):
        """
# Total execution time of 2 iterations of evrard up to t = 0.000231: 13.7324s
        """
        s1 = sn.assert_found(self.regex_elapsed, self.stdout)
        return sn.all([s1])

    @performance_function('s')
    def elapsed(self):
        return sn.extractsingle(self.regex_elapsed, self.stdout, 'sec', float)

    @performance_function('s')
    def sec_per_step(self):
        sec = sn.extractsingle(self.regex_elapsed, self.stdout, 'sec', float)
        steps = sn.extractsingle(self.regex_elapsed, self.stdout, 'steps',
                                 float)
        return sec / steps

    _ref_sec_per_step = {
        'evrard': {
            'mi200': 5.6,
            'mi300': 5.1,
            'gh200': 0.9,
            'a100':  1.9},
    }

    @run_before('performance')
    def set_perf_reference(self):
        self.uarch = uarch(self.current_partition)
        ref_sec_per_step = self._ref_sec_per_step.get(
            self.sph_testcase, {}).get(self.uarch)
        if ref_sec_per_step is not None:
            self.reference = {
                self.current_partition.fullname: {
                    'sec_per_step': (ref_sec_per_step, None, 0.15, 's')
                }
            }


@rfm.simple_test
class SphExa_Skybox(SphExa_CE):
    descr = 'SPH-EXA for CE/Skybox'
    tags = {'ce_dev', 'skybox'}
    spank_option = 'edf'
    container_env_key_values = {
        'devices': ["alps.cscs/cxi=all", "nvidia.com/gpu=all", "/dev/gdrdrv"]
    }