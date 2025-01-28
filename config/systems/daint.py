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
    'partitions': [
#login         {
#login             'name': 'login',
#login             'descr': 'Login nodes',
#login             'scheduler': 'local',
#login             'time_limit': '10m',
#login             'environs': [
#login                 'builtin',
#login                 #'PrgEnv-cray',
#login                 'PrgEnv-gnu',
#login                 #'PrgEnv-nvidia',
#login                 #'PrgEnv-nvhpc'
#login             ],
#login             'max_jobs': 4,
#login             'launcher': 'local'
#login         },
        {
            'name': 'normal',
            'descr': 'GH200',
            'scheduler': 'slurm',
            'launcher': 'srun',
            'time_limit': '10m',
            'sched_options': {
                'use_nodes_option': True
            },
            'environs': [
                'builtin',
                # 'PrgEnv-cray',
                'PrgEnv-gnu',
                # 'PrgEnv-nvidia',
                # 'PrgEnv-nvhpc'
            ],
            'max_jobs': 100,
            'container_platforms': [],
            'extras': {
                'cn_memory': 825,
            },
            # 'features': ['ce', 'gpu', 'nvgpu', 'remote', 'scontrol', 'uenv'],
            'features': ['uenv', 'remote', 'cpe_ce'],
#ok             'resources': [
#ok                 {
#ok                     'name': 'switches',
#ok                     'options': ['--switches={num_switches}']
#ok                 },
#ok                 {
#ok                     'name': 'gres',
#ok                     'options': ['--gres={gres}']
#ok                 },
#ok                 {
#ok                     'name': 'memory',
#ok                     'options': ['--mem={mem_per_node}']
#ok                 },
#ok                 {
#ok                     'name': 'cpe',
#ok                     # 'options': ['--environment=/capstor/scratch/cscs/anfink/cpe/cpe-gnu.sqsh']
#ok                     'options': ['--environment={cpe_sqfs}']
#ok                 }
#ok             ],
            'devices': [
                {
                    'type': 'gpu',
                    'arch': 'sm_90',
                    'num_devices': 4
                }
                ],
        },
    ]
}

base_config['name'] = 'daint'
base_config['descr'] = 'Alps daint vcluster'
base_config['hostnames'] = ['daint']

site_configuration = {
    'systems': [
        base_config,
    ],
    'environments': [
#         {
#             'name': 'PrgEnv-cray',
#             'features': ['serial', 'openmp', 'mpi', 'cuda', 'openacc', 'hdf5',
#                          'netcdf-hdf5parallel', 'pnetcdf'],
#             'target_systems': ['daint'],
#             'modules': ['cray', 'PrgEnv-cray', 'craype-arm-grace']
#         },
        {
            'name': 'PrgEnv-gnu',
            'target_systems': ['daint'],
            # NOTE: DO NOT USE -p PrgEnv-gnu !
            #'features': ['serial', 'openmp', 'mpi', 'cuda', 'alloc_speed', 'uenv',
            #             'hdf5', 'netcdf-hdf5parallel', 'pnetcdf', 'openmp'],
            'features': ['mpi'],
            #'resources': {
            #    'name': 'cpe',
            #    'options': '--environment=/users/piccinal/.edf/cpe-gnu.toml'
            #}

            # -------------------------- 
            # #SBATCH --environment=cpe-gnu
            # 'extras': {'cpe_sqfs': '/capstor/scratch/cscs/anfink/cpe/cpe-gnu.sqsh'}
            # -------------------------- 
            # 'modules': ['cray', 'PrgEnv-gnu', 'craype-arm-grace'],
            # {{{ CPEJG
#yaml             'prepare_cmds': [
#yaml                 'source /user-environment/etc/environment',
#yaml                 'source /user-environment/etc/profile.d/zz_default-modules.sh',
#yaml                 'module list',
#yaml             ],
            # }}}
        },
#         {
#             'name': 'PrgEnv-nvidia',
#             'target_systems': ['daint'],
#             'features': ['serial', 'openmp', 'mpi', 'cuda', 'alloc_speed',
#                          'hdf5', 'netcdf-hdf5parallel', 'pnetcdf'],
#             'modules': ['cray', 'PrgEnv-gnu', 'craype-arm-grace']
#         },
#         {
#             'name': 'PrgEnv-nvhpc',
#             'target_systems': ['daint'],
#             'features': ['serial', 'openmp', 'mpi', 'cuda', 'alloc_speed',
#                          'hdf5', 'netcdf-hdf5parallel', 'pnetcdf'],
#             'modules': ['cray', 'PrgEnv-gnu', 'craype-arm-grace']
#         },
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
