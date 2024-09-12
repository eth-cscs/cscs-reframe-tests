import logging
import os
import requests
import sys


api_url = "https://oneuptime.com"
project_id = "ee08f8ce-375c-4082-95c6-dd55b2f0d1fd"
# api_key defined from environment variable in __main__
monitor_id_d = {
    # https://confluence.cscs.ch/display/SRM/
    # -> Status+Page+%7C+Phase-5%3A+list+of+monitors+provided+for+other+WS
    'cpe': {
        'todi': 'ae91f715-6595-4bd4-8c79-193b2cfcad00',
        'daint': '3fcb96ca-b7d1-4013-bc72-7833c4b17207',
        'eiger': 'eb64b621-2235-4835-a40a-97208fc05e89',
        'santis': 'd6902bfc-3ada-4f47-b4b1-26cf49267eb6',
        'clariden': '40203d20-1155-423b-9526-bce4c14a5181',
    },
    'uenv': {
        'todi': '9a93f7e5-96d1-414a-849d-d69de85208e6',
        'daint': '7a16cf8b-9936-4c2c-8f97-3d419c754753',
        'eiger': '4675d745-af62-4685-b86f-c18cd4507dda',
        'santis': '7f22e928-73a0-4337-b7e7-fab16f491a42',
        'clariden': 'cd133b6d-3968-48f3-b14d-9c689f4ac5b5',
    }
}
status_page_url = \
    'https://oneuptime.com/status-page/5edbd971-8b4b-4ff3-8f14-691a1fc94c31'
monitor_status = {
    "Operational": "834d4bc9-ae87-4a64-a281-fc91ffe2ea0a",
    "Degraded": "e8136eb1-2fb3-42f9-a3b6-f88d0772577a",
    "Offline": "c7d4079b-47d8-4011-917e-567409b5b4f2"
}


# {{{ set_monitor_status
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
# }}}        


if __name__ == '__main__':
    api_key = os.environ.get('RFM_ONEUPTIME_APIKEY', None)
    if api_key is None:
        print(f'Error: $RFM_ONEUPTIME_APIKEY is not set, exiting...')
        sys.exit(1)

    cluster_name, num_failures, cpe = sys.argv[1:4]
    if int(num_failures) == 0:
        status_label = "Operational"
    elif int(num_failures) == -1:
        status_label = "Offline"
    else:
        status_label = "Degraded"

    try:
        print(f"Updating {status_page_url} # {cpe}@{cluster_name}@{status_label}")
        set_monitor_status(monitor_id_d[cpe][cluster_name], status_label)
    except KeyError as e:
        print(f'Error: Unknown key err={e}')
        sys.exit(1)
    except Exception as e:
        print(f'Error: Unknown error err={e}')
        sys.exit(1)
