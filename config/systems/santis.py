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
            'name': 'santis',
            'descr': 'santis vcluster',
            'hostnames': ['santis'],
            'modules_system': 'tmod',
            'partitions': [
                {
                    'name': 'login',
                    'scheduler': 'local',
                    'time_limit': '10m',
                    'environs': [
                        'builtin',
                        'PrgEnv-gnu',
                        #'PrgEnv-cray',
                        #'PrgEnv-nvhpc',
                        #'PrgEnv-nvidia'
                    ],
                    #'features': [
                    #    'enroot'
                    #],
                    'descr': 'Login nodes',
                    'max_jobs': 4,
                    'launcher': 'local'
                },
                {
                    'name': 'mc',
                    'scheduler': 'slurm',
                    'time_limit': '10m',
                    'environs': [
                        'builtin',
                        'PrgEnv-gnu',
                        #'PrgEnv-cray',
                        #'PrgEnv-nvhpc',
                        #'PrgEnv-nvidia'
                    ],
                    'max_jobs': 100,
                    #'extras': {
                    #    'cn_memory': 500,
                    #},
                    'access': ['-psantis'],
                    'prepare_cmds': ['export PATH=$PATH:.'],
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
                        'remote', 'scontrol'
                        #'gpu', 'nvgpu', 'remote', 'enroot', 'pyxis', 'buildah', 'scontrol'
                    ],
                    #'devices': [
                    #    {
                    #        'type': 'gpu',
                    #        'arch': 'sm_80',
                    #        'num_devices': 4
                    #    }
                    #],
                    'launcher': 'mpirun'
                },
            ]
        },
    ],
    'environments': [
        {
            'name': 'PrgEnv-cray',
            'target_systems': ['santis'],
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
            'target_systems': ['santis'],
            #'modules': ['cray', 'PrgEnv-gnu'],
            #'features': ['serial', 'openmp', 'mpi', 'cuda', 'alloc_speed',
            #             'hdf5', 'netcdf-hdf5parallel', 'pnetcdf', 'openmp'],
            'cc': 'mpicc',
            'cxx': 'mpicxx',
            'ftn': 'mpif90',
            'modules': ['gnu-mpich'],
            'features': [
                'serial', 'openmp', 'mpi', 'alloc_speed',
                'hdf5', 'netcdf-hdf5parallel', 'pnetcdf', 'cdo', 'nco'
            ],
            'extras': {
                'hugepages2M': ['craype-hugepages2M'],
                'c_openmp_flags': ['-fopenmp']
            }
        },
        {
            'name': 'PrgEnv-nvhpc',
            'target_systems': ['santis'],
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
            'target_systems': ['santis'],
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
            'target_systems': ['santis'],
        }
    ]
}
