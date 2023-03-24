import reframe as rfm
import reframe.utility.sanity as sn


class BaseCheck(rfm.RunOnlyRegressionTest):
    valid_systems = ['*']
    valid_prog_environs = ['+osu-micro-benchmarks']
    sourcesdir = None
    num_tasks = 2
    num_tasks_per_node = 1
    modules = ['osu-micro-benchmarks']
    pmi = variable(str, value='')
    env_vars = {
        'MPIR_CVAR_ENABLE_GPU': 0,
        # Set to one byte more than the last entry of the test
        'MPIR_CVAR_CH4_OFI_MULTI_NIC_STRIPING_THRESHOLD': 4194305
    }
    maintainers = ['TM']
    tags = {'uenv'}

    @run_after('init')
    def set_descr(self):
        self.descr = f'{self.name} on {self.num_tasks} nodes(s)'

    @run_after('setup')
    def set_launcher_options(self):
        if self.pmi != '':
            self.job.launcher.options = [f'--mpi={self.pmi}']

    @sanity_function
    def assert_sanity(self):
        # Only check for the last entry in the latency test,
        # if exists program completed successfully
        return sn.assert_found(r'4194304', self.stdout)


@rfm.simple_test
class OSULatency(BaseCheck):
    reference = {
        '*': {
            'latency_256': (2.3, None, 0.50, 'us'),
            'latency_4M':  (180., None, 0.15, 'us')
        },
    }
    executable = 'osu_latency'

    @run_before('performance')
    def set_perf(self):
        self.perf_patterns = {
            'latency_256': sn.extractsingle(r'256\s+(?P<latency_256>\S+)',
                                            self.stdout, 'latency_256', float),
            'latency_4M': sn.extractsingle(r'4194304\s+(?P<latency_4M>\S+)',
                                           self.stdout, 'latency_4M', float)
        }

@rfm.simple_test
class OSUBandwidth(BaseCheck):
    executable = 'osu_bw'
    reference = {
        '*': {
            'bandwidth_256': (600., -0.50, None, 'MB/s'),
            'bandwidth_4M':  (24000., -0.15, None, 'MB/s')
        },
    }
    
    @run_before('performance')
    def set_perf(self):
        # For performance we only evaluate two points of output
        self.perf_patterns = {
            'bandwidth_256':
                sn.extractsingle(r'256\s+(?P<bandwidth_256>\S+)', self.stdout,
                                 'bandwidth_256', float),
            'bandwidth_4M':
                sn.extractsingle(r'4194304\s+(?P<bandwidth_4M>\S+)',
                                 self.stdout, 'bandwidth_4M', float)
        }


@rfm.simple_test
class OSUBandwidthCuda(OSUBandwidth):
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['+osu-micro-benchmarks +cuda']
    env_vars = {
        'MPIR_CVAR_ENABLE_GPU': 1,
        'MPICH_GPU_SUPPORT_ENABLED': 1,
        'CUDA_VISIBLE_DEVICES': 0,
        # Set to one byte more than the last entry of the test
        'MPIR_CVAR_CH4_OFI_MULTI_NIC_STRIPING_THRESHOLD': 4194305
    }
    executable_opts = ['-d', 'cuda', 'D', 'D']


@rfm.simple_test
class OSULatencyCuda(OSUBandwidth):
    valid_systems = ['+nvgpu']
    valid_prog_environs = ['+osu-micro-benchmarks +cuda']
    env_vars = {
        'MPIR_CVAR_ENABLE_GPU': 1,
        'MPICH_GPU_SUPPORT_ENABLED': 1,
        'CUDA_VISIBLE_DEVICES': 0,
        # Set to one byte more than the last entry of the test
        'MPIR_CVAR_CH4_OFI_MULTI_NIC_STRIPING_THRESHOLD': 4194305
    }
    executable_opts = ['-d', 'cuda', 'D', 'D']
