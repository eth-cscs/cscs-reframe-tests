import os
import sys
import pathlib
import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))
from container_engine import ContainerEngineMixin  # noqa: E402


class pytorch_distr_cnn(rfm.RunOnlyRegressionTest):
    descr = 'Check the training throughput of a cnn with torch.distributed'
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['builtin']
    num_nodes = parameter([1, 2, 4, 8])
    sourcesdir = 'src'
    throughput_per_gpu = 800
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
class PyTorchDdpCE(pytorch_distr_cnn, ContainerEngineMixin):
    valid_systems = ['+ce +nvgpu']
    container_image = 'nvcr.io#nvidia/pytorch:24.01-py3'


@rfm.simple_test
class PyTorchDdpSarus(pytorch_distr_cnn):
    valid_systems = ['+nvgpu']
    platform = 'Sarus'

    @run_before('run')
    def set_container_variables(self):
        self.container_platform = self.platform
        self.container_platform.command = self.executable
        self.container_platform.image = 'nvcr.io/nvidia/pytorch:22.12-py3'  # cuda11.8
        self.job.launcher.options.append('--mpi=pmi2')
