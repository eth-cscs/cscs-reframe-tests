# Copyright 2016-2023 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings
#

# import reframe.utility.osext as osext
import copy

base_config =  {
    'modules_system': 'tmod',
    'resourcesdir': '/apps/common/UES/reframe/resources',
    'partitions': [
        {
            'name': 'login',
            'scheduler': 'local',
            'environs': [
                'PrgEnv-pgi',
                'PrgEnv-pgi-nompi',
                'PrgEnv-pgi-nocuda',
                'PrgEnv-pgi-nompi-nocuda',
                'PrgEnv-gnu',
                'PrgEnv-gnu-nompi',
                'PrgEnv-gnu-nocuda',
                'PrgEnv-gnu-nompi-nocuda'
            ],
            'descr': 'Tsa login nodes',
            'max_jobs': 4,
            'launcher': 'local'
        },
        {
            'name': 'pn',
            'scheduler': 'slurm',
            'access': ['--partition=pn-regression'],
            'environs': [
                'PrgEnv-pgi',
                'PrgEnv-pgi-nompi',
                'PrgEnv-pgi-nocuda',
                'PrgEnv-pgi-nompi-nocuda',
                'PrgEnv-gnu',
                'PrgEnv-gnu-nompi',
                'PrgEnv-gnu-nocuda',
                'PrgEnv-gnu-nompi-nocuda'
            ],
            'descr': 'Tsa post-processing nodes',
            'max_jobs': 20,
            'extras': {
                'cn_memory': 377,
            },
            'launcher': 'srun',
            'features': ['remote'],
        },
        {
            'name': 'cn',
            'scheduler': 'slurm',
            'access': ['--partition=cn-regression'],
            'environs': [
                'PrgEnv-gnu',
                'PrgEnv-gnu-nompi',
                'PrgEnv-gnu-nocuda',
                'PrgEnv-gnu-nompi-nocuda',
                'PrgEnv-pgi',
                'PrgEnv-pgi-nompi',
                'PrgEnv-pgi-nocuda',
                'PrgEnv-pgi-nompi-nocuda'
            ],
            'descr': 'Tsa compute nodes',
            'max_jobs': 20,
            'extras': {
                'cn_memory': 377,
            },
            'features': ['gpu', 'nvgpu', 'remote'],
            'resources': [
                {
                    'name': '_rfm_gpu',
                    'options': ['--gres=gpu:{num_gpus_per_node}']
                }
            ],
            'devices': [
                {
                    'type': 'gpu',
                    'arch': 'sm_70',
                    'num_devices': 8
                }
            ],
            'launcher': 'srun'
        }
    ]
}

tsa_sys = copy.deepcopy(base_config)
tsa_sys['name'] = 'tsa'
tsa_sys['descr'] = 'Tsa MCH'
tsa_sys['hostnames'] = [r'tsa-\w+\d+']

site_configuration = {
    'systems': [
        tsa_sys,
    ],
    'environments': [
        {
            'name': 'PrgEnv-pgi-nompi-nocuda',
            'target_systems': ['tsa'],
            'modules': ['PrgEnv-pgi/20.4-nocuda'],
            'cc': 'pgcc',
            'cxx': 'pgc++',
            'ftn': 'pgf90'
        },
        {
            'name': 'PrgEnv-pgi-nompi',
            'target_systems': ['tsa'],
            'modules': ['PrgEnv-pgi/20.4'],
            'features': ['cuda'],
            'cc': 'pgcc',
            'cxx': 'pgc++',
            'ftn': 'pgf90'
        },
        {
            'name': 'PrgEnv-pgi',
            'target_systems': ['tsa'],
            'modules': ['PrgEnv-pgi/20.4'],
            'features': ['cuda'],
            'cc': 'mpicc',
            'cxx': 'mpicxx',
            'ftn': 'mpifort'
        },
        {
            'name': 'PrgEnv-pgi-nocuda',
            'target_systems': ['tsa'],
            'modules': ['PrgEnv-pgi/20.4-nocuda'],
            'cc': 'mpicc',
            'cxx': 'mpicxx',
            'ftn': 'mpifort'
        },
        {
            'name': 'PrgEnv-gnu',
            'target_systems': ['tsa'],
            'modules': ['PrgEnv-gnu/19.2'],
            'features': ['cuda'],
            'cc': 'mpicc',
            'cxx': 'mpicxx',
            'ftn': 'mpifort'
        },
        {
            'name': 'PrgEnv-gnu-nocuda',
            'target_systems': ['tsa'],
            'modules': ['PrgEnv-gnu/19.2-nocuda'],
            'cc': 'mpicc',
            'cxx': 'mpicxx',
            'ftn': 'mpifort'
        },
        {
            'name': 'PrgEnv-gnu-nompi',
            'target_systems': ['tsa'],
            'modules': ['PrgEnv-gnu/19.2'],
            'features': ['cuda'],
            'cc': 'gcc',
            'cxx': 'g++',
            'ftn': 'gfortran'
        },
        {
            'name': 'PrgEnv-gnu-nompi-nocuda',
            'target_systems': ['tsa'],
            'modules': ['PrgEnv-gnu/19.2-nocuda'],
            'cc': 'gcc',
            'cxx': 'g++',
            'ftn': 'gfortran'
        },
    ]
}
