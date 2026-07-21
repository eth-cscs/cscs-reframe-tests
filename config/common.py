# Copyright ETH Zurich/Swiss National Supercomputing Centre (CSCS)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import json
import os


def _format_httpjson(record, extras, ignore_keys):
    """
    https://github.com/eth-cscs/cscs-reframe-tests/pull/380
    """
    data = {}
    for attr, val in record.__dict__.items():
        if attr in ignore_keys or attr.startswith('_'):
            continue

        if attr == 'check_perf_value' and val is not None:
            data[attr] = float(val)
        elif attr == 'check_perf_ref' and val is not None:
            data[attr] = float(val)
        else:
            data[attr] = val

    data.update(extras)

    return json.dumps(data)


def _format_victoriametrics(record, extras, ignore_keys):
    data = {}
    for attr, val in record.__dict__.items():
        if attr in ignore_keys or attr.startswith('_'):
            continue

        if attr in ('check_perf_value', 'check_perf_ref') and val is not None:
            data[attr] = float(val)
        else:
            data[attr] = val

    data.update(extras)

    timestamp = data.get('check_job_completion_time_unix')
    timestamps = [int(timestamp * 1000)] if timestamp is not None else None

    # VMetrics labels must be strings; keep perf values out of labels
    labels = {
        k: str(v) if v is not None else ''
        for k, v in data.items()
        if k not in ('check_perf_value', 'check_perf_ref')
    }
    labels.setdefault('__name__', labels.get('check_unique_name', 'reframe'))

    lines = []
    for perf_key, perf_type in (
        ('check_perf_value', 'value'),
        ('check_perf_ref', 'ref'),
    ):
        perf_val = data.get(perf_key)
        if perf_val is None:
            continue

        payload = {
            'metric': {**labels, 'check_perf_type': perf_type},
            'values': [perf_val],
        }
        if timestamps is not None:
            payload['timestamps'] = timestamps

        lines.append(json.dumps(payload, separators=(',', ':')))

    return '\n'.join(lines) + '\n' if lines else None


reframe_dir = os.getenv(
    'CSCS_RFM_DIR',
    '/capstor/store/cscs/cscs/public/reframe/reframe-stable/$CLUSTER_NAME'
)
target_dir_var_exists = bool(os.getenv('CSCS_RFM_TARGET_DIR'))
target_dir_base = (
    '$SCRATCH/reframe/$CLUSTER_NAME' if not target_dir_var_exists else ''
)


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
            'perflog_multiline': True,
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
                    # Push to Elastic when $CSCS_RFM_HTTPJSON_URL_ES is set
                    # (see reframe/frontend/cli.py)
                    'url': os.getenv('CSCS_RFM_HTTPJSON_URL_ES',
                                     'http://dummy:1234/rfm'),
                    'level': 'info',
                    'extras': {
                        'data_stream': {
                            'type': 'logs',
                            'dataset': 'performance_values',
                            'namespace': 'reframe'
                        },
                        'rfm_ci_pipeline': os.getenv('CI_PIPELINE_URL', '#'),
                        'rfm_ci_project':
                            os.getenv('CI_PROJECT_PATH', 'Unknown CI Project')
                    },
                    'json_formatter': _format_httpjson,
                    'ignore_keys': ['check_perfvalues'],
                    'debug': False
                },
                {
                    'type': 'httpjson',
                    # Push to VictoriaMetrics when $CSCS_RFM_HTTPJSON_URL_VM is
                    # set (see reframe/frontend/cli.py)
                    'url': os.getenv('CSCS_RFM_HTTPJSON_URL_VM',
                                     'http://dummy:1234/rfm'),
                    'level': 'info',
                    'extra_headers': {
                        'Content-Type': 'application/x-ndjson'
                    },
                    'extras': {
                        'rfm_ci_pipeline': os.getenv('CI_PIPELINE_URL', '#'),
                        'rfm_ci_project':
                            os.getenv('CI_PROJECT_PATH', 'Unknown CI Project')
                    },
                    'json_formatter': _format_victoriametrics,
                    'ignore_keys': [
                        'check_perfvalues',
                        'check_info', 'version', 'check_fail_phase',
                        'check_fail_reason', 'check_perf_result',
                        'check_job_exitcode', 'check_job_nodelist',
                        'check_build_locally', 'check_build_time_limit',
                        'check_descr', 'check_env_vars',
                        'check_exclusive_access', 'check_executable',
                        'check_executable_opts', 'check_extra_resources',
                        'check_keep_files', 'check_local',
                        'check_maintainers', 'check_max_pending_time',
                        'check_modules', 'check_num_cpus_per_task',
                        'check_num_gpus_per_node', 'check_num_tasks',
                        'check_num_tasks_per_core', 'check_num_tasks_per_node',
                        'check_num_tasks_per_socket', 'check_postbuild_cmds',
                        'check_postrun_cmds', 'check_prebuild_cmds',
                        'check_prefix', 'check_prerun_cmds',
                        'check_readonly_files', 'check_short_name',
                        'check_sourcepath', 'check_sourcesdir',
                        'check_stagedir', 'check_strict_check', 'check_tags',
                        'check_time_limit', 'check_use_multithreading',
                        'check_valid_prog_environs', 'check_valid_systems',
                        'check_variables'
                    ],
                    'debug': False
                },
            ]
        }
    ],
    'modes': [
        {
            'name': 'maintenance',
            'options': [
                '-Sstrict_check=1',
                f'-c {reframe_dir}/cscs-reframe-tests.git/checks',
                '--max-retries=1',
                '--failure-stats',
                '--tag=maintenance|production',
                '-p \'(?!PrgEnv-ce)\'',
                f'--prefix={os.getenv("CSCS_RFM_TARGET_DIR") if target_dir_var_exists else target_dir_base + "/maint"}',  # noqa: E501
                f'--output={os.getenv("CSCS_RFM_TARGET_DIR") if target_dir_var_exists else target_dir_base + "/maint"}',  # noqa: E501
                '--timestamp=%F_%H-%M-%S'
            ]
        },
        {
            'name': 'production',
            'options': [
                '-Sstrict_check=1',
                f'-c {reframe_dir}/cscs-reframe-tests.git/checks',
                '--max-retries=1',
                '--failure-stats',
                '--tag=production',
                '-p \'(?!PrgEnv-ce)\'',
                f'--prefix={os.getenv("CSCS_RFM_TARGET_DIR") if target_dir_var_exists else target_dir_base + "/prod"}',  # noqa: E501
                f'--output={os.getenv("CSCS_RFM_TARGET_DIR") if target_dir_var_exists else target_dir_base + "/prod"}',  # noqa: E501
                '--timestamp=%F_%H-%M-%S'
            ]
        },
        {
            'name': 'veto',
            'options': [
                '-Sstrict_check=1',
                f'-c {reframe_dir}/cscs-reframe-tests.git/checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py',  # noqa: E501
                '--max-retries=1',
                '-S nb_duration=300',
                '--distribute=all',
                f'--prefix={os.getenv("CSCS_RFM_TARGET_DIR") if target_dir_var_exists else target_dir_base + "/veto"}',  # noqa: E501
                f'--output={os.getenv("CSCS_RFM_TARGET_DIR") if target_dir_var_exists else target_dir_base + "/veto"}',  # noqa: E501
                '--timestamp=%F_%H-%M-%S'
            ]
        },
        {
            'name': 'veto_flexible',
            'options': [
                '-Sstrict_check=1',
                f'-c {reframe_dir}/cscs-reframe-tests.git/checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py',  # noqa: E501
                '--max-retries=1',
                '-S nb_duration=300',
                '-S flexible=True',
                '--flex-alloc-nodes=avail',
                '--exec-policy=serial',
                f'--prefix={os.getenv("CSCS_RFM_TARGET_DIR") if target_dir_var_exists else target_dir_base + "/veto"}',  # noqa: E501
                f'--output={os.getenv("CSCS_RFM_TARGET_DIR") if target_dir_var_exists else target_dir_base + "/veto"}',  # noqa: E501
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
               '--max-retries=1',
               '--report-file=$PWD/latest.json',
               '-c checks',
               '--tag=maintenance|production',
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
                '--report-file=$SCRATCH/regression/production/reports/'
                'prod_report_{sessionid}.json',
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
                '--report-file=$SCRATCH/regression/production/reports/'
                'prod_report_{sessionid}.json',
                '--save-log-files',
                '--tag=appscheckout',
                '--exclude-tag=flexible',
                '--distribute=all',
                '-p \'(?!PrgEnv-ce)\'',
                '--timestamp=%F_%H-%M-%S'
            ]
        },
        {
            'name': 'daily_bencher',
            'options': [
                '--report-junit=report.xml',
                '--report-file=latest.json',
                '-c checks',
                '--tag=bencher'
            ],
        },
    ],
    'general': [
        {
            'check_search_path': ['checks/'],
            'check_search_recursive': True,
            'remote_detect': True,
            'resolve_module_conflicts': False,
            'pipeline_timeout': 1000
            # https://reframe-hpc.readthedocs.io/en/stable/pipeline.html
        }
    ],
#     'autodetect_methods': [
#         'cat /etc/xthostname', 'hostname'
#     ]
}
