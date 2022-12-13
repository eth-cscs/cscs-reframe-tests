import os
import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class pytorch_distr_cnn(rfm.RunOnlyRegressionTest):
    descr = 'Check the training throughput of a cnn with torch.distributed'
    platform = parameter(['native', 'Sarus'])
    valid_systems = ['hohgant:nvgpu']
    valid_prog_environs = ['builtin']
    sourcesdir = 'src'
    num_tasks = 16
    num_tasks_per_node = 4
    num_gpus_per_node = 4
    throughput_per_gpu = 864.62
    executable = 'python cnn_distr.py'
    throughput_total = throughput_per_gpu * num_tasks
    reference = {
        'hohgant:nvgpu': {
            'samples_per_sec_per_gpu': (throughput_per_gpu,
                                        -0.1, None, 'samples/sec'),
            'samples_per_sec_total': (throughput_total,
                                      -0.1, None, 'samples/sec')
        }
    }
    tags = {'production'}

    @run_after('init')
    def skip_native_test(self):
        # FIXME: Remove this when PyTorch is available on Hohgant
        self.modules = ['cray', 'cray-python']
        self.prerun_cmds = [
            '. /apps/hohgant/sarafael/deeplearning-env/bin/activate'
        ]

    @run_before('run')
    def set_container_variables(self):
        if self.platform != 'native':
            self.container_platform = self.platform
            self.container_platform.command = self.executable
            self.container_platform.image = 'nvcr.io/nvidia/pytorch:22.08-py3'

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

    @run_before('run')
    def set_visible_devices_per_rank(self):
        if self.platform != 'native':
            self.job.launcher.options == ['--mpi=pmi2']

        self.job.launcher.options.append('./set_visible_devices.sh')
