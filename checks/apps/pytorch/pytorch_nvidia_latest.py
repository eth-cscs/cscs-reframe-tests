import reframe as rfm
import reframe.utility.sanity as sn
from pytorch_test_base import PyTorchTestBase
import requests
import re
from packaging.version import Version
import pathlib
pathlib.Path(__file__).parent
from pytorch_nvidia import PyTorchDdpCeNv  # noqa: E402


def latest_nvidia_pytorch_image_tags():

    token_response = requests.get("https://nvcr.io/proxy_auth?scope=repository:nvidia/pytorch:pull,push")


    tags_url = "https://nvcr.io/v2/nvidia/pytorch/tags/list?n=5"
    headers = {
        "Authorization": f"Bearer {token_response.json().get('token')}"
    }

    image_tags_response = requests.get(tags_url, headers=headers)

    tags = image_tags_response.json().get("tags", [])
    versions = [re.search(r"^(\d+\.\d+)-.+$", tag, re.IGNORECASE).group(1) for tag in tags if re.match(r"^\d+\.\d+-.+$", tag)]
    latest_version = sorted(versions, key=Version, reverse=True)[0]
    latest_tags = [tag for tag in tags if tag.startswith(latest_version)]

    return latest_tags


@rfm.simple_test
class version_test(rfm.RunOnlyRegressionTest):
    valid_systems = ['*']
    valid_prog_environs = ['*']
    executable = 'echo "hello"'

    @sanity_function
    def validate(self):
        return sn.assert_found(r'hello', self.stdout)
    
    @run_before('run')
    def set_container_variables(self):
        tags = latest_nvidia_pytorch_image_tags()
        print(tags)
            



@rfm.simple_test
class PyTorchDdpSarus(PyTorchTestBase):
    valid_systems = ['+nvgpu +sarus']
    platform = 'Sarus'

    @run_before('run')
    def set_container_variables(self):
        self.container_platform = self.platform
        self.container_platform.command = self.executable
        self.container_platform.image = parameter(["nvcr.io/nvidia/pytorch:" + tag for tag in latest_nvidia_pytorch_image_tags()])
        self.job.launcher.options.append('--mpi=pmi2')

@rfm.simple_test
class PyTorchDdpCeNvLatest(PyTorchDdpCeNv):
    image = parameter(["nvcr.io/nvidia/pytorch:" + tag for tag in latest_nvidia_pytorch_image_tags()])

