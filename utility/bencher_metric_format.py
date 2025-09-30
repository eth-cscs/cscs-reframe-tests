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

    # Bencher Metric Format
    # Bencher can upload JSON files that follow this format
    bmf = {}

    environ = set()
    partition = set()
    system = set()
    for run in data["runs"]:
        for testcase in run["testcases"]:
            if testcase["result"] != "pass":
                continue

            environ.add(testcase["environ"])
            partition.add(testcase["partition"])
            system.add(testcase["system"])

            perfvalues = testcase["perfvalues"]
            benchmark_measures = {}
            for k, v in perfvalues.items():
                measure = k.split(':')[-1]
                benchmark_measures[measure] = {"value": v[0]}

            benchmark_name = testcase["display_name"]
            if benchmark_name in bmf:
                raise ValueError(
                    f"Error: Duplicate benchmark name '{benchmark_name}' "
                    f"found in the report."
                )
            bmf[benchmark_name] = benchmark_measures

    if not environ or not partition or not system:
        raise ValueError(
            "Error: No passing testcases found; "
            "cannot determine environment, partition, or system."
        )

    environ_ = environ.pop()
    partition_ = partition.pop()
    system_ = system.pop()
    if len(environ) != 0 or len(partition) != 0 or len(system) != 0:
        raise ValueError(
            "Error: A Bencher JSON file must report exactly one "
            "environment, partition, and system."
        )

    # The bencher file name is used in CI/CD as the testbed option
    bencher_file_name = f"bencher={system_}={partition_}={environ_}.json"
    with open(bencher_file_name, "w") as f:
        json.dump(bmf, f, indent=2)

    print(f"Bencher Metric Format file created: {bencher_file_name}",
          flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(f"Usage: your_python {sys.argv[0]} <reframe_report.json>")

    reframe_to_bmf(sys.argv[1])
