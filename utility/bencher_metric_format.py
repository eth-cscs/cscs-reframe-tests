# https://bencher.dev/docs/reference/bencher-metric-format/

import json

def reframe_to_bmf(reframe_report):
    with open(reframe_report, "r", encoding="utf-8") as f:
        data = json.load(f)

    for run in data["runs"]:
        for testcase in run["testcases"]:
            if testcase["result"] != "pass":
                continue
            environ = testcase["environ"]
            partition = testcase["partition"]
            system = testcase["system"]
            executable_opts = testcase["executable_opts"]
            perfvalues = testcase["perfvalues"]
            benchermark_name = testcase["display_name"]

            print(f"Environment: {environ}")
            print(f"Partition: {partition}")
            print(f"System: {system}")
            print(f"Executable Options: {executable_opts}")
            print(f"Performance Values: {perfvalues}")
            exit()

if __name__ == "__main__":
    reframe_to_bmf("latest.json")
