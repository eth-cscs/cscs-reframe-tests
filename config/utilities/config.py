# Copyright 2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import asyncio
import os
import re
import socket
from typing import Union
from utilities.io import (getlogger, request_modules,
                          user_descr, user_selection)
from utilities.job_util import Launcher, Scheduler, SlurmContext
from utilities.modules import ModulesSystem, modules_impl


class SystemConfig:
    '''Describes the system configuration'''

    def __init__(self):
        self._systemname = ''
        self._hostnames = []
        self._resourcesdir = ''
        self._modules_system = 'nomod'
        self._modules = []
        self._partitions = {}
        self._remote_launcher = ''
        self._remote_scheduler = ''

    @property
    def systemname(self):
        return self._systemname

    @property
    def hostnames(self):
        return self._hostnames

    @property
    def resourcesdir(self):
        return self._resourcesdir

    @property
    def modules_system(self):
        return self._modules_system

    @property
    def modules(self):
        return self._modules

    @property
    def partitions(self):
        return self._partitions

    def find_systemname(self):
        '''Try to get the system name from the
           environment variable CLUSTER_NAME
        '''
        systemname = os.getenv('CLUSTER_NAME')
        if systemname:
            self._systemname = systemname
            getlogger().info(f'System name is {systemname}')
        else:
            self._systemname = 'cluster'
            getlogger().warning(
                f'System name not found set to "{self._systemname}"'
            )

    def find_hostname(self):
        '''Try to get the hostname'''
        try:
            hostname = socket.gethostname()
        except Exception as e:
            self._hostnames.append('<hostname>')
            getlogger().error('Hostname not found')
            getlogger().error(f'Trying to retrieve the hostname raised:\n{e}')
        else:
            hostname = hostname.strip()
            hostname = re.search(r'^[A-Za-z]+', hostname)
            self._hostnames.append(hostname.group(0))
            getlogger().info(f'Hostname is {hostname.group(0)}')

    def find_modules_system(self) -> Union[ModulesSystem, None]:
        '''Detect the modules system and return it'''
        for mod in modules_impl:
            modules_system = modules_impl[mod]
            if modules_system().found:
                self._modules_system = modules_system().name
                getlogger().info(
                    f'Found a sane {self._modules_system} '
                    'installation in the system')
                break

        if self._modules_system:
            return modules_system()
        else:
            return None

    def _get_resourcesdir(self):
        '''Ask about a possible resources dir'''
        res_dir = user_descr(('Directory prefix where external test resources '
                             '(e.g., large input files) are stored.'),
                             cancel_n=True)
        while not os.path.exists(res_dir) and not res_dir:
            getlogger().warning('The specified directory does not exist.')
            res_dir = user_descr(('Directory prefix where external test '
                                  'resources (e.g., large input files) '
                                  'are stored.'), cancel_n=True)
        if res_dir:
            self._resourcesdir = res_dir

    def find_scheduler(self, user_input: bool, detect_containers: bool,
                       detect_devices: bool, wait: bool, access_opt: list,
                       tmp_dir: Union[str, None]) -> Union[SlurmContext, None]:
        '''Detect the remote scheduler'''
        scheduler = Scheduler()
        scheduler.detect_scheduler(user_input)
        self._remote_scheduler = scheduler.name
        if self._remote_scheduler == 'slurm' or \
           self._remote_scheduler == 'squeue':
            return SlurmContext(self._modules_system,
                                detect_containers=detect_containers,
                                detect_devices=detect_devices,
                                access_opt=access_opt,
                                wait=wait, tmp_dir=tmp_dir)
        else:
            return None

    def find_launcher(self, user_input: bool):
        '''Detect the parallel launcher'''
        launcher = Launcher()
        launcher.detect_launcher(user_input)
        self._remote_launcher = launcher.name

    def build_config(self, user_input: bool = True,
                     detect_containers: bool = True,
                     detect_devices: bool = True,
                     wait: bool = True, exclude_feats: list = [],
                     reservs: list = [], access_opt: list = [],
                     tmp_dir: Union[str, None] = None):
        '''Build the configuration with all the information'''
        # System name
        self.find_systemname()
        # Hostname
        self.find_hostname()
        # Modules system
        modules_system = self.find_modules_system()
        # TODO: not available for spack yet
        if modules_system and user_input:
            getlogger().debug('You can require some modules to be loaded '
                              'every time reframe is run on this system')
            self._modules = request_modules(modules_system)

        if user_input:
            self._get_resourcesdir()
        # Scheduler
        self._slurm_schd = self.find_scheduler(
            user_input,
            detect_containers=detect_containers,
            detect_devices=detect_devices,
            access_opt=access_opt,
            wait=wait, tmp_dir=tmp_dir
        )
        # Launcher
        self.find_launcher(user_input)
        # Partition detection only available with Slurm
        if self._slurm_schd:
            # Search node types
            self._slurm_schd.search_node_types(exclude_feats)
            # Start creation of the partitions if slurm is the scheduler
            self._slurm_schd.create_login_partition(user_input=user_input)
            # Initialize the asynchronous loop
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._slurm_schd.create_partitions(
                launcher=self._remote_launcher,
                scheduler=self._remote_scheduler,
                user_input=user_input))
            loop.close()
            # Assign the partitions to SystemConfig object
            self._partitions = self._slurm_schd.partitions
            # Create / search for the partitions based on the reservations
            if user_input or reservs:
                self._slurm_schd.search_reservations()
                if not user_input:
                    for reserv in reservs:
                        if reserv not in self._slurm_schd.reservations:
                            getlogger().warning(
                                f'Reservation {reserv} not found, '
                                'skipping...\n')
                        else:
                            self._slurm_schd.create_reserv_partition(
                                launcher=self._remote_launcher,
                                scheduler=self._remote_scheduler,
                                user_input=False,
                                reserv=reserv
                            )
                else:
                    reserv = True
                    while reserv:
                        getlogger().debug(
                            'Do you want to create a partition for '
                            'a reservation?')
                        getlogger().debug(f'{self._slurm_schd.reservations}\n')
                        reserv = user_selection(
                            self._slurm_schd.reservations, cancel_n=True)
                        if reserv:
                            self._slurm_schd.create_reserv_partition(
                                launcher=self._remote_launcher,
                                scheduler=self._remote_scheduler,
                                user_input=True,
                                reserv=reserv
                            )

    def format_for_jinja(self) -> dict:
        '''Generate an iterable for the jinja template'''
        system_dict = {}
        system_dict.update({'name': self.systemname})
        system_dict.update({'hostnames': self.hostnames})
        system_dict.update({'modules_system': self._modules_system})
        system_dict.update({'modules': self.modules})
        system_dict.update({'resourcesdir': self.resourcesdir})
        system_dict.update({'partitions': self.partitions})
        return system_dict
