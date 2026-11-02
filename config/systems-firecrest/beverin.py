# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings for beverin through FirecREST
#

import os

_account = os.environ.get('CSCS_RFM_FIRECREST_ACCOUNT')

site_configuration = {
    'systems': [
        {
            'name': 'beverin',
            'descr': 'beverin vcluster (through FirecREST)',
            'hostnames': ['beverin'],
            'modules_system': 'nomod',
            'partitions': [
                {
                    'name': 'mi200',
                    'descr': 'MI200 gfx90a',
                    'scheduler': 'firecrest-slurm',
                    'time_limit': '10m',
                    'environs': [
                        'builtin',
                    ],
                    'max_jobs': 100,
                    'extras': {
                        'cn_memory': 515208,
                    },
                    'features': ['gpu', 'amdgpu', 'remote'],
                    'access': [f'--account={_account}', '--partition=mi200'] if _account else ['--partition=mi200'],
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
                            'arch': 'gfx90a',
                            'num_devices': 8
                        }
                    ],
                    'launcher': 'srun',
                },
                {
                    'name': 'mi300',
                    'descr': 'MI300 gfx942',
                    'scheduler': 'firecrest-slurm',
                    'time_limit': '10m',
                    'environs': [
                        'builtin',
                    ],
                    'max_jobs': 100,
                    'extras': {
                        'cn_memory': 513700,
                    },
                    'features': ['gpu', 'amdgpu', 'remote'],
                    'access': [f'--account={_account}', '--partition=mi300'] if _account else ['--partition=mi300'],
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
                            'arch': 'gfx942',
                            'num_devices': 4
                        }
                    ],
                    'launcher': 'srun',
                }
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
            'target_systems': ['beverin'],
            'pipeline_timeout': 1000
        }
    ],
}
