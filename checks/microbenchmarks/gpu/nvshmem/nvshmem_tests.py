# Copyright Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib
import sys

import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(
    str(pathlib.Path(__file__).parent.parent.parent.parent / 'mixins'))
sys.path.append(
    str(pathlib.Path(__file__).parent.parent.parent.parent.parent /
        'config' / 'utilities'))

from uenv import uarch                                       # noqa: E402
from uenv_slurm_mpi_options import UenvSlurmMpiOptionsMixin  # noqa: E402


class NVSHMEMPerftestBase(rfm.RunOnlyRegressionTest,
                          UenvSlurmMpiOptionsMixin):
    '''Run the device perftests shipped with NVSHMEM in the uenv.'''

    valid_systems = ['+nvgpu +uenv']
    valid_prog_environs = ['+uenv +nvshmem']
    maintainers = ['SSA']
    sourcesdir = None
    tags = {'production', 'uenv', 'bencher'}
    time_limit = '10m'
    benchmark = variable(str)
    min_size = variable(str, value='8')
    max_size = variable(str, value='1M')

    @run_after('setup')
    def set_executable(self):
        # The perftests are not part of the view: locate the nvshmem
        # installation in the uenv store
        self.prerun_cmds = [
            'NVSHMEM_PERFTEST=$(echo /user-environment/linux-*/nvshmem-*'
            '/bin/perftest/device)',
            'echo "NVSHMEM_PERFTEST=$NVSHMEM_PERFTEST"',
            'nvshmem-info -a | head -2'
        ]
        self.executable = f'$NVSHMEM_PERFTEST/{self.benchmark}'
        self.executable_opts = [
            f'--min_size {self.min_size}', f'--max_size {self.max_size}'
        ]
        # One GPU per PE
        self.job.launcher.options += ['--gpus-per-task=1']

    @run_before('performance')
    def set_reference(self):
        arch = uarch(self.current_partition)
        if arch in self.reference_per_uarch:
            self.reference = {
                self.current_partition.fullname: self.reference_per_uarch[arch]
            }


@rfm.simple_test
class NVSHMEMPutBandwidthUENV(NVSHMEMPerftestBase):
    descr = 'NVSHMEM device put bandwidth between two GPUs'
    benchmark = 'pt-to-pt/shmem_put_bw'
    max_size = '8M'
    # intranode: NVLink between 2 GPUs of the same node
    # internode: Slingshot (libfabric/cxi) between 2 nodes
    placement = parameter(['intranode', 'internode'])
    reference_per_placement = {
        'intranode': {
            'gh200': {'bw': (120.0, -0.10, None, 'GB/s')},
        },
        'internode': {
            'gh200': {'bw': (23.0, -0.10, None, 'GB/s')},
        },
    }

    @run_after('init')
    def set_placement(self):
        self.num_tasks = 2
        self.num_tasks_per_node = 2 if self.placement == 'intranode' else 1
        self.reference_per_uarch = self.reference_per_placement[
            self.placement]

    @sanity_function
    def assert_sanity(self):
        return sn.assert_found(r'^#shmem_put_bw_uni', self.stdout)

    @performance_function('GB/s')
    def bw(self):
        # Bandwidth of the largest message size (last row of the table)
        return sn.extractall(
            r'^\d+\s+None\s+(?P<bw>\S+)', self.stdout, 'bw', float)[-1]


@rfm.simple_test
class NVSHMEMAlltoallLatencyUENV(NVSHMEMPerftestBase):
    descr = 'NVSHMEM device alltoall latency on all GPUs of 2 nodes'
    benchmark = 'coll/alltoall_latency'
    num_nodes = variable(int, value=2)
    reference_per_uarch = {
        'gh200': {
            'latency': (36.0, None, 0.25, 'us'),
            'busbw': (8.7, -0.15, None, 'GB/s'),
        },
    }

    # 32-bit, block scope rows: size count type scope latency algbw busbw
    _row = (r'^\d+\s+\d+\s+32-bit\s+block\s+(?P<lat>\S+)\s+\S+\s+'
            r'(?P<busbw>\S+)')

    @run_after('setup')
    def set_num_tasks(self):
        num_gpus = self.current_partition.select_devices('gpu')[0].num_devices
        self.num_tasks_per_node = num_gpus
        self.num_tasks = self.num_nodes * num_gpus

    @sanity_function
    def assert_sanity(self):
        return sn.all([
            sn.assert_found(r'^#alltoall_device', self.stdout),
            sn.assert_found(self._row, self.stdout),
        ])

    @performance_function('us')
    def latency(self):
        # Smallest message size
        return sn.extractall(self._row, self.stdout, 'lat', float)[0]

    @performance_function('GB/s')
    def busbw(self):
        # Largest message size
        return sn.extractall(self._row, self.stdout, 'busbw', float)[-1]


@rfm.simple_test
class NVSHMEMRingUENV(rfm.RegressionTest, UenvSlurmMpiOptionsMixin):
    '''Build and run the dev-guide-ring example shipped with NVSHMEM.

    The example is the one from
    https://github.com/NVIDIA/nvshmem/blob/devel/examples/dev-guide-ring.cu,
    which the nvshmem package installs under share/src/examples.  Every PE
    sends its PE number to its right neighbour, so each PE must receive the
    number of its left neighbour.  The PEs select their GPU with
    cudaSetDevice(mype_node) after nvshmem_init(), as recommended by the
    NVSHMEM documentation, and the ring spans all GPUs of all nodes, so both
    NVLink and the network are exercised.

    Two bootstraps are tested:

    - mpi: the default of the uenv (NVSHMEM_BOOTSTRAP=mpi).  With
      MPICH_GPU_SUPPORT_ENABLED=1, MPI_Init creates a CUDA context on GPU 0
      before the application selects its GPU, so all PEs of a node end up on
      GPU 0 and internode puts fail with an illegal memory access.  GPU
      support in Cray MPICH is therefore disabled for this case.
    - pmi2: NVSHMEM_BOOTSTRAP=pmi with NVSHMEM_BOOTSTRAP_PMI=PMI-2 and
      srun --mpi=pmi2 (the plain PMI bootstrap does not work with libfabric).
    '''

    descr = 'Build and run the NVSHMEM dev-guide-ring example'
    valid_systems = ['+nvgpu +uenv']
    valid_prog_environs = ['+uenv +nvshmem']
    maintainers = ['SSA']
    sourcesdir = None
    build_system = 'SingleSource'
    build_locally = False
    sourcepath = 'dev-guide-ring.cu'
    executable = './dev-guide-ring'
    tags = {'production', 'uenv'}
    time_limit = '10m'
    num_nodes = variable(int, value=2)
    bootstrap = parameter(['mpi', 'pmi2'])

    @run_before('compile')
    def set_build(self):
        gpu = self.current_partition.select_devices('gpu')[0]
        view = '/user-environment/env/default'
        self.prebuild_cmds = [
            'cp /user-environment/linux-*/nvshmem-*/share/src/examples/'
            'dev-guide-ring.cu .'
        ]
        self.build_system.cxxflags = [
            '-rdc=true', f'-arch={gpu.arch}', '-ccbin mpicxx',
            f'-I{view}/include'
        ]
        self.build_system.ldflags = [
            f'-L{view}/lib', '-lnvshmem_host', '-lnvshmem_device'
        ]

    @run_after('setup')
    def set_num_tasks(self):
        # One PE per GPU; no GPU binding, since the example selects the GPU
        # itself and needs to see all GPUs of the node
        num_gpus = self.current_partition.select_devices('gpu')[0].num_devices
        self.num_tasks_per_node = num_gpus
        self.num_tasks = self.num_nodes * num_gpus

    @run_after('setup')
    def set_bootstrap(self):
        if self.bootstrap == 'mpi':
            self.env_vars['NVSHMEM_BOOTSTRAP'] = 'mpi'
            self.env_vars['MPICH_GPU_SUPPORT_ENABLED'] = '0'
        else:
            self.env_vars['NVSHMEM_BOOTSTRAP'] = 'pmi'
            self.env_vars['NVSHMEM_BOOTSTRAP_PMI'] = 'PMI-2'
            # Replace the --mpi option set by UenvSlurmMpiOptionsMixin
            self.job.launcher.options = [
                opt for opt in self.job.launcher.options
                if not opt.startswith('--mpi=')
            ] + ['--mpi=pmi2']

    @sanity_function
    def assert_sanity(self):
        pes = sn.extractall(r'^(\d+): received message (\d+)', self.stdout,
                            1, int)
        msgs = sn.extractall(r'^(\d+): received message (\d+)', self.stdout,
                             2, int)
        npes = self.num_tasks
        return sn.all([
            sn.assert_eq(sn.sorted(pes), list(range(npes))),
            sn.all(sn.map(
                lambda pm: sn.assert_eq(pm[1], (pm[0] - 1 + npes) % npes),
                sn.zip(pes, msgs))),
        ])
