import sys
import pathlib
import reframe as rfm
import reframe.utility.sanity as sn
import requests
import re
from packaging.version import Version
from pytorch_test_base import PyTorchTestBase
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))
from container_engine import ContainerEngineMixin  # noqa: E402



def latest_nvidia_pytorch_image_tags():

    token_response = requests.get("https://nvcr.io/proxy_auth?scope=repository:nvidia/pytorch:pull,push")
    tags_url = "https://nvcr.io/v2/nvidia/pytorch/tags/list"
    headers = {
        "Authorization": f"Bearer {token_response.json().get('token')}"
    }
    
    #Note: onle the "-py3" image is supported by the downstream tests (e.g. PyTorchDdpCeNv)
    supported_flavors = ["-py3"] 

    image_tags_response = requests.get(tags_url, headers=headers)
    tags = image_tags_response.json().get("tags", [])
    latest_tags = []
    for flavor in supported_flavors:

        versions = [tag[:-len(flavor)] for tag in tags if re.match(rf"^\d+\.\d+{flavor}$", tag)]
        if versions:
            latest_version = sorted(versions, key=Version, reverse=True)[0]
            latest_tags += [latest_version+flavor]

    return latest_tags

@rfm.simple_test
class test_image_latest_tag_retreival(rfm.RunOnlyRegressionTest):
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['builtin']
    executable = 'echo'

    @sanity_function
    def validate(self):
        return sn.assert_found(r'latest tags:', self.stdout)
    
    @run_before('run')
    def set_container_variables(self):
        self.executable_opts = ["latest tags:" + ",".join(latest_nvidia_pytorch_image_tags())]


@rfm.simple_test
class PyTorchDdpCeNv(PyTorchTestBase, ContainerEngineMixin):
    descr = 'Check the training throughput using the ContainerEngine and NVIDIA NGC'
    valid_systems = ['+ce +nvgpu']
    aws_ofi_nccl = parameter([True])
    curated_images = [
        #'nvcr.io#nvidia/pytorch:22.08-py3', # same as AMD   pt1.13.1
        #'nvcr.io#nvidia/pytorch:22.12-py3', # same as Sarus pt1.14.0
        #'nvcr.io#nvidia/pytorch:23.10-py3', # same as AMD   pt2.1.0
        'nvcr.io#nvidia/pytorch:24.01-py3', # Latest        pt2.2.0
    ]
    latest_images = ["nvcr.io#nvidia/pytorch:" + tag for tag in latest_nvidia_pytorch_image_tags()]
    image = parameter(curated_images + latest_images)

    env_vars = {
        'NCCL_DEBUG': 'Info',
    }
    tags = {'production', 'ce'}

    @run_after('init')
    def set_image(self):
        self.container_image = self.image
        if self.aws_ofi_nccl:
            cuda_major = 'cuda12' if self.image > 'nvcr.io#nvidia/pytorch:23' else 'cuda11'
            self.container_env_table = {
                'annotations.com.hooks': {
                    'aws_ofi_nccl.enabled': 'true',
                    'aws_ofi_nccl.variant': cuda_major,
                },
            }

@rfm.simple_test
class PyTorchDdpCeNvlarge(PyTorchDdpCeNv):
    aws_ofi_nccl = parameter([True, False])
    num_nodes = parameter([3, 8])

    curated_images = [
        'nvcr.io#nvidia/pytorch:24.01-py3', # Latest        pt2.2.0
    ]
    latest_images = ["nvcr.io#nvidia/pytorch:" + tag for tag in latest_nvidia_pytorch_image_tags()]
    image = parameter(curated_images + latest_images)


@rfm.simple_test
class PyTorchDdpMambaNv(PyTorchTestBase):
    descr = 'Check the training throughput on bare-metal'
    valid_systems = ['+nvgpu']
    time_limit = '30m'
    torch_version = parameter([
        #'pytorch torchvision nccl pytorch-cuda=11.8', # Latest cu11.8; aws-ofi-ccl-plugin/cuda11 not available
         'pytorch torchvision nccl pytorch-cuda=12.1', # Latest cu12.1; incompatible driver
    ])
    tags = {'production'}

    @run_after('setup')
    def activate_venv(self):
        self.prerun_cmds = [
            f'set -xe', f'. setup_conda.sh $PWD/forge',
            f'conda create -p $PWD/forge/envs/rfm {self.torch_version} '
            f'-c pytorch -c nvidia -y',
            f'conda activate $PWD/forge/envs/rfm',
            f'pip install python-hostlist',
            f'. activate_ofi.sh cuda11',
        ]

        self.postrun_cmds = ['rm Miniforge*.sh', 'rm -rf forge']
