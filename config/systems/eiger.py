# Copyright 2025 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings
#

import os

import reframe.utility.osext as osext


def _cpe_ce_env():
    return {
        'name': 'PrgEnv-ce',
        'features': [
            'cpe', 'prgenv',
            'serial', 'openmp', 'mpi', 'containerized_cpe'],
        'resources': {
            'cpe_ce_image': {
                'image':
                    # Avoid interpreting '#' as a start of a comment
                    os.environ['CSCS_RFM_CPE_CE'].replace(r'#', r'\#')
            }
        }
    }

_cpe_ce_environs = (
    ['builtin', 'PrgEnv-ce'] if 'CSCS_RFM_CPE_CE' in os.environ else ['builtin']
)


site_configuration = {
    'systems': [
        {
            'name': 'eiger',
            'descr': 'Alps Eiger vcluster',
            'hostnames': ['eiger'],
            'modules_system': 'lmod',
            'resourcesdir':
                '/capstor/store/cscs/cscs/public/reframe/resources',
            'max_local_jobs': 50,
            'partitions': [
                {
                    'name': 'login',
                    'scheduler': 'local',
                    'time_limit': '10m',
                    'environs': [
                        'builtin',
                    ],
                    'descr': 'Login nodes',
                    'max_jobs': 50,
                    'launcher': 'local'
                },
                {
                    'name': 'normal',
                    'scheduler': 'slurm',
                    'time_limit': '10m',
                    'environs': _cpe_ce_environs,
                    'max_jobs': 1000,
                    'extras': {
                        'cn_memory': 485540,
                    },
                    'resources': [
                        {
                            'name': 'memory',
                            'options': ['--mem={mem_per_node}']
                        },
                        {
                            'name': 'cpe_ce_image',
                            'options': [
                                '--container-image={image}',
                             ]
                        },
                        {
                            'name': 'cpe_ce_mount',
                            'options': [
                                # Mount both the stagedir and the directory related
                                # used 3 levels above (the one related to the system)
                                # to be able to find fixtures
                                '--container-mounts={stagedir}/../../../,'  # split
                                '{stagedir}:/rfm_workdir',
                                '--container-workdir=/rfm_workdir'
                             ]
                        },
                        {
                            'name': 'cpe_ce_extra_mounts',
                            'options': [
                                '--container-mounts={mount}:{mount}',
                             ]
                        }
                    ],
                    'access': [f'--account={osext.osgroup()}'],
                    'features': ['ce', 'remote', 'scontrol', 'uenv'],
                    'launcher': 'srun'
                },
            ]
        },
    ],
    'environments': (
        [_cpe_ce_env()] if 'CSCS_RFM_CPE_CE' in os.environ else []
    ),
}
