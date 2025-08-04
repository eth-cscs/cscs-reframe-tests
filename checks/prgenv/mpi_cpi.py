import reframe as rfm
import reframe.utility.sanity as sn

@rfm.simple_test
class cpi_build_test(rfm.RegressionTest):
    valid_systems = ['+remote']
    valid_prog_environs = ['+mpi']
    build_system = 'SingleSource'
    sourcepath = 'mpi_cpi/cpi.c'
    executable = './cpi.x'
    num_tasks = -2
    num_tasks_per_node = 1
    build_locally = False
    env_vars = {'MPICH_GPU_SUPPORT_ENABLED': 0}
    tags = {'appscheckout', 'uenv', 'flexible'}
    maintainers = ['VCUE', 'PA']

    @sanity_function
    def validate(self):
        return sn.assert_found(r'Error is 0.00000000', self.stdout)
