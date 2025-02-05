import copy
import os


base_config = {
    'modules_system': 'lmod',
    # 'resourcesdir': '/apps/common/UES/reframe/resources',
    'partitions': [
        {
            'name': 'mc',
            'scheduler': 'firecrest-slurm',
            'time_limit': '10m',
            'container_platforms': [
                {
                    'type': 'Sarus',
                    'modules': ['sarus']
                },
                {
                    'type': 'Singularity',
                    'modules': ['singularity/3.6.4-eiger']
                }
            ],
            'modules': ['cray'],
            'access': [
                f'--constraint=mc',
                f'--account=csstaff'
            ],
            'environs': [
                'builtin',
                'PrgEnv-cray',
                'PrgEnv-gnu',
            ],
            'descr': 'Multicore nodes (AMD_EPYC_7742)',
            'max_jobs': 100,
            'extras': {
                'cn_memory': 64,
            },
            'features': ['remote', 'sarus', 'singularity'],
            'resources': [
                {
                    'name': 'switches',
                    'options': ['--switches={num_switches}']
                },
                {
                    'name': 'gres',
                    'options': ['--gres={gres}']
                }
            ],
            'launcher': 'srun'
        },
    ]
}

eiger_sys = copy.deepcopy(base_config)
eiger_sys['name'] = 'eiger'
eiger_sys['descr'] = 'Eiger'
eiger_sys['hostnames'] = ['eiger']


site_configuration = {
    'systems': [
        eiger_sys
    ],
    'environments': [
        {
            'name': 'PrgEnv-cray',
            'modules': ['PrgEnv-cray'],
            'target_systems': ['eiger', 'dom'],
            'features': ['mpi', 'openmp']
        },
        {
            'name': 'PrgEnv-gnu',
            'modules': ['PrgEnv-gnu'],
            'target_systems': ['eiger', 'dom'],
            'prepare_cmds': ['module unload PrgEnv-cray'],
            'features': ['mpi', 'openmp'],
        },
    ],
    'general': [
        {
            'resolve_module_conflicts': False,
            'use_login_shell': True,
            # Autodetection with this scheduler is really slow,
            # so it's better to disable it.
            'remote_detect': False,
            'target_systems': ['eiger', 'pilatus'],
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
            'target_systems': ['eiger'],
        }
    ]
}
