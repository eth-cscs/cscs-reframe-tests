import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps

@rfm.simple_test
class fio_compile_test(rfm.RegressionTest):
    '''
    Check title: Check if we can compile fio
    
    This test was taken from https://github.com/victorusu/reframe-tests-library
    '''
    descr = ('Make sure that we can compile fio.')
    executable = './fio'
    executable_opts = ['--version']
    valid_systems = ['*']
    valid_prog_environs = ['builtin']
    build_system = 'Autotools'

    @run_after('setup')
    def set_num_procs(self):
        proc = self.current_partition.processor
        if proc:
            self.num_cpus_per_task = max(proc.num_cores, 8)
        else:
            self.num_cpus_per_task = 1

    @run_before('compile')
    def set_download_fio_cmds(self):
        self.prebuild_cmds = [
            '_rfm_download_time="$(date +%s%N)"',
            r"/usr/bin/curl -s https://api.github.com/repos/axboe/fio/releases/latest | /bin/grep tarball_url | /bin/awk -F'\"' '{print $4}' | /usr/bin/xargs -I{} /usr/bin/curl -LJ {} -o fio.tar.gz",
            '_rfm_download_time="$(($(date +%s%N)-_rfm_download_time))"',
            'echo "Download time (ns): $_rfm_download_time"',
            '_rfm_extract_time="$(date +%s%N)"',
            fr'/bin/tar xf fio.tar.gz --strip-components=1 -C {self.stagedir}',
            '_rfm_extract_time="$(($(date +%s%N)-_rfm_extract_time))"',
            'echo "Extraction time (ns): $_rfm_extract_time"',
        ]

    @run_before('compile')
    def set_build_opts(self):
        self.build_system.flags_from_environ = False
        self.prebuild_cmds += ['_rfm_build_time="$(date +%s%N)"']
        self.postbuild_cmds += [
            '_rfm_build_time="$(($(date +%s%N)-_rfm_build_time))"',
            'echo "Compilation time (ns): $_rfm_build_time"',
        ]

    @performance_function('s')
    def compilation_time(self):
        return sn.extractsingle(r'Compilation time \(ns\): (\d+)',
                                self.build_stdout, 1, float) * 1.0e-9

    @performance_function('s')
    def download_time(self):
        return sn.extractsingle(r'Download time \(ns\): (\d+)',
                                self.build_stdout, 1, float) * 1.0e-9

    @performance_function('s')
    def extraction_time(self):
        return sn.extractsingle(r'Extraction time \(ns\): (\d+)',
                                self.build_stdout, 1, float) * 1.0e-9

    @sanity_function
    def assert_sanity(self):
        return sn.assert_found(r'fio-\S+', self.stdout)

@rfm.simple_test
class stuck_gpu_mem_test(rfm.RunOnlyRegressionTest):
    valid_prog_environs = ['builtin']
    valid_systems = ['*']

    @run_after('init')
    def set_parent(self):
        self.depends_on('fio_compile_test', how=udeps.fully)

    @run_before('run')
    def set_executable_path(self):
        self.executable = ("./run.sh") 

    @sanity_function
    def assert_passed(self):
        return sn.assert_eq(self.job.exitcode, 0)
