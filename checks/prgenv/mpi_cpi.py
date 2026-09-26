import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class cpi_build_test(rfm.RegressionTest):
    """
    Simple MPI CPI build/run test.

    When ``flexible`` is enabled, the test is submitted with
    ``num_tasks=0`` so the scheduler can allocate any available
    nodes. In the default non-flexible mode, ``num_tasks`` is left
    unchanged (``-2``), which asks ReFrame to reserve two nodes.
    """
    descr = ('MPI CPI test with flexible or fixed two-node '
             'allocation depending on the flexible parameter')
    valid_systems = ['+remote']
    valid_prog_environs = ['+mpi +prgenv -cpe']
    maintainers = ['UE', 'PA']
    build_system = 'SingleSource'
    sourcesdir = 'src/mpi_cpi'
    sourcepath = 'cpi.c'
    executable = './cpi.x'
    num_tasks = -2
    num_tasks_per_node = 1
    build_locally = False
    tags = {'appscheckout', 'uenv', 'flexible'}
    env_vars = {'MPICH_GPU_SUPPORT_ENABLED': 0}
    flexible = variable(bool, value=False)

    @run_before('run')
    def setup_job(self):
        if self.flexible:
            self.num_tasks = 0

    @sanity_function
    def validate(self):
        return sn.assert_found(r'Error is 0.00000000', self.stdout)
