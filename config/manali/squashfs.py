# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings
#
import os

import reframe.core.launchers.mpi as mpi
import reframe.utility.osext as osext


@mpi.register_launcher('squashfs-run')
class MyLauncher(mpi.SrunLauncher):
    def run_command(self, job):
        return ' '.join(
            self.command(job) + self.options +
            ['squashfs-run', '$USER_ENV_IMAGE']
        )


site_configuration = {
    'systems': [
        {
            'name': 'manali',
            'descr': 'Manali virtual cluster',
            'hostnames': ['manali'],
            'modules_system': 'lmod',
            # TODO: use jfrog
            'resourcesdir': '/scratch/e1000/piccinal/resources',
            'partitions': [
                {
                    'name': 'login',
                    'scheduler': 'local',
                    'time_limit': '10m',
                    'environs': [
                        'builtin',
                        'PrgEnv-gnu',
                        'PrgEnv-nvidia'
                    ],
                    'descr': 'Login nodes',
                    'max_jobs': 4,
                    'launcher': 'local',
                },
                {
                    'name': 'gpu-squashfs',
                    'scheduler': 'slurm',
                    'environs': [
                        'builtin',
                        'PrgEnv-gnu',
                        'PrgEnv-nvidia',
                    ],
                    'container_platforms': [
                        {
                            'type': 'Sarus',
                        },
                        {
                            'type': 'Singularity',
                        }
                    ],
                    'max_jobs': 100,
                    'extras': {
                        'cn_memory': 500,
                    },
                    # TODO: use an env variable here ?
                    'access': ['-x nid003048'],
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
                    'features': ['gpu'],
                    'devices': [
                        {
                            'type': 'gpu',
                            'arch': 'sm_80',
                            'num_devices': 4
                        }
                    ],
                    'launcher': 'squashfs-run'
                }
            ]
        },
    ],
    'environments': [
        # {{{ squashfs pe
        # 'PrgEnv-gnu',
        # 'PrgEnv-nvidia'
        {
            'target_systems': ['manali'],
            'name': 'PrgEnv-gnu',
            'variables': [
                ['USER_ENV_IMAGE',
                 os.environ.get('USER_ENV_IMAGE',
                                '/scratch/e1000/bcumming/balfrin.squashfs')],
                ['USER_ENV_ROOT',
                 os.environ.get('USER_ENV_ROOT',
                                '/user-environment/modules')],
                ['USER_ENV_CUDA_VISIBLE',
                 os.environ.get('USER_ENV_CUDA_VISIBLE',
                                '$HOME/cuda_visible_devices.sh')],
                ['MODULEPATH',
                 os.path.join(os.environ.get('USER_ENV_ROOT',
                                             '/user-environment'), 'modules')],
            ],
            'modules': [
                {
                    'name': 'cray-mpich-binary/8.1.18.4-gcc',
                    'path': os.path.join(
                        os.environ.get('USER_ENV_ROOT', '/user-environment'),
                        'modules'
                    ),
                },
            ],
            'features': ['squashfs'],
            'cc': 'mpicc',
            'cxx': 'mpicxx',
            'ftn': 'mpif90',
            'cppflags': ['-I$CUDA_HOME/include'],
            'ldflags': ['-L$CUDA_HOME/lib64', '-Wl,-rpath=$CUDA_HOME/lib64'],
        },
        {
            'target_systems': ['manali'],
            'name': 'PrgEnv-nvidia',
            'variables': [
                ['USER_ENV_IMAGE',
                 os.environ.get('USER_ENV_IMAGE',
                                '/scratch/e1000/bcumming/balfrin.squashfs')],
                ['USER_ENV_ROOT',
                 os.environ.get('USER_ENV_ROOT',
                                '/user-environment/modules')],
                ['USER_ENV_CUDA_VISIBLE',
                 os.environ.get('USER_ENV_CUDA_VISIBLE',
                                '$HOME/cuda_visible_devices.sh')],
                ['MODULEPATH',
                 os.path.join(os.environ.get('USER_ENV_ROOT',
                                             '/user-environment'), 'modules')],
            ],
            'modules': [
                {
                    'name': 'cray-mpich-binary/8.1.18.4-nvhpc',
                    'path': os.path.join(
                        os.environ.get('USER_ENV_ROOT', '/user-environment'),
                        'modules'
                    ),
                },
            ],
            'features': ['squashfs'],
            'cc': 'mpicc',
            'cxx': 'mpicxx',
            'ftn': 'mpif90',
            'cppflags': ['-I$CUDA_HOME/include'],
            'ldflags': ['-L$CUDA_HOME/lib64', '-Wl,-rpath=$CUDA_HOME/lib64'],
        },
        # }}}
        {
            'name': 'builtin',
            'cc': 'cc',
            'cxx': 'CC',
            'ftn': 'ftn'
        },
        {
            'name': 'builtin-gcc',
            'cc': 'gcc',
            'cxx': 'g++',
            'ftn': 'gfortran'
        }
    ],
    'logging': [
        {
            'handlers': [
                {
                    'type': 'file',
                    'name': 'reframe.log',
                    'level': 'debug2',
                    'format': '[%(asctime)s] %(levelname)s: %(check_info)s: %(message)s',   # noqa: E501
                    'append': False
                },
                {
                    'type': 'stream',
                    'name': 'stdout',
                    'level': 'info',
                    'format': '%(message)s'
                },
                {
                    'type': 'file',
                    'name': 'reframe.out',
                    'level': 'info',
                    'format': '%(message)s',
                    'append': False
                }
            ],
            'handlers_perflog': [
                {
                    'type': 'filelog',
                    'prefix': '%(check_system)s/%(check_partition)s',
                    'level': 'info',
                    'format': '%(check_job_completion_time)s|reframe %(version)s|%(check_info)s|jobid=%(check_jobid)s|num_tasks=%(check_num_tasks)s|%(check_perf_var)s=%(check_perf_value)s|ref=%(check_perf_ref)s (l=%(check_perf_lower_thres)s, u=%(check_perf_upper_thres)s)|%(check_perf_unit)s',   # noqa: E501
                    'datefmt': '%FT%T%:z',
                    'append': True
                },
#                 {
#                     'type': 'httpjson',
#                     'url': 'http://httpjson-server:12345/rfm',
#                     'level': 'info',
#                     'extras': {
#                         'facility': 'reframe',
#                         'data-version': '1.0',
#                     }
#                 }
            ]
        }
    ],
    'modes': [
        {
            'name': 'maintenance',
            'options': [
                '--unload-module=reframe',
                '--exec-policy=async',
                '--strict',
                '--output=$APPS/UES/$USER/regression/maintenance',
                '--perflogdir=$APPS/UES/$USER/regression/maintenance/logs',
                '--stage=$SCRATCH/regression/maintenance/stage',
                '--report-file=$APPS/UES/$USER/regression/maintenance/reports/'
                'maint_report_{sessionid}.json',
                '-Jreservation=maintenance',
                '--save-log-files',
                '--tag=maintenance',
                '--timestamp=%F_%H-%M-%S'
            ]
        },
        {
            'name': 'production',
            'options': [
                '--unload-module=reframe',
                '--exec-policy=async',
                '--strict',
                '--output=$APPS/UES/$USER/regression/production',
                '--perflogdir=$APPS/UES/$USER/regression/production/logs',
                '--stage=$SCRATCH/regression/production/stage',
                '--report-file=$APPS/UES/$USER/regression/production/reports/'
                'prod_report_{sessionid}.json',
                '--save-log-files',
                '--tag=production',
                '--timestamp=%F_%H-%M-%S'
            ]
        },
        {
            'name': 'production',
            'options': [
                '--unload-module=reframe',
                '--exec-policy=async',
                '--strict',
                '--prefix=$SCRATCH/$USER/regression/production',
                '--report-file=$SCRATCH/$USER/regression/production/reports/'
                'prod_report_{sessionid}.json',
                '--save-log-files',
                '--tag=production',
                '--timestamp=%F_%H-%M-%S'
            ],
            'target_systems': ['hohgant'],
        }
    ],
    'general': [
        {
            'resolve_module_conflicts': False,
            'check_search_path': ['checks/'],
            'check_search_recursive': True,
            'remote_detect': True
        }
    ]
}
