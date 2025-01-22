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
                'PrgEnv-nvidia',
                'PrgEnv-nvhpc'
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
            'modules': ['cray', 'PrgEnv-cray', 'craype-arm-grace']
        },
        {
            'name': 'PrgEnv-gnu',
            'target_systems': ['daint'],
            'features': ['serial', 'openmp', 'mpi', 'cuda', 'alloc_speed',
                         'hdf5', 'netcdf-hdf5parallel', 'pnetcdf', 'openmp'],
            # 'modules': ['cray', 'PrgEnv-gnu', 'craype-arm-grace'],
            'prepare_cmds': [
                '#{{{',
                'module purge',
                'pwd',
                'mkdir -p MF/opt/cray/pe/lmod/modulefiles',
                'mkdir -p MF/opt/cray/modulefiles',
                'mkdir -p MF/opt/cscs/modulefiles',
                'export UU=/user-environment',
                # TODO: export UU=`echo $UENV_MOUNT_LIST |cut -d: -f2`
                #
                'ls -l /user-environment/opt/cray/pe/lmod/modulefiles/craype-targets/default/craype-arm-grace.lua',
                'ls -l /user-environment/opt/cray/pe/lmod/modulefiles/craype-targets/default/craype-network-ofi.lua',
                'ls -l /user-environment/opt/cray/pe/lmod/modulefiles/core/gcc-native/13.2.lua',
                'ls -l /user-environment/opt/cray/pe/lmod/modulefiles/core/gcc-native/13.2.lua',
                'ls -l /user-environment/opt/cray/pe/lmod/modulefiles/core/gcc-native/13.2.lua',
                'ls -l /user-environment/opt/cray/pe/lmod/modulefiles/core/craype/2.7.32.lua',
                'ls -l /user-environment/opt/cray/pe/lmod/modulefiles/comnet/gnu/12.0/ofi/1.0/cray-mpich/8.1.30.lua',
                'ls -l /user-environment/opt/cscs/modulefiles/cuda/12.6.lua',
                #
                'cp -a $UU/opt/cray/pe/lmod/modulefiles/* MF/opt/cray/pe/lmod/modulefiles/',
                'cp -a $UU/opt/cray/modulefiles/* MF/opt/cray/modulefiles/',
                'cp -a $UU/opt/cscs/modulefiles/* MF/opt/cscs/modulefiles/',
                'export XX=$PWD/MF',
                #
                'sed -i "s@/opt@$XX/opt@" $XX/opt/cray/pe/lmod/modulefiles/craype-targets/default/craype-arm-grace.lua',
                'sed -i "s@/opt@$XX/opt@" $XX/opt/cray/pe/lmod/modulefiles/craype-targets/default/craype-network-ofi.lua',
                'sed -i "s@/opt/cray/pe/@$XX/opt/cray/pe/@" $XX/opt/cray/pe/lmod/modulefiles/core/gcc-native/13.2.lua',
                'sed -i "s@/usr/lib64@$XX/usr/lib6@" $XX/opt/cray/pe/lmod/modulefiles/core/gcc-native/13.2.lua',
                'sed -i "s@/usr/bin@$XX/usr/bin@" $XX/opt/cray/pe/lmod/modulefiles/core/gcc-native/13.2.lua',
                'sed -i "s@/opt/cray@$XX/opt/cray@" $XX/opt/cray/pe/lmod/modulefiles/core/craype/2.7.32.lua',
                'sed -i "s@/opt/cray@$XX/opt/cray@" $XX/opt/cray/pe/lmod/modulefiles/comnet/gnu/12.0/ofi/1.0/cray-mpich/8.1.30.lua',
                'sed -i "s@/usr/local/cuda@$XX/usr/local/cuda@" $XX/opt/cscs/modulefiles/cuda/12.6.lua',
                #
                'cp /user-environment/etc/environment .',
                'sed -i "s@/usr@$PWD/MF/usr@g" environment',
                'sed -i "s@/opt@$PWD/MF/opt@g" environment',
                'source ./environment',
                #
                'source /user-environment/etc/profile.d/zz_default-modules.sh',
                'module list',
                '#}}}',
            ],
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
