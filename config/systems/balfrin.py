# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings
#

site_configuration = {
    'systems': [
        {
            'name': 'balfrin',
            'descr': 'Balfrin vcluster',
            'hostnames': ['balfrin'],
            'modules_system': 'nomod',
            'partitions': [
                {
                    'name': 'login',
                    'scheduler': 'local',
                    'time_limit': '10m',
                    'environs': [
                        'builtin',
                    ],
                    'features': [
                        'remote', 'uenv',
                    ],
                    'descr': 'Login nodes',
                    'max_jobs': 4,
                    'launcher': 'local'
                },
                {
                    'name': 'nvgpu',
                    'scheduler': 'slurm',
                    'time_limit': '10m',
                    'environs': [
                        'builtin',
                    ],
                    'container_platforms': [
                        {
                             'type': 'Sarus',
                        },
                    ],
                    'max_jobs': 100,
                    'access': ['-pnormal'],
                    'resources': [
                        {
                            'name': 'switches',
                            'options': ['--switches={num_switches}']
                        },
                        {
                            'name': 'memory',
                            'options': ['--mem={mem_per_node}']
                        },
                    ],
                    'features': [
                        'gpu', 'nvgpu', 'uenv', 'remote', 'sarus', 'scontrol'
                    ],
                    'devices': [
                        {
                            'type': 'gpu',
                            'arch': 'sm_80',
                            'num_devices': 4
                        }
                    ],
                    'launcher': 'srun'
                },
                {
                    'name': 'cpu',
                    'scheduler': 'slurm',
                    'time_limit': '10m',
                    'container_platforms': [
                        {
                            'type': 'Sarus',
                        }
                    ],
                    'environs': [
                        'builtin',
                    ],
                    'max_jobs': 100,
                    'access': ['-ppostproc'],
                    'resources': [
                        {
                            'name': 'switches',
                            'options': ['--switches={num_switches}']
                        },
                        {
                            'name': 'memory',
                            'options': ['--mem={mem_per_node}']
                        },
                    ],
                    'features': [
                        'remote', 'uenv', 'sarus', 'scontrol'
                    ],
                    'launcher': 'srun'
                },
            ]
        },
    ],
}
