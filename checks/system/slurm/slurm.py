# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import pathlib
import re
import sys

import reframe as rfm
import reframe.core.runtime as rt
import reframe.utility.osext as osext
import reframe.utility.sanity as sn

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / 'mixins'))
from uenv_slurm_mpi_options import UenvSlurmMpiOptionsMixin  # noqa: E402


class SlurmSimpleBaseCheck(rfm.RunOnlyRegressionTest):
    '''Base class for Slurm simple binary tests'''
    valid_systems = ['+remote']
    valid_prog_environs = ['+prgenv']
    tags = {'slurm', 'maintenance', 'ops', 'production', 'single-node'}
    num_tasks_per_node = 1
    maintainers = ['VCUE', 'PA']


class SlurmCompiledBaseCheck(rfm.RegressionTest):
    '''Base class for Slurm tests that require compiling some code'''
    valid_systems = ['+remote']
    valid_prog_environs = ['+prgenv']
    build_locally = False
    tags = {'slurm', 'maintenance', 'ops', 'production', 'single-node'}
    num_tasks_per_node = 1
    maintainers = ['VCUE', 'PA']


@rfm.simple_test
class HostnameCheck(SlurmSimpleBaseCheck):
    descr = 'Check hostname pattern nidXXXXXX on the CN'
    sourcesdir = None
    time_limit = '1m'
    executable = '/bin/hostname'
    valid_prog_environs = ['builtin']
    tags.add('flexible')

    @run_before('sanity')
    def set_sanity_patterns(self):
        num_matches = sn.count(sn.findall(r'^nid\d{6}$', self.stdout))
        self.sanity_patterns = sn.assert_eq(self.num_tasks, num_matches)


@rfm.simple_test
class EnvironmentVariableCheck(SlurmSimpleBaseCheck):
    descr = 'Test if user env variables are propagated to CN'
    sourcesdir = None
    time_limit = '1m'
    num_tasks = 1
    valid_prog_environs = ['builtin']
    executable = '/bin/echo'
    executable_opts = ['$MY_VAR']
    env_vars = {'MY_VAR': 'TEST123456!'}

    @sanity_function
    def assert_num_tasks(self):
        num_matches = sn.count(sn.findall(r'TEST123456!', self.stdout))
        return sn.assert_eq(self.num_tasks, num_matches)


@rfm.simple_test
class RequiredConstraintCheck(SlurmSimpleBaseCheck):
    descr = 'Test if -C constraint is required (deprecated)'
    sourcesdir = None
    time_limit = '1m'
    valid_prog_environs = ['builtin']
    valid_systems = []  # will never run, we use slurm partitions now
    executable = 'srun'
    executable_opts = ['-A', osext.osgroup(), 'hostname']

    @sanity_function
    def assert_found_missing_constraint(self):
        return sn.assert_found(
            r'ERROR: you must specify -C with one of the following: mc,gpu',
            self.stderr
        )


@rfm.simple_test
class RequestLargeMemoryNodeCheck(SlurmSimpleBaseCheck):
    descr = '''Check if slurm memory flag works (deprecated,
        replaced by MemoryOverconsumptionCheck)'''
    sourcesdir = None
    time_limit = '1m'
    valid_systems = []  # use MemoryOverconsumptionCheck instead
    valid_prog_environs = ['builtin']
    executable = '/usr/bin/free'
    executable_opts = ['-h']

    @run_before('run')
    def set_memory_limit(self):
        self.job.options = ['--mem=120000']

    @sanity_function
    def assert_memory_is_bounded(self):
        mem_obtained = sn.extractsingle(r'Mem:\s+(?P<mem>\S+)G',
                                        self.stdout, 'mem', float)
        return sn.assert_bounded(mem_obtained, 122.0, None)


@rfm.simple_test
class NvidiaSmiDriverVersion(SlurmSimpleBaseCheck):
    descr = 'Nvidia-smi sanity check (output driver version)'
    sourcesdir = None
    time_limit = '1m'
    valid_prog_environs = ['builtin']
    valid_systems = ['+nvgpu']
    executable = 'nvidia-smi'

    @sanity_function
    def asser_found_nvidia_driver_version(self):
        return sn.assert_found(r'NVIDIA-SMI.*Driver Version.*',
                               self.stdout)


@rfm.simple_test
class DefaultRequestGPUSetsGRES(SlurmSimpleBaseCheck):
    descr = 'Checks slurm config for 4-GPUs per node'
    sourcesdir = None
    time_limit = '1m'
    valid_prog_environs = ['builtin']
    valid_systems = ['+gpu']
    executable = 'scontrol show job ${SLURM_JOB_ID}'
    tags.add('flexible')

    @sanity_function
    def assert_found_resources(self):
        return sn.assert_found(r'.*(AllocTRES|Gres)=.*gres/gpu=4.*',
                               self.stdout)


@rfm.simple_test
class DefaultRequest(SlurmSimpleBaseCheck):
    descr = 'Sanity check for core count (needs to be updated)'
    valid_systems = []  # will never run, TODO: use .reframe/topology/
    # This is a basic test that should return the number of CPUs on the
    # system which, on a MC node should be 72
    executable = 'lscpu -p |grep -v "^#" -c'

    @sanity_function
    def assert_found_num_cpus(self):
        return sn.assert_found(r'288', self.stdout)


@rfm.simple_test
class ConstraintRequestCabinetGrouping(SlurmSimpleBaseCheck):
    descr = 'Checks if constraint works for requesting specific cabinets (deprecated, needs attention)'  # noqa: E501
    valid_systems = []  # will never run, TODO: update
    executable = 'cat /proc/cray_xt/cname'
    cabinets = {
        'daint:gpu': 'c0-1',
        'daint:mc': 'c1-0',
    }

    @run_before('run')
    def set_slurm_constraint(self):
        cabinet = self.cabinets.get(self.current_partition.fullname)
        if cabinet:
            self.job.options = [f'--constraint={cabinet}']

    @sanity_function
    def assert_found_cabinet(self):
        # We choose a default pattern that will cause assert_found() to fail
        cabinet = self.cabinets.get(self.current_system.name, r'$^')
        return sn.assert_found(fr'{cabinet}.*', self.stdout)


@rfm.simple_test
class MemoryOverconsumptionCheck(SlurmCompiledBaseCheck):
    # TODO: maintainers = ['@jgphpc', '@ekouts']
    descr = 'Tests if requested memory limit works'
    valid_prog_environs = ['+uenv -cpe +prgenv']
    time_limit = '2m'
    tags.add('mem')
    build_system = 'SingleSource'
    sourcepath = 'eatmem/eatmemory.c'
    executable_opts = ['4000M']

    @run_before('compile')
    def oneapi_compilers(self):
        if 'oneapi' in self.current_environ.features:
            self.build_system.cflags += ['-g']

    @run_before('run')
    def set_memory_limit(self):
        self.job.options = ['--mem=2000']

    @sanity_function
    def assert_found_exceeded_memory(self):
        return sn.assert_found(r'(exceeded memory limit)|(Out Of Memory)',
                               self.stderr)


@rfm.simple_test
class MemoryOverconsumptionCheckMPI(SlurmCompiledBaseCheck,
                                    UenvSlurmMpiOptionsMixin):
    descr = 'Testing max "allocatable" memory'
    maintainers = ['@jgphpc', '@ekouts']
    valid_systems = ['+remote']
    valid_prog_environs = ['+uenv -cpe +prgenv +mpi']
    time_limit = '4m'
    build_system = 'SingleSource'
    sourcepath = 'eatmem/eatmemory_mpi.c'
    # env_vars = {'MPICH_GPU_SUPPORT_ENABLED': 0}
    tags.add('mem')

    @run_before('compile')
    def oneapi_compilers(self):
        if 'oneapi' in self.current_environ.features:
            self.build_system.cflags += ['-g']

    @run_before('run')
    def set_num_tasks(self):
        self.skip_if_no_procinfo()
        cpu = self.current_partition.processor
        # Limit number of tasks because PMIx/OpenMPI can take very long to
        # initialize with e.g. 288 ranks on one GH200 node. The test still
        # fails in a reasonable time with a limited number of ranks.
        self.num_tasks_per_node = min(16, int(
            cpu.info['num_cpus'] / cpu.info['num_cpus_per_core']))
        self.num_tasks = self.num_tasks_per_node
        self.job.launcher.options += ['-u']

    @sanity_function
    def assert_found_oom(self):
        return sn.assert_found(r'(oom-kill)|(Killed)', self.stderr)

    @performance_function('GB')
    def cn_avail_memory_from_sysconf(self):
        regex = r'memory from sysconf: total: \S+ \S+ avail: (?P<mem>\S+) GB'
        # return float to avoid truncation in Elastic
        return sn.extractsingle(regex, self.stdout, 'mem', float)

    @performance_function('GB')
    def cn_max_allocated_memory(self):
        regex = (r'^Eating \d+ MB\/mpi \*\d+mpi = -\d+ MB memory from \/proc\/'
                 r'meminfo: total: \d+ GB, free: \d+ GB, avail: \d+ GB, using:'
                 r' (\d+) GB')
        # return float to avoid truncation in Elastic
        return sn.max(sn.extractall(regex, self.stdout, 1, float))

    @run_before('performance')
    def set_reference_from_config_systems_file(self):
        """
                    ref-1%< ref <ref+1%
        beverin/mi200: 498< 503 <508
        beverin/mi300: 496< 501 <506
        daint:         845< 854 <863
        clariden:      514< 519 <524 # grep MaxMemPerNode /etc/slurm/slurm.conf
        santis:        845< 854 <863
        starlex:       847< 856 <865
        and eiger is a special case with 2 type of nodes: std=256G, large=512G
        """
        reference_mem = self.current_partition.extras['cn_memory']
        lower = -0.51 if self.current_system.name == 'eiger' else -0.01
        upper = 0.03 if 'openmpi' in self.current_environ.features else 0.01
        self.reference = {
            '*': {
                'cn_max_allocated_memory': (reference_mem, lower, upper, 'GB')
            }
        }


@rfm.simple_test
class slurm_response_check(rfm.RunOnlyRegressionTest):
    descr = 'Slurm basic commands test (squeue, sacct)'
    command = parameter(['squeue', 'sacct'])
    sourcesdir = None
    valid_systems = ['-remote']
    valid_prog_environs = ['builtin']
    maintainers = ['VCUE', 'PA']
    num_tasks = 1
    num_tasks_per_node = 1
    reference = {
        'squeue': {
            'real_time': (0.02, None, 0.1, 's')
        },
        'sacct': {
            'real_time': (0.1, None, 0.1, 's')
        }
    }
    executable = 'time -p'
    tags = {'diagnostic', 'health'}

    @run_before('run')
    def set_exec_opts(self):
        self.executable_opts = [self.command]

    @sanity_function
    def assert_exitcode_zero(self):
        return sn.assert_eq(self.job.exitcode, 0)

    @performance_function('s')
    def real_time(self):
        return sn.extractsingle(r'real (?P<real_time>\S+)', self.stderr,
                                'real_time', float)


def get_system_partitions():
    system_partitions = {
        'eiger': [
            'debug', 'normal*', 'prepost', 'low'
        ],
        'pilatus': [
            'debug', 'normal*', 'prepost', 'low'
        ]
    }
    cur_sys_name = rt.runtime().system.name
    if cur_sys_name in system_partitions.keys():
        return system_partitions[cur_sys_name]
    else:
        return ['debug', 'normal*']


@rfm.simple_test
class SlurmQueueStatusCheck(rfm.RunOnlyRegressionTest):
    descr = 'check system queue status (# of nodes)'
    valid_systems = ['-remote']
    valid_prog_environs = ['builtin']
    maintainers = ['VCUE', 'PA']
    tags = {'slurm', 'ops', 'single-node'}
    min_avail_nodes = variable(int, value=1)
    ratio_minavail_nodes = variable(float, value=0.1)
    local = True
    executable = 'sinfo'
    executable_opts = ['-o', '%P,%a,%D,%T']
    slurm_partition = parameter(get_system_partitions())
    reference = {
        '*': {
            'available_nodes': (min_avail_nodes, -0.0001, None, 'nodes'),
            'available_nodes_percentage': (ratio_minavail_nodes*100,
                                           -0.0001, None, '%')
        }
    }

    @run_after('init')
    def xfer_queue_correction(self):
        if self.slurm_partition == 'xfer':
            self.ratio_minavail_nodes = 0.3

    def assert_partition_exists(self):
        avail_nodes = sn.extractall(
            fr'^{re.escape(self.slurm_partition)},up,'
            fr'(?P<nodes>\d+),(allocated|reserved|idle|mixed)',
            self.stdout, 'nodes', int
        )
        self.num_matches = sn.sum(avail_nodes)

        all_matches = sn.extractall(fr'^{re.escape(self.slurm_partition)},up,'
                                    fr'(?P<nodes>\d+),.*', self.stdout,
                                    'nodes', int)
        self.num_all_matches = sn.sum(all_matches)

        partition_matches = sn.count(
            sn.findall(fr'^{re.escape(self.slurm_partition)}.*', self.stdout)
        )
        return sn.assert_gt(
            partition_matches, 0,
            msg=f'{self.slurm_partition!r} not defined '
                f'for partition {self.current_partition.fullname!r}')

    def assert_percentage_nodes(self):
        matches = sn.extractall(
            fr'^{re.escape(self.slurm_partition)},up,'
            fr'(?P<nodes>\d+),(allocated|reserved|idle|mixed)',
            self.stdout, 'nodes', float
        )
        num_matches = sn.sum(matches)
        all_matches = sn.extractall(fr'^{re.escape(self.slurm_partition)},up,'
                                    fr'(?P<nodes>\d+),.*', self.stdout,
                                    'nodes', float)
        self.num_all_matches = sn.sum(all_matches)
        diff_matches = self.num_all_matches - num_matches
        return sn.assert_le(diff_matches,
                            self.num_all_matches * self.ratio_minavail_nodes,
                            msg=f'more than '
                                f'{self.ratio_minavail_nodes * 100.0:.0f}% '
                                f'({diff_matches} out of '
                                f'{self.num_all_matches}) '
                                f'of nodes are unavailable for '
                                f'partition {self.slurm_partition}')

    @sanity_function
    def assert_partition_sanity(self):
        return sn.all([
            self.assert_partition_exists(),
            # self.assert_min_nodes(),
            # self.assert_percentage_nodes(),
        ])

    @performance_function('nodes')
    def all_nodes(self):
        return self.num_all_matches

    @performance_function('nodes')
    def idle_nodes(self):
        return sn.sum(
            sn.extractall(
                fr'^{re.escape(self.slurm_partition)},up,'
                fr'(?P<nodes>\d+),idle',
                self.stdout, 'nodes', float
            )
        )

    @performance_function('nodes')
    def allocated_nodes(self):
        return sn.sum(
            sn.extractall(
                fr'^{re.escape(self.slurm_partition)},up,'
                fr'(?P<nodes>\d+),allocated',
                self.stdout, 'nodes', float
            )
        )

    @performance_function('nodes')
    def mixed_nodes(self):
        return sn.sum(
            sn.extractall(
                fr'^{re.escape(self.slurm_partition)},up,'
                fr'(?P<nodes>\d+),mixed',
                self.stdout, 'nodes', float
            )
        )

    @performance_function('nodes')
    def reserved_nodes(self):
        return sn.sum(
            sn.extractall(
                fr'^{re.escape(self.slurm_partition)},up,'
                fr'(?P<nodes>\d+),reserved',
                self.stdout, 'nodes', float
            )
        )

    @performance_function('nodes')
    def available_nodes(self):
        return self.num_matches

    @performance_function('%')
    def available_nodes_percentage(self):
        return 100.0 * self.num_matches / self.num_all_matches


@rfm.simple_test
class SlurmPrologEpilogCheck(rfm.RunOnlyRegressionTest):
    descr = 'Runs Prolog and Epilog tests'
    valid_systems = ['*']
    valid_prog_environs = ['builtin']
    maintainers = ['VCUE', 'PA']
    time_limit = '2m'
    kafka_logger = '/etc/slurm/utils/kafka_logger'
    prolog_dir = '/etc/slurm/node_prolog.d/'
    epilog_dir = '/etc/slurm/node_epilog.d/'
    prerun_cmds = [f'ln -s {kafka_logger} ./kafka_logger']
    test_files = []
    try:
        for file in os.listdir(epilog_dir):
            if os.path.isfile(os.path.join(epilog_dir, file)):
                test_files.append(os.path.join(epilog_dir, file))
    except PermissionError:
        pass

    try:
        for file in os.listdir(prolog_dir):
            if os.path.isfile(os.path.join(prolog_dir, file)):
                test_files.append(os.path.join(prolog_dir, file))
    except PermissionError:
        pass

    test_file = parameter(test_files)
    tags = {'vs-node-validator'}

    @run_after('setup')
    def set_executable(self):
        self.executable = f'bash {self.test_file} --drain=off'

    @sanity_function
    def validate(self):
        reason = sn.extractall(r'reason:\s*(.*)', self.stdout, tag=1)

        if reason:
            return sn.assert_not_found('will be drained with reason',
                                       self.stdout, msg=f'{reason[0]}')
        else:
            return True


@rfm.simple_test
class SlurmTransparentHugepagesCheck(rfm.RunOnlyRegressionTest):
    descr = 'Checks if Slurm transparent hugepages constraint works'

    hugepages_options = parameter(['default', 'always', 'madvise', 'never'])
    valid_systems = ['+hugepages_slurm']
    valid_prog_environs = ['builtin']
    maintainers = ['VCUE', 'PA']
    descr = 'Check Slurm transparent hugepages configuration'
    time_limit = '2m'
    num_tasks_per_node = 1
    sourcesdir = None
    executable = 'cat /sys/kernel/mm/transparent_hugepage/enabled'

    tags = {'production', 'maintenance', 'slurm'}
    maintainers = ['VCUE']

    @run_after('setup')
    def set_executable(self):
        if self.hugepages_options != 'default':
            slurm_opt = f'thp_{self.hugepages_options}'
            self.job.options += [f'-C {slurm_opt}']

    @sanity_function
    def validate(self):
        if self.hugepages_options != 'default':
            opt = f'{self.hugepages_options}'
        else:
            # Default option should be 'always'
            opt = 'always'

        return sn.assert_found(rf'\[{opt}\]', self.stdout)


@rfm.simple_test
class SlurmParanoidCheck(rfm.RunOnlyRegressionTest):
    valid_systems = ['+remote +scontrol']
    valid_prog_environs = ['builtin']
    maintainers = ['PA', '@jgphpc']
    descr = (
        'Check that perf_event_paranoid enables per-process and system wide'
        'performance monitoring')
    time_limit = '1m'
    num_tasks_per_node = 1
    sourcesdir = None
    executable = 'cat /proc/sys/kernel/perf_event_paranoid'
    tags = {'production', 'maintenance', 'slurm'}
    maintainers = ['SSA']

    @sanity_function
    def validate(self):
        return sn.assert_found(r'0', self.stdout)


@rfm.simple_test
class SlurmNoIsolCpus(rfm.RunOnlyRegressionTest):
    valid_systems = ['+remote +scontrol']
    valid_prog_environs = ['builtin']
    maintainers = ['msimberg', 'SSA']
    descr = '''
    Check that isolcpus isn\'t enabled as it prevents threads from migrating
    between cores. This makes e.g. make jobs or OpenMPI threads all be stuck to
    one core. See e.g.
    https://www.kernel.org/doc/html/latest/admin-guide/kernel-parameters.html
    and https://access.redhat.com/solutions/480473 for more details.
    '''
    time_limit = '1m'
    num_tasks_per_node = 1
    sourcesdir = None
    executable = 'cat /proc/cmdline'
    tags = {'production', 'maintenance', 'slurm'}

    @sanity_function
    def validate(self):
        return sn.assert_not_found(r'\bisolcpus=', self.stdout)


@rfm.simple_test
class NVreg_RestrictProfilingToAdminUsers(rfm.RunOnlyRegressionTest):
    valid_systems = ['+remote +nvgpu']
    valid_prog_environs = ['builtin']
    maintainers = ['PA', '@jgphpc']
    descr = '''
    Allow access to the GPU Performance Counters for NVIDIA tools:
    https://developer.nvidia.com/nvidia-development-tools-solutions-err_nvgpuctrperm-permission-issue-performance-counters
    '''
    time_limit = '1m'
    num_tasks_per_node = 1
    sourcesdir = None
    executable = 'hostname'
    tags = {'production', 'maintenance', 'slurm'}

    @run_before('run')
    def test_settings(self):
        self.postrun_cmds = [
            'grep ^NVRM /proc/driver/nvidia/version',
            'grep -H RmProfilingAdminOnly /proc/driver/nvidia/params',
            'grep NVreg_RestrictProfilingToAdminUsers /etc/modprobe.d/*'
        ]

    @sanity_function
    def validate(self):
        regex1 = r'RmProfilingAdminOnly: (?P<adminonly>\d+)'
        sanity1 = sn.extractsingle(regex1, self.stdout, 'adminonly')
        expected1 = '0'

        regex2 = r'NVreg_RestrictProfilingToAdminUsers=(?P<adminonly>\d+)'
        sanity2 = sn.extractsingle(regex2, self.stdout, 'adminonly')
        expected2 = '0'

        return sn.all([
            sn.assert_eq(sanity1, expected1),
            sn.assert_eq(sanity2, expected2)
        ])


@rfm.simple_test
class SlurmUvmPerfAccessCounterMigration(rfm.RunOnlyRegressionTest):
    valid_systems = ['+remote +scontrol +nvgpu']
    valid_prog_environs = ['builtin']
    maintainers = ['msimberg', 'SSA']
    descr = '''
    Check that uvm_perf_access_counter_mimc_migration_enable is set to 0
    as it is buggy in older drivers. If the driver is at least version 565, the
    name of the option is different and should be set to the default (-1).
    '''
    time_limit = '1m'
    num_tasks_per_node = 1
    executable = 'bash'
    executable_opts = ['check_uvm_perf_access_counter_migration.sh']
    tags = {'production', 'maintenance', 'slurm'}

    @sanity_function
    def validate(self):
        driver_ver = sn.extractsingle(r'driver_version=(\d+)', self.stdout, 1,
                                      int)
        if driver_ver >= 565:
            param = 'uvm_perf_access_counter_migration_enable'
            expected = '-1'
        else:
            param = 'uvm_perf_access_counter_mimc_migration_enable'
            expected = '0'
        value = sn.extractsingle(rf'{param}=(.+)', self.stdout, 1)
        return sn.assert_eq(value, expected)


@rfm.simple_test
class SlurmGPUGresTest(SlurmSimpleBaseCheck):
    descr = '''
       Ensure that the Slurm GRES (Generic REsource Scheduling) of the
       number of gpus is correctly set on all the nodes of each partition.

       For the current partition, the test performs the following steps:
        1) count the number of nodes (node_count)
        2) count the number of nodes having Gres=gpu:N (gres_count) where
           N=num_devices from the configuration
        3) ensure that 1) and 2) match
    '''
    valid_systems = ['+scontrol +gpu']
    valid_prog_environs = ['builtin']
    maintainers = ['VCUE', 'PA']
    sourcesdir = None
    time_limit = '1m'
    num_tasks_per_node = 1
    executable = 'scontrol'
    executable_opts = ['show', 'nodes', '--oneliner']
    tags = {'production', 'maintenance'}

    @sanity_function
    def assert_gres_valid(self):
        partition_name = self.current_partition.name
        gpu_count = self.current_partition.select_devices('gpu')[0].num_devices
        part_re = rf'Partitions=\S*{partition_name}'
        gres_re = rf'gres/gpu={gpu_count} '
        node_re = r'NodeName=(\S+)'

        all_nodes = sn.evaluate(
            sn.extractall(rf'{node_re}.*{part_re}', self.stdout, 1)
        )
        good_nodes = sn.evaluate(
            sn.extractall(rf'{node_re}.*{part_re}.*{gres_re}',
                          self.stdout, 1)
        )
        bad_nodes = ','.join(sorted(set(all_nodes) - set(good_nodes)))

        return sn.assert_true(
            len(bad_nodes) == 0,
            msg=(f'{len(good_nodes)}/{len(all_nodes)} of '
                 f'{partition_name} nodes satisfy {gres_re}. Bad nodes: '
                 f'{bad_nodes}')
        )
