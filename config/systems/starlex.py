# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings
#

reframe_dir = '/capstor/store/cscs/cscs/public/reframe/reframe-stable/$CLUSTER_NAME'

site_configuration = {
    'systems': [
        {
            'name': 'starlex',
            'descr': 'starlex vcluster',
            'hostnames': ['starlex'],
            'modules_system': 'lmod',
            'resourcesdir':
                '/capstor/store/cscs/cscs/public/reframe/resources',
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
                    'name': 'normal',
                    'scheduler': 'slurm',
                    'time_limit': '10m',
                    'environs': [
                        'builtin',
                    ],
                    'max_jobs': 100,
                    'extras': {
                        'cn_memory': 850,
                    },
                    'resources': [
                        {
                            'name': 'memory',
                            'options': ['--mem={mem_per_node}']
                        },
                        {
                            'name': 'gres',
                            'options': ['--gres={gres}']
                        },
                    ],
                    'features': ['ce', 'gpu', 'nvgpu', 'remote', 'scontrol',
                                 'uenv', 'hugepages_slurm'],
                    'devices': [
                        {
                            'type': 'gpu',
                            'arch': 'sm_90',
                            'num_devices': 4
                        }
                    ],
                    'launcher': 'srun'
                },
            ]
        },
    ],
    'modes': [
        {
            'name': 'production',
            'options': [
                f'-C {reframe_dir}/cscs-reframe-tests.git/config/cscs.py',
                f'-c {reframe_dir}/cscs-reframe-tests.git/checks/apps/quantumespresso',
                f'-c {reframe_dir}/cscs-reframe-tests.git/checks/apps/cp2k',
                f'-c {reframe_dir}/cscs-reframe-tests.git/checks/apps/namd',
                '--report-junit=report.xml',
                '--report-file=latest.json',
                '--tag=production',
                '--failure-stats',
                '--max-retries=2',
                '--prefix=/capstor/store/cscs/cscs/public/reframe/reframe-stable/$CLUSTER_NAME',
                '--timestamp=%F_%H-%M-%S',
                '-Sstrict_check=1',
            ],
            'target_systems': ['starlex'],
        },
        {
            'name': 'maintenance',
            'options': [
                f'-C {reframe_dir}/cscs-reframe-tests.git/config/cscs.py',
                f'-c {reframe_dir}/cscs-reframe-tests.git/checks',
                '--report-junit=report.xml',
                '--report-file=latest.json',
                '--tag=maintenance',
                '--failure-stats',
                '--max-retries=2',
                '--prefix=/capstor/store/cscs/cscs/public/reframe/reframe-stable/$CLUSTER_NAME',
                '--timestamp=%F_%H-%M-%S',
                '-Sstrict_check=1',
            ],
            'target_systems': ['starlex'],
        },
        {
            'name': 'veto',
            'options': [
                f'-C {reframe_dir}/cscs-reframe-tests.git/config/cscs.py',
                f'-c {reframe_dir}/cscs-reframe-tests.git/checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py',
                '--report-junit=report.xml',
                '--report-file=latest.json',
                '-S nb_duration=300',
                '--distribute=all',
                '--failure-stats',
                '--max-retries=2',
                '--prefix=/capstor/store/cscs/cscs/public/reframe/reframe-stable/$CLUSTER_NAME',
                '--timestamp=%F_%H-%M-%S',
                '-Sstrict_check=1',
            ],
            'target_systems': ['starlex'],
        }
    ]
}
