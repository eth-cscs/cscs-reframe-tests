import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class SarusCudaNBodyCheck(rfm.RunOnlyRegressionTest):
    valid_systems = ['dom:gpu', 'daint:gpu']
    valid_prog_environs = ['builtin']
    sourcesdir = None
    container_platform = 'Sarus'
    num_tasks = 1
    num_tasks_per_node = 1
    num_gpus_per_node = 1
    reference = {
        '*': {
            'gflops': (2730., -0.15, None, 'Gflop/s')
        }
    }
    maintainers = ['amadonna', 'taliaga']
    tags = {'production'}

    @run_after('setup')
    def setup_executable(self):
        nbody_exec = '/usr/local/cuda/samples/bin/x86_64/linux/release/nbody'
        self.container_platform.image = 'ethcscs/cudasamples:8.0'
        self.prerun_cmds = ['sarus --version']
        self.container_platform.command = (
            f'{nbody_exec} -benchmark -fp64 -numbodies=200000 '
            f'-numdevices={self.num_gpus_per_node}'
        )

    @sanity_function
    def assert_sanity(self):
        return sn.assert_found(r'.+double-precision GFLOP/s.+', self.stdout)

    @run_before('performance')
    def set_perf(self):
        self.perf_patterns = {
        'gflops': sn.extractsingle(r'= (?P<gflops>\S+)\sdouble-precision '
                                   r'GFLOP/s.+', self.stdout, 'gflops', float)
        }
