# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings
#

import reframe.utility.osext as osext
import reframe.utility.sanity as sn
import os


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
                'PrgEnv-nvidia',
                'PrgEnv-nvhpc'
            ],
            'descr': 'Login nodes',
            'max_jobs': 4,
            'launcher': 'local'
        },
        {
            'name': 'normal',
            'descr': 'GH200',
            'scheduler': 'slurm',
            'time_limit': '10m',
            'environs': [
                'builtin',
                'PrgEnv-cray',
                'PrgEnv-gnu',
                'PrgEnv-gnu-ce',
                'PrgEnv-nvidia',
                'PrgEnv-nvhpc',
                'PrgEnv-gnu-ce',
            ],
            'max_jobs': 100,
            'extras': {
                'cn_memory': 825,
            },
            'features': ['ce', 'gpu', 'nvgpu', 'remote', 'scontrol', 'uenv'],
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
                        '--container-mounts={stagedir}:/rfm_workdir',
                        '--container-workdir=/rfm_workdir'
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
}

base_config['name'] = 'daint'
base_config['descr'] = 'Piz Daint vcluster'
base_config['hostnames'] = ['daint']

site_configuration = {
    'systems': [
        base_config,
    ],
    'environments': [
        {
            'name': 'PrgEnv-cray',
            'features': ['serial', 'openmp', 'mpi', 'cuda', 'openacc', 'hdf5',
                         'netcdf-hdf5parallel', 'pnetcdf'],
            'target_systems': ['daint'],
            'modules': ['cray', 'PrgEnv-cray', 'craype-arm-grace'],
        },
        {
            'name': 'PrgEnv-gnu-ce',
            'features': ['serial', 'openmp', 'mpi', 'cuda', 'openacc', 'hdf5',
                         'netcdf-hdf5parallel', 'pnetcdf'],
            'resources': {
                'cpe_ce_image': {
                    'image': '/capstor/scratch/cscs/jenkssl/cpe/cpe-gnu.sqsh',
                }
             }
        },
        {
            'name': 'PrgEnv-gnu',
            'target_systems': ['daint'],
            'features': ['serial', 'openmp', 'mpi', 'cuda', 'alloc_speed',
                         'hdf5', 'netcdf-hdf5parallel', 'pnetcdf', 'openmp'],
            'modules': ['cray', 'PrgEnv-gnu', 'craype-arm-grace']
        },
        {
            'name': 'PrgEnv-nvidia',
            'target_systems': ['daint'],
            'features': ['serial', 'openmp', 'mpi', 'cuda', 'alloc_speed',
                         'hdf5', 'netcdf-hdf5parallel', 'pnetcdf'],
            'modules': ['cray', 'PrgEnv-gnu', 'craype-arm-grace']
        },
        {
            'name': 'PrgEnv-nvhpc',
            'target_systems': ['daint'],
            'features': ['serial', 'openmp', 'mpi', 'cuda', 'alloc_speed',
                         'hdf5', 'netcdf-hdf5parallel', 'pnetcdf'],
            'modules': ['cray', 'PrgEnv-gnu', 'craype-arm-grace']
        },
    ],
    'modes': [
       {
           'name': 'cpe_production',
           'options': [
               '--max-retries=1',
               '--report-file=$PWD/latest.json',
               '-c checks',
               '--tag=production'
           ],
           'target_systems': ['daint'],
       },
       {
           'name': 'uenv_production',
           'options': [
               '--max-retries=1',
               '--report-file=$PWD/latest.json',
               '-c checks/apps',
               '--tag=production'
           ],
           'target_systems': ['daint'],
       }
   ]
}
