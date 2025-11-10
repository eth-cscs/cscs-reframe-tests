# Copyright 2025 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings
#

import os

import reframe.utility.osext as osext


site_configuration = {
    'systems': [
        {
            'name': 'eiger',
            'descr': 'Alps Eiger vcluster',
            'hostnames': ['eiger', 'eiger-alps'],
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
                        'PrgEnv-ce',
                    ],
                    'max_jobs': 100,
                    'extras': {
                        'cn_memory': 256,
                    },
                    'resources': [
                        {
                            'name': 'memory',
                            'options': ['--mem={mem_per_node}']
                        },
                        {
                            'name': 'cpe_ce_image',
                            'options': [
                                '--container-image={image}',
                             ]
                        },
                        {
                            'name': 'cpe_ce_mount',
                            'options': [
                                # Mount both the stagedir and the directory related
                                # used 3 levels above (the one related to the system)
                                # to be able to find fixtures
                                '--container-mounts={stagedir}/../../../,'  # split
                                '{stagedir}:/rfm_workdir',
                                '--container-workdir=/rfm_workdir'
                             ]
                        },
                        {
                            'name': 'cpe_ce_extra_mounts',
                            'options': [
                                '--container-mounts={mount}:{mount}',
                             ]
                        }
                    ],
                    'access': [f'--account={osext.osgroup()}'],
                    'features': ['ce', 'remote', 'scontrol', 'uenv'],
                    'launcher': 'srun'
                },
            ]
        },
    ],
    'environments': [
        {
            'name': 'PrgEnv-ce',
            'features': [
                'cpe', 'prgenv',
                'serial', 'openmp', 'mpi', 'containerized_cpe'],
            'resources': {
                'cpe_ce_image': {
                    'image':
                        # Avoid interpretting '#' as a start of a comment
                        os.environ.get(
                            'CPE_CE', ''
                        ).replace(r'#', r'\#')
                }
             }
        },
    ],
    'modes': [
        {
            'name': 'production',
            'options': [
                '--exec-policy=async',
                '-Sstrict_check=1',
                '--prefix=$SCRATCH/regression/production',
                '--report-file=$SCRATCH/regression/production/reports/prod_report_{sessionid}.json',
                '--save-log-files',
                '--tag=production',
                '--timestamp=%F_%H-%M-%S'
            ],
            'target_systems': ['eiger'],
        },
    ]
}
