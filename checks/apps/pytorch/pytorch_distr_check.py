import os
import reframe as rfm
import reframe.utility.sanity as sn


class pytorch_distr_cnn_base(rfm.RunOnlyRegressionTest):
    valid_systems = ['hohgant:gpu']
    valid_prog_environs = ['builtin']
    sourcesdir = 'src'
    num_tasks = 16
    num_tasks_per_node = 4
    num_gpus_per_node = 4
    throughput_per_gpu = 864.62
    throughput_total = throughput_per_gpu * num_tasks
    reference = {
        'hohgant:gpu': {
            'samples_per_sec_per_gpu': (throughput_per_gpu,
                                        -0.1, None, 'samples/sec'),
            'samples_per_sec_total': (throughput_total,
                                      -0.1, None, 'samples/sec')
        }
    }

    @sanity_function
    def assert_job_is_complete(self):
        return sn.assert_found(r'Total average', self.stdout),

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
class pytorch_distr_cnn(pytorch_distr_cnn_base):
    descr = 'Check the training throughput of a cnn'
    executable = './set_visible_devices.sh python cnn_distr.py'
    valid_systems = []  # FIXME: Remove when PyTorch is available on Hohgant


class pytorch_distr_cnn_containers(pytorch_distr_cnn_base):
    descr = 'Check the training throughput of a cnn with torch.distributed'

    @run_before('run')
    def set_visible_devices_per_rank(self):
        self.job.launcher.options = ['--mpi=pmi2', './set_visible_devices.sh']

    @run_before('run')
    def set_container_variables(self):
        self.container_platform.command = 'python cnn_distr.py'


@rfm.simple_test
class pytorch_distr_cnn_sarus(pytorch_distr_cnn_containers):
    container_platform = 'Sarus'

    @run_before('run')
    def set_container_variables(self):
        super().set_container_variables()
        self.container_platform.image = 'nvcr.io/nvidia/pytorch:22.08-py3'


@rfm.simple_test
class pytorch_distr_cnn_singularity(pytorch_distr_cnn_containers):
    container_platform = 'Singularity'

    @run_before('run')
    def set_container_variables(self):
        super().set_container_variables()
        self.container_platform.image = '/scratch/e1000/sarafael/pytorch_22.08-py3.sif'  # noqa E501
        self.container_platform.with_cuda = True
