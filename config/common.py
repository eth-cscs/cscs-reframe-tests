# Copyright 2016 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# ReFrame CSCS settings
#

import json
import os
import pprint


def _format_httpjson(record, extras, ignore_keys):
    """
    https://github.com/eth-cscs/cscs-reframe-tests/pull/380
    """
    data = {}
    for attr, val in record.__dict__.items():
        if attr in ignore_keys or attr.startswith('_'):
            continue

        if attr == "check_perf_value" and val:
            data[attr] = float(val)
        elif attr == "check_perf_ref" and val:
            data[attr] = float(val)
        else:
            data[attr] = val

    print(data["check_perf_value"])
    print(data["check_perf_ref"])

    data.update(extras)

    return json.dumps(data)


site_configuration = {
    'environments': [
        {
            'name': 'builtin',
            'cc': 'cc',
            'cxx': 'CC',
            'ftn': 'ftn',
            'features': ['builtin'],
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
            'perflog_compat': True,
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
                {
                    'type': 'httpjson',
                    # We are setting this from the environment
                    # to avoid polluting the logs from tests in the
                    # login nodes
                    'url': 'http://httpjson-server:12345/rfm',
                    'level': 'info',
                    'extras': {
                        'data_stream': {
                            'type': 'logs',
                            'dataset': 'performance_values',
                            'namespace': 'reframe'
                        },
                        'rfm_ci_pipeline': os.getenv("CI_PIPELINE_URL", "#"),
                        'rfm_ci_project': os.getenv("CI_PROJECT_PATH", "Unknown CI Project")
                    },
                    'debug': True,
                    "json_formatter": _format_httpjson,
#del                     'format_perfvars': (
#del                         '%(check_perf_value)s.xx|%(check_perf_unit)s|'
#del                         #'%(check_perf_ref)s|%(check_perf_lower_thres)s|'
#del                         #'%(check_perf_upper_thres)s|'
#del                     ),
                    'ignore_keys': ['check_perfvalues']
                }
            ]
        }
    ],
    'modes': [
        {
            'name': 'maintenance',
            'options': [
                '--unload-module=reframe',
                '-Sstrict_check=1',
                '--output=$SCRATCH/regression/maintenance',
                '--perflogdir=$SCRATCH/regression/maintenance/logs',
                '--stage=$SCRATCH/regression/maintenance/stage',
                '--report-file=$SCRATCH/regression/maintenance/reports/maint_report_{sessionid}.json',
                '--save-log-files',
                '-p \'(?!PrgEnv-ce)\'',
                '--tag=maintenance',
                '--timestamp=%F_%H-%M-%S',
            ]
        },
        {
            'name': 'production',
            'options': [
                '--unload-module=reframe',
                '-Sstrict_check=1',
                '--output=$SCRATCH/regression/production',
                '--perflogdir=$SCRATCH/regression/production/logs',
                '--stage=$SCRATCH/regression/production/stage',
                '--report-file=$SCRATCH/regression/production/reports/prod_report_{sessionid}.json',
                '--save-log-files',
                '-p \'(?!PrgEnv-ce)\'',
                '--tag=production',
                '--timestamp=%F_%H-%M-%S'
            ]
        },
        {
           'name': 'daily_production',
           'options': [
               '-Sstrict_check=1',
               '--max-retries=1',
               '--report-file=$PWD/latest.json',
               '-c checks',
               '-p \'(?!PrgEnv-ce)\'',
               '--tag=production',
               # TODO: re-enable once test is fixed
               '-x MLperfStorageCE'
           ]
        },
        {
            'name': 'cpe_ce_production',
            'options': [
                '--max-retries=1',
                '--report-file=$PWD/latest.json',
                '-c ../cscs-reframe-tests/checks/',
                '--tag=production',
                '-p PrgEnv-ce'
            ],
        },
        {
           'name': 'uenv_production',
           'options': [
               '-Sstrict_check=1',
               '--max-retries=1',
               '--report-file=$PWD/latest.json',
               '-c checks/apps',
               '-c checks/libraries',
               '-p \'(?!PrgEnv-ce)\'',
               '--tag=production'
           ]
        },
        {
           'name': 'uenv_deployment',
           'options': [
               '-Sstrict_check=1',
               '--report-file=$PWD/latest.json',
               '-c checks/apps',
               '-c checks/libraries',
               '-c checks/prgenv',
               "-p '(?!PrgEnv-.*|builtin)'",
           ]
        },
        {
            'name': 'appscheckout_flexible',
            'options': [
                '--unload-module=reframe',
                '-Sstrict_check=1',
                '--output=$SCRATCH/regression/production',
                '--perflogdir=$SCRATCH/regression/production/logs',
                '--stage=$SCRATCH/regression/production/stage',
                '--report-file=$SCRATCH/regression/production/reports/prod_report_{sessionid}.json',
                '--save-log-files',
                '--tag=appscheckout',
                '--tag=flexible',
                '--flex-alloc-nodes=all',
               '-p \'(?!PrgEnv-ce)\'',
                '--timestamp=%F_%H-%M-%S'
            ]
        },
        {
            'name': 'appscheckout_distributed',
            'options': [
                '--unload-module=reframe',
                '-Sstrict_check=1',
                '--output=$SCRATCH/regression/production',
                '--perflogdir=$SCRATCH/regression/production/logs',
                '--stage=$SCRATCH/regression/production/stage',
                '--report-file=$SCRATCH/regression/production/reports/prod_report_{sessionid}.json',
                '--save-log-files',
                '--tag=appscheckout',
                '--exclude-tag=flexible',
                '--distribute=all',
                '-p \'(?!PrgEnv-ce)\'',
                '--timestamp=%F_%H-%M-%S'
            ]
        },
    ],
    'general': [
        {
            'check_search_path': ['checks/'],
            'check_search_recursive': True,
            'remote_detect': True,
            'resolve_module_conflicts': False
        }
    ],
#     'autodetect_methods': [
#         'cat /etc/xthostname', 'hostname'
#     ]
}
