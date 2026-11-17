# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings for santis through FirecREST
#

import os

_account = os.environ.get('CSCS_RFM_FIRECREST_ACCOUNT')

site_configuration = {
    'systems': [
        {
            'name': 'santis',
            'descr': 'santis vcluster (through FirecREST)',
            'hostnames': ['santis'],
            'modules_system': 'nomod',
            'partitions': [
                {
                    'name': 'normal',
                    'descr': 'GH200',
                    'scheduler': 'firecrest-slurm',
                    'time_limit': '10m',
                    'environs': [
                        'builtin',
                    ],
                    'max_jobs': 100,
                    'extras': {
                        'cn_memory': 870000,
                    },
                    'features': ['gpu', 'nvgpu', 'remote'],
                    'access': [f'--account={_account}', '--gpus-per-node=4'] if _account else ['--gpus-per-node=4'],
                    'resources': [
                        {
                            'name': 'switches',
                            'options': ['--switches={num_switches}']
                        },
                        {
                            'name': 'gres',
                            'options': ['--gres={gres}']
                        },
                        {
                            'name': 'memory',
                            'options': ['--mem={mem_per_node}']
                        },
                    ],
                    'devices': [
                        {
                            'type': 'gpu',
                            'arch': 'sm_90',
                            'num_devices': 4
                        }
                    ],
                    'launcher': 'srun',
                },
            ]
        },
    ],
    'general': [
        {
            'resolve_module_conflicts': False,
            'use_login_shell': True,
            # Autodetection with this scheduler is really slow,
            # so it's better to disable it.
            'remote_detect': False,
            'target_systems': ['santis'],
            'pipeline_timeout': 1000
        }
    ],
}
