import logging
import os
import requests
import sys


api_url = "https://oneuptime.com"
project_id = "ee08f8ce-375c-4082-95c6-dd55b2f0d1fd"
# api_key defined as environment variable in __main__
monitor_id_d = {
    # https://confluence.cscs.ch/display/SRM/
    # -> Status+Page+%7C+Phase-5%3A+list+of+monitors+provided+for+other+WS
    'todi': '2de73dd3-0e06-437f-a8fd-fec3169e8b05',
    'daint': '6fff497c-941c-4289-b170-4743406fbae6',
    'eiger': '70f287fe-aa75-41fb-87fa-00458f2fa269',
    'santis': '693fe39c-a9e7-43ad-9f6e-a21c0123b8a6',
    'clariden': 'fac424a7-e4ae-4b19-987f-5f29e904a071'
    }
status_page_url = \
    'https://oneuptime.com/status-page/5edbd971-8b4b-4ff3-8f14-691a1fc94c31'
monitor_status = {
    "Operational": "834d4bc9-ae87-4a64-a281-fc91ffe2ea0a",
    "Degraded": "e8136eb1-2fb3-42f9-a3b6-f88d0772577a",
    "Offline": "c7d4079b-47d8-4011-917e-567409b5b4f2"
}


def set_monitor_status(monitor_id, status_label):
    # taken from Project -> Settings -> Monitor Status
    headers = {
        "Content-Type": "application/json",
        "ApiKey": f"{api_key}",
        "ProjectID": f"{project_id}"
    }

    body = {
        "data": {
            "currentMonitorStatusId": monitor_status[status_label]
        }
    }

    response = requests.put(
        f"{api_url}/api/monitor/{monitor_id}",
        headers=headers, json=body
    )

    logger = logging.getLogger(__name__)
    if response.status_code == 200:
        logger.info(
            f"PUT request was successful; monitor {monitor_id} is updated with"
            f" status {status_label}"
        )
    else:
        logger.error(
            f"PUT request failed with status code: {response.status_code}")
        raise Exception(
            f"PUT request failed with status code: {response.status_code}")


if __name__ == '__main__':
    api_key = os.environ.get('RFM_ONEUPTIME_APIKEY', None)
    if api_key is None:
        print(f'Error: $RFM_ONEUPTIME_APIKEY is not set, exiting...')
        sys.exit(1)

    cluster_name, num_failures = sys.argv[1:3]
    if int(num_failures) == 0:
        status_label = "Operational"
    elif int(num_failures) == -1:
        status_label = "Offline"
    else:
        status_label = "Degraded"

    try:
        print(f"Updating {status_page_url} # {cluster_name}@{status_label}")
        set_monitor_status(monitor_id_d[cluster_name], status_label)
    except KeyError as e:
        print(f'Error: Unknown key err={e}')
        sys.exit(1)
    except Exception as e:
        print(f'Error: Unknown error err={e}')
        sys.exit(1)
