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
                # 'PrgEnv-nvidia'
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

base_config['name'] = 'todi'
base_config['descr'] = 'Piz Todi vcluster'
base_config['hostnames'] = ['todi']

site_configuration = {
    'systems': [
        base_config,
    ],
    'environments': [
        {
            'name': 'PrgEnv-cray',
            'features': ['serial', 'openmp', 'mpi', 'cuda', 'openacc', 'hdf5',
                         'netcdf-hdf5parallel', 'pnetcdf'],
            'target_systems': ['todi'],
            'modules': ['cray', 'PrgEnv-cray', 'craype-arm-grace']
        },
        {
            'name': 'PrgEnv-gnu',
            'target_systems': ['todi'],
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
               '-c checks/system/integration/todi.py',
               '-c checks/prgenv/mpi.py',
               '-c checks/microbenchmarks/mpi/osu/osu_run.py',
               '-c checks/microbenchmarks/mpi/osu/osu_tests.py',
               '-c checks/microbenchmarks/cpu/alloc_speed/alloc_speed.py',
               '-c checks/microbenchmarks/cpu/stream/stream.py',
               '-c checks/prgenv/affinity_check.py',
           ],
           'target_systems': ['todi'],
       },
       {
           'name': 'uenv_production',
           'options': [
               '--max-retries=1',
               '--report-file=$PWD/latest.json',
               '-c checks/prgenv/mpi.py',
           ],
           'target_systems': ['todi'],
       }
   ]
}
