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


target_system = 'manali'
rfm_prefix = os.path.normpath(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
)
with open(f'{rfm_prefix}/common_logging.json', 'r') as cfg_file:
    logging_section = json.load(cfg_file)

site_configuration = {
    'systems': [
        {
            'name': target_system,
            'descr': 'Manali virtual cluster',
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
                        'PrgEnv-aocc',
                        'PrgEnv-cray',
                        'PrgEnv-gnu',
                        'PrgEnv-nvhpc',
                        'PrgEnv-nvidia'
                    ],
                    'descr': 'Login nodes',
                    'max_jobs': 4,
                    'launcher': 'local',
                },
                {
                    'name': 'gpu',
                    'scheduler': 'slurm',
                    'environs': [
                        'builtin',
                        'PrgEnv-aocc',
                        'PrgEnv-cray',
                        'PrgEnv-gnu',
                        'PrgEnv-nvhpc',
                        'PrgEnv-nvidia'
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
                    'features': ['gpu', 'alps'],
                    'devices': [
                        {
                            'type': 'gpu',
                            'arch': 'sm_80',
                            'num_devices': 4
                        }
                    ],
                    'launcher': 'srun'
                }
            ]
        },
    ],
    'environments': [
        # {{{ cray pe
        # NOTE: MPIDI_CRAY_init: GPU_SUPPORT_ENABLED is requested,
        #       but GTL library is not linked -> add -lgtl
        # 'PrgEnv-aocc',
        # 'PrgEnv-cray',
        # 'PrgEnv-gnu',
        # 'PrgEnv-nvhpc',
        # 'PrgEnv-nvidia'
        {
            'target_systems': [target_system],
            'name': 'PrgEnv-aocc',
            # adding 'cpe' to workaround error:
            # /opt/cray/pe/libsci/22.08.1.1/AOCC/2.0/x86_64/lib/libsci_aocc_mp.so:
            # undefined reference to __kmpc_omp_task_alloc_with_deps@VERSION
            'modules': ['cray', 'PrgEnv-aocc', 'cpe'],
            'cppflags': ['-I$CUDA_HOME/include'],
            'ldflags': [
                '-L$CUDA_HOME/lib64', '-Wl,-rpath=$CUDA_HOME/lib64',
                '$PE_MPICH_GTL_DIR_nvidia80 $PE_MPICH_GTL_LIBS_nvidia80']
        },
        {
            'target_systems': ['manali'],
            'name': 'PrgEnv-cray',
            'modules': ['cray', 'PrgEnv-cray'],
            'cppflags': ['-I$CUDA_HOME/include'],
            'ldflags': [
                '-L$CUDA_HOME/lib64', '-Wl,-rpath=$CUDA_HOME/lib64',
                '$PE_MPICH_GTL_DIR_nvidia80 $PE_MPICH_GTL_LIBS_nvidia80']
        },
        {
            'target_systems': [target_system],
            'name': 'PrgEnv-gnu',
            'modules': ['cray', 'PrgEnv-gnu'],
            'cppflags': ['-I$CUDA_HOME/include'],
            'ldflags': [
                '-L$CUDA_HOME/lib64', '-Wl,-rpath=$CUDA_HOME/lib64',
                '$PE_MPICH_GTL_DIR_nvidia80 $PE_MPICH_GTL_LIBS_nvidia80']
        },
        {
            'target_systems': ['manali'],
            'name': 'PrgEnv-nvhpc',
            'modules': ['cray', 'PrgEnv-nvhpc'],
            # PrgEnv-nvhpc will not load cudatoolkit: CUDA_HOME will not be set
            'cppflags': ['-I$NVHPC/Linux_x86_64/2022/cuda/include'],
            'ldflags': [
                '-L$NVHPC/Linux_x86_64/2022/cuda/lib64',
                '-Wl,-rpath=$NVHPC/Linux_x86_64/2022/cuda/lib64',
                '$PE_MPICH_GTL_DIR_nvidia80 $PE_MPICH_GTL_LIBS_nvidia80'
            ],
            'extras': {
                # PrgEnv-nvhpc requires --mpi=pmi2 at runtime
                # "MPIR_pmi_init(83)....: PMI2_Job_GetId returned 14"
                'launcher_options': ['--mpi=pmi2'],
            },
        },
        {
            'target_systems': [target_system],
            'name': 'PrgEnv-nvidia',
            'modules': ['cray', 'PrgEnv-nvidia'],
            'cppflags': ['-I$CUDA_HOME/include'],
            'ldflags': [
                '-L$CUDA_HOME/lib64', '-Wl,-rpath=$CUDA_HOME/lib64',
                '$PE_MPICH_GTL_DIR_nvidia80 $PE_MPICH_GTL_LIBS_nvidia80'
            ],
            'extras': {
                # PrgEnv-nvidia requires --mpi=pmi2 at runtime:
                # "MPIR_pmi_init(83)....: PMI2_Job_GetId returned 14"
                'launcher_options': ['--mpi=pmi2'],
            },
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
