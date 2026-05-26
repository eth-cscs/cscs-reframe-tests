import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class cpi_build_test(rfm.RegressionTest):
    descr = 'Simple mpi test'
    valid_systems = ['+remote']
    valid_prog_environs = ['+mpi']
    build_system = 'SingleSource'
    sourcesdir = 'src/mpi_cpi'
    sourcepath = 'cpi.c'
    executable = './cpi.x'
    _num_tasks = -2
    # num_tasks_per_node = 1
    build_locally = False
    env_vars = {'MPICH_GPU_SUPPORT_ENABLED': 0}
    tags = {'appscheckout', 'uenv', 'flexible'}
    maintainers = ['VCUE', 'PA']
    flexible = variable(bool, value=False)

    @run_before('run')
    def setup_job(self):
        self.num_tasks = 0 if self.flexible else self._num_tasks
        # if self.flexible:
        #     self.num_tasks = 0
        # else:
        #     self.num_tasks = self.num_tasks_per_node

    @sanity_function
    def validate(self):
        return sn.assert_found(r'Error is 0.00000000', self.stdout)

