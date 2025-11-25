# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn
import uenv


qe_references = {
    'Au surf': {
        'gh200': {'time_run': (50, None, 0.05, 's')},
        'mi300': {'time_run': (112, None, 0.05, 's')},
        'mi200': {'time_run': (78, None, 0.05, 's')},
    },
}


slurm_config = {
    'Au surf': {
        'gh200': {
            'nodes': 1,
            'ntasks-per-node': 4,
            'cpus-per-task': 72,
            'walltime': '0d0h20m0s',
            'gpu': True,
        },
        'mi200': {
            'nodes': 1,
            'ntasks-per-node': 8,
            'cpus-per-task': 8,
            'walltime': '0d0h20m0s',
            'gpu': True,
        },
        'mi300': {
            'nodes': 1,
            'ntasks-per-node': 12,
            'gpus-per-task': 1,
            'cpus-per-task': 8,
            'extra_job_options': ['--constraint=amdgpu_tpx'],
            'walltime': '0d0h20m0s',
            'gpu': True,
        },
        'zen2': {
            'nodes': 1,
            'ntasks-per-node': 16,
            'cpus-per-task': 8,
            'walltime': '0d0h20m0s',
            'gpu': False,
        },
    },
}


class QeSiriusCheckUENV(rfm.RunOnlyRegressionTest):
    pwx_executable = 'pw.x'
    maintainers = ['simonpintarelli', 'SSA']
    valid_systems = ['*']
    # valid_systems = ['+uenv +amdgpu', '+uenv +nvgpu']
    # valid_prog_environs = ['+uenv +prgenv +rocm', '+uenv +prgenv +cuda']

    @run_before('run')
    def prepare_run(self):
        self.uarch = uenv.uarch(self.current_partition)
        config = slurm_config[self.test_name][self.uarch]
        # sbatch options
        self.job.options = [
            f'--nodes={config["nodes"]}',
        ]
        self.num_tasks_per_node = config['ntasks-per-node']
        self.num_tasks = config['nodes'] * self.num_tasks_per_node
        self.num_cpus_per_task = config['cpus-per-task']
        self.ntasks_per_core = 1
        self.time_limit = config['walltime']

        # environment variables
        self.env_vars['OMP_NUM_THREADS'] = config['cpus-per-task']
        self.env_vars['SIRIUS_PRINT_TIMING'] = '1'
        self.env_vars['SIRIUS_PRINT_MPI_LAYOUT'] = '1'
        self.env_vars['SIRIUS_VERBOSITY'] = '2'
        self.env_vars['SLURM_HINT'] = 'nomultithread'
        if self.uarch == 'gh200':
            self.env_vars['MPICH_GPU_SUPPORT_ENABLED'] = '1'
            self.env_vars['OMP_NUM_THREADS'] = str(20)
        if self.uarch == 'mi200':
            self.env_vars['MPICH_GPU_SUPPORT_ENABLED'] = '1'
            self.env_vars['OMP_NUM_THREADS'] = str(8)
        if self.uarch == 'mi300':
            self.env_vars['MPICH_GPU_SUPPORT_ENABLED'] = '1'
            self.env_vars['OMP_NUM_THREADS'] = str(8)
        if self.uarch in ('mi300', 'mi200'):
            self.env_vars['PIKA_MPI_ENABLE_POOL'] = '1'
            self.env_vars['PIKA_MPI_COMPLETION_MODE'] = '28'
            self.env_vars['DLAF_BAND_TO_TRIDIAG_1D_BLOCK_SIZE_BASE'] = '2048'
            self.env_vars['DLAF_NUM_NP_GPU_STREAMS'] = '4'
            self.env_vars['DLAF_NUM_HP_GPU_STREAMS'] = '4'

        # set reference
        if self.uarch is not None and self.uarch in qe_references[self.test_name]:
            self.reference = {
                self.current_partition.fullname:
                qe_references[self.test_name][self.uarch]
            }

    @sanity_function
    def assert_energy_diff(self):
        # TODO, update for QE
        energy = sn.extractsingle(
            r'^!\s+total energy\s+=\s+(?P<energy>\S+)',
            self.stdout,
            'energy',
            float,
            item=-1,
        )
        energy_diff = sn.abs(energy - self.energy_reference)
        successful_termination = sn.assert_found(r'JOB DONE', self.stdout)
        correct_energy = sn.assert_lt(energy_diff, 5e-4)
        return sn.all(
            [
                successful_termination,
                correct_energy,
            ]
        )

    # INFO: The name of this function needs to match with the reference dict!
    @performance_function('s')
    def time_run(self):
        return sn.extractsingle(
            r'electrons.+\s(?P<wtime>\S+)s WALL', self.stdout, 'wtime', float
        )


class QeSiriusCheckAuSurfUENV(QeSiriusCheckUENV):
    test_name = 'Au surf'
    executable_opts = ['-i', 'ausurf.in']
    energy_reference = -11427.09017218


@rfm.simple_test
class QeCheckAuSurfUENVExec(QeSiriusCheckAuSurfUENV):
    valid_prog_environs = ['+q-e-sirius']
    tags = {'uenv', 'production', 'bencher'}

    @run_after('setup')
    def setup_executable(self):
        self.executable = f'pw.x'
        uarch = uenv.uarch(self.current_partition)
        if uarch == 'gh200':
            self.executable = f'./mps-wrapper.sh pw.x'
        if uarch == 'mi200':
            self.executable = \
                f'./amdgpu-wrapper.sh pw.x -sirius_cfg sirius-amd.json'
        if uarch == 'mi300':
            self.executable = \
                f'./tpx-wrapper.sh pw.x -sirius_cfg sirius-amd.json'
