import os
import sys
import pathlib
import reframe as rfm
import reframe.utility.sanity as sn
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
    valid_systems = ['+ce +nvgpu']
    image = parameter([
        'nvcr.io#nvidia/pytorch:22.08-py3', # same as AMD   pt1.13.1
        'nvcr.io#nvidia/pytorch:22.12-py3', # same as Sarus pt1.14.0
        'nvcr.io#nvidia/pytorch:23.10-py3', # same as AMD   pt2.1.0
        'nvcr.io#nvidia/pytorch:24.01-py3', # Latest        pt2.2.0
    ])

    @run_after('init')
    def set_image(self):
        self.container_image = self.image
