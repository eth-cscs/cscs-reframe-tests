# https://bencher.dev/docs/reference/bencher-metric-format/

import json
import sys
from pathlib import Path


def reframe_to_bmf(reframe_report):
    path = Path(reframe_report)
    if not path.exists():
        sys.exit(f"Error: File '{reframe_report}' not found.")

    print("Converting ReFrame report to Bencher Metric Format...", flush=True)
    print(f"File: {reframe_report}", flush=True)

    with open(reframe_report, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Bencher Metric Format: format used to upload JSON files on bencher.dev
    # testcases with key (system, partition, environ) to handle multiple
    # partitions
    bmf_testcase = {}

    for run in data["runs"]:
        for testcase in run["testcases"]:
            if testcase["result"] != "pass":
                if testcase["fail_phase"] != "performance":
                    continue

            key = (testcase["system"],
                   testcase["partition"],
                   testcase["environ"])

            if key not in bmf_testcase:
                bmf_testcase[key] = {}

            perfvalues = testcase["perfvalues"]
            benchmark_measures = {}
            for k, v in perfvalues.items():
                measure = k.split(':')[-1]
                benchmark_measures[measure] = {"value": v[0]}

            benchmark_name = testcase["display_name"]
            if benchmark_name in bmf_testcase[key]:
                raise ValueError(
                    f"Error: Duplicate benchmark name '{benchmark_name}' "
                    f"found in the report for {key}."
                )
            bmf_testcase[key][benchmark_name] = benchmark_measures

    if not bmf_testcase:
        raise ValueError(
            "Error: No passing testcases found; "
            "cannot determine environment, partition, or system."
        )

    # The bencher file name is used in CI/CD as the testbed option
    for (system_, partition_, environ_), bmf in bmf_testcase.items():
        bencher_file_name = f"bencher={system_}={partition_}={environ_}.json"
        with open(bencher_file_name, "w") as f:
            json.dump(bmf, f, indent=2)

        print(f"Bencher Metric Format file created: {bencher_file_name}",
              flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(f"Usage: your_python {sys.argv[0]} <reframe_report.json>")

    reframe_to_bmf(sys.argv[1])
