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
        'rocm/pytorch:rocm6.0_ubuntu20.04_py3.9_pytorch_1.13.1', # pt1.13.1
        'rocm/pytorch:rocm6.0_ubuntu20.04_py3.9_pytorch_2.1.1',  # pt2.1.0
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
    valid_systems = ['+ce +amdgpu']
    throughput_per_gpu = 500
    num_nodes = parameter([1, 3])
    venv = fixture(SetupAmdContainerVenv)

    @run_after('setup')
    def activate_venv(self):
        self.container_mounts = [f'{self.venv.stagedir}:{self.venv.stagedir}']
        self.container_image = self.venv.image
        self.executable = f""" bash -exc '
            unset CUDA_VISIBLE_DEVICES;  #HACK: ROCR & CUDA devs cannot be both set
            source {self.venv.path}/bin/activate;
            {self.executable}
        ' """
        self.job.launcher.options.append('--container-writable')
