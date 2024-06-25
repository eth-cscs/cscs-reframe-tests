import sys
import pathlib

from pkg_resources import working_set
import reframe as rfm
import reframe.utility.sanity as sn
from pytorch_test_base import PyTorchTestBase

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))
from container_engine import ContainerEngineMixin  # noqa: E402


"""
./benchmark.sh run --hosts localhost --workload unet3d --accelerator-type h100 --num-accelerators 1 --results-dir resultsdir --param dataset.num_files_train=40 --param dataset.data_folder=unet3d_data
HYDRA_FULL_ERROR=1 RDMAV_FORK_SAFE=1 ./benchmark.sh run --hosts localhost --workload unet3d --accelerator-type h100 --num-accelerators 1 --results-dir resultsdir --param dataset.num_files_train=40 --param dataset.data_folder=unet3d_data
"""

class MLperfStorageBase(rfm.RunOnlyRegressionTest):
    descr = 'Check the training throughput using the ContainerEngine and NVIDIA NGC'
    image = 'henriquemendonca/mlperf-storage:v1.0-rc1'
    valid_prog_environs = ['builtin']
    num_nodes = parameter([1, 2])
    num_files = 512
    accelerator_type = 'h100'
    workload = 'unet3d'
    tags = {'production'}
    env_vars = {
        'HYDRA_FULL_ERROR': '1',
        'RDMAV_FORK_SAFE': '1',
    }
    
    @run_after('setup')
    def setup_test(self):
        curr_part = self.current_partition
        self.num_gpus_per_node = curr_part.select_devices('gpu')[0].num_devices
        self.num_tasks_per_node = self.num_gpus_per_node
        self.num_tasks = self.num_nodes * self.num_tasks_per_node
        
        self.prerun_cmds = [
            'set -x',
            'export HOSTS=$(scontrol show hostname $SLURM_NODELIST|paste -sd,)',
        ]
       
        self.executable = f""" bash -c ' \
            set -x; \
            ./benchmark.sh datagen --workload {self.workload} --accelerator-type {self.accelerator_type} --num-parallel {self.num_tasks} \
                --param dataset.num_files_train={self.num_files} --param dataset.data_folder=unet3d_data; \
            ./benchmark.sh run --workload {self.workload} --accelerator-type {self.accelerator_type} --num-accelerators {self.num_tasks} \
                --hosts $HOSTS \
                --results-dir resultsdir --param dataset.num_files_train={self.num_files} \
                --param dataset.data_folder=unet3d_data; \
        ' """
        # # clean up data
        # self.postrun_cmds = ['rm -rf unet3d_data']

        self.reference = {
            '*': {
                'mb_per_sec_total': (800, -0.1, None, 'MB/second'),
            }
        }

        # self.throughput_total = self.throughput_per_gpu * self.num_tasks
        # self.reference = {
        #     '*': {
        #         'samples_per_sec_per_gpu': (self.throughput_per_gpu,
        #                                     -0.1, None, 'samples/sec'),
        #         'samples_per_sec_total': (self.throughput_total,
        #                                 -0.1, None, 'samples/sec')
        #     }
        # }
        self.job.launcher.options += ['-l']

    @sanity_function
    def assert_job_is_complete(self):
        return sn.assert_found(r'train_au_meet_expectation', self.stderr)

    @performance_function('MB/second')
    def samples_per_sec_total(self):
        return sn.avg(sn.extractall(
            r'Training I/O Throughput \(MB/second\): (?P<mb_per_sec_total>)', # \((?P<mb_per_sec_per_gpu>)\)',
            self.stderr, 'mb_per_sec_total', float
        ))



@rfm.simple_test
class MLperfStorageBaseCEtest(MLperfStorageBase, ContainerEngineMixin):
    descr = 'Check the training throughput using the ContainerEngine and NVIDIA NGC'
    valid_systems = ['+ce']
    tags = {'production', 'ce'}
    sourcesdir = 'src'
    
    @run_before('run')
    def set_container_variables(self):
        self.container_image = self.image


@rfm.simple_test
class MLperfStorageBaseSarusTest(MLperfStorageBase):
    valid_systems = ['+nvgpu +sarus']
    platform = 'Sarus'
    # num_nodes = parameter([1])
    num_files = 16

    @run_before('run')
    def set_container_variables(self):
        self.container_platform = self.platform
        self.container_platform.command = self.executable
        self.container_platform.image = self.image
        self.container_platform.workdir = None
        self.container_platform.mount_points = [("/users/dealmeih/dev/storage/benchmark.sh", "/workspace/storage/benchmark.sh")]
        self.job.launcher.options.append('--mpi=pmi2')


@rfm.simple_test
class MLperfStorageBaseDockerTest(MLperfStorageBase):
    platform = 'Docker'
    num_nodes = parameter([1])
    num_files = 16

    @run_before('run')
    def set_container_variables(self):
        self.container_platform = self.platform
        self.container_platform.command = self.executable
        self.container_platform.image = self.image
        self.container_platform.workdir = None
        self.container_platform.options = ['-e RDMAV_FORK_SAFE=1']

"""
module load daint-mc   # or daint-gpu for GPU nodes
module load Buildah
salloc -N1 -Ausup -Cssd -t1440
srun --pty bash
buildah bud --format=docker --tag henriquemendonca/mlperf-storage:v1.0-rc1 .


# Create the docker-archive (preferably on /dev/shm for better performance)
buildah push henriquemendonca/mlperf-storage:v1.0-rc1 docker-archive:/dev/shm/$USER/mlperf-storage_v1.0-rc1.tar
 
# Copy the image to $SCRATCH to make it available after the job allocation ends
cp /dev/shm/$USER/mlperf-storage_v1.0-rc1.tar $SCRATCH
"""