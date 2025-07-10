# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import re

import reframe as rfm
import reframe.core.runtime as rt
import reframe.utility.osext as osext
import reframe.utility.sanity as sn


class SlurmSimpleBaseCheck(rfm.RunOnlyRegressionTest):
    '''Base class for Slurm simple binary tests'''
    valid_systems = ['daint:normal', 'eiger:mc', 'pilatus:mc']
    valid_prog_environs = ['PrgEnv-cray']
    tags = {'slurm', 'maintenance', 'ops', 'production', 'single-node'}
    num_tasks_per_node = 1

    @run_after('init')
    def customize_systems(self):
        if self.current_system.name in ['arolla', 'tsa']:
            self.valid_prog_environs = ['PrgEnv-gnu', 'PrgEnv-pgi']
            self.exclusive_access = True


class SlurmCompiledBaseCheck(rfm.RegressionTest):
    '''Base class for Slurm tests that require compiling some code'''

    valid_systems = []
    valid_prog_environs = ['PrgEnv-cray']
    tags = {'slurm', 'maintenance', 'ops',
            'production', 'single-node'}
    num_tasks_per_node = 1


@rfm.simple_test
class HostnameCheck(SlurmSimpleBaseCheck):
    executable = '/bin/hostname'
    valid_prog_environs = ['builtin']
    hostname_patt = {
        'daint:normal': r'^nid\d{6}$',
        'eiger:mc': r'^nid\d{6}$',
        'pilatus:mc': r'^nid\d{6}$'
    }

    @run_before('sanity')
    def set_sanity_patterns(self):
        partname = self.current_partition.fullname
        num_matches = sn.count(
            sn.findall(self.hostname_patt[partname], self.stdout)
        )
        self.sanity_patterns = sn.assert_eq(self.num_tasks, num_matches)


@rfm.simple_test
class EnvironmentVariableCheck(SlurmSimpleBaseCheck):
    num_tasks = 2
    valid_systems = ['daint:normal', 'eiger:mc', 'pilatus:mc']
    executable = '/bin/echo'
    executable_opts = ['$MY_VAR']
    env_vars = {'MY_VAR': 'TEST123456!'}
    tags.remove('single-node')

    @sanity_function
    def assert_num_tasks(self):
        num_matches = sn.count(sn.findall(r'TEST123456!', self.stdout))
        return sn.assert_eq(self.num_tasks, num_matches)


@rfm.simple_test
class RequiredConstraintCheck(SlurmSimpleBaseCheck):
    valid_systems = []
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
    valid_systems = []
    executable = '/usr/bin/free'
    executable_opts = ['-h']

    @sanity_function
    def assert_memory_is_bounded(self):
        mem_obtained = sn.extractsingle(r'Mem:\s+(?P<mem>\S+)G',
                                        self.stdout, 'mem', float)
        return sn.assert_bounded(mem_obtained, 122.0, 128.0)

    @run_before('run')
    def set_memory_limit(self):
        self.job.options = ['--mem=120000']


@rfm.simple_test
class DefaultRequestGPU(SlurmSimpleBaseCheck):
    valid_systems = ['daint:normal']
    executable = 'nvidia-smi'

    @sanity_function
    def asser_found_nvidia_driver_version(self):
        return sn.assert_found(r'NVIDIA-SMI.*Driver Version.*',
                               self.stdout)


@rfm.simple_test
class DefaultRequestGPUSetsGRES(SlurmSimpleBaseCheck):
    valid_systems = []
    executable = 'scontrol show job ${SLURM_JOB_ID}'

    @sanity_function
    def assert_found_resources(self):
        return sn.assert_found(r'.*(TresPerNode|Gres)=.*gpu=4.*', self.stdout)


@rfm.simple_test
class DefaultRequest(SlurmSimpleBaseCheck):
    valid_systems = ['daint:normal']
    # This is a basic test that should return the number of CPUs on the
    # system which, on a MC node should be 72
    executable = 'lscpu -p |grep -v "^#" -c'

    @sanity_function
    def assert_found_num_cpus(self):
        return sn.assert_found(r'288', self.stdout)


@rfm.simple_test
class ConstraintRequestCabinetGrouping(SlurmSimpleBaseCheck):
    valid_systems = []
    executable = 'cat /proc/cray_xt/cname'
    cabinets = {
        'daint:gpu': 'c0-1',
        'daint:mc': 'c1-0',
    }

    @sanity_function
    def assert_found_cabinet(self):
        # We choose a default pattern that will cause assert_found() to fail
        cabinet = self.cabinets.get(self.current_system.name, r'$^')
        return sn.assert_found(fr'{cabinet}.*', self.stdout)

    @run_before('run')
    def set_slurm_constraint(self):
        cabinet = self.cabinets.get(self.current_partition.fullname)
        if cabinet:
            self.job.options = [f'--constraint={cabinet}']


@rfm.simple_test
class MemoryOverconsumptionCheck(SlurmCompiledBaseCheck):
    time_limit = '1m'
    valid_systems = ['daint:normal', 'eiger:mc', 'pilatus:mc']
    tags.add('mem')
    sourcepath = 'eatmemory.c'
    executable_opts = ['4000M']

    @sanity_function
    def assert_found_exceeded_memory(self):
        return sn.assert_found(r'(exceeded memory limit)|(Out Of Memory)',
                               self.stderr)

    @run_before('run')
    def set_memory_limit(self):
        self.job.options = ['--mem=2000']


@rfm.simple_test
class MemoryOverconsumptionMpiCheck(SlurmCompiledBaseCheck):
    maintainers = ['@jgphpc', '@ekouts']
    valid_systems = ['+remote']
    time_limit = '5m'
    build_system = 'SingleSource'
    sourcepath = 'eatmemory_mpi.c'
    env_vars = {'MPICH_GPU_SUPPORT_ENABLED': 0}
    tags.add('mem')

    @run_before('compile')
    def unset_ldflags(self):
        if 'alps' in self.current_partition.features:
            self.build_system.ldflags = ['-L.']

    @run_before('run')
    def set_job_parameters(self):
        # fix for "MPIR_pmi_init(83)....: PMI2_Job_GetId returned 14"
        self.job.launcher.options += (
            self.current_environ.extras.get('launcher_options', [])
        )

    @run_before('run')
    def set_num_tasks(self):
        self.skip_if_no_procinfo()
        cpu = self.current_partition.processor
        self.num_tasks_per_node = int(
            cpu.info['num_cpus'] / cpu.info['num_cpus_per_core'])
        self.num_tasks = self.num_tasks_per_node
        self.job.launcher.options += ['-u']

    @sanity_function
    def assert_found_oom(self):
        return sn.assert_found(r'(oom-kill)|(Killed)', self.stderr)

    @performance_function('GB')
    def cn_avail_memory_from_sysconf(self):
        regex = r'memory from sysconf: total: \S+ \S+ avail: (?P<mem>\S+) GB'
        return sn.extractsingle(regex, self.stdout, 'mem', int)

    @performance_function('GB')
    def cn_max_allocated_memory(self):
        regex = (r'^Eating \d+ MB\/mpi \*\d+mpi = -\d+ MB memory from \/proc\/'
                 r'meminfo: total: \d+ GB, free: \d+ GB, avail: \d+ GB, using:'
                 r' (\d+) GB')
        return sn.max(sn.extractall(regex, self.stdout, 1, int))

    @run_before('performance')
    def set_references(self):
        reference_mem = self.current_partition.extras['cn_memory'] - 3
        self.reference = {
            '*': {
                'cn_max_allocated_memory': (reference_mem, -0.10, None, 'GB'),
            }
        }


@rfm.simple_test
class slurm_response_check(rfm.RunOnlyRegressionTest):
    command = parameter(['squeue', 'sacct'])
    descr = 'Slurm command test'
    valid_systems = ['-remote']
    valid_prog_environs = ['builtin']
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
    maintainers = ['CB', 'VH']

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
    '''check system queue status'''

    valid_systems = ['-remote']
    valid_prog_environs = ['builtin']
    tags = {'slurm', 'ops', 'production', 'single-node'}
    min_avail_nodes = variable(int, value=1)
    ratio_minavail_nodes = variable(float, value=0.1)
    local = True
    executable = 'sinfo'
    executable_opts = ['-o', '%P,%a,%D,%T']
    slurm_partition = parameter(get_system_partitions())
    reference = {
        '*': {
            'available_nodes': (min_avail_nodes, -0.0001, None, 'nodes'),
            'available_nodes_percentage': (ratio_minavail_nodes*100, -0.0001, None, '%')
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
        return sn.assert_gt(partition_matches, 0,
                            msg=f'{self.slurm_partition!r} not defined for '
                                f'partition {self.current_partition.fullname!r}')

    def assert_percentage_nodes(self):
        matches = sn.extractall(
            fr'^{re.escape(self.slurm_partition)},up,'
            fr'(?P<nodes>\d+),(allocated|reserved|idle|mixed)',
            self.stdout, 'nodes', int
        )
        num_matches = sn.sum(matches)
        all_matches = sn.extractall(fr'^{re.escape(self.slurm_partition)},up,'
                                    fr'(?P<nodes>\d+),.*', self.stdout,
                                    'nodes', int)
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
                self.stdout, 'nodes', int
            )
        )

    @performance_function('nodes')
    def allocated_nodes(self):
        return sn.sum(
            sn.extractall(
                fr'^{re.escape(self.slurm_partition)},up,'
                fr'(?P<nodes>\d+),allocated',
                self.stdout, 'nodes', int
            )
        )

    @performance_function('nodes')
    def mixed_nodes(self):
        return sn.sum(
            sn.extractall(
                fr'^{re.escape(self.slurm_partition)},up,'
                fr'(?P<nodes>\d+),mixed',
                self.stdout, 'nodes', int
            )
        )

    @performance_function('nodes')
    def reserved_nodes(self):
        return sn.sum(
            sn.extractall(
                fr'^{re.escape(self.slurm_partition)},up,'
                fr'(?P<nodes>\d+),reserved',
                self.stdout, 'nodes', int
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
    valid_systems = ['*']
    valid_prog_environs = ['builtin']
    time_limit = '2m'
    kafka_logger = '/etc/slurm/utils/kafka_logger'
    prolog_dir = '/etc/slurm/node_prolog.d/'
    epilog_dir = '/etc/slurm/node_epilog.d/'
    prerun_cmds = [f'ln -s {kafka_logger} ./kafka_logger']
    test_files = []
    for file in os.listdir(epilog_dir):
        if os.path.isfile(os.path.join(epilog_dir, file)):
            test_files.append(os.path.join(epilog_dir, file))

    for file in os.listdir(prolog_dir):
        if os.path.isfile(os.path.join(prolog_dir, file)):
            test_files.append(os.path.join(prolog_dir, file))

    test_file = parameter(test_files)
    tags = {'vs-node-validator'}

    @run_after('setup')
    def set_executable(self):
        self.executable = f'bash {self.test_file} --drain=off'

    @sanity_function
    def validate(self):
        reason = sn.extractall(r'reason:\s*(.*)', self.stdout, tag=1)

        if reason:
            return sn.assert_not_found('will be drained with reason', self.stdout,
                                       msg=f'{reason[0]}')
        else:
            return True


@rfm.simple_test
class SlurmTransparentHugepagesCheck(rfm.RunOnlyRegressionTest):
    '''Check Slurm transparent hugepages configuration'''

    hugepages_options = parameter(['default', 'always', 'madvise', 'never'])
    valid_systems = ['+hugepages_slurm']
    valid_prog_environs = ['builtin']
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
