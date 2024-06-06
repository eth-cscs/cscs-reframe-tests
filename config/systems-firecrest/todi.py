# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)

import os


site_configuration = {
    'systems': [
        {
            'name': 'todi',
            'descr': 'Todi vcluster',
            'hostnames': ['todi'],
            'modules_system': 'lmod',
            'partitions': [
                {
                    'name': 'normal',
                    'scheduler': 'firecrest-slurm',
                    'time_limit': '10m',
                    'environs': [
                        'builtin',
                        'PrgEnv-cray',
                        'PrgEnv-gnu',
                    ],
                    'max_jobs': 100,
                    'extras': {
                        # 'cn_memory': 500,
                    },
                    'access': ['-pnormal'],
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
                            'arch': 'sm_90',
                            'model': 'GH200/120GB',
                            'num_devices': 4
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
            'target_systems': ['todi'],
            'modules': ['cray', 'PrgEnv-cray', 'craype-arm-grace'],
            'features': ['serial', 'openmp', 'mpi', 'cuda', 'openacc', 'hdf5',
                         'netcdf-hdf5parallel', 'pnetcdf', 'openmp', 'opencl'],
            'extras': {
                'c_openmp_flags': ['-fopenmp'],
                'f_openmp_flags': ['-homp']
            }
        },
        {
            'name': 'PrgEnv-gnu',
            'target_systems': ['todi'],
            'modules': ['cray', 'PrgEnv-gnu', 'craype-arm-grace'],
            'features': ['serial', 'openmp', 'mpi', 'cuda', 'alloc_speed',
                         'hdf5', 'netcdf-hdf5parallel', 'pnetcdf', 'openmp'],
            'extras': {
                'hugepages2M': ['craype-hugepages2M'],
                'c_openmp_flags': ['-fopenmp']
            }
        },
    ],
    'general': [
        {
            'resolve_module_conflicts': False,
            'use_login_shell': True,
            # Autodetection with this scheduler is really slow,
            # so it's better to disable it.
            'remote_detect': False,
            'target_systems': ['todi'],
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
            'target_systems': ['todi'],
        }
    ]
}
