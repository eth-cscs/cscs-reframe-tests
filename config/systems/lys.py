
# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings
#


import os

site_configuration = {
    'systems': [
         {
            'name': 'lys',
            'descr': 'Lys vcluster',
            'hostnames': ['lys'],
            'modules_system': 'lmod',
            'resourcesdir': '/vast/scratch/firecr02/reframe/resources',
            'partitions': [        
                {
                    'name': 'normal',
                    'descr': 'GH200',
                    'scheduler': 'slurm',
                    'time_limit': '10m',
                    'environs': [
                        'builtin',
                        # 'PrgEnv-cray',
                        # 'PrgEnv-gnu',
                        # 'PrgEnv-ce',
                        # FIXME: Problem loading the following environments
                        # 'PrgEnv-nvidia',
                        # 'PrgEnv-nvhpc'
                    ],
                    'max_jobs': 100,
                    'extras': {
                        'cn_memory': 825,
                    },
                    'features': [
                        'ce', 'gpu', 'nvgpu', 'remote', 'scontrol', 'uenv',
                        'hugepages_slurm'],
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
    'environments': [        
    ],
}
