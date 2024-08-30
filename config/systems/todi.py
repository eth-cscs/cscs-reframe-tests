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
            'name': 'todi',
            'descr': 'todi vcluster',
            'hostnames': ['todi'],
            'modules_system': 'lmod',
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
                        'PrgEnv-cray',
                        'PrgEnv-gnu'
                    ],
                    'max_jobs': 100,
                    'extras': {
                        'cn_memory': 500,
                    },
                    'resources': [
                        {
                            'name': 'memory',
                            'options': ['--mem={mem_per_node}']
                        },
                    ],
                    'features': ['ce', 'gpu', 'nvgpu', 'remote', 'scontrol', 'uenv'],
                    'devices': [
                        {
                            'type': 'gpu',
                            'arch': 'sm_90',
                            'num_devices': 4
                        }
                    ],
                    'launcher': 'srun'
                },
            ],
        },

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
    'modes': [
        {
            'name': 'production',
            'options': [
                '--unload-module=reframe',
                '--exec-policy=async',
                '-Sstrict_check=1',
                '--prefix=$SCRATCH/regression/production',
                '--report-file=$SCRATCH/regression/production/reports/prod_report_{sessionid}.json',
                '--save-log-files',
                '--tag=production',
                '--timestamp=%F_%H-%M-%S'
            ],
            'target_systems': ['todi'],
        }
    ]
}
