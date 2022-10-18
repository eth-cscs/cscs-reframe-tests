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


# @mpi.register_launcher('squashfs-run')
# class MyLauncher(mpi.SrunLauncher):
#     def run_command(self, job):
#         return ' '.join(self.command(job) + self.options + ['squashfs-run', '$STACKFILE'])

site_configuration = {
    'systems': [
        {
            'name': 'manali',
            'descr': 'Manali virtual cluster',
            'hostnames': ['manali', 'nid003120'],
            'modules_system': 'lmod',
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
                        # NOTE: /opt/cray/pe/lmod/modulefiles/core/
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
                    # TODO: use an env variable here ?
                    'access': ['-x nid003120,nid003240,nid003241'],
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
        #{{{ cray pe
        # NOTE: MPIDI_CRAY_init: GPU_SUPPORT_ENABLED is requested,
        #       but GTL library is not linked -> add -lgtl
        # 'PrgEnv-aocc',
        # 'PrgEnv-cray',
        # 'PrgEnv-gnu',
        # 'PrgEnv-nvhpc',
        # 'PrgEnv-nvidia'
        {
            'target_systems': ['manali'],
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
            'target_systems': ['manali'],
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
                'launcher_options': '--mpi=pmi2',
            },
        },
        {
            'target_systems': ['manali'],
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
                'launcher_options': '--mpi=pmi2',
            },
        },
        #}}}
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
    # {{{ logs and modes
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
                '--report-file=$APPS/UES/$USER/regression/maintenance/reports/maint_report_{sessionid}.json',
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
                '--report-file=$APPS/UES/$USER/regression/production/reports/prod_report_{sessionid}.json',
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
                '--report-file=$SCRATCH/$USER/regression/production/reports/prod_report_{sessionid}.json',
                '--save-log-files',
                '--tag=production',
                '--timestamp=%F_%H-%M-%S'
            ],
            'target_systems': ['hohgant'],
        }
    ],
    # }}}
    'general': [
        {
            'resolve_module_conflicts': False,
            'check_search_path': ['checks/'],
            'check_search_recursive': True,
            'remote_detect': True
        }
    ]
}
