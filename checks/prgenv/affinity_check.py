# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause


import os

import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.osext as osext
from reframe.core.exceptions import SanityError, ReframeError


class CompileAffinityTool(rfm.CompileOnlyRegressionTest):
    valid_systems = [
        '*'
    ]
    valid_prog_environs = ['+mpi']
    build_system = 'Make'
    build_locally = False
    env_vars = {'MPICH_GPU_SUPPORT_ENABLED': 0} 
    
    sourcesdir = 'https://github.com/vkarak/affinity'
    tags = {'production', 'scs', 'maintenance', 'craype'}

    @run_before('compile')
    def set_build_opts(self):
        self.build_system.options = ['MPI=1']

    @run_before('compile')
    def prgenv_nvidia_workaround(self):
        ce = self.current_environ.name
        if ce == 'PrgEnv-nvidia':
            self.build_system.cppflags = [
                '-D__GCC_ATOMIC_TEST_AND_SET_TRUEVAL'
            ]

    @sanity_function
    def assert_exec_exists(self):
        return sn.path_exists(os.path.join(self.stagedir, 'affinity'))


class CompileAffinityToolNoOmp(CompileAffinityTool):
    valid_systems = ['*']
    valid_prog_environs = ['+mpi +openmp']

    @run_before('compile')
    def set_build_opts(self):
        self.build_system.options = ['MPI=1', 'OPENMP=0']


class AffinityTestBase(rfm.RunOnlyRegressionTest):
    '''Base class for the affinity checks.

    It sets up the processor's topology, based on the configuration.
    '''

    # Variables to control the hint and binding options on the launcher.
    multithread = variable(bool, type(None), value=None)
    cpu_bind = variable(str, type(None), value=None)
    hint = variable(str, type(None), value=None)
    affinity_tool = fixture(CompileAffinityTool, scope='environment')
    sourcesdir = None

    valid_systems = [
        '+remote'
    ]
    valid_prog_environs = [
        '+openmp'
    ]

    tags = {'production', 'scs', 'maintenance', 'craype'}

    @run_after('setup')
    def skip_cpe_2312(self):
        cpe = osext.cray_cdt_version()
        self.skip_if(cpe == '23.12' and
                     'uenv' not in self.current_environ.features,
                     f'skipping xpmem_attach known error with cpe/{cpe}')

    @run_before('run')
    def add_launcher_opts_from_env_extras(self):
        self.job.launcher.options += (
            self.current_environ.extras.get('launcher_options', [])
        )

    @run_before('run')
    def set_executable(self):
        scheduler = (
            self.affinity_tool.current_partition.scheduler.registered_name
        )
        if scheduler != 'firecrest-slurm':
            remote_stagedir = self.affinity_tool.stagedir
        else:
            remote_stagedir = self.affinity_tool.build_job.remotedir

        self.executable = os.path.join(
            remote_stagedir, 'affinity'
        )

    def bitmask_to_list(self, bitmask):
        positions = []
        position = 0

        bitmask_int = int(bitmask, 16)
        while bitmask_int:
            if bitmask_int & 1:
                positions.append(position)

            bitmask_int >>= 1
            position += 1

        return positions

    @run_after('setup')
    def setup_proc_topo(self):
        '''Import the processor's topology from the partition's configuration.

        This hook inserts the following attributes based on the processor's
        topology:
            - cpu_set: set containing all the cpu IDs
            - num_cpus
            - num_cpus_per_core
            - num_numa_nodes
            - num_sockets
            - numa_nodes: list containing the cpu sets for each numa node
            - sockets: list containing the cpu sets for each socket
            - cores: list containing the cpu sets for each core
        '''

        self.skip_if_no_procinfo()
        processor_info = self.current_partition.processor
        # Build the cpu set
        self.num_cpus = processor_info.num_cpus
        self.cpu_set = {i for i in range(self.num_cpus)}

        # Build the numa sets
        self.numa_nodes = [
            set(self.bitmask_to_list(i))
            for i in processor_info.topology['numa_nodes']
        ]
        self.num_numa_nodes = len(self.numa_nodes)

        # Build the core sets
        self.num_cpus_per_core = processor_info.num_cpus_per_core
        self.cores = [
            set(self.bitmask_to_list(i))
            for i in processor_info.topology['cores']
        ]

        # Build the socket sets
        self.num_sockets = processor_info.num_sockets
        self.sockets = [
            set(self.bitmask_to_list(i))
            for i in processor_info.topology['sockets']
        ]

    def get_sibling_cpus(self, cpuid, by=None):
        '''Return a cpu set where cpuid belongs to.

        The cpu set can be extracted by matching core, numa domain or socket.
        This is controlled by the `by` argument.
        '''

        if (cpuid < 0) or (cpuid >= self.num_cpus):
            raise ReframeError(f'a cpuid with value {cpuid} is invalid')

        if by is None:
            raise ReframeError('must specify the sibling level')
        else:
            if by == 'core':
                for cpu_set in self.cores:
                    if cpuid in cpu_set:
                        return cpu_set
            elif by == 'socket':
                for cpu_set in self.sockets:
                    if cpuid in cpu_set:
                        return cpu_set
            elif by == 'node':
                for cpu_set in self.numa_nodes:
                    if cpuid in cpu_set:
                        return cpu_set
            else:
                raise ReframeError('invalid sibling level')

            return ReframeError(f'could not find the siblings by {by} '
                                f'for cpu {cpuid}')

    @sanity_function
    def assert_consumed_cpu_set(self):
        '''Check that all the resources have been consumed.

        Tests derived from this class must implement a hook that consumes
        the cpu set as the results from the affinity tool are processed.
        '''
        return sn.assert_eq(self.cpu_set, set())

    @run_after('run')
    def parse_output(self):
        '''Extract the data from the affinity tool.'''

        re_aff_cpus = r'CPU affinity: \[\s+(?P<cpus>[\d+\s+]+)\]'

        def parse_cpus(x):
            return sorted([int(xi) for xi in x.split()])

        with osext.change_dir(self.stagedir):
            self.aff_cpus = sn.extractall(
                re_aff_cpus, self.stdout, 'cpus', parse_cpus
            ).evaluate()

    @run_before('run')
    def set_multithreading(self):
        self.use_multithreading = self.multithread

    @run_before('run')
    def set_launcher(self):
        if self.cpu_bind:
            self.job.launcher.options += [f'--cpu-bind={self.cpu_bind}']

        if self.hint:
            self.job.launcher.options += [f'--hint={self.hint}']


class AffinityOpenMPBase(AffinityTestBase):
    '''Extend affinity base with OMP hooks.

    The tests derived from this class book the full node and place the
    threads acordingly based exclusively on the OMP_BIND env var. The
    number of total OMP_THREADS will vary depending on what are we
    binding the OMP threads to (e.g. if we bind to sockets, we'll have as
    many threads as sockets).
    '''

    omp_bind = variable(str)
    omp_proc_bind = variable(str, value='spread')
    num_tasks = 1

    @property
    def ncpus_per_task(self):
        '''We use this property to set the hook below and keep exec order.'''
        return self.num_cpus

    @run_before('run')
    def set_num_cpus_per_task(self):
        self.num_cpus_per_task = self.ncpus_per_task

    @run_before('run')
    def set_omp_vars(self):
        self.env_vars = {
            'OMP_NUM_THREADS': self.num_omp_threads,
            'OMP_PLACES': self.omp_bind,
            'OMP_PROC_BIND': self.omp_proc_bind,
        }

    @run_before('sanity')
    def consume_cpu_set(self):
        raise NotImplementedError('this function must be overridden')


@rfm.simple_test
class OneThreadPerLogicalCoreOpenMP(AffinityOpenMPBase):
    '''Pin each OMP thread to a different logical core.'''

    omp_bind = 'threads'
    descr = 'Pin one OMP thread per CPU.'

    @property
    def num_omp_threads(self):
        # One OMP thread per logical core
        return self.num_cpus

    @run_before('sanity')
    def consume_cpu_set(self):
        '''Threads are bound to cpus.'''
        for affinity_set in self.aff_cpus:
            # Affinity set must be of length 1 and CPU ID cannot be repeated
            if ((len(affinity_set) > 1) or not all(x in self.cpu_set
                                                   for x in affinity_set)):
                # This will force the sanity function to fail.
                raise SanityError('incorrect affinity set')

            # Decrement the affinity set from the cpu set
            self.cpu_set -= set(affinity_set)


@rfm.simple_test
class OneThreadPerPhysicalCoreOpenMP(AffinityOpenMPBase):
    '''Pin each OMP thread to a different physical core.'''

    omp_bind = 'cores'
    descr = 'Pin one OMP thread per core.'

    @property
    def num_omp_threads(self):
        # One OMP thread per core
        return int(self.num_cpus/self.num_cpus_per_core)

    @run_before('sanity')
    def consume_cpu_set(self):
        '''Threads are bound to cores.'''
        for affinity_set in self.aff_cpus:

            # Get CPU siblings by core
            cpu_siblings = self.get_sibling_cpus(affinity_set[0], by='core')

            # All CPUs in the set must belong to the same core
            if (not all(x in self.cpu_set for x in affinity_set) or
               not all(x in cpu_siblings for x in affinity_set)):
                raise SanityError('incorrect affinity set')

            # Decrement the cpu set with all the CPUs that belong to this core
            self.cpu_set -= cpu_siblings


@rfm.simple_test
class OneThreadPerPhysicalCoreOpenMPnomt(OneThreadPerPhysicalCoreOpenMP):
    '''Only one cpu per core booked without multithread.'''

    use_multithreading = False
    descr = 'Pin one OMP thread per core wo. multithreading.'

    @property
    def ncpus_per_task(self):
        return self.num_omp_threads

    @run_before('sanity')
    def assert_aff_set_length(self):
        '''Only 1 CPU pinned per thread.'''
        if not all(len(aff_set) == 1 for aff_set in self.aff_cpus):
            raise SanityError('incorrect affinity set')


@rfm.simple_test
class OneThreadPerSocketOpenMP(AffinityOpenMPBase):
    '''Pin each OMP thread to a different socket.'''

    omp_bind = 'sockets'
    descr = 'Pin one OMP thread per socket.'

    @property
    def num_omp_threads(self):
        # One OMP thread per core
        return self.num_sockets

    @run_before('sanity')
    def consume_cpu_set(self):
        '''Threads are bound to sockets.'''
        for affinity_set in self.aff_cpus:

            # Get CPU siblings by socket
            cpu_siblings = self.get_sibling_cpus(
                affinity_set[0], by='socket')

            # Alll CPUs in the affinity set must belong to the same socket
            if (not all(x in self.cpu_set for x in affinity_set) or
               not all(x in cpu_siblings for x in affinity_set)):
                raise SanityError('incorrect affinity set')

            # Decrement all the CPUs in this socket from the cpu set.
            self.cpu_set -= cpu_siblings


@rfm.simple_test
class OneTaskPerSocketOpenMPnomt(AffinityOpenMPBase):
    '''One task per socket, and 1 OMP thread per physical core.'''

    omp_bind = 'sockets'
    omp_proc_bind = 'close'
    descr = 'One task per socket - wo. multithreading.'
    use_multithreading = False

    @property
    def num_omp_threads(self):
        return int(self.num_cpus/self.num_cpus_per_core/self.num_sockets)

    @property
    def ncpus_per_task(self):
        return self.num_omp_threads

    @run_before('run')
    def set_num_tasks(self):
        self.num_tasks = self.num_sockets

    @run_before('sanity')
    def consume_cpu_set(self):

        threads_in_socket = [0]*self.num_sockets

        def get_socket_id(cpuid):
            for i in range(self.num_sockets):
                if cpuid in self.sockets[i]:
                    return i

        for affinity_set in self.aff_cpus:
            # Count the number of OMP threads that live on each socket
            threads_in_socket[get_socket_id(affinity_set[0])] += 1

            # Get CPU siblings by socket
            cpu_siblings = self.get_sibling_cpus(
                affinity_set[0], by='socket'
            )

            # The size of the affinity set matches the number of OMP threads
            # and all CPUs from the set belong to the same socket.
            if ((self.num_omp_threads != len(affinity_set)) or
               not all(x in cpu_siblings for x in affinity_set)):
                raise SanityError('incorrect affinity set')

        # Remove the sockets the cpu set.
        for i, socket in enumerate(self.sockets):
            if threads_in_socket[i] == self.num_omp_threads:
                self.cpu_set -= socket


@rfm.simple_test
class OneTaskPerSocketOpenMP(OneTaskPerSocketOpenMPnomt):
    '''One task per socket, and as many OMP threads as CPUs per socket.

    We can reuse the test above. Just need to change the multithreading flag
    and the number of OMP threads.
    '''

    descr = 'One task per socket - w. multithreading.'
    use_multithreading = True

    @property
    def num_omp_threads(self):
        return int(self.num_cpus/self.num_sockets)

    @run_after('setup')
    def skip_if_no_mt(self):
        self.skip_if(self.num_cpus_per_core == 1,
                     'the cpu does not support multithreading')


@rfm.simple_test
class ConsecutiveSocketFilling(AffinityTestBase):
    '''Fill the sockets with the tasks in consecutive order.

    This test uses as many tasks as physical cores available in a node.
    Multithreading is disabled.
    '''

    cpu_bind = 'rank'
    use_multithreading = False

    @run_before('run')
    def set_tasks(self):
        self.num_tasks = int(self.num_cpus/self.num_cpus_per_core)
        self.num_cpus_per_task = 1

    @run_before('sanity')
    def consume_cpu_set(self):
        '''Check that all physical cores have been used in the right order.'''
        task_count = 0
        for socket_number in range(self.num_sockets):
            # Keep track of the CPUs present in this socket
            cpus_present = set()
            for task_number in range(int(self.num_tasks/self.num_sockets)):
                # Get the list of CPUs with affinity
                affinity_set = self.aff_cpus[task_count]

                # Only 1 CPU per affinity set allowed.
                if (len(affinity_set) > 1) or (any(cpu in cpus_present
                                                   for cpu in affinity_set)):
                    raise SanityError(
                        f'incorrect affinity set for task {task_count}'
                    )

                else:
                    cpus_present.update(
                        self.get_sibling_cpus(affinity_set[0], by='core')
                    )

                task_count += 1

            # Ensure all CPUs belong to the same socket
            cpuset_by_socket = self.get_sibling_cpus(
                next(iter(cpus_present)), by='socket'
            )
            if (not all(cpu in cpuset_by_socket for cpu in cpus_present) and
               len(cpuset_by_socket) == len(cpus_present)):
                raise SanityError(
                    f'socket {socket_number} not filled in order'
                )

            else:
                # Decrement the current NUMA node from the available CPU set
                self.cpu_set -= cpus_present


@rfm.simple_test
class AlternateSocketFilling(AffinityTestBase):
    '''Sockets are filled in a round-robin fashion.

    This test uses as many tasks as physical cores available in a node.
    Multithreading is disabled.
    '''

    use_multithreading = False

    @run_before('run')
    def set_tasks(self):
        self.num_tasks = int(self.num_cpus/self.num_cpus_per_core)
        self.num_cpus_per_task = 1
        self.num_tasks_per_socket = int(self.num_tasks/self.num_sockets)

    @run_before('sanity')
    def consume_cpu_set(self):
        '''Check that consecutive tasks are round-robin pinned to sockets.'''

        # Get a set per socket to keep track of the CPUs
        sockets = [set() for s in range(self.num_sockets)]
        task_count = 0
        for task in range(self.num_tasks_per_socket):
            for s in range(self.num_sockets):
                # Get the list of CPUs with affinity
                affinity_set = self.aff_cpus[task_count]

                # Only 1 CPU per affinity set is allowed
                if ((len(affinity_set) > 1) or
                   (any(cpu in sockets[s] for cpu in affinity_set)) or
                   (any(cpu not in self.sockets[s] for cpu in affinity_set))):
                    raise SanityError(
                        f'incorrect affinity set for task {task_count}'
                    )

                else:
                    sockets[s].update(
                        self.get_sibling_cpus(affinity_set[0], by='core')
                    )

                task_count += 1

            # Check that all sockets have the same CPU count
            if not all(len(s) == (task + 1) * self.num_cpus_per_core
                       for s in sockets):
                self.cpu_set.add(-1)

        # Decrement the socket set from the CPU set
        for s in sockets:
            self.cpu_set -= s


@rfm.simple_test
class OneTaskPerNumaNode(AffinityTestBase):
    '''Place a task on each NUMA node.

    The trick here is to "pad" the tasks with --cpus-per-task.
    The same could be done to target any cache level instead.
    Multithreading is disabled.
    '''

    valid_systems = ['+remote']
    use_multithreading = False
    num_cpus_per_task = required
    affinity_tool = fixture(CompileAffinityToolNoOmp, scope='environment')

    @run_before('run')
    def set_executable(self):
        scheduler = (
            self.affinity_tool.current_partition.scheduler.registered_name
        )
        if scheduler != 'firecrest-slurm':
            remote_stagedir = self.affinity_tool.stagedir
        else:
            remote_stagedir = self.affinity_tool.build_job.remotedir

        self.executable = os.path.join(
            remote_stagedir, 'affinity'
        )

    @run_before('run')
    def set_tasks(self):
        self.num_tasks = self.num_numa_nodes
        self.num_cpus_per_task = int(self.num_cpus / self.num_numa_nodes
                                     / self.num_cpus_per_core)

    @run_before('sanity')
    def consume_cpu_set(self):
        '''Check that each task lives in a different NUMA node.'''

        if len(self.aff_cpus) != self.num_numa_nodes:
            raise SanityError(
                'number of tasks does not match the number of numa nodes'
            )

        for numa_node, aff_set in enumerate(self.aff_cpus):
            cpuset_by_numa = self.get_sibling_cpus(aff_set[0], by='node')
            if (len(aff_set) != self.num_cpus_per_task or
               any(cpu not in cpuset_by_numa for cpu in aff_set)):
                raise SanityError(
                    f'incorrect affinity set for numa node {numa_node}'
                )
            else:
                # Decrement the current NUMA node from the available CPU set
                self.cpu_set -= cpuset_by_numa
