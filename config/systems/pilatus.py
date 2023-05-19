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
    'resourcesdir': '/apps/common/UES/reframe/resources',
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
                    'modules': ['cray', 'singularity/3.5.3-eiger']
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

pilatus_sys = copy.deepcopy(base_config)
pilatus_sys['name'] = 'pilatus'
pilatus_sys['descr'] = 'Alps Cray EX Supercomputer TDS'
pilatus_sys['hostnames'] = ['pilatus']

site_configuration = {
    'systems': [
        pilatus_sys
    ],
    'environments': [
        {
            'name': 'PrgEnv-aocc',
            'target_systems': ['pilatus'],
            'modules': ['cray', 'PrgEnv-aocc']
        },
        {
            'name': 'PrgEnv-cray',
            'target_systems': ['pilatus'],
            'modules': ['cray', 'PrgEnv-cray']
        },
        {
            'name': 'PrgEnv-gnu',
            'target_systems': ['pilatus'],
            'modules': ['cray', 'PrgEnv-gnu']
        },
        {
            'name': 'PrgEnv-intel',
            'target_systems': ['pilatus'],
            'modules': ['cray', 'PrgEnv-intel']
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
}
