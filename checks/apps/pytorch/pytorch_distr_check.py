import os
import sys
import pathlib
import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))
from container_engine import ContainerEngineMixin  # noqa: E402


class PyTorchTestBase(rfm.RunOnlyRegressionTest):
    descr = 'Check the training throughput of a cnn with torch.distributed'
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['builtin']
    num_nodes = parameter([1, 3, 8])
    sourcesdir = 'src'
    throughput_per_gpu = 950
    executable = 'python cnn_distr.py'
    tags = {'production'}

    @run_after('setup')
    def setup_test(self):
        curr_part = self.current_partition
        self.num_gpus_per_node = curr_part.select_devices('gpu')[0].num_devices
        self.num_tasks_per_node = self.num_gpus_per_node
        self.num_tasks = self.num_nodes * self.num_tasks_per_node
        self.throughput_total = self.throughput_per_gpu * self.num_tasks
        self.reference = {
            '*': {
                'samples_per_sec_per_gpu': (self.throughput_per_gpu,
                                            -0.1, None, 'samples/sec'),
                'samples_per_sec_total': (self.throughput_total,
                                        -0.1, None, 'samples/sec')
            }
        }
        self.job.launcher.options += ['-l --gpus-per-task=1']

    @sanity_function
    def assert_job_is_complete(self):
        return sn.assert_found(r'Total average', self.stdout)

    @performance_function('samples/sec')
    def samples_per_sec_per_gpu(self):
        return sn.avg(sn.extractall(
            r'Epoch\s+\d+\:\s+(?P<samples_per_sec_per_gpu>\S+)\s+images',
            self.stdout, 'samples_per_sec_per_gpu', float
        ))

    @performance_function('samples/sec')
    def samples_per_sec_total(self):
        return sn.avg(sn.extractall(
            r'Total average: (?P<samples_per_sec_total>\S+)\s+images',
            self.stdout, 'samples_per_sec_total', float
        ))



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



class SetupAmdContainerVenv(rfm.RunOnlyRegressionTest, ContainerEngineMixin):
    """ Test Fixture to install missing python packages in a venv """
    descr = ''
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
