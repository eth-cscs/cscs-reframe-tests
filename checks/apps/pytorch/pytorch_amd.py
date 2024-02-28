import os
import sys
import pathlib
import reframe as rfm
import reframe.utility.sanity as sn
from pytorch_test_base import PyTorchTestBase

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))
from container_engine import ContainerEngineMixin  # noqa: E402


class SetupAmdContainerVenv(rfm.RunOnlyRegressionTest, ContainerEngineMixin):
    descr = 'Test Fixture to install missing python packages in a venv'
    valid_systems = ['+ce +amdgpu']
    valid_prog_environs = ['builtin']
    num_tasks = 1
    tags = {'production'}
    image = parameter([
        # 'rocm/pytorch:rocm5.5_ubuntu20.04_py3.8_pytorch_1.13.1',
        'rocm/pytorch:rocm5.6_ubuntu20.04_py3.8_pytorch_1.13.1',
        # 'rocm/pytorch:rocm5.7_ubuntu20.04_py3.9_pytorch_1.13.1',
        # 'rocm/pytorch:rocm5.7_ubuntu20.04_py3.9_pytorch_2.0.1',  # F.conv2d/run_backward RuntimeError: miopenStatusUnknownError
        # 'rocm/pytorch:rocm5.7_ubuntu22.04_py3.10_pytorch_2.0.1',  # F.conv2d RuntimeError: miopenStatusUnknownError
        # 'rocm/pytorch:rocm6.0_ubuntu20.04_py3.9_pytorch_2.1.1',  # flacky segfaults
    ])
    executable = 'python -c \"import hostlist\"'
    venv_name = 'pyenv'

    @run_after('setup')
    def create_venv(self):
        self.container_mounts = [f'{self.stagedir}:{self.stagedir}']
        self.path = os.path.join(self.stagedir, self.venv_name)
        self.container_image = self.image
        self.executable = f""" bash -exc '
            python -m venv --system-site-packages {self.path}
            source {self.path}/bin/activate
            pip install python-hostlist
            {self.executable}
        ' """

    @sanity_function
    def assert_job_is_complete(self):
        return sn.assert_found(r'Successfully installed python-hostlist', self.stdout)


@rfm.simple_test
class PyTorchDdpCeAmd(PyTorchTestBase, ContainerEngineMixin):
    descr = 'Check the training throughput using the ContainerEngine and ROCm images'
    valid_systems = ['+ce +amdgpu']
    throughput_per_gpu = 530
    venv = fixture(SetupAmdContainerVenv)
    num_nodes = parameter([1, 2, 3])
    aws_ofi_nccl = parameter([True, False])
    env_vars = {
        'NCCL_DEBUG': 'Info',
    }

    @run_after('setup')
    def activate_venv(self):
        self.container_mounts = [f'{self.venv.stagedir}:{self.venv.stagedir}']
        self.container_image = self.venv.image
        self.job.launcher.options.append('--container-writable')
        self.executable = f""" bash -exc '
            unset CUDA_VISIBLE_DEVICES;  #HACK: ROCR & CUDA devs cannot be both set
            source {self.venv.path}/bin/activate;
            env;
            {self.executable}
        ' """
        if self.aws_ofi_nccl:
            rocm_major = 'rocm6' if 'rocm6' in self.venv.image else 'rocm5'
            self.container_env_table = {
                'annotations.com.hooks': {
                    'aws_ofi_nccl.enabled': 'true',
                    'aws_ofi_nccl.variant': rocm_major,
                },
            }


@rfm.simple_test
class PyTorchDdpPipAmd(PyTorchTestBase):
    descr = 'Check the training throughput with native cray-python and rocm'
    valid_systems = ['+amdgpu']
    modules = ['cray', 'rocm', 'cray-python']
    throughput_per_gpu = 530
    torch_version = parameter([
        'torch torchvision --index-url https://download.pytorch.org/whl/rocm5.0', # match cray rocm
        'torch torchvision --index-url https://download.pytorch.org/whl/rocm5.2', # pt1.13.1
        # 'torch torchvision --index-url https://download.pytorch.org/whl/rocm5.7', # Latest; rccl mismatch!
    ])
    prerun_cmds = [
        'python -m venv pyenv',
        '. pyenv/bin/activate',
        '. activate_ofi.sh rocm5 $ROCM_PATH/lib',
        'pip install python-hostlist',
    ]
    env_vars = {
        'MIOPEN_USER_DB_PATH': '/tmp',
        'NCCL_DEBUG': 'Info',
    }

    @run_after('setup')
    def activate_venv(self):
        self.executable = f""" bash -exc '
            unset CUDA_VISIBLE_DEVICES;  #HACK: ROCR & CUDA devs cannot be both set
            {self.executable}
        ' """
        self.prerun_cmds.append(f'pip install {self.torch_version}')
