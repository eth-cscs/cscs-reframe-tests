import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class SarusMPIWithGPUDirect(rfm.RunOnlyRegressionTest):
    valid_systems = ['dom:gpu', 'daint:gpu']
    valid_prog_environs = ['builtin']
    sourcesdir = None
    container_platform = 'Sarus'
    num_tasks = 2
    num_tasks_per_node = 1
    num_gpus_per_node = 1
    maintainers = ['amadonna', 'taliaga']
    tags = {'production'}

    @run_after('setup')
    def set_container_platform(self):
        self.container_platform.image = ('ethcscs/dockerfiles:'
                                         'mpi_gpudirect-all_gather')
        self.container_platform.command = (
            "bash -c 'MPICH_RDMA_ENABLED_CUDA=1 "
            "LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libcuda.so "
            "/opt/mpi_gpudirect/all_gather'"
        )
        self.container_platform.with_mpi = True
        self.prerun_cmds = ['sarus --version']

    @sanity_function
    def assert_sanity(self):
        return sn.assert_found(r'Success!', self.stdout)
