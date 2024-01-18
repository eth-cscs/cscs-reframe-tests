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
                    ],
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
                    ],
                    'launcher': 'mpirun'
                },
            ]
        },
    ],
    'environments': [
        {
            'name': 'PrgEnv-gnu',
            'target_systems': ['santis'],
            'cc': 'mpicc',
            'cxx': 'mpicxx',
            'ftn': 'mpif90',
            'modules': ['gnu-mpich'],
            'features': [
                'serial', 'openmp', 'mpi', 'alloc_speed',
                'hdf5', 'netcdf-hdf5parallel', 'pnetcdf', 'cdo', 'nco'
            ],
            'extras': {
                'c_openmp_flags': ['-fopenmp']
            }
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
