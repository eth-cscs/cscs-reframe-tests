# Copyright ETH Zurich/Swiss National Supercomputing Centre (CSCS)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import json
import os


def _format_victoriametrics(record, extras, ignore_keys):
    """
    From httpjson formatting:
      httpjson_record_1.json: {check_name:.._A, check_perf_var:A, check_perf_value:3.2, check_perf_ref:3.0}
      httpjson_record_2.json: {check_name:.._A, check_perf_var:B, check_perf_value:4.2, check_perf_ref:4.0}
      etc...

    to victoriametrics formatting:
      {metric:{__name__:check_name_A, check_perf_type:value, check_system:daint}, values:[3.2], timestamps:[2026-05-11]}
      {metric:{__name__:check_name_A, check_perf_type:ref, check_system:daint}, values:[3.0], timestamps:[2026-05-11]}
      and
      {metric:{__name__:check_name_A, check_perf_type:value, check_system:daint}, values:[4.2], timestamps:[2026-05-11]}
      {metric:{__name__:check_name_A, check_perf_type:ref, check_system:daint}, values:[4.0], timestamps:[2026-05-11]}
      etc...
    """
    _ = extras, ignore_keys
    selected_fields = {
        'check_name', 'check_perf_var', 'check_perf_unit', 'check_result', 'hostname',
        'check_partition', 'check_environ', 'check_perf_result', 'check_jobid',
        'check_system', 'check_executable', 'check_hashcode',
        'check_short_name', 'check_unique_name',
        'check_job_completion_time_unix', 'check_perf_value', 'check_perf_ref'
    }

    values = {
        key: value for key, value in vars(record).items()
        if key in selected_fields
    }

    def _or_default(field, default='x'):
        value = values.get(field)
        return value if value is not None else default

    base_metric = {
        "__name__": _or_default("check_unique_name"),
        "check_perf_var": _or_default("check_perf_var"),
        "check_perf_unit": _or_default("check_perf_unit"),
        "check_result": _or_default("check_result"),
        "hostname": _or_default("hostname"),
        "check_partition": _or_default("check_partition"),
        "check_environ": _or_default("check_environ"),
        "check_perf_result": _or_default("check_perf_result"),
        "check_jobid": _or_default("check_jobid"),
        "check_system": _or_default("check_system"),
        "check_executable": _or_default("check_executable"),
        "check_hashcode": _or_default("check_hashcode"),
        "data_stream_type": "logs",
        "data_stream_dataset": "performance_values",
        "data_stream_namespace": "reframe"
    }

    timestamp = values.get("check_job_completion_time_unix")
    timestamps = [1000 * int(timestamp)] if timestamp is not None else []

    payloads = []
    for perf_type, perf_key in (
        ("perf_ref", "check_perf_ref"),
        ("perf_value", "check_perf_value"),
    ):
        perf_value = values.get(perf_key)
        if perf_value is None:
            continue

        payloads.append({
            "metric": {**base_metric, "check_perf_type": perf_type},
            "values": [float(perf_value)],
            "timestamps": timestamps,
        })

    if not payloads:
        return None

    vm_data = "\n".join(json.dumps(payload) for payload in payloads)

    return vm_data


def _format_httpjson(record, extras, ignore_keys):
    """
    https://github.com/eth-cscs/cscs-reframe-tests/pull/380
    """
    data = {}
    for attr, val in record.__dict__.items():
        if attr in ignore_keys or attr.startswith('_'):
            continue

        if attr == "check_perf_value" and val is not None:
            data[attr] = float(val)
        elif attr == "check_perf_ref" and val is not None:
            data[attr] = float(val)
        else:
            data[attr] = val

    data.update(extras)

    return json.dumps(data)


reframe_dir = os.getenv(
    'REFRAME_DIR',
    '/capstor/store/cscs/cscs/public/reframe/reframe-stable/$CLUSTER_NAME'
)
target_dir_var_exists = bool(os.getenv('TARGET_DIR'))
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
                    # export RFM_HTTPJSON_URL='http://vminsert.o11y.cscs.ch:8480/insert/0/prometheus/api/v1/import'
                    'url': 'http://httpjson-server:12345/rfm',
                    'level': 'info',
                    'extra_headers': {
                        'Content-Type': 'application/x-ndjson'
                    },
                    # 'extras': {
                    #     'data_stream': {
                    #         'type': 'logs',
                    #         'dataset': 'performance_values',
                    #         'namespace': 'reframe'
                    #     },
                    #     'rfm_ci_pipeline': os.getenv("CI_PIPELINE_URL", "#"),
                    #     'rfm_ci_project': os.getenv("CI_PROJECT_PATH", "Unknown CI Project")
                    # },
                    # 'debug': True,
                    # "json_formatter": _format_httpjson,
                    "json_formatter": _format_victoriametrics,
                    'ignore_keys': ['check_perfvalues']
                }
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
                f'--prefix={os.getenv("TARGET_DIR") if target_dir_var_exists else target_dir_base + "/maint"}',  # noqa: E501
                f'--output={os.getenv("TARGET_DIR") if target_dir_var_exists else target_dir_base + "/maint"}',  # noqa: E501
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
                f'--prefix={os.getenv("TARGET_DIR") if target_dir_var_exists else target_dir_base + "/prod"}',  # noqa: E501
                f'--output={os.getenv("TARGET_DIR") if target_dir_var_exists else target_dir_base + "/prod"}',  # noqa: E501
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
                f'--prefix={os.getenv("TARGET_DIR") if target_dir_var_exists else target_dir_base + "/veto"}',  # noqa: E501
                f'--output={os.getenv("TARGET_DIR") if target_dir_var_exists else target_dir_base + "/veto"}',  # noqa: E501
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
                f'--prefix={os.getenv("TARGET_DIR") if target_dir_var_exists else target_dir_base + "/veto"}',  # noqa: E501
                f'--output={os.getenv("TARGET_DIR") if target_dir_var_exists else target_dir_base + "/veto"}',  # noqa: E501
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
            'pipeline_timeout': 1000  # https://reframe-hpc.readthedocs.io/en/stable/pipeline.html#tweaking-the-throughput-and-interactivity-of-test-jobs-in-the-asynchronous-execution-policy
        }
    ],
#     'autodetect_methods': [
#         'cat /etc/xthostname', 'hostname'
#     ]
}
