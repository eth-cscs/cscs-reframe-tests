# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings
#

import reframe.utility.osext as osext
import copy


base_config = {
    'modules_system': 'tmod',
    'resourcesdir': '/apps/common/UES/reframe/resources',
    'partitions': [
        {
            'name': 'login',
            'scheduler': 'local',
            'time_limit': '10m',
            'environs': [
                'builtin',
                'PrgEnv-cray',
                'PrgEnv-gnu',
                'PrgEnv-intel',
                'PrgEnv-nvidia'
            ],
            'descr': 'Login nodes',
            'max_jobs': 4,
            'launcher': 'local'
        },
        {
            'name': 'gpu',
            'scheduler': 'slurm',
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
                f'--account={osext.osgroup()}'
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
                    'num_devices': 1
                }
                ],
            'launcher': 'srun',
        },
        {
            'name': 'mc',
            'scheduler': 'slurm',
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
                f'--account={osext.osgroup()}'
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
            'scheduler': 'slurm',
            'time_limit': '10m',
            'environs': ['builtin'],
            'access': [
                f'-Cgpu',
                f'--reservation=interact_gpu',
                f'--account={osext.osgroup()}'
            ],
            'descr': 'JupyterHub GPU nodes',
            'max_jobs': 10,
            'launcher': 'srun',
            'features': ['gpu', 'nvgpu', 'remote'],
        },
        {
            'name': 'jupyter_mc',
            'scheduler': 'slurm',
            'time_limit': '10m',
            'environs': ['builtin'],
            'access': [
                f'-Cmc',
                f'--reservation=interact_mc',
                f'--account={osext.osgroup()}'
            ],
            'descr': 'JupyterHub multicore nodes',
            'max_jobs': 10,
            'launcher': 'srun',
            'features': ['remote'],
        },
        {
            'name': 'xfer',
            'scheduler': 'slurm',
            'time_limit': '10m',
            'environs': ['builtin'],
            'access': [
                f'--partition=xfer',
                f'--account={osext.osgroup()}'
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
dom_sys['descr'] = 'Dom TDS'
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
            'features': ['mpi', 'openmp']
        },
        {
            'name': 'PrgEnv-intel',
            'modules': ['PrgEnv-intel'],
            'target_systems': ['daint', 'dom'],
            'features': ['mpi', 'openmp']
        },
        {
            'name': 'PrgEnv-nvidia',
            'modules': ['PrgEnv-nvidia'],
            'features': ['cuda', 'mpi', 'openmp'],
            'target_systems': ['daint', 'dom'],
        }
    ],
}
