# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings
#
import json
import os

import reframe.core.launchers.mpi as mpi
import reframe.utility.osext as osext


# @mpi.register_launcher('squashfs-run')
# class MyLauncher(mpi.SrunLauncher):
#     def run_command(self, job):
#         return ' '.join(
#             self.command(job) + self.options +
#             [f'--uenv-mount-file={uenv_mount_file}',
#              f'--uenv-mount-point={uenv_mount_point}',
#             ]
#             # ['squashfs-run', '$USER_ENV_IMAGE']
#         )


target_system = 'hohgant'
uenv_mount_file = os.environ.get('UENV_MOUNT_FILE', '/scratch/e1000/bcumming/balfrin.squashfs')
uenv_mount_point = os.environ.get('UENV_MOUNT_POINT', '/user-environment')
uenv_mpi_modulefile_gnu = os.environ.get('USER_ENV_MPI_GNU', 'cray-mpich-binary/8.1.18.4-gcc')
uenv_mpi_modulefile_nv = os.environ.get('USER_ENV_MPI_NV', 'cray-mpich-binary/8.1.18.4-nvhpc')
rfm_prefix = os.path.normpath(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
)
with open(f'{rfm_prefix}/common_logging.json', 'r') as cfg_file:
    logging_section = json.load(cfg_file)

site_configuration = {
    'systems': [
        {
            'name': target_system,
            'descr': 'Hohgant virtual cluster',
            'hostnames': [target_system],
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
                    'access': [
                        '-x nid003192',
                        f'--uenv-mount-file={uenv_mount_file}',
                        f'--uenv-mount-point={uenv_mount_point}',
                    ],
                    'prepare_cmds': [
                        'echo "# UENV_MOUNT_FILE=$UENV_MOUNT_FILE"',
                        'echo "# UENV_MOUNT_POINT=$UENV_MOUNT_POINT"',
                    ],
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
                    'launcher': 'srun'
                    # 'launcher': 'squashfs-run'
                }
            ]
        },
    ],
    'environments': [
        # {{{ squashfs pe
        # 'PrgEnv-gnu',
        # 'PrgEnv-nvidia'
        {
            'target_systems': [target_system],
            'name': 'PrgEnv-gnu',
            'variables': [
                ['USER_ENV_CUDA_VISIBLE',
                 os.environ.get('USER_ENV_CUDA_VISIBLE',
                                '$HOME/cuda_visible_devices.sh')],
                # ['MODULEPATH',
                #  os.path.join(os.environ.get('USER_ENV_ROOT', uenv_mount_point),
                #               'modules')],
            ],
            'modules': [
                {
                    'name': uenv_mpi_modulefile_gnu,
                    'path': os.path.join(
                        os.environ.get('USER_ENV_ROOT', uenv_mount_point),
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
            'target_systems': [target_system],
            'name': 'PrgEnv-nvidia',
            'variables': [
                ['USER_ENV_CUDA_VISIBLE',
                 os.environ.get('USER_ENV_CUDA_VISIBLE',
                                '$HOME/cuda_visible_devices.sh')],
                # ['MODULEPATH',
                #  os.path.join(os.environ.get('USER_ENV_ROOT', uenv_mount_point),
                #               'modules')],
            ],
            'modules': [
                {
                    'name': uenv_mpi_modulefile_nv,
                    'path': os.path.join(
                        os.environ.get('USER_ENV_ROOT', uenv_mount_point),
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
    'logging': [logging_section],
    'modes': [
        {
            'name': 'maintenance',
            'options': [
                '--unload-module=reframe',
                '--exec-policy=async',
                '-Sstrict_check=1',
                '--output=$SCRATCH/regression/maintenance',
                '--perflogdir=$SCRATCH/regression/maintenance/logs',
                '--stage=$SCRATCH/regression/maintenance/stage',
                '--report-file=$SCRATCH/regression/maintenance/reports/'
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
                '-Sstrict_check=1',
                '--output=$/regression/production',
                '--perflogdir=$CRATCH/regression/production/logs',
                '--stage=$SCRATCH/regression/production/stage',
                '--report-file=$SCRATCH/regression/production/reports/'
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
                '-Sstrict_check=1',
                '--prefix=$SCRATCH/$USER/regression/production',
                '--report-file=$SCRATCH/$USER/regression/production/reports/'
                'prod_report_{sessionid}.json',
                '--save-log-files',
                '--tag=production',
                '--timestamp=%F_%H-%M-%S'
            ],
            'target_systems': [target_system],
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
