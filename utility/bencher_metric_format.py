# https://bencher.dev/docs/reference/bencher-metric-format/

import json
import sys
from pathlib import Path


def reframe_to_bmf(reframe_report):
    path = Path(reframe_report)
    if not path.exists():
        sys.exit(f"Error: File '{reframe_report}' not found.")

    with open(reframe_report, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Bencher Metric Format
    bmf = {}

    for run in data["runs"]:
        for testcase in run["testcases"]:
            if testcase["result"] != "pass":
                continue

            environ = testcase["environ"]
            partition = testcase["partition"]
            system = testcase["system"]

            perfvalues = testcase["perfvalues"]
            benchmark_measures = {}
            for k, v in perfvalues.items():
                measure = k.split(':')[-1]
                benchmark_measures[measure] = {"value": v[0]}

            benchmark_name = testcase["display_name"]
            bmf[benchmark_name] = benchmark_measures

    bencher_file_name = f"bencher={system}={partition}={environ}.json"
    with open(bencher_file_name, "w") as f:
        json.dump(bmf, f, indent=2)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(f"Usage: your_python {sys.argv[0]} <reframe_report.json>")

    reframe_to_bmf(sys.argv[1])
