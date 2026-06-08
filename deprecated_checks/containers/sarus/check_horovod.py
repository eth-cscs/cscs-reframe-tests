import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class SarusHorovodTFCNNCheck(rfm.RunOnlyRegressionTest):
    sourcesdir = 'https://github.com/tensorflow/benchmarks'
    valid_systems = ['dom:gpu', 'daint:gpu']
    valid_prog_environs = ['builtin']
    container_platform = 'Sarus'
    num_tasks = 4
    num_tasks_per_node = 1

    reference = {
        '*': {
            'total_imgs_sec': (933, -0.05, None, 'images/s')
        }
    }
    maintainers = ['amadonna', 'taliaga']
    tags = {'production'}

    @run_after('setup')
    def setup_container_platform(self):
        self.prerun_cmds = [
            'sarus --version', 'git checkout cnn_tf_v1.8_compatible',
        ]
        self.container_platform.image = (
            'ethcscs/horovod:0.15.1-tf1.7.0-cuda9.0-mpich3.1.4-no-nccl'
        )
        self.container_platform.mount_points = [
            ('$(pwd)/scripts/', '/tf-scripts')
        ]
        self.container_platform.command = (
            'python /tf-scripts/tf_cnn_benchmarks/tf_cnn_benchmarks.py '
            '--model resnet50 --batch_size 64 --variable_update horovod'
        )
        self.container_platform.with_mpi = True

    @sanity_function
    def assert_sanity(self):
        found_imgs_per_sec = sn.extractall(
            r'total images/sec: (?P<total_imgs_sec>\S+)', self.stdout,
            'total_imgs_sec', float
        )
        return sn.assert_eq(sn.len(found_imgs_per_sec), 4)

    @run_before('performance')
    def set_perf(self):
        self.perf_patterns = {
            'total_imgs_sec':
                sn.extractsingle(r'total images/sec: (?P<total_imgs_sec>\S+)',
                                 self.stdout, 'total_imgs_sec', float)
        }
