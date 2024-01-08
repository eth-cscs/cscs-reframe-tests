# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
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
    'resourcesdir': '/capstor/apps/cscs/common/regression/resources',
    'partitions': [
        {
            'name': 'login',
            'scheduler': 'local',
            'time_limit': '10m',
            'environs': [
                'builtin',
                'PrgEnv-aocc',
                'PrgEnv-cray',
                'PrgEnv-gnu',
                'PrgEnv-intel',
                'cpeAMD',
                'cpeCray',
                'cpeGNU',
                'cpeIntel'
            ],
            'descr': 'Login nodes',
            'max_jobs': 4,
            'launcher': 'local'
        },
        {
            'name': 'mc',
            'descr': 'Multicore nodes (AMD EPYC 7742, 256|512GB/cn)',
            'scheduler': 'slurm',
            'time_limit': '10m',
            'container_platforms': [
                {
                    'type': 'Sarus',
                },
                {
                    'type': 'Singularity',
                    'modules': ['cray', 'singularity/3.6.4-eiger']
                }
            ],
            'environs': [
                'builtin',
                'PrgEnv-aocc',
                'PrgEnv-cray',
                'PrgEnv-gnu',
                'PrgEnv-intel',
                'cpeAMD',
                'cpeCray',
                'cpeGNU',
                'cpeIntel'
            ],
            'max_jobs': 100,

            #FIXME temporary workaround for uenv=prgenv-gnu_23.11
            'env_vars': [
                [
                    'LD_LIBRARY_PATH',
                    '$LD_LIBRARY_PATH:/opt/cray/libfabric/1.15.2.0/lib64'
                ]
            ],
            'extras': {
                'cn_memory': 256,
            },
            'features': ['remote', 'sarus', 'singularity', 'uenv'],
            'access': ['-Cmc', f'--account={osext.osgroup()}'],
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
            'launcher': 'srun'
        },
    ]
}

pilatus_sys = copy.deepcopy(base_config)
pilatus_sys['name'] = 'pilatus'
pilatus_sys['descr'] = 'Alps Cray EX Supercomputer TDS'
pilatus_sys['hostnames'] = ['pilatus']
# pilatus_sys['partitions'].append(...)

site_configuration = {
    'systems': [
        pilatus_sys
    ],
    'environments': [
        {
            'name': 'PrgEnv-aocc',
            'target_systems': ['pilatus'],
            'modules': ['cray', 'PrgEnv-aocc'],
            'features': ['serial', 'openmp', 'mpi', 'cuda',
                         'hdf5', 'netcdf-hdf5parallel', 'pnetcdf', 'openmp']
        },
        {
            'name': 'PrgEnv-cray',
            'features': ['serial', 'openmp', 'mpi', 'cuda', 'openacc', 'hdf5',
                         'netcdf-hdf5parallel', 'pnetcdf', 'openmp', 'opencl'],
            'target_systems': ['pilatus'],
            'modules': ['cray', 'PrgEnv-cray']
        },
        {
            'name': 'PrgEnv-gnu',
            'target_systems': ['pilatus'],
            'features': ['serial', 'openmp', 'mpi', 'cuda', 'alloc_speed',
                         'hdf5', 'netcdf-hdf5parallel', 'pnetcdf', 'openmp'],
            'modules': ['cray', 'PrgEnv-gnu']
        },
        {
            'name': 'PrgEnv-intel',
            'target_systems': ['pilatus'],
            'modules': ['cray', 'PrgEnv-intel'],
            'features': ['serial', 'openmp', 'mpi', 'cuda', 'alloc_speed',
                         'hdf5', 'netcdf-hdf5parallel', 'pnetcdf', 'openmp']
        },
        {
            'name': 'cpeAMD',
            'target_systems': ['pilatus'],
            'modules': ['cray', 'cpeAMD']
        },
        {
            'name': 'cpeCray',
            'target_systems': ['pilatus'],
            'modules': ['cray', 'cpeCray']
        },
        {
            'name': 'cpeGNU',
            'target_systems': ['pilatus'],
            'modules': ['cray', 'cpeGNU']
        },
        {
            'name': 'cpeIntel',
            'target_systems': ['pilatus'],
            'modules': ['cray', 'cpeIntel']
        },
    ],
    'modes': [
       {
           'name': 'cpe_production',
           'options': [
               '--report-file=$PWD/latest.json',
               '-c checks/system/integration/eiger.py',
               '-c checks/prgenv/mpi.py',
               '-c checks/microbenchmarks/mpi/osu/osu_run.py',
               '-c checks/microbenchmarks/mpi/osu/osu_tests.py',
               '-c checks/microbenchmarks/cpu/alloc_speed/alloc_speed.py',
               '-c checks/microbenchmarks/cpu/stream/stream.py',
               '-c checks/prgenv/affinity_check.py',
           ],
           'target_systems': ['pilatus'],
       }
   ]

}
