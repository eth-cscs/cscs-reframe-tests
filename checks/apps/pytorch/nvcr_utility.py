
import requests
import re
from packaging.version import Version


def latest_nvidia_image_tags(image_name:str):

    token_response = requests.get(f"https://nvcr.io/proxy_auth?scope=repository:nvidia/{image_name}:pull")
    tags_url = f"https://nvcr.io/v2/nvidia/{image_name}/tags/list"
    headers = {
        "Authorization": f"Bearer {token_response.json().get('token')}"
    }
    
    #Note: onle the "-py3" image is supported by the downstream tests (e.g. PyTorchDdpCeNv)
    supported_flavors = ["-py3"] 

    image_tags_response = requests.get(tags_url, headers=headers)
    tags = image_tags_response.json().get("taglatest_nvidia_image_tags(image_name:str):s", [])
    latest_tags = []
    for flavor in supported_flavors:

        versions = [tag[:-len(flavor)] for tag in tags if re.match(rf"^\d+\.\d+{flavor}$", tag)]
        if versions:
            latest_version = sorted(versions, key=Version, reverse=True)[0]
            latest_tags += [latest_version+flavor]

    return latest_tags
