import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class SarusNvidiaSmiCheck(rfm.RunOnlyRegressionTest):
    valid_systems = ['+nvgpu +sarus']
    valid_prog_environs = ['builtin']
    num_tasks = 1
    num_tasks_per_node = 1
    container_platform = 'Sarus'
    image = 'nvidia/cuda:11.8.0-base-ubuntu18.04'
    tags = {'production'}

    @run_after('setup')
    def setup_gpu_options(self):
        curr_part = self.current_partition
        self.gpu_count = curr_part.select_devices('gpu')[0].num_devices
        cuda_visible_devices = ','.join(f'{i}' for i in range(self.gpu_count))
        self.env_vars['CUDA_VISIBLE_DEVICES'] = cuda_visible_devices
        self.num_gpus_per_node = self.gpu_count

    @run_after('setup')
    def setup_sarus(self):
        self.container_platform.image = self.image
        self.prerun_cmds = ['sarus --version', 'unset XDG_RUNTIME_DIR',
                            'nvidia-smi -L > native.out']
        self.container_platform.command = 'nvidia-smi -L > sarus.out'

    @sanity_function
    def assert_same_output(self):
        native_output = sn.extractall('GPU.*', 'native.out')
        sarus_output = sn.extractall('GPU.*', 'sarus.out')
        return sn.all([
            sn.assert_eq(native_output, sarus_output),
            sn.assert_eq(sn.len(native_output), self.gpu_count)
        ])
