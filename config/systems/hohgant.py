# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings
#

site_configuration = {
    'systems': [
        {
            'name': 'hohgant',
            'descr': 'Hohgant vcluster',
            'hostnames': ['hohgant'],
            'modules_system': 'lmod',
            'partitions': [
                {
                    'name': 'login',
                    'scheduler': 'local',
                    'time_limit': '10m',
                    'environs': [
                        'builtin',
                        'PrgEnv-cray',
                        'PrgEnv-gnu',
                        'PrgEnv-nvhpc',
                        'PrgEnv-nvidia'
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
                        'PrgEnv-cray',
                        'PrgEnv-gnu',
                        'PrgEnv-nvhpc',
                        'PrgEnv-nvidia'
                    ],
                    'container_platforms': [
                        {
                            'type': 'Sarus',
                        },
                        {
                            'type': 'Singularity',
                        }
                    ],
                    'max_jobs': 100,
                    'extras': {
                        'cn_memory': 500,
                    },
                    'access': ['-pnvgpu'],
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
                        'gpu', 'nvgpu', 'remote', 'sarus', 'singularity'
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
                    'name': 'amdgpu',
                    'scheduler': 'slurm',
                    'time_limit': '10m',
                    'environs': [
                        'builtin',
                        'PrgEnv-cray',
                        'PrgEnv-gnu'
                    ],
                    'container_platforms': [
                        {
                            'type': 'Sarus',
                        },
                        {
                            'type': 'Singularity',
                        }
                    ],
                    'max_jobs': 100,
                    'extras': {
                        'cn_memory': 500,
                    },
                    'access': ['-pamdgpu'],
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
                        'gpu', 'amdgpu', 'remote', 'sarus', 'singularity',
                    ],
                    'launcher': 'srun'
                },
                {
                    'name': 'cpu',
                    'scheduler': 'slurm',
                    'time_limit': '10m',
                    'environs': [
                        'builtin',
                        'PrgEnv-cray',
                        'PrgEnv-gnu',
                        'PrgEnv-nvhpc',
                        'PrgEnv-nvidia'
                    ],
                    'container_platforms': [
                        {
                            'type': 'Sarus',
                        },
                        {
                            'type': 'Singularity',
                        }
                    ],
                    'max_jobs': 100,
                    'extras': {
                        'cn_memory': 500,
                    },
                    'access': ['-pcpu'],
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
                    'features': ['remote', 'sarus', 'singularity'],
                    'launcher': 'srun'
                }
            ]
        },
    ],
    'environments': [
        {
            'name': 'PrgEnv-cray',
            'target_systems': ['hohgant'],
            'modules': ['cray', 'PrgEnv-cray'],
            'features': ['serial', 'openmp', 'mpi', 'cuda', 'openacc',
                         'netcdf-hdf5parallel', 'pnetcdf', 'openmp', 'opencl'],
            'extras': {
                'openmp_flags': ['-fopenmp']
            }
        },
        {
            'name': 'PrgEnv-gnu',
            'target_systems': ['hohgant'],
            'modules': ['cray', 'PrgEnv-gnu'],
            'features': ['serial', 'openmp', 'mpi', 'cuda', 'alloc_speed',
                         'netcdf-hdf5parallel', 'pnetcdf', 'openmp'],
            'extras': {
                'hugepages2M': ['craype-hugepages2M'],
                'openmp_flags': ['-fopenmp']
            }
        },
        {
            'name': 'PrgEnv-nvhpc',
            'target_systems': ['hohgant'],
            'modules': ['cray', 'PrgEnv-nvhpc'],
            'features': ['serial', 'openmp', 'mpi', 'cuda',
                         'netcdf-hdf5parallel', 'pnetcdf', 'openmp'],
            'extras': {
                'launcher_options': ['--mpi=pmi2'],
                'openmp_flags': ['-fopenmp']
            },
        },
        {
            'name': 'PrgEnv-nvidia',
            'target_systems': ['hohgant'],
            'modules': ['cray', 'PrgEnv-nvidia'],
            'features': ['serial', 'openmp', 'mpi', 'cuda-fortran', 'openacc',
                         'netcdf-hdf5parallel', 'pnetcdf', 'openmp', 'opencl'],
            'extras': {
                # Workaround "MPIR_pmi_init(83)....: PMI2_Job_GetId returned 14" error
                'launcher_options': ['--mpi=pmi2'],
                'openmp_flags': ['-mp']
            },
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
            'target_systems': ['hohgant'],
        }
    ]
}
