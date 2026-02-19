# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings
#

import os

reframe_dir = os.getenv(
    'REFRAME_DIR',
    '/capstor/store/cscs/cscs/public/reframe/reframe-stable/$CLUSTER_NAME'
)
target_dir_var_exists = bool(os.getenv('TARGET_DIR'))
target_dir_base = (
    '$SCRATCH/reframe/$CLUSTER_NAME' if not target_dir_var_exists else ''
)

site_configuration = {
    'systems': [
        {
            'name': 'starlex',
            'descr': 'starlex vcluster',
            'hostnames': ['starlex'],
            'modules_system': 'lmod',
            'resourcesdir':
                '/capstor/store/cscs/cscs/public/reframe/resources',
            'partitions': [
                {
                    'name': 'login',
                    'scheduler': 'local',
                    'time_limit': '10m',
                    'environs': [
                        'builtin',
                    ],
                    'descr': 'Login nodes',
                    'max_jobs': 4,
                    'launcher': 'local'
                },
                {
                    'name': 'normal',
                    'scheduler': 'slurm',
                    'time_limit': '10m',
                    'environs': [
                        'builtin',
                    ],
                    'max_jobs': 100,
                    'extras': {
                        'cn_memory': 850,
                    },
                    'resources': [
                        {
                            'name': 'memory',
                            'options': ['--mem={mem_per_node}']
                        },
                        {
                            'name': 'gres',
                            'options': ['--gres={gres}']
                        },
                    ],
                    'features': ['ce', 'gpu', 'nvgpu', 'remote', 'scontrol',
                                 'uenv', 'hugepages_slurm'],
                    'devices': [
                        {
                            'type': 'gpu',
                            'arch': 'sm_90',
                            'num_devices': 4
                        }
                    ],
                    'launcher': 'srun'
                },
            ]
        },
    ],
}
