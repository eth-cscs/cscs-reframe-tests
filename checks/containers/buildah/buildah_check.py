import os

import reframe as rfm
import reframe.utility.sanity as sn

from reframe.core.backends import getlauncher


class BuildahTestBase(rfm.RunOnlyRegressionTest):
    valid_systems = ['eiger:mc', 'pilatus:mc']
    valid_prog_environs = ['builtin']
    num_tasks = 1
    num_nodes = 1
    time_limit = '1h'
    executable = 'buildah'
    prerun_cmds = ['buildah --version']
    graphroot = variable(str)
    runroot = variable(str)
    maintainers = ['manitart']
    tags = {'production'}

    @run_after('setup')
    def setup_buildah(self):
        self.archive_name = self.image_tag.split(':')[0]
        self.graphroot = '/dev/shm/$USER/buildah_root'
        self.runroot = '/dev/shm/$USER/buildah_runroot'
        self.env_vars = {'XDG_DATA_HOME': '/dev/shm/$USER/xdg_data_home'}
        self.prerun_cmds = ['unset XDG_RUNTIME_DIR'] + self.prerun_cmds
 
        if self.current_system.name in {'dom', 'daint'}:
            self.modules = ['Buildah']

        self.prerun_cmds += [
            f'rm -f {self.runroot}/{self.archive_name}.tar',
            f'rm -f {self.stagedir}/{self.archive_name}.tar'
        ]

    @run_after('setup')
    def set_executable_opts(self):
        self.executable_opts = [
            'bud', f'--root={self.graphroot}', f'--runroot={self.runroot}',
            '--storage-driver=vfs', f'--tag={self.image_tag}',
            '--registries-conf=registries.conf',
            f'-f {self.dockerfile}', '.', '2>&1'
        ]

    @run_after('setup')
    def set_postrun_cmds(self):
        self.postrun_cmds = [
            f'buildah push --root={self.graphroot} --runroot={self.runroot} '
            f'--storage-driver=vfs {self.image_tag} '
            f'docker-archive:{self.runroot}/{self.archive_name}.tar',
            f'cp {self.runroot}/{self.archive_name}.tar .'
        ]

    @run_after('setup')
    def set_job_options(self):
        self.job.launcher = getlauncher('local')()
        self.job.options += ['--nodes=1']

    @sanity_function
    def assert_committed_image(self):
        return sn.all([
            sn.assert_found(r'buildah version\s+\d+', self.stdout),
            sn.assert_found(
                rf'STEP\s+\d+:\s+COMMIT\s+|COMMIT\s+{self.image_tag}',
                self.stdout),
        ])


@rfm.simple_test
class BuildahCudaDeviceQueryTest(BuildahTestBase):
    valid_systems = []
    dockerfile = 'Dockerfile_cuda'
    image_tag = 'cuda_query:latest'


@rfm.simple_test
class BuildahMpichOSUTest(BuildahTestBase):
    dockerfile = 'Dockerfile_osu'
    image_tag = 'mpich_osu:latest'


@rfm.simple_test
class ContainerCudaDeviceQueryTest(rfm.RunOnlyRegressionTest):
    valid_systems = []
    valid_prog_environs = ['builtin']
    platform = parameter(['Sarus', 'Singularity'])
    num_tasks = 1
    image_path = variable(str)
    maintainers = ['manitart']
    tags = {'production'}

    @require_deps
    def set_image_path(self, BuildahCudaDeviceQueryTest):
        self.image_path = os.path.join(
            BuildahCudaDeviceQueryTest().stagedir, 'cuda_query.tar')

    @run_after('init')
    def set_dependencies(self):
        self.depends_on('BuildahCudaDeviceQueryTest')

    @run_after('setup')
    def config_container_platform(self):
        self.container_platform = self.platform
        partition_name = self.current_partition.fullname.replace(':', '_')
        self.container_platform.pull_image = False
        if self.platform == 'Sarus':
            self.container_platform.image = (f'load/library/cuda_query:'
                                             f'{partition_name}')
            self.prerun_cmds = [
                f'sarus rmi load/library/cuda_query:{partition_name}',
                f'sarus load {self.image_path} cuda_query:{partition_name}']
            self.postrun_cmds = [
                f'sarus rmi load/library/cuda_query:{partition_name}'
        ]
        else:
            self.container_platform.with_cuda = True
            self.container_platform.image = f'cuda_device_query.sif'
            self.prerun_cmds = [
                f'singularity build {self.container_platform.image} '
                f'docker-archive:{self.image_path}'
            ]

    @run_after('setup')
    def set_cuda_visible_devices(self):
        curr_part = self.current_partition
        self.gpu_count = curr_part.select_devices('gpu')[0].num_devices
        cuda_visible_devices = ','.join(f'{i}' for i in range(self.gpu_count))
        self.env_vars['CUDA_VISIBLE_DEVICES'] = cuda_visible_devices

    @sanity_function
    def detect_cuda_device(self):
        return sn.assert_found(
            rf'^Detected {self.gpu_count} CUDA Capable device\(s\)',
            self.stdout)


@rfm.simple_test
class ContainerMpichOSUTest(rfm.RunOnlyRegressionTest):
    valid_systems = ['eiger:mc', 'pilatus:mc']
    valid_prog_environs = ['builtin']
    platform = parameter(['Sarus', 'Singularity'])
    num_tasks_per_node = 1
    num_tasks = 2
    reference = {
        '*': {
            'bw': (24000.0, -0.15, None, 'MB/s')
        },
    }
    image_path = variable(str)
    maintainers = ['manitart']
    tags = {'production'}

    @require_deps
    def set_image_path(self, BuildahMpichOSUTest):
        self.image_path = os.path.join(
            BuildahMpichOSUTest().stagedir, 'mpich_osu.tar'
        )

    @run_after('init')
    def set_dependencies(self):
        self.depends_on('BuildahMpichOSUTest')

    @run_after('setup')
    def config_container_platform(self):
        self.container_platform = self.platform
        osu_exe = '/usr/local/libexec/osu-micro-benchmarks/mpi/pt2pt/osu_bw'
        partition_name = self.current_partition.fullname.replace(':', '_')
        self.container_platform.pull_image = False
        self.container_platform.image = f'mpich_osu_{partition_name}'
        self.container_platform.command = f"bash -c '{osu_exe} -x 100 -i 1000'"

        if self.platform == 'Sarus':
            self.container_platform.image = (f'load/library/mpich_osu:'
                                             f'{partition_name}')
            self.container_platform.with_mpi = True
            self.prerun_cmds = [
                f'sarus rmi load/library/mpich_osu:{partition_name}',
                f'sarus load {self.image_path} mpich_osu:{partition_name}'
            ]
            self.postrun_cmds = [
                f'sarus rmi load/library/mpich_osu:{partition_name}'
            ]
        else:
            self.env_vars = {
                'SINGULARITY_CACHEDIR': self.stagedir
            }
            self.container_platform.image = 'mpich_osu.sif'
            self.prerun_cmds = [
               f'singularity build {self.container_platform.image} '
               f'docker-archive:{self.image_path}'
            ]

    @sanity_function
    def assert_message_4KB_bw(self):
        return sn.assert_found(r'^4194304\s+\S+', self.stdout)

    @performance_function('MB/s')
    def bw(self):
        return  sn.extractsingle(
            r'^4194304\s+(?P<bw>\S+)', self.stdout, 'bw', float)
