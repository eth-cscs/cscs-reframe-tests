import reframe as rfm
import reframe.utility.sanity as sn


class PyTorchTestBase(rfm.RunOnlyRegressionTest):
    descr = 'Check the training throughput of a cnn with torch.distributed'
    valid_systems = ['+gpu']
    valid_prog_environs = ['builtin']
    num_nodes = parameter([1])
    sourcesdir = 'src'
    throughput_per_gpu = 980
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
