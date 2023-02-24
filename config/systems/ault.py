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
            'name': 'ault',
            'descr': 'Ault TDS',
            'hostnames': ['ault'],
            'modules_system': 'lmod',
            'resourcesdir': '/apps/common/UES/reframe/resources',
            'partitions': [
                {
                    'name': 'login',
                    'scheduler': 'local',
                    'time_limit': '10m',
                    'environs': ['gnu'],
                    'descr': 'Login nodes',
                    'max_jobs': 4,
                    'launcher': 'local'
                },
                {
                    'name': 'a64fx',
                    'scheduler': 'slurm',
                    'time_limit': '10m',
                    'access': ['-pa64fx'],
                    'environs': ['gnu'],
                    'descr': 'Fujitsu A64FX CPUs',
                    'max_jobs': 100,
                    'launcher': 'srun',
                    'features': ['remote'],
                },
                {
                    'name': 'amda100',
                    'scheduler': 'slurm',
                    'time_limit': '10m',
                    'access': ['-pamda100'],
                    'environs': ['gnu', 'cuda'],
                    'descr': 'AMD Naples 32c + 4x NVIDIA A100',
                    'max_jobs': 100,
                    'launcher': 'srun',
                    'features': ['gpu', 'nvgpu', 'remote'],
                    'devices': [
                        {
                            'type': 'gpu',
                            'arch': 'sm_80',
                            'num_devices': 4
                        }
                    ]
                },
                {
                    'name': 'amdv100',
                    'scheduler': 'slurm',
                    'time_limit': '10m',
                    'access': ['-pamdv100'],
                    'environs': ['gnu', 'cuda'],
                    'descr': 'AMD Naples 32c + 2x NVIDIA V100',
                    'max_jobs': 100,
                    'launcher': 'srun',
                    'features': ['gpu', 'nvgpu', 'remote'],
                    'devices': [
                        {
                            'type': 'gpu',
                            'arch': 'sm_70',
                            'num_devices': 2
                        }
                    ]
                },
                {
                    'name': 'amdvega',
                    'scheduler': 'slurm',
                    'time_limit': '10m',
                    'access': ['-pamdvega'],
                    'environs': ['gnu', 'rocm'],
                    'descr': 'AMD Naples 32c + 3x AMD GFX900',
                    'max_jobs': 100,
                    'launcher': 'srun',
                    'features': ['gpu', 'amdgpu', 'remote'],
                    'devices': [
                        {
                            'type': 'gpu',
                            'arch': 'gfx900,gfx906',
                            'num_devices': 3
                        }
                    ]
                },
                {
                    'name': 'intelv100',
                    'scheduler': 'slurm',
                    'time_limit': '10m',
                    'access': ['-pintelv100'],
                    'environs': ['gnu', 'cuda'],
                    'descr': 'Intel Skylake 36c + 4x NVIDIA V100',
                    'max_jobs': 100,
                    'launcher': 'srun',
                    'features': ['gpu', 'nvgpu', 'remote'],
                    'devices': [
                        {
                            'type': 'gpu',
                            'arch': 'sm_70',
                            'num_devices': 4
                        }
                    ]
                },
                {
                    'name': 'intel',
                    'scheduler': 'slurm',
                    'time_limit': '10m',
                    'access': ['-pintel'],
                    'environs': ['gnu'],
                    'descr': 'Intel Skylake 36c',
                    'max_jobs': 100,
                    'launcher': 'srun',
                    'features': ['remote'],
                }
            ]
        },
    ],
    'environments': [
        {
            'name': 'gnu',
            'modules': ['gcc'],
            'cc': 'gcc',
            'cxx': 'g++',
            'ftn': 'gfortran',
            'target_systems': ['ault']
        },
        {
            'name': 'cuda',
            'modules': ['gcc', 'cuda'],
            'cc': 'gcc',
            'cxx': 'g++',
            'ftn': 'gfortran',
            'target_systems': ['ault'],
            'features': ['cuda']
        },
        {
            'name': 'rocm',
            'modules': ['gcc', 'rocm'],
            'cc': 'gcc',
            'cxx': 'g++',
            'ftn': 'gfortran',
            'target_systems': ['ault'],
            'features': ['hip']
        },
    ],

}
