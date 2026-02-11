import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class MPIIntranodePinned(rfm.RegressionTest):
    valid_systems = ['+remote']
    valid_prog_environs = ['+uenv -ce']

    sourcesdir = 'src'
    build_system = 'CMake'

    executable = 'intranode_pinned_host_comm'
    executable_opts = [
        '1',
        '2',
        'host',
        str(1 << 27)   # expands $((1 << 27))
    ]

    @run_after('setup')
    def setup_job(self):

        self.num_tasks = 2
        self.num_tasks_per_node = 2
        self.num_nodes = 1

        # extra srun options
        self.job.options += ['--cpu-bind=sockets']

    @performance_function('s')
    def time_value(self):
        regex = r'\[\d+:\d+\]\s*time:\s*(?P<t>\S+)'
        return sn.extractsingle(regex, self.stdout, 't', float)

    @run_after('init')
    def set_reference(self):
        self.reference = {
            '*': {
                'time_value': (0.003, None, 0.10, 's')   
            }
        }
