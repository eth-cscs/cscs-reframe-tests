import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class cpi_build_test(rfm.RegressionTest):
    """
    Simple MPI CPI build/run test.

    Default production and maintenance run: fixed 2-node / 2-task functionality test.

    Flexible allocation can be enabled by setting ``flexible=True`` on
    the command line:

    - ``-S flexible=True`` allocates all currently idle nodes
      (ReFrame's default ``--flex-alloc-nodes=idle``).
    - ``-S flexible=True --flex-alloc-nodes=N`` caps the allocation to
      ``N`` nodes.
    - ``-S flexible=True --flex-alloc-nodes=all`` considers all partition
      nodes.

    This is useful for manual tests or future health-check runs.
    """
    descr = ('MPI CPI functionality test on two nodes; '
             'flexible allocation when requested')
    valid_systems = ['+remote']
    valid_prog_environs = ['+mpi +prgenv -cpe']
    maintainers = ['UE', 'PA']
    build_system = 'SingleSource'
    sourcesdir = 'src/mpi_cpi'
    sourcepath = 'cpi.c'
    executable = './cpi.x'

    # Fixed 2-node allocation for the default production/maintenance run
    num_tasks = 2
    num_tasks_per_node = 1

    build_locally = False
    tags = {'production', 'maintenance', 'appscheckout', 'uenv', 'flexible'}
    env_vars = {'MPICH_GPU_SUPPORT_ENABLED': 0}
    flexible = variable(bool, value=False)

    @run_before('run')
    def setup_job(self):
        # Only switch to flexible allocation when explicitly requested
        if self.flexible:
            self.num_tasks = 0

    @sanity_function
    def validate(self):
        return sn.assert_found(r'Error is 0.00000000', self.stdout)
