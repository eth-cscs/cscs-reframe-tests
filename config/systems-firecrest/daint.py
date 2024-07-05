# Copyright 2016 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings
#

import copy
import os


base_config = {
    'modules_system': 'tmod',
    # 'resourcesdir': '/apps/common/UES/reframe/resources',
    'partitions': [
        {
            'name': 'gpu',
            'scheduler': 'firecrest-slurm',
            'time_limit': '10m',
            'container_platforms': [
                {
                    'type': 'Sarus',
                    'modules': ['sarus']
                },
                {
                    'type': 'Singularity',
                    'modules': ['singularity/3.6.4-daint']
                }
            ],
            'modules': ['daint-gpu'],
            'access': [
                f'--constraint=gpu',
                f'--account=csstaff'
            ],
            'environs': [
                'builtin',
                'PrgEnv-cray',
                'PrgEnv-gnu',
                'PrgEnv-intel',
                'PrgEnv-nvidia'
            ],
            'descr': 'Hybrid nodes (Haswell/P100)',
            'max_jobs': 100,
            'extras': {
                'cn_memory': 64,
            },
            'features': ['gpu', 'nvgpu', 'remote', 'sarus', 'singularity'],
            'resources': [
                {
                    'name': 'switches',
                    'options': ['--switches={num_switches}']
                },
                {
                    'name': 'gres',
                    'options': ['--gres={gres}']
                }
            ],
            'devices': [
                {
                    'type': 'gpu',
                    'arch': 'sm_60',
                    'model': 'P100-PCIE-16GB',
                    'num_devices': 1
                }
                ],
            'launcher': 'srun',
        },
        {
            'name': 'mc',
            'scheduler': 'firecrest-slurm',
            'time_limit': '10m',
            'container_platforms': [
                {
                    'type': 'Sarus',
                    'modules': ['sarus']
                },
                {
                    'type': 'Singularity',
                    'modules': ['singularity/3.6.4-daint']
                }
            ],
            'modules': ['daint-mc'],
            'access': [
                f'--constraint=mc',
                f'--account=csstaff'
            ],
            'environs': [
                'builtin',
                'PrgEnv-cray',
                'PrgEnv-gnu',
                'PrgEnv-intel',
                'PrgEnv-nvidia'
            ],
            'descr': 'Multicore nodes (Broadwell)',
            'max_jobs': 100,
            'extras': {
                'cn_memory': 64,
            },
            'features': ['remote', 'sarus', 'singularity'],
            'resources': [
                {
                    'name': 'switches',
                    'options': ['--switches={num_switches}']
                },
                {
                    'name': 'gres',
                    'options': ['--gres={gres}']
                }
            ],
            'launcher': 'srun'
        },
        {
            'name': 'jupyter_gpu',
            'scheduler': 'firecrest-slurm',
            'time_limit': '10m',
            'environs': ['builtin'],
            'access': [
                f'-Cgpu',
                f'--reservation=interact_gpu',
                f'--account=csstaff'
            ],
            'descr': 'JupyterHub GPU nodes',
            'max_jobs': 10,
            'launcher': 'srun',
            'features': ['gpu', 'nvgpu', 'remote'],
        },
        {
            'name': 'jupyter_mc',
            'scheduler': 'firecrest-slurm',
            'time_limit': '10m',
            'environs': ['builtin'],
            'access': [
                f'-Cmc',
                f'--reservation=interact_mc',
                f'--account=csstaff'
            ],
            'descr': 'JupyterHub multicore nodes',
            'max_jobs': 10,
            'launcher': 'srun',
            'features': ['remote'],
        },
        {
            'name': 'xfer',
            'scheduler': 'firecrest-slurm',
            'time_limit': '10m',
            'environs': ['builtin'],
            'access': [
                f'--partition=xfer',
                f'--account=csstaff'
            ],
            'descr': 'Nordend nodes for internal transfers',
            'max_jobs': 10,
            'launcher': 'srun',
            'features': ['remote'],
        }
    ]
}

daint_sys = copy.deepcopy(base_config)
daint_sys['name'] = 'daint'
daint_sys['descr'] = 'Piz Daint'
daint_sys['hostnames'] = ['daint']

dom_sys = copy.deepcopy(base_config)
dom_sys['name'] = 'dom'
dom_sys['descr'] = 'Piz Daint tds'
dom_sys['hostnames'] = ['dom']

site_configuration = {
    'systems': [
        daint_sys,
        dom_sys
    ],
    'environments': [
        {
            'name': 'PrgEnv-cray',
            'modules': ['PrgEnv-cray'],
            'target_systems': ['daint', 'dom'],
            'features': ['mpi', 'openmp']
        },
        {
            'name': 'PrgEnv-gnu',
            'modules': ['PrgEnv-gnu'],
            'target_systems': ['daint', 'dom'],
            'prepare_cmds': ['module unload PrgEnv-cray'],
            'features': ['mpi', 'openmp'],
        },
        {
            'name': 'PrgEnv-intel',
            'modules': ['PrgEnv-intel'],
            'target_systems': ['daint', 'dom'],
            'prepare_cmds': ['module unload PrgEnv-cray'],
            'features': ['mpi', 'openmp']
        },
        {
            'name': 'PrgEnv-nvidia',
            'modules': ['PrgEnv-nvidia'],
            'features': ['cuda', 'mpi', 'openmp'],
            'target_systems': ['daint', 'dom'],
            'prepare_cmds': ['module unload PrgEnv-cray'],
        }
    ],
    'general': [
        {
            'resolve_module_conflicts': False,
            'use_login_shell': True,
            # Autodetection with this scheduler is really slow,
            # so it's better to disable it.
            'remote_detect': False,
            'target_systems': ['daint', 'dom'],
            'pipeline_timeout': 1000 # https://reframe-hpc.readthedocs.io/en/stable/pipeline.html#tweaking-the-throughput-and-interactivity-of-test-jobs-in-the-asynchronous-execution-policy
        }
    ],
    'autodetect_methods': [
        f'echo {os.environ.get("FIRECREST_SYSTEM")}'
    ],
    'modes': [
        {
            'name': 'production',
            'options': [
                '--exec-policy=async',
                '-Sstrict_check=1',
                '--save-log-files',
                '--tag=production',
                '--timestamp=%F_%H-%M-%S'
            ],
            'target_systems': ['daint'],
        }
    ]
}
