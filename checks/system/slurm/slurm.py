# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import re

import reframe as rfm
import reframe.core.runtime as rt
import reframe.utility.osext as osext
import reframe.utility.sanity as sn


class SlurmSimpleBaseCheck(rfm.RunOnlyRegressionTest):
    '''Base class for Slurm simple binary tests'''

    valid_systems = [
        'daint:gpu', 'daint:mc', 'dom:gpu', 'dom:mc',
        'arolla:cn', 'arolla:pn', 'tsa:cn', 'tsa:pn',
        'daint:xfer', 'dom:xfer', 'eiger:mc', 'pilatus:mc'
    ]
    valid_prog_environs = ['PrgEnv-cray']
    tags = {'slurm', 'maintenance', 'ops',
            'production', 'single-node'}
    num_tasks_per_node = 1
    maintainers = ['RS', 'VH']

    @run_after('init')
    def customize_systems(self):
        if self.current_system.name in ['arolla', 'tsa']:
            self.valid_prog_environs = ['PrgEnv-gnu', 'PrgEnv-pgi']
            self.exclusive_access = True


class SlurmCompiledBaseCheck(rfm.RegressionTest):
    '''Base class for Slurm tests that require compiling some code'''

    valid_systems = ['daint:gpu', 'daint:mc',
                     'dom:gpu', 'dom:mc']
    valid_prog_environs = ['PrgEnv-cray']
    tags = {'slurm', 'maintenance', 'ops',
            'production', 'single-node'}
    num_tasks_per_node = 1
    maintainers = ['RS', 'VH']


@rfm.simple_test
class HostnameCheck(SlurmSimpleBaseCheck):
    executable = '/bin/hostname'
    valid_prog_environs = ['builtin']
    hostname_patt = {
        'arolla:cn': r'^arolla-cn\d{3}$',
        'arolla:pn': r'^arolla-pp\d{3}$',
        'tsa:cn': r'^tsa-cn\d{3}$',
        'tsa:pn': r'^tsa-pp\d{3}$',
        'daint:gpu': r'^nid\d{5}$',
        'daint:mc': r'^nid\d{5}$',
        'daint:xfer': r'^datamover\d{2}.cscs.ch$',
        'dom:gpu': r'^nid\d{5}$',
        'dom:mc': r'^nid\d{5}$',
        'dom:xfer': r'^nid\d{5}$',
        'eiger:mc': r'^nid\d{6}$',
        'pilatus:mc': r'^nid\d{6}$'
    }

    @run_before('run')
    def set_pending_time(self):
        if self.current_partition.name == 'xfer':
            self.max_pending_time = '2m'

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
    valid_systems = ['daint:gpu', 'daint:mc',
                     'dom:gpu', 'dom:mc',
                     'arolla:cn', 'arolla:pn',
                     'tsa:cn', 'tsa:pn',
                     'eiger:mc', 'pilatus:mc',
                     'hohgant:nvgpu']
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
    valid_systems = ['daint:login', 'dom:login']
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
    valid_systems = ['daint:mc']
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
    valid_systems = ['daint:gpu', 'dom:gpu',
                     'arolla:cn', 'tsa:cn']
    executable = 'nvidia-smi'

    @sanity_function
    def asser_found_nvidia_driver_version(self):
        return sn.assert_found(r'NVIDIA-SMI.*Driver Version.*',
                               self.stdout)


@rfm.simple_test
class DefaultRequestGPUSetsGRES(SlurmSimpleBaseCheck):
    valid_systems = ['daint:gpu', 'dom:gpu']
    executable = 'scontrol show job ${SLURM_JOB_ID}'

    @sanity_function
    def assert_found_resources(self):
        return sn.assert_found(r'.*(TresPerNode|Gres)=.*gpu:1.*', self.stdout)


@rfm.simple_test
class DefaultRequestMC(SlurmSimpleBaseCheck):
    valid_systems = ['daint:mc', 'dom:mc']
    # This is a basic test that should return the number of CPUs on the
    # system which, on a MC node should be 72
    executable = 'lscpu -p |grep -v "^#" -c'

    @sanity_function
    def assert_found_num_cpus(self):
        return sn.assert_found(r'72', self.stdout)


@rfm.simple_test
class ConstraintRequestCabinetGrouping(SlurmSimpleBaseCheck):
    valid_systems = ['daint:gpu', 'daint:mc',
                     'dom:gpu', 'dom:mc']
    executable = 'cat /proc/cray_xt/cname'
    cabinets = {
        'daint:gpu': 'c0-1',
        'daint:mc': 'c1-0',
        # Numbering is inverse in Dom
        'dom:gpu': 'c0-0',
        'dom:mc': 'c0-1',
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
    valid_systems += ['eiger:mc', 'pilatus:mc']
    tags.add('mem')
    sourcepath = 'eatmemory.c'
    executable_opts = ['4000M']

    @run_after('setup')
    def set_skip(self):
        self.skip_if(self.current_partition.name == 'login',
                     'MemoryOverconsumptionCheck not needed on login node')

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
    valid_systems += ['*']
    valid_prog_environs += ['PrgEnv-gnu', 'PrgEnv-nvidia']
    time_limit = '5m'
    build_system = 'SingleSource'
    sourcepath = 'eatmemory_mpi.c'
    tags.add('mem')

    @run_after('setup')
    def set_skip(self):
        self.skip_if(self.current_partition.name == 'login',
                     'MemoryOverconsumptionMpiCheck not needed on login node')

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
                'cn_max_allocated_memory': (reference_mem, -0.05, None, 'GB'),
            }
        }


@rfm.simple_test
class slurm_response_check(rfm.RunOnlyRegressionTest):
    command = parameter(['squeue', 'sacct'])
    descr = 'Slurm command test'
    valid_systems = ['daint:login', 'dom:login', 'hohgant:login']
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
        'daint': [
            'cscsci', 'long', 'large', 'normal*', 'prepost', '2go', 'low',
            'xfer', 'debug'
        ],
        'dom': [
            'cscsci', 'long', 'large', 'normal*', 'prepost', '2go', 'low',
            'xfer'
        ],
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
        return ['normal']


@rfm.simple_test
class SlurmQueueStatusCheck(rfm.RunOnlyRegressionTest):
    '''check system queue status'''

    valid_systems = ['daint:login', 'dom:login', 'eiger:login',
                     'pilatus:login']
    valid_prog_environs = ['builtin']
    tags = {'slurm', 'ops',
            'production', 'single-node'}
    min_avail_nodes = variable(int, value=1)
    ratio_minavail_nodes = variable(float, value=0.1)
    local = True
    executable = 'sinfo'
    executable_opts = ['-o', '%P,%a,%D,%T']
    slurm_partition = parameter(get_system_partitions())
    maintainers = ['RS', 'VH']

    @run_after('init')
    def xfer_queue_correction(self):
        if self.slurm_partition == 'xfer':
            self.ratio_minavail_nodes = 0.3
        if self.current_system.name == 'dom':
            self.ratio_minavail_nodes = 0.5

    def assert_partition_exists(self):
        num_matches = sn.count(
            sn.findall(fr'^{re.escape(self.slurm_partition)}.*', self.stdout)
        )
        return sn.assert_gt(num_matches, 0,
                            msg=f'{self.slurm_partition!r} not defined for '
                                f'partition {self.current_partition.fullname!r}')

    def assert_min_nodes(self):
        matches = sn.extractall(
            fr'^{re.escape(self.slurm_partition)},up,'
            fr'(?P<nodes>\d+),(allocated|reserved|idle|mixed)',
            self.stdout, 'nodes', int
        )
        num_matches = sn.sum(matches)
        return sn.assert_ge(
            num_matches, self.min_avail_nodes,
            msg=f'found {num_matches} nodes in partition '
                f'{self.slurm_partition} with status allocated, '
                f'reserved, or idle. Expected at least {self.min_avail_nodes}')

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
        num_all_matches = sn.sum(all_matches)
        diff_matches = num_all_matches - num_matches
        return sn.assert_le(diff_matches,
                            num_all_matches * self.ratio_minavail_nodes,
                            msg=f'more than '
                                f'{self.ratio_minavail_nodes * 100.0:.0f}% '
                                f'({diff_matches} out of {num_all_matches}) '
                                f'of nodes are unavailable for '
                                f'partition {self.slurm_partition}')

    @sanity_function
    def assert_partition_sanity(self):
        return sn.all([
            self.assert_partition_exists(),
            self.assert_min_nodes(),
            self.assert_percentage_nodes(),
        ])


class SlurmPrologCheck(rfm.RunOnlyRegressionTest):

    valid_systems = ['*']
    valid_prog_environs = ['builtin']
    time_limit = '2m'
    tags = {'vs-node-validator'}

class SlurmPrologGPUCheck(SlurmPrologCheck):

    prolog_file = '/etc/slurm/node_prolog.d/003_gpu_check.sh'

@rfm.simple_test
class SlurmPrologGPUModelCheck(SlurmPrologGPUCheck):

    descr = 'Test the GPU model found in the node'
    pattern = r"GPUTYPEEXPECTED='([^']+)'"
    with open(SlurmPrologGPUCheck.prolog_file, 'r') as file:
        file_content = file.read()
    match = re.search(pattern, file_content)
    if match:
        GPUTYPEEXPECTED = match.group(1)
    else:
        valid_systems = []

    @run_after('setup')
    def set_executable(self):
        self.executable = "/usr/bin/nvidia-smi -i 0 -q | grep 'Product Name' | awk -F': ' '{print $2}'"

    @sanity_function
    def validate(self):
        return sn.assert_found(self.GPUTYPEEXPECTED, self.stdout,
                               msg='GPU type is not the expected $GPUTYPEEXPECTED')

@rfm.simple_test
class SlurmPrologGPUNumberCheck(SlurmPrologGPUCheck):

    descr = 'Test the number of GPUs found in the node'
    pattern = r"GPUNUM=(\d+)"
    with open(SlurmPrologGPUCheck.prolog_file, 'r') as file:
        file_content = file.read()
    match = re.search(pattern, file_content)
    if match:
        GPUNUM = int(match.group(1))
    else:
        valid_systems = []

    @run_after('setup')
    def set_executable(self):
        self.executable = "/usr/bin/nvidia-smi --list-gpus | wc -l"

    @sanity_function
    def validate(self):
        with open(str(self.stdout), "r") as file:
            DETECTED_GPUS = int(file.read())
        return sn.assert_eq(self.GPUNUM, DETECTED_GPUS,
                            msg=f'Number of GPUs {DETECTED_GPUS}, expected {self.GPUNUM}')

@rfm.simple_test
class SlurmPrologGPUPowerCheck(SlurmPrologGPUCheck):

    descr = 'Test the number of GPUs found in the node'
    pattern = r"GPUNUM=(\d+)"
    with open(SlurmPrologGPUCheck.prolog_file, 'r') as file:
        file_content = file.read()
    match = re.search(pattern, file_content)
    if match:
        gpu_num = parameter(list(range(int(match.group(1)))))
    else:
        valid_systems = []
    pattern = r'POWERCAPEXPECTED="(\d+(\.\d+)?)\s([A-Za-z])"'
    with open(SlurmPrologGPUCheck.prolog_file, 'r') as file:
        file_content = file.read()
    match = re.search(pattern, file_content)
    if match and valid_systems:
        POWERCAPEXPECTED = match.group(1)
    else:
        valid_systems = []

    @run_after('setup')
    def set_executable(self):
        self.executable = f"/usr/bin/nvidia-smi -i {self.gpu_num} -q | grep -A2 'Module Power Readings' | tail -1 | awk -F': ' '{'{'}print $2{'}'}'"

    @sanity_function
    def validate(self):
        return sn.assert_found(self.POWERCAPEXPECTED, self.stdout,
                               msg=f"Power cap on GPU {self.gpu_num} does not match the expected {self.POWERCAPEXPECTED}")

@rfm.simple_test
class SlurmPrologGPUECCErrorsCheck(SlurmPrologGPUCheck):

    descr = 'Test the number of GPUs found in the node'
    pattern = r"GPUNUM=(\d+)"
    with open(SlurmPrologGPUCheck.prolog_file, 'r') as file:
        file_content = file.read()
    match = re.search(pattern, file_content)
    if match:
        gpu_num = parameter(list(range(int(match.group(1)))))
    else:
        valid_systems = []

    @run_after('setup')
    def set_executable(self):
        self.executable = f"nvidia-smi --query-gpu=ecc.errors.uncorrected.volatile.total --format=csv,noheader --id={self.gpu_num}"

    @sanity_function
    def validate(self):
        status = "ok"
        with open(str(self.stdout), "r") as file:
            unrecorable_errors = file.read().strip().split()
        for error in unrecorable_errors:
            result = sn.assert_eq(int(error), 0,
                                  msg=f'GPU {self.gpu_num}: {error} uncorrected ECC errors'
                                  ' since last driver restart')
            if not result:
                return result
        return result

@rfm.simple_test
class SlurmPrologllibfabricErrorCheck(SlurmPrologCheck):

    @run_after('setup')
    def set_executable(self):
        self.executable = "/opt/cray/libfabric/1.15.2.0/bin/fi_info 2>&1 | awk -F'[:, ]' '/cxip_query_if_list/ {r=r s $13;s=\",\"} END{print r}'"

    @sanity_function
    def validate(self):
        with open(str(self.stdout), "r") as file:
            LIBFABERR = file.read().strip()
        return sn.assert_false(LIBFABERR,
                               msg = f'libfabric error on {LIBFABERR}')

@rfm.simple_test
class SlurmProloglcxistateCheck(SlurmPrologCheck):

    @run_after('setup')
    def set_executable(self):
        self.executable = "cxi_stat |grep -c \"Link state: up\""

    @sanity_function
    def validate(self):
        with open(str(self.stdout), "r") as file:
            lstate = int(file.read())
        return sn.assert_eq(lstate, 4,
                            msg=f'cxi: only {lstate} are up')

@rfm.simple_test
class SlurmPrologPCIESpeedCheck(SlurmPrologCheck):

    command = "cxi_stat -l"
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if result.returncode == 0:
        cxi_param = parameter(result.stdout.splitlines())
    else:
        valid_systems = []

    @run_after('setup')
    def set_executable(self):
        self.executable = f"cxi_stat -d {self.cxi_param}|awk '/PCIE speed\/width/{'{'}print $3, $6{'}'}'"

    @sanity_function
    def validate(self):
        with open(str(self.stdout), "r") as file:
            PCIE = file.read().strip().split()
        if len(PCIE) == 2:
            return sn.and_(sn.assert_eq(PCIE[0], "16.0",
                                        msg=f'PCIE speed degrade on {self.cxi_param}: {PCIE[0]}'),
                           sn.assert_eq(PCIE[1], "x16",
                                        msg=f'PCIE speed degrade on {self.cxi_param}: {PCIE[0]}'))
        else:
            return False

@rfm.simple_test
class SlurmPrologHSNNumberCheck(SlurmPrologGPUCheck):

    valid_systems = ['*']
    valid_prog_environs = ['builtin']
    time_limit = '2m'
    prolog_file = '/etc/slurm/node_prolog.d/004_hsn.sh'
    tags = {'vs-node-validator'}
    descr = 'Test the number of HSN interfaces'
    pattern = r"EXPECTED_HSN=(\d+)"
    with open(prolog_file, 'r') as file:
        file_content = file.read()
    match = re.search(pattern, file_content)
    if match:
        EXPECTED_HSN = int(match.group(1))
    else:
        valid_systems = []

    @run_after('setup')
    def set_executable(self):
        self.executable = "cxi_stat | grep 'Network device' | grep -oP 'hsn[0-3]' | wc -l"

    @sanity_function
    def validate(self):
        with open(str(self.stdout), "r") as file:
            NUM_HSN = int(file.read())
        return sn.assert_eq(self.EXPECTED_HSN, NUM_HSN,
                            msg=f'HSN interfaces found: {NUM_HSN}, expected {self.EXPECTED_HSN}')

