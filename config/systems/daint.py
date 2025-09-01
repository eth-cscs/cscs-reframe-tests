# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings
#


import os

base_config = {
    'modules_system': 'lmod',
    'resourcesdir': '/capstor/store/cscs/cscs/public/reframe/resources',
    'partitions': [
        {
            'name': 'login',
            'scheduler': 'local',
            'time_limit': '10m',
            'environs': [
                'builtin',
                'PrgEnv-cray',
                'PrgEnv-gnu',
                # FIXME: Problem loading the following environments
                # 'PrgEnv-nvidia',
                # 'PrgEnv-nvhpc'
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
                'PrgEnv-ce',
                # FIXME: Problem loading the following environments
                # 'PrgEnv-nvidia',
                # 'PrgEnv-nvhpc'
            ],
            'max_jobs': 100,
            'extras': {
                'cn_memory': 825,
            },
            'features': ['ce', 'gpu', 'nvgpu', 'remote', 'scontrol', 'uenv', 'hugepages_slurm'],
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
                        '--container-mounts={stagedir}/../../../,{stagedir}:/rfm_workdir',
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
}

base_config['name'] = 'daint'
base_config['descr'] = 'Piz Daint vcluster'
base_config['hostnames'] = ['daint', 'alps-daint']

site_configuration = {
    'systems': [
        base_config,
    ],
    'environments': [
        {
            'name': 'PrgEnv-cray',
            'features': ['cpe',
                'serial', 'openmp', 'mpi', 'cuda', 'openacc', 'hdf5',
                # 'netcdf-hdf5parallel',
                # FIXME MPI Error when using pnetcdf
                # 'pnetcdf'
            ],
            'target_systems': ['daint'],
            'modules': ['cray', 'PrgEnv-cray', 'craype-arm-grace'],
        },
        {
            'name': 'PrgEnv-ce',
            'features': ['ce',
                'serial', 'openmp', 'mpi', 'cuda', 'containerized_cpe'],
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
        {
            'name': 'PrgEnv-gnu',
            'target_systems': ['daint'],
            'features': ['cpe',
                'serial', 'openmp', 'mpi', 'cuda', 'alloc_speed',
                'hdf5'
                # 'netcdf-hdf5parallel',
                # FIXME MPI Error when using pnetcdf
                # 'pnetcdf'
            ],
            'modules': ['cray', 'PrgEnv-gnu', 'craype-arm-grace']
        },
        {
            'name': 'PrgEnv-nvidia',
            'target_systems': ['daint'],
            'features': ['cpe',
                'serial', 'openmp', 'mpi', 'cuda', 'alloc_speed',
                'hdf5', 'netcdf-hdf5parallel', 'pnetcdf'],
            'modules': ['cray', 'PrgEnv-nvidia', 'craype-arm-grace']
        },
        {
            'name': 'PrgEnv-nvhpc',
            'target_systems': ['daint'],
            'features': ['cpe',
                'serial', 'openmp', 'mpi', 'cuda', 'alloc_speed',
                'hdf5', 'netcdf-hdf5parallel', 'pnetcdf'],
            'modules': ['cray', 'PrgEnv-nvhpc', 'craype-arm-grace']
        },
    ],
}
