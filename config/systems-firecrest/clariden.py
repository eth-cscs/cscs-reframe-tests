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
            'name': 'clariden',
            'descr': 'Clariden vcluster',
            'hostnames': ['clariden'],
            'modules_system': 'lmod',
            'partitions': [
                {
                    'name': 'nvgpu',
                    'scheduler': 'firecrest-slurm',
                    'time_limit': '10m',
                    'environs': [
                        'builtin',
                        'PrgEnv-cray',
                        'PrgEnv-gnu',
                        'PrgEnv-nvhpc',
                        'PrgEnv-nvidia'
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
                        'gpu', 'nvgpu', 'remote', 'enroot', 'pyxis', 'buildah', 'scontrol'
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
                    'scheduler': 'firecrest-slurm',
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
                        'gpu', 'amdgpu', 'remote', 'enroot', 'pyxis', 'buildah', 'scontrol'
                    ],
                    'devices': [
                        {
                            'type': 'gpu',
                            'arch': 'gfx90a',
                            'num_devices': 8
                        }
                    ],
                    'launcher': 'srun'
                },
            ]
        },
    ],
    'environments': [
        {
            'name': 'PrgEnv-cray',
            'target_systems': ['clariden'],
            'modules': ['cray', 'PrgEnv-cray'],
            'features': ['serial', 'openmp', 'mpi', 'cuda', 'openacc', 'hdf5',
                         'netcdf-hdf5parallel', 'pnetcdf', 'openmp', 'opencl'],
            'extras': {
                'c_openmp_flags': ['-fopenmp'],
                'f_openmp_flags': ['-homp']
            }
        },
        {
            'name': 'PrgEnv-gnu',
            'target_systems': ['clariden'],
            'modules': ['cray', 'PrgEnv-gnu'],
            'features': ['serial', 'openmp', 'mpi', 'cuda', 'alloc_speed',
                         'hdf5', 'netcdf-hdf5parallel', 'pnetcdf', 'openmp'],
            'extras': {
                'hugepages2M': ['craype-hugepages2M'],
                'c_openmp_flags': ['-fopenmp']
            }
        },
        {
            'name': 'PrgEnv-nvhpc',
            'target_systems': ['clariden'],
            'modules': ['cray', 'PrgEnv-nvhpc'],
            'features': ['serial', 'openmp', 'mpi', 'cuda',
                         'hdf5', 'netcdf-hdf5parallel', 'pnetcdf', 'openmp'],
            'extras': {
                'launcher_options': ['--mpi=pmi2'],
                'c_openmp_flags': ['-fopenmp']
            },
        },
        {
            'name': 'PrgEnv-nvidia',
            'target_systems': ['clariden'],
            'modules': ['cray', 'PrgEnv-nvidia'],
            'features': ['serial', 'openmp', 'mpi', 'cuda-fortran', 'openacc',
                         'netcdf-hdf5parallel', 'pnetcdf', 'openmp', 'opencl'
                         'hdf5'],
            'extras': {
                # Workaround "MPIR_pmi_init(83)....: PMI2_Job_GetId returned 14" error
                'launcher_options': ['--mpi=pmi2'],
                'c_openmp_flags': ['-mp']
            },
        },
    ],
    'general': [
        {
            'resolve_module_conflicts': False,
            'use_login_shell': True,
            # Autodetection with this scheduler is really slow,
            # so it's better to disable it.
            'remote_detect': False,
            'target_systems': ['clariden'],
            'pipeline_timeout': 1000 # https://reframe-hpc.readthedocs.io/en/stable/pipeline.html#tweaking-the-throughput-and-interactivity-of-test-jobs-in-the-asynchronous-execution-policy
        }
    ],
    'autodetect_methods': [
        f'echo {os.environ.get("FIRECREST_SYSTEM")}'
    ],
    'modes': [
        {
            'name': 'production',
            'options': [
                '--exec-policy=async',
                '-Sstrict_check=1',
                '--save-log-files',
                '--tag=production',
                '--timestamp=%F_%H-%M-%S'
            ],
            'target_systems': ['clariden'],
        }
    ]
}
