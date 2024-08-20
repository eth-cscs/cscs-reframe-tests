# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings
#

import reframe.utility.osext as osext
import copy


base_config = {
    'modules_system': 'lmod',
    # 'resourcesdir': '/apps/common/UES/reframe/resources',
    'partitions': [
        {
            'name': 'login',
            'scheduler': 'local',
            'time_limit': '10m',
            'environs': [
                'builtin',
                'PrgEnv-cray',
                'PrgEnv-gnu',
                #'PrgEnv-nvidia'
            ],
            'descr': 'Login nodes',
            'max_jobs': 4,
            'launcher': 'local'
        },
        {
            'name': 'normal',
            'descr': 'Grace-Hopper GH200',
            'scheduler': 'slurm',
            'time_limit': '10m',
            'container_platforms': [
#                 {
#                     'type': 'Sarus',
#                     #'modules': ['sarus']
#                 },
#                 {
#                     'type': 'Singularity',
#                     #'modules': ['singularity/3.6.4-todi']
#                 }
            ],
            'environs': [
                'builtin',
                'PrgEnv-cray',
                'PrgEnv-gnu',
            ],
            'max_jobs': 100,
            'extras': {
                'cn_memory': 825,
            },
            'features': ['gpu', 'nvgpu', 'remote'],
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
                    'arch': 'sm_90',
                    'num_devices': 4
                }
                ],
            'launcher': 'srun',
        },
    ]
}

todi_sys = copy.deepcopy(base_config)
todi_sys['name'] = 'todi'
todi_sys['descr'] = 'Piz todi'
todi_sys['hostnames'] = ['todi']

site_configuration = {
    'systems': [
        todi_sys,
    ],
    'environments': [
        {
            'name': 'PrgEnv-cray',
            'features': ['serial', 'openmp', 'mpi', 'cuda', 'openacc', 'hdf5',
                         'netcdf-hdf5parallel', 'pnetcdf', 'openmp', 'opencl'],
            'target_systems': ['todi'],
            'modules': ['cray', 'PrgEnv-cray', 'craype-arm-grace']
        },
        {
            'name': 'PrgEnv-gnu',
            'target_systems': ['todi'],
            'features': ['serial', 'openmp', 'mpi', 'cuda', 'alloc_speed',
                         'hdf5', 'netcdf-hdf5parallel', 'pnetcdf', 'openmp'],
            'modules': ['cray', 'PrgEnv-gnu', 'craype-arm-grace']
        },
    ],
}
