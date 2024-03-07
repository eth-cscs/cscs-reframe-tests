import sys
import pathlib
import reframe as rfm
from pytorch_test_base import PyTorchTestBase

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))
from container_engine import ContainerEngineMixin  # noqa: E402


@rfm.simple_test
class PyTorchDdpSarus(PyTorchTestBase):
    valid_systems = ['+nvgpu +sarus']
    platform = 'Sarus'

    @run_before('run')
    def set_container_variables(self):
        self.container_platform = self.platform
        self.container_platform.command = self.executable
        self.container_platform.image = 'nvcr.io/nvidia/pytorch:22.12-py3'  # cuda11.8 pt1.14.0
        self.job.launcher.options.append('--mpi=pmi2')


@rfm.simple_test
class PyTorchDdpCeNv(PyTorchTestBase, ContainerEngineMixin):
    descr = 'Check the training throughput using the ContainerEngine and NVIDIA NGC'
    valid_systems = ['+ce +nvgpu']
    aws_ofi_nccl = parameter([True])
    image = parameter([
        'nvcr.io#nvidia/pytorch:22.08-py3', # same as AMD   pt1.13.1
        'nvcr.io#nvidia/pytorch:22.12-py3', # same as Sarus pt1.14.0
        'nvcr.io#nvidia/pytorch:23.10-py3', # same as AMD   pt2.1.0
        'nvcr.io#nvidia/pytorch:24.01-py3', # Latest        pt2.2.0
    ])
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
    image = parameter([
        'nvcr.io#nvidia/pytorch:24.01-py3', # Latest        pt2.2.0
    ])


@rfm.simple_test
class PyTorchDdpMambaNv(PyTorchTestBase):
    descr = 'Check the training throughput on bare-metal'
    valid_systems = ['+nvgpu']
    time_limit = '30m'
    torch_version = parameter([
        'pytorch torchvision nccl pytorch-cuda=11.8', # Latest cu11.8
        # 'pytorch torchvision nccl pytorch-cuda=12.1', # Latest cu12.1; incompatible driver
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
