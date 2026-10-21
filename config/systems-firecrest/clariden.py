# Copyright 2026 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings for clariden through FirecREST
#

import os

_account = os.environ.get('CSCS_RFM_FIRECREST_ACCOUNT')

site_configuration = {
    'systems': [
        {
            'name': 'clariden',
            'descr': 'Clariden vcluster (through FirecREST)',
            'hostnames': ['clariden'],
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
                        'cn_memory': 850000,
                    },
                    'features': ['gpu', 'nvgpu', 'remote'],
                    'access': [f'--account={_account}'] if _account else [],
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
            'target_systems': ['clariden'],
            'pipeline_timeout': 1000
        }
    ],
}
