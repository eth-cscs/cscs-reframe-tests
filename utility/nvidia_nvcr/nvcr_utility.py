import requests
import re
from packaging.version import Version


def nvidia_image_tags(image_name:str):
    token_response = requests.get(
        f'https://nvcr.io/proxy_auth?scope=repository:nvidia/{image_name}:pull'
    )
    tags_url = f'https://nvcr.io/v2/nvidia/{image_name}/tags/list'
    headers = {
        'Authorization': f'Bearer {token_response.json().get("token")}'
    }
    image_tags_response = requests.get(tags_url, headers=headers)

    return image_tags_response.json().get('tags', [])
