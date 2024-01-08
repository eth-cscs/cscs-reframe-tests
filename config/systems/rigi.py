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
                    'modules': ['singularity/3.5.3-eiger']
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
            'extras': {
                'cn_memory': 256,
            },
            'features': ['remote', 'sarus', 'singularity'],
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


rigi_sys = copy.deepcopy(base_config)
rigi_sys['name'] = 'rigi'
rigi_sys['descr'] = 'Alps Cray EX Supercomputer TDS'
rigi_sys['hostnames'] = ['rigi']

site_configuration = {
    'systems': [
        rigi_sys
    ],
    'environments': [
        {
            'name': 'PrgEnv-aocc',
            'target_systems': ['rigi'],
            'modules': ['PrgEnv-aocc']
        },
        {
            'name': 'PrgEnv-cray',
            'target_systems': ['rigi'],
            'modules': ['PrgEnv-cray']
        },
        {
            'name': 'PrgEnv-gnu',
            'target_systems': ['rigi'],
            'modules': ['PrgEnv-gnu']
        },
        {
            'name': 'PrgEnv-intel',
            'target_systems': ['rigi'],
            'modules': ['PrgEnv-intel']
        },
        {
            'name': 'cpeAMD',
            'target_systems': ['rigi'],
            'modules': ['cpeAMD']
        },
        {
            'name': 'cpeCray',
            'target_systems': ['rigi'],
            'modules': ['cpeCray']
        },
        {
            'name': 'cpeGNU',
            'target_systems': ['rigi'],
            'modules': ['cpeGNU']
        },
        {
            'name': 'cpeIntel',
            'target_systems': ['rigi'],
            'modules': ['cpeIntel']
        },
    ],
}
