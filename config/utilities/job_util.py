# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import asyncio
import fnmatch
import grp
import os
import re
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from typing import Union
from utilities.constants import (amd_gpu_architecture,
                                 containers_detect_bash,
                                 devices_detect_bash,
                                 nvidia_gpu_architecture,
                                 resources)
from utilities.io import (getlogger, status_bar, user_descr,
                          user_integer, user_selection, user_yn)

WDIR = os.getcwd()
TIME_OUT_POLICY = 200


@contextmanager
def change_dir(destination: str):
    try:
        os.chdir(destination)  # Change to the new directory
        yield
    finally:
        os.chdir(WDIR)  # Change back to the original directory

# TODO: create a common base class for Scheduler and Launcher


class Scheduler:
    '''Scheduler detector'''

    def __init__(self):
        self._scheduler_dic = [{'name': 'flux',   'cmd': 'flux'},
                               {'name': 'lsf',    'cmd': 'bsub'},
                               {'name': 'oar',    'cmd': 'oarsub'},
                               {'name': 'pbs',    'cmd': 'pbsnodes'},
                               {'name': 'sge',    'cmd': 'qconf'},
                               {'name': 'squeue', 'cmd': 'squeue'},
                               {'name': 'slurm',  'cmd': 'sacct'}]
        self._name = None

    def detect_scheduler(self, user_input: bool = True):

        schedulers_found = []
        for schd in self._scheduler_dic:
            try:
                subprocess.run(
                    ['which', f'{schd["cmd"]}'],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    universal_newlines=True, check=True
                )
            except subprocess.CalledProcessError:
                pass
            else:
                schedulers_found.append(schd['name'])

        if not schedulers_found:
            self._scheduler = 'local'
            getlogger().warning(
                'No remote scheduler was detected in the system'
            )
        elif len(schedulers_found) > 1:
            getlogger().debug(
                'The following schedulers were found: '
                f'{", ".join(schedulers_found)}'
            )
            if user_input:
                self._name = user_selection(schedulers_found)
            else:
                self._name = schedulers_found[-1]
        else:
            self._name = schedulers_found[0]

        getlogger().info(f'The scheduler is set to {self._name}\n')

    @property
    def name(self):
        return self._name


class Launcher:
    '''Launcher detector'''

    def __init__(self):
        self._launcher_dic = [{'name': 'alps',    'cmd': 'aprun'},
                              {'name': 'clush',   'cmd': 'clush'},
                              {'name': 'ibrun',   'cmd': 'ibrun'},
                              {'name': 'lrun',    'cmd': 'lrun'},
                              {'name': 'mpirun',  'cmd': 'mpirun'},
                              {'name': 'mpiexec', 'cmd': 'mpiexec'},
                              {'name': 'pdsh',    'cmd': 'pdsh'},
                              {'name': 'srun',    'cmd': 'srun'}]
        self._name = None

    def detect_launcher(self, user_input: bool = True):

        launchers_found = []
        for lnchr in self._launcher_dic:
            try:
                subprocess.run(
                    ['which', f'{lnchr["cmd"]}'],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    universal_newlines=True, check=True
                )
            except subprocess.CalledProcessError:
                pass
            else:
                launchers_found.append(lnchr['name'])

        if not launchers_found:
            self._name = 'local'
            getlogger().warning(
                'No parallel launcher was detected in the system'
            )
        elif len(launchers_found) > 1:
            getlogger().debug('The following launchers were found: '
                              f'{", ".join(launchers_found)}')
            if user_input:
                self._name = user_selection(launchers_found)
            else:
                self._name = launchers_found[-1]
        else:
            self._name = launchers_found[0]

        getlogger().info(f'The launcher is set to {self._name}\n')

    @property
    def name(self):
        return self._name


class SlurmContext:

    def __init__(self, modules_system: str, detect_containers: bool = True,
                 detect_devices: bool = True, wait: bool = True,
                 access_opt: list = [], tmp_dir: str = None):
        self.node_types = []
        self.default_nodes = []
        self.reservations = []
        self.partitions = []
        self._account = grp.getgrgid(os.getgid()).gr_name
        self._modules_system = modules_system
        self._detect_containers = detect_containers
        self._detect_devices = detect_devices
        self._wait = wait
        self._access = access_opt
        self._job_poll = []  # Job id's to poll
        self._p_n = 0  # Number of partitions created
        self._keep_tmp_dir = False
        if not tmp_dir:
            self.TMP_DIR = tempfile.mkdtemp(
                prefix='reframe_config_detection_', dir=os.getenv('SCRATCH'))
        else:
            self.TMP_DIR = tempfile.mkdtemp(
                prefix='reframe_config_detection_', dir=tmp_dir)

    def search_node_types(self, exclude_feats: list = []):

        getlogger().debug('Filtering nodes based on ActiveFeatures...')
        try:
            nodes_info = subprocess.run(
                'scontrol show nodes -o | grep "ActiveFeatures"',
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                universal_newlines=True, check=True, shell=True
            )
            nodes_info = nodes_info.stdout
            raw_node_types = re.findall(
                r'ActiveFeatures=([^ ]+) .*? Partitions=([^ ]+)', nodes_info)
            # Unique combinations of features and partitions
            raw_node_types = set(raw_node_types)
            # List of [[features, partition]...]
            raw_node_types = [[tuple(n[0].split(',')), tuple(
                n[1].split(','))] for n in raw_node_types]
        except Exception:
            getlogger().error(
                'Node types could not be retrieved from scontrol'
            )
            return

        default_partition = subprocess.run(
            'scontrol show partitions -o | grep "Default=YES"',
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            universal_newlines=True, check=True, shell=True
        )
        default_partition = re.findall(
            r'PartitionName=([\w]+)', default_partition.stdout)[0]
        getlogger().debug(f'Detected default partition: {default_partition}')
        if not default_partition:
            default_partition = None
            getlogger().warning('Default partition could not be detected')

        self._set_nodes_types(exclude_feats, raw_node_types, default_partition)

    def _set_nodes_types(self, exclude_feats: list, raw_node_types: list,
                         default_partition: Union[str, None]):

        default_nodes = []  # Initialize the list of node types in the default
        # Initialize the list of node types (with filtered features)
        node_types = []

        for node in raw_node_types:
            node_feats_raw = list(node[0])  # Before filtering features
            node_feats = node_feats_raw
            node_partition = node[1]
            if exclude_feats:  # Filter features
                node_feats = self._filter_node_feats(
                    exclude_feats, node_feats_raw)
            if node_feats:  # If all features were removed, empty list
                node_types.append(tuple(node_feats))
                # The nodes in the default partition based on their raw feats
                if default_partition in node_partition:
                    # default_nodes.append([tuple(node_feats_raw),tuple(node_feats)])
                    default_nodes.append(tuple(node_feats))

        default_nodes = set(default_nodes)
        if len(default_nodes) > 1:
            # Then all node types require the features in the access options
            self.default_nodes = set()
        else:
            # self.default_nodes = default_nodes[0][1] # Get the filtered feats
            self.default_nodes = default_nodes  # Get the filtered features

        getlogger().debug(
            f'\nThe following {len(set(node_types))} '
            'node types were detected:')
        for node_t in set(node_types):
            getlogger().debug(node_t)
        getlogger().info('')

        self.node_types = set(node_types)  # Get the unique combinations

    @staticmethod
    def _filter_node_feats(exclude_feats: list, node_feats: list) -> list:
        '''Filter the node types excluding the specified fixtures'''
        node_valid_feats = []
        for feat in node_feats:  # loop around the features
            feat_valid = not any([fnmatch.fnmatch(feat, pattern)
                                 for pattern in exclude_feats])
            if feat_valid:
                node_valid_feats.append(feat)
        return node_valid_feats

    def _find_devices(self, node_feats: list) -> Union[dict, None]:

        getlogger().debug(
            f'Detecting devices for node with features {node_feats}...')
        devices = subprocess.run(
            'scontrol show nodes -o | grep '
            f'"ActiveFeatures=.*{".*,.*".join(node_feats)}.*"',
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            universal_newlines=True, check=True, shell=True)
        try:
            devices_raw = re.findall(r'Gres=([\w,:()]+)', devices.stdout)[0]
        except Exception:
            getlogger().warning('Unable to detect the devices in the node')
            return None

        devices = [item.rsplit(':', 1)[0]
                   for item in devices_raw.split(',')]  # Remove the number
        devices = [','.join(devices)]
        if len(devices) > 1:
            # This means that the nodes with this set of features
            # do not all have the same devices installed. If the
            # nodes have all the same model of GPUs but different
            # number, it is considered as the same devices type
            # so we don't raise this msg
            getlogger().warning('Detected different devices in nodes '
                                'with the same set of features.\n'
                                'Please check the devices option in '
                                'the configuration file.')
            return None
        elif '(null)' in list(devices) or 'gpu' not in next(iter(devices)):
            # Detects if the nodes have no devices installed at
            # all or if not GPUs are installed
            getlogger().debug('No devices were found for this node type.')
            return None
        else:
            getlogger().debug('Detected GPUs.')
            # We only reach here if the devices installation
            # is homogeneous accross the nodes
            return self._count_gpus(devices_raw)

    @staticmethod
    def _get_access_partition(node_feats: list) -> Union[str, None]:

        nd_partitions = subprocess.run(
            'scontrol show nodes -o | grep '
            f'"ActiveFeatures=.*{".*,.*".join(node_feats)}.*"',
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            universal_newlines=True, check=True, shell=True)
        nd_partitions = re.findall(
            r'Partitions=([\w,:()]+)', nd_partitions.stdout)
        nd_partitions = set(nd_partitions)
        if len(nd_partitions) > 1:
            return None
        else:
            nd_partitions = nd_partitions.pop().split(",")
            for n_f in node_feats:
                if n_f in nd_partitions:
                    return f'-p{n_f}'
            if len(nd_partitions) == 1:
                return f'-p{nd_partitions[0]}'

    @staticmethod
    def _count_gpus(node_devices_raw: str) -> dict:

        # This method receives as input a string with the
        # devices in the nodes

        # If more than one device is installed, we get the list
        # Example: node_devices = 'gpu:2,craynetwork:6'
        node_devices = node_devices_raw.split(",")
        devices_dic = {}
        for dvc in node_devices:
            # Check if the device is a GPU
            # There will be at least 1 GPU
            if 'gpu' in dvc:
                # Get the device model gpu or gpu:a100
                device_type = dvc.rsplit(":", 1)[0]
                # Get the number of devices
                devices_n = int(dvc.rsplit(":", 1)[1])
                # Save the minimum number found in all nodes
                if device_type in devices_dic:
                    dvc_n = devices_dic[device_type]
                    if devices_n < dvc_n:
                        devices_dic[device_type] = devices_n
                else:
                    devices_dic.update({device_type: devices_n})

        return devices_dic

    def search_reservations(self):

        getlogger().debug('Searching for reservations...')
        reservations_info = subprocess.run(
            'scontrol show res | grep "ReservationName"',
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            universal_newlines=True, check=True, shell=True
        )
        reservations_info = reservations_info.stdout
        # Detecting the different types of nodes in the system
        reservations = None
        reservations = re.findall(
            r'ReservationName=([\w-]+)', reservations_info)
        self.reservations = reservations
        if not reservations:
            getlogger().warning('Unable to retrieve reservations')
        getlogger().info('')

    @staticmethod
    def _check_gpus_count(node_devices_slurm: dict,
                          node_devices_job: dict) -> list:

        gpus_slurm_count = 0  # Number of GPUs from Slurm Gres
        gpus_job_count = 0   # Number of GPUs from remote job detection
        devices = []

        # Check that the same number of GPU models are the same
        if len(node_devices_job) != len(node_devices_slurm):
            getlogger().warning(
                'WARNING: discrepancy between the '
                'number of GPU models\n'
                f'GPU models from Gres ({len(node_devices_slurm)}) '
                f'GPU models from job ({len(node_devices_job)}) '
            )

        # Get the total number of GPUs (independently of the model)
        for gpu_slurm in node_devices_slurm:
            gpus_slurm_count += node_devices_slurm[gpu_slurm]

        # Format the dictionary of the devices for the configuration file
        # and get the total number of GPUs found
        for gpu_job in node_devices_job:
            devices.append({'type': 'gpu',
                            'model': gpu_job,
                            'arch': nvidia_gpu_architecture.get(gpu_job) or
                                    amd_gpu_architecture.get(gpu_job),
                            'num_devices': node_devices_job[gpu_job]})
            gpus_job_count += node_devices_job[gpu_job]

        if gpus_job_count != gpus_slurm_count:
            getlogger().warning('The total number of detected GPUs '
                                f'({gpus_job_count}) '
                                'differs from the (minimum) in GRes '
                                f'from slurm({gpus_slurm_count}).')
            if gpus_job_count > gpus_slurm_count:
                getlogger().debug('It might be that nodes in this partition '
                                  'have different number of GPUs '
                                  'of the same model.\nIn the config, the '
                                  'minimum number of GPUs that will '
                                  'be found in the nodes of this partition '
                                  'is set.\n')
            elif gpus_job_count < gpus_slurm_count:
                getlogger().error(
                    'Lower number of GPUs were detected in the node.\n')

        return devices

    def create_login_partition(self, user_input: bool = True):
        create_p = True
        if user_input:
            create_p = user_yn('Do you want to create a partition '
                               'for the login nodes?')
        if create_p:
            max_jobs = 4
            time_limit = '2m'
            if user_input:
                max_jobs = user_integer('Maximum number of forced local build '
                                        'or run jobs allowed?',
                                        default_value=max_jobs)
                time_limit = user_descr('Time limit for the jobs submitted '
                                        'on this partition?\nEnter "null" for'
                                        ' no time limit',
                                        default_value=time_limit)
            self.partitions.append(
                {'name':      'login',
                 'scheduler':  'local',
                 'time_limit': time_limit,
                 'environs':   ['builtin'],
                 'max_jobs':   max_jobs,
                 'launcher':   'local'})

    async def create_remote_partition(self, node_feats: tuple, launcher: str,
                                      scheduler: str, user_input: bool = True):

        node_features = list(node_feats)
        _detect_devices = self._detect_devices
        _detect_containers = self._detect_containers
        create_p = True
        if user_input:
            create_p = user_yn('Do you want to create a partition '
                               f'for the node with features: {node_feats}?')
        if create_p:
            self._p_n += 1
            access_options = [f'--account={self._account}']
            if self._access:
                access_options = access_options + self._access
            access_node = []
            if node_feats not in self.default_nodes:
                access_node = '&'.join(node_features)
            name = f'partition_{self._p_n}'
            if not user_input:
                getlogger().info(f'{name} : {node_feats}', color=False)
            max_jobs = 100
            time_limit = '10m'
            container_platforms = []
            devices = []

            # If user_input requested, these values will be changed according
            if user_input:
                name = user_descr('How do you want to name the partition?',
                                  default_value=name)

                max_jobs = user_integer('Maximum number of forced local build '
                                        'or run jobs allowed?',
                                        default_value=max_jobs)

                time_limit = user_descr('Time limit for the jobs submitted '
                                        'on this partition?\nEnter "null" for '
                                        'no time limit',
                                        default_value=time_limit)

                getlogger().debug(
                    f'The associated group "{self._account}" was added to the '
                    'slurm access options -A'
                )
                if access_node:
                    getlogger().debug(
                        'This node type is not the node type by '
                        'default, I added the required constraints:'
                        f' --constraint="{access_node}".'
                    )
                access_user = user_descr(
                    'Do you need any additional access options?',
                    cancel_n=True
                )
                if access_user:
                    access_options.append(access_user)

                _detect_containers = user_yn(
                    'Do you require remote containers detection?')

            if _detect_devices:
                # Retrieve a dictionary with the devices info
                # If GRes for these nodes is 'gpu:a100:*'
                # The returned dict will be:
                # {'gpu:a100' : min(*)}
                _detect_devices = self._find_devices(node_features)

            getlogger().info('')

            # Handle the job submission only if required
            if _detect_devices or _detect_containers:
                self._keep_tmp_dir = True
                # All this must be inside a function
                remote_job = JobRemoteDetect(
                    self.TMP_DIR, _detect_containers, _detect_devices)
                access_partition = self._get_access_partition(node_features)
                access_options = await remote_job.job_submission(
                    name, access_options, access_node,
                    access_partition, wait=self._wait
                )
                if not self._wait and remote_job.job_id:
                    self._job_poll.append(remote_job.job_id)
                    # Here, the job failed or the output was already read
                else:
                    if remote_job.container_platforms:
                        container_platforms = remote_job.container_platforms
                        if 'tmod' not in self._modules_system and \
                                'lmod' not in self._modules_system:
                            getlogger().warning(
                                '\nContainer platforms were '
                                'detected but the automatic detection '
                                'of required modules is not possible '
                                f'with {self._modules_system}.'
                            )
                        else:
                            getlogger().info('')
                        # Add the container platforms in the features
                        for cp_i, cp in enumerate(container_platforms):
                            getlogger().debug(
                                f'Detected container platform {cp["type"]} '
                                'in partition "{name}"'
                            )
                            node_features.append(cp['type'].lower())
                    else:
                        getlogger().debug(
                            '\n\nNo container platforms were detected in '
                            f'partition "{name}"'
                        )

                    if remote_job.devices:
                        # Issue any warning regarding missconfigurations
                        # between Gres and the detected devices
                        getlogger().info(f"\nGPUs found in partition {name}")
                        devices = self._check_gpus_count(
                            _detect_devices, remote_job.devices)

            elif access_node:
                # No jobs were launched so we cannot check the access options
                access_options.append(access_node)

            # Create the partition
            self.partitions.append(
                {'name':      name,
                 'scheduler':  scheduler,
                 'time_limit': time_limit,
                 'environs':   ['builtin'],
                 'max_jobs':   max_jobs,
                 'resources':  resources,
                 'extras':     {},
                 'env_vars':   [],
                 'launcher':   launcher,
                 'access':     access_options,
                 'features':   node_features+['remote'],
                 'devices':    devices,
                 'container_platforms': container_platforms}
            )
        else:
            getlogger().info('')

    def create_reserv_partition(self, reserv: str, launcher: str,
                                scheduler: str, user_input: bool = True):

        self._p_n += 1
        access_options = [f'--account={self._account}']
        access_options.append(f'--reservation={reserv}')
        name = f'{reserv}'
        if not user_input:
            getlogger().info(
                f'Creating partition "{name}" for reservation: {reserv}',
                color=False
            )
        max_jobs = 100
        time_limit = '10m'
        max_jobs = 100
        time_limit = '10m'
        container_platforms = []
        devices = []

        # If user_input requested, these values will be changed according
        if user_input:
            name = user_descr('How do you want to name the partition?',
                              default_value=name)

            max_jobs = user_integer('Maximum number of forced local build '
                                    'or run jobs allowed?',
                                    default_value=max_jobs)

            time_limit = user_descr('Time limit for the jobs submitted '
                                    'on this partition?\nEnter "null" for no '
                                    'time limit', default_value=time_limit)

            getlogger().debug(
                f'The associated group "{self._account}" was added to the '
                'slurm access options - A'
            )
            getlogger().debug(
                'The reservation was added to the slurm access options '
                f'--reservation{reserv}.')
            access_user = user_descr(
                'Do you need any additional access options?', cancel_n=True)
            if access_user:
                access_options.append(access_user)

        # Create the partition
        self.partitions.append(
            {'name':      name,
             'scheduler':  scheduler,
             'time_limit': time_limit,
             'environs':   ['builtin'],
             'max_jobs':   max_jobs,
             'resources':  resources,
             'extras':     {},
             'env_vars':   [],
             'launcher':   launcher,
             'access':     access_options,
             'features':   [reserv, 'remote'],
             'devices':    devices,
             'container_platforms': container_platforms}
        )
        getlogger().info('')

    async def create_partitions(self, launcher: str, scheduler: str,
                                user_input: bool = True):

        # With no status bar
        # await asyncio.gather(*(self.create_remote_partition(node,launcher,
        # scheduler, user_input) for node in self.node_types))

        all_partitions = asyncio.ensure_future(asyncio.gather(
            *(self.create_remote_partition(
                node, launcher, scheduler, user_input
            ) for node in self.node_types)))

        status_task = None
        try:
            # 5 seconds delay until the bar appears
            done, pending = await asyncio.wait(
                [all_partitions, asyncio.ensure_future(
                    asyncio.sleep(10))],
                return_when=asyncio.FIRST_COMPLETED
            )
            # If the tasks are still running after 5 seconds,
            # start the status bar
            if not all_partitions.done():
                status_task = asyncio.ensure_future(status_bar())
            else:
                # If no jobs were submitted it is possible that
                # the sleep 5 secs is still pending
                for task in pending:
                    task.cancel()
            # Wait for all tasks to complete
            await all_partitions
        finally:
            # Print warning if no partitions were created
            if not self.partitions:
                getlogger().error(
                    '\nNo partitions were created, ReFrame '
                    'requires at least one.\n'
                )
            # Remove unused temp dir or print it
            if self._keep_tmp_dir:
                getlogger().info(
                    '\nYou can check the job submissions '
                    f'in {self.TMP_DIR}.\n', color=False
                )
            else:
                shutil.rmtree(self.TMP_DIR)
            # Cancel the status bar if it was started
            if status_task:
                status_task.cancel()
                try:
                    await status_task  # Ensure the status bar is canceled
                except asyncio.CancelledError:
                    # Handle the cancellation gracefully
                    pass
            sys.stdout.flush()


class JobRemoteDetect:
    '''Job to detect information about the remote nodes'''

    _SBATCH_HEADER = (
        '#!/bin/bash\n'
        '#SBATCH --job-name="Config_autodetection"\n'
        '#SBATCH --ntasks=1\n'
        '#SBATCH --output=config_autodetection_{partition_name}.out\n'
        '#SBATCH --error=config_autodetection_{partition_name}.out\n'
        '#SBATCH --time=0:2:0\n'
    )
    _SBATCH_FILE = 'autodetection_{partition_name}.sh'
    _OUTPUT_FILE = 'config_autodetection_{partition_name}.out'

    def __init__(self, tmp_dir: str, detect_containers: bool = True,
                 detect_devices: bool = True):
        self._detect_containers = detect_containers
        self._detect_devices = detect_devices
        self.container_platforms = []
        self.devices = {}
        self.job_id = None
        self.TMP_DIR = tmp_dir

    def _prepare_job(self, partition_name: str, access_options: list):
        with change_dir(self.TMP_DIR):
            with open(self._SBATCH_FILE.format(partition_name=partition_name),
                      "w") as file:
                file.write(self._SBATCH_HEADER.format(
                    partition_name=partition_name))
                for access in access_options:
                    file.write(f"#SBATCH {access}\n")
                if self._detect_containers:
                    file.write(containers_detect_bash)
                file.write("\n")
                file.write("\n")
                if self._detect_devices:
                    file.write(devices_detect_bash)

    async def _submit_job(self, partition_name: str,
                          wait: bool) -> Union[bool, None, str]:

        with change_dir(self.TMP_DIR):
            cmd_parts = ['sbatch']
            if wait:
                cmd_parts.append('-W')
            cmd_parts += [f'autodetection_{partition_name}.sh']
            cmd = ' '.join(cmd_parts)
            completed = await asyncio.create_subprocess_shell(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            cmd_out = await completed.stdout.readline()
            cmd_out = cmd_out.decode().strip()
            job_id = re.search(r'Submitted batch job (?P<jobid>\d+)', cmd_out)
            if job_id:
                job_id = job_id.group('jobid')
                getlogger().info(
                    f'\nJob submitted to partition {partition_name}: {job_id}'
                )
            elif 'error' in cmd_out or not cmd_out:
                return False

            try:
                stdout, stderr = await asyncio.wait_for(
                    completed.communicate(), timeout=TIME_OUT_POLICY
                )
            except asyncio.TimeoutError:
                getlogger().warning(
                    f'\nJob submitted to {partition_name} took too long...'
                )
                getlogger().info('Cancelling...', color=False)
                subprocess.run(
                    f'scancel {job_id}', universal_newlines=True,
                    check=True, shell=True
                )
                return 'cancelled'

            if completed.returncode != 0:
                # Do not print error, second attempt with -p
                return False

            stdout = stdout.decode('utf-8')
            stdout = stdout.strip()
            if not wait:
                jobid = re.search(r'Submitted batch job (?P<jobid>\d+)',
                                  stdout)
                if not jobid:
                    return None
                else:
                    return jobid.group('jobid')
            else:
                return True

    async def job_submission(self, partition_name: str,
                             access_options: list,
                             access_node: list,
                             access_partition: Union[str, None],
                             wait: bool = False):

        if access_node:
            self._prepare_job(partition_name, access_options +
                              [f'--constraint="{access_node}"'])
        else:
            self._prepare_job(partition_name, access_options)
        job_exec = await self._submit_job(partition_name, wait)
        cancelled = False
        if job_exec == 'cancelled':
            access_partition = ''  # Avoid a resubmission
            job_exec = False
            cancelled = True
            access_options.append(access_partition)
        if job_exec and access_node:
            access_options.append(f'--constraint="{access_node}"')
        elif access_partition:
            self._prepare_job(partition_name, [access_partition])
            job_exec = await self._submit_job(partition_name, wait)
            if job_exec == 'cancelled':
                job_exec = False
                cancelled = True
                access_options.append(access_partition)
            if job_exec:
                access_options.append(access_partition)

        if job_exec and wait:
            self._extract_info(partition_name)
        elif not job_exec and not cancelled:
            if access_node:
                access_options.append(f'--constraint="{access_node}"')
            getlogger().error(
                f'The autodetection script for "{partition_name}" '
                'could not be submitted\n'
                'Please check the sbatch options ("access" field '
                'in the partition description).'
            )
        else:
            # TODO I should check here that job_exec is a number
            self.job_id = job_exec

        return access_options  # return the access options that worked

    @staticmethod
    def _parse_devices(file_path: str) -> dict:
        '''Extract the information about the GPUs from the job output'''
        gpu_info = {}  # Initialize the dict for GPU info
        nvidia_gpus_found = False
        amd_gpus_found = False

        with open(file_path, 'r') as file:
            lines = file.readlines()

        for line in lines:
            # Check for NVIDIA GPUs
            if "NVIDIA GPUs installed" in line:
                nvidia_gpus_found = True
            elif line == '\n':
                nvidia_gpus_found = False
            elif not line or "Batch Job Summary" in line:
                break
            elif nvidia_gpus_found:
                model = [
                    gpu_m for gpu_m in nvidia_gpu_architecture
                    if gpu_m in line
                ]
                if len(model) > 1:
                    model = []
                if model:
                    if model[0] not in gpu_info:
                        gpu_info.update({model[0]: 1})
                    else:
                        gpu_info[model[0]] += 1

            # Check for AMD GPUs
            if "AMD GPUs" in line:
                amd_gpus_found = True
                amd_lines = []
            elif line == '\n' or "lspci" in line:
                amd_gpus_found = False
            elif not line or "Batch Job Summary" in line:
                break
            elif amd_gpus_found:
                if line not in amd_lines:
                    amd_lines.append(line)
                    model = [
                        gpu_m for gpu_m in amd_gpu_architecture
                        if gpu_m in line
                    ]
                    if len(model) > 1:
                        model = []
                    if model:
                        if model[0] not in gpu_info:
                            gpu_info.update({model[0]: 1})
                        else:
                            gpu_info[model[0]] += 1
                else:
                    pass

        return gpu_info

    @staticmethod
    def _parse_containers(file_path: str) -> list:
        '''Extract the information about the containers from the job output'''
        containers_info = []
        containers_found = False

        with open(file_path, 'r') as file:
            lines = file.readlines()

        for line in lines:
            if "Installed containers" in line:
                containers_found = True
            elif "GPU" in line or line == "\n" or "Batch Job Summary" in line:
                containers_found = False
                break
            elif containers_found:
                type = line.split(' modules: ')[0].strip()
                try:
                    modules = line.split(' modules: ')[1].split(', ')
                    modules = [m.strip() for m in modules]
                    if modules[0] != '':
                        modules.append(type.lower())
                    else:
                        modules = [type.lower()]
                except Exception:
                    modules = []
                containers_info.append({'type': type, 'modules': modules})

        return containers_info

    def _extract_info(self, partition_name: str):

        file_path = os.path.join(
            self.TMP_DIR, self._OUTPUT_FILE.format(
                partition_name=partition_name
            )
        )
        if self._detect_containers:
            self.container_platforms = self._parse_containers(file_path)

        if self._detect_devices:
            self.devices = self._parse_devices(file_path)
