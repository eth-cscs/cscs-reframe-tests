# Copyright 2016-2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import re
import sys
import os
import grp
import subprocess
import json
import shlex
import traceback
from jinja2 import Environment, FileSystemLoader

# https://reframe-hpc.readthedocs.io/en/stable/config_reference.html#config.systems.partitions.time_limit
TIME_LIMIT_LOGIN = '10m' # Time limit for jobs running in the login partition
# https://reframe-hpc.readthedocs.io/en/stable/config_reference.html#config.systems.partitions.max_jobs
MAX_JOBS_LOGIN = 4 # Max number of jobs in login partition
MAX_JOBS_RMT = 100 # Max number of jobs in remote partition
MAX_JOBS_INTERACT = 10 # Max number of jobs in interactive partition

system_config   = {}

SCHEDULERS = [{'name': 'flux',   'cmd': 'flux'}, 
              {'name': 'lsf',    'cmd': 'bsub'}, 
              {'name': 'oar',    'cmd': 'oarsub'}, 
              {'name': 'pbs',    'cmd': 'pbsnodes'},  
              {'name': 'sge',    'cmd': 'qconf'}, 
              {'name': 'squeue', 'cmd': 'squeue'},  
              {'name': 'slurm',  'cmd': 'sacct'}]

LAUNCHERS = [{'name': 'alps',    'cmd': 'aprun'}, 
             {'name': 'clush',   'cmd': 'clush'}, 
             {'name': 'ibrun',   'cmd': 'ibrun'}, 
             {'name': 'lrun',    'cmd': 'lrun'},  
             {'name': 'mpirun',  'cmd': 'mpirun'}, 
             {'name': 'mpiexec', 'cmd': 'mpiexec'},  
             {'name': 'pdsh',    'cmd': 'pdsh'},  
             {'name': 'srun',    'cmd': 'srun'}]

CONTAINERS = [{'name': 'Sarus',       'cmd': 'sarus'}, 
              {'name': 'Apptainer',   'cmd': 'apptainer'}, 
              {'name': 'Docker',      'cmd': 'docker'}, 
              {'name': 'Singularity', 'cmd': 'singularity'},
              {'name': 'Shifter',     'cmd': 'shifter'}]

class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

RFM_DOCUMENTATION = {'modules':              'https://reframe-hpc.readthedocs.io/en/stable/config_reference.html#config.systems.modules',
                     'resourcesdir':         'https://reframe-hpc.readthedocs.io/en/stable/config_reference.html#config.systems.resourcesdir',
                     'schedulers':           'https://reframe-hpc.readthedocs.io/en/stable/config_reference.html#config.systems.partitions.scheduler',\
                     'devices':              'https://reframe-hpc.readthedocs.io/en/stable/config_reference.html#config.systems.partitions.devices',
                     'sched_resources':      'https://reframe-hpc.readthedocs.io/en/stable/config_reference.html#custom-job-scheduler-resources',
                     'extras':               'https://reframe-hpc.readthedocs.io/en/stable/config_reference.html#config.systems.partitions.extras',
                     'partition_resources':  'https://reframe-hpc.readthedocs.io/en/stable/config_reference.html#config.systems.partitions.resources',
                     'partition_envvars':    'https://reframe-hpc.readthedocs.io/en/stable/config_reference.html#config.systems.partitions.env_vars',
                     'container_platforms':  'https://reframe-hpc.readthedocs.io/en/stable/config_reference.html#container-platform-configuration',
                     'container_platformsm': 'https://reframe-hpc.readthedocs.io/en/stable/config_reference.html#config.systems.partitions.container_platforms.modules',
                     'environments':         'https://reframe-hpc.readthedocs.io/en/stable/config_reference.html#environments',
                     'modes':                'https://reframe-hpc.readthedocs.io/en/stable/config_reference.html#execution-mode-configuration'}

resources = [{'name': 'switches',
              'options': ['--switches={num_switches}']},
             {'name': 'gres',
             'options': ['--gres={gres}']},
             {'name': 'memory',
              'options': ['--mem={mem_per_node}']}]


def main():

    system_config['systems']   = []

    # Get the system name 
    # OK, TESTED
    cluster_name = os.getenv('CLUSTER_NAME')
    # TEST: 
    # cluster_name = os.getenv('CLUSTER_BLANCA')
    # cluster_name = "blanca"
    if cluster_name:
        print(f'{bcolors.BOLD}{bcolors.UNDERLINE}' + 
              f'System name{bcolors.ENDC}{bcolors.ENDC}' +
              f' is {bcolors.GREEN}{cluster_name}{bcolors.ENDC}')
    else:
        cluster_name = 'cluster'
        print(f'{bcolors.BOLD}{bcolors.UNDERLINE}' + 
              f'System name{bcolors.ENDC}{bcolors.ENDC}' +
              f' {bcolors.WARNING}not found{bcolors.ENDC}, ' +
              f'set to {bcolors.WARNING}{cluster_name}{bcolors.ENDC}')
            
    print()
    system_config['systems'].append({'name': cluster_name})

    # Get the hostname
    # OK, TESTED
    try:
        hostname = subprocess.run(
            ['hostname'], 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        # TEST:
        # hostname = subprocess.run(
        #     ['hostblanca'], 
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE,
        #     universal_newlines=True
        # )
    except FileNotFoundError:
        print(f'{bcolors.BOLD}{bcolors.UNDERLINE}' + 
              f'Hostname{bcolors.ENDC}{bcolors.ENDC} ' +
              f'{bcolors.FAIL}not found{bcolors.ENDC}')
        hostname = '<hostname>'
    else:
        hostname = hostname.stdout.strip()
        hostname = re.search(r'(^\w+)', hostname)
        hostname = hostname.group(0)
        print(f'{bcolors.BOLD}{bcolors.UNDERLINE}' +
              f'Hostname{bcolors.ENDC}{bcolors.ENDC} ' +
              f'is {bcolors.GREEN}{hostname}{bcolors.ENDC}')

    if hostname != '<hostname>' and cluster_name != 'cluster':  
        if hostname != cluster_name:
           print(f'{bcolors.WARNING}Detected hostname and ' +
                 f'systemname are different{bcolors.ENDC}') 

    print()
    system_config['systems'][0].update({'hostnames': [hostname]})

    # Get the modules system
    # OK, TESTED
    module_system = 'nomod'
    # Detect lmod and tmod
    module_info = os.getenv('LMOD_CMD')
    # TEST:
    # module_info = os.getenv('BLANCA_CMD')
    # module_info = subprocess.run(
    #             [f"{module_info}","list"], 
    #             stdout=subprocess.PIPE,
    #             stderr=subprocess.PIPE,
    #             universal_newlines=True
    #         )
    # print(module_info.stderr)
    if not module_info:
        try:
            module_info = subprocess.run(
                ['modulecmd','-V'], 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
        except FileNotFoundError:
            try:
                module_info = subprocess.run(
                    ['spack','-V'], 
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
            except FileNotFoundError:
                pass
            else:
                module_system = "spack"
        else:
            # TEST:
            # module_info = 'VERSION=3.2.11.4\n DATE=2019-10-23 \n AUTOLOADPATH=undef \n BASEPREFIX="/opt/cray/pe/modules"'
            # module_info = 'VERSION=3.0.11.4\n DATE=2019-10-23 \n AUTOLOADPATH=undef \n BASEPREFIX="/opt/cray/pe/modules"'
            # module_info = 'VERSION=4.2.11.4\n DATE=2019-10-23 \n AUTOLOADPATH=undef \n BASEPREFIX="/opt/cray/pe/modules"'
            version_tmod = re.search(r'^VERSION=(\S+)', module_info.stderr,
                                  re.MULTILINE)
            if version_tmod:
                version = version_tmod.group(1)
                try:
                    ver_major, ver_minor = [int(v) for v in version.split('.')[:2]]
                except ValueError:
                    raise ValueError(
                        'could not parse TMod version string: ' + 
                        version) from None
                if ver_major >= 4 and ver_minor >= 1:
                    module_system = "tmod4"
                elif ver_major >= 3 and ver_minor >= 2:
                    module_system = "tmod32"
                elif ver_major >= 3 and ver_minor >= 1:
                    module_system = "tmod31"
                else:
                    print(f'{bcolors.WARNING}Detected unsupported ' +
                        f'TMod version: {version}{bcolors.ENDC}') 
    else:
        module_system = "lmod"

    if module_system != "nomod":
        print(f'The {bcolors.BOLD}{bcolors.UNDERLINE}module system' +
              f'{bcolors.ENDC}{bcolors.ENDC} for the system {cluster_name}' +
              f' is set to {bcolors.GREEN}{module_system}{bcolors.ENDC}')
    else:
        print(f'{bcolors.WARNING}No valid {bcolors.BOLD}{bcolors.UNDERLINE}' +
              f'module system{bcolors.ENDC} {bcolors.WARNING}was detected.' +
              f'{bcolors.ENDC} Set to nomod.')

    print()
    system_config['systems'][0].update({'modules_system': module_system})

    # Ask for modules to be loaded
    # OK, TESTED
    if module_system != "nomod":
        print("You can require some modules to be loaded every time reframe is run on this system")
        modules_list = []
        load_modules = input("Do you require any modules to be loaded?\n" +
                            "If yes please write the modules names separated by commas\n" + 
                            "If no please enter n\n")

        if load_modules.lower() == 'n':
            print("No modules will be added.")
        elif module_system == "lmod":
            modules_list = [mod.strip() for mod in load_modules.split(",")]
            modules_valid = []
            wrong_modules = len(modules_list)
            index_remove = []
            while wrong_modules != 0:
                wrong_modules = len(modules_list)
                for m_i, m in enumerate(modules_list):
                    m_output = subprocess.run(
                        f'module spider {m}', 
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                        check=False,
                        shell=True
                        )
                    if "Versions" in m_output.stdout:
                        m_output = m_output.stdout.split("\n")
                        m_output = [m_i.strip() for m_i in m_output]
                        versions = []
                        v_i = m_output.index("Versions:")+1
                        all_versions = False
                        while not all_versions:
                            versions.append(m_output[v_i])
                            if "Other" in m_output[v_i+1]:
                                v_i += 2
                            elif not m_output[v_i+1]:
                                all_versions = True
                            else:
                                v_i += 1
                        new_module = input(f"There are multiple versions of the module {versions}.\n" 
                                           f"Please select one (or enter n to remove it):")
                        while new_module not in versions and new_module.lower() != "n":
                            new_module = input(f"Check the syntax please:")
                        if new_module.lower() != "n":
                            modules_list[m_i] = new_module
                            wrong_modules -= 1
                        else:
                            index_remove.append(m_i) 
                            wrong_modules -= 1
                    elif "error" in  m_output.stdout:
                        new_module = input(f"Module {modules_list[m_i]} not available.\n" 
                                           f"Specify the right one or enter n to remove it from the required modules:")
                        if new_module.lower() != "n":
                            modules_list[m_i] = new_module
                        else:
                            index_remove.append(m_i)
                            wrong_modules -= 1
                    else:
                        wrong_modules -= 1
                if index_remove:
                    for i in index_remove[::-1]:
                        modules_list.pop(i)
                index_remove = []
            print(f"Required {bcolors.UNDERLINE}{bcolors.BOLD}modules{bcolors.ENDC}: {modules_list}")
        else:
            modules_list = [mod.strip() for mod in load_modules.split(",")]
            modules_valid = []
            print(f"Required {bcolors.UNDERLINE}{bcolors.BOLD}modules{bcolors.ENDC}: {modules_list}")
            print(f"{bcolors.WARNING}WARNING: I won't check the syntax " +
                  f"and availability of the specified modules.{bcolors.ENDC}")

        if modules_list:
            system_config['systems'][0].update({'modules': modules_list})
    print()

    # Additional fields that must be manually configured
    resourcesdir = input("Do you want to add a resources directory for the system?\n" +
                        "Directory prefix where external test resources (e.g., large input files) are stored.\n" +
                        "If no just enter n.\n" )

    if resourcesdir.lower() != "n":
        while not os.path.exists(resourcesdir):
            resourcesdir = input("The specified directory does not exist.\n" +
                                "Please enter a valid directory (or n):\n")
            if resourcesdir.lower() == "n":
                break
        if resourcesdir.lower() != "n":
            system_config['systems'][0].update({'resourcesdir': resourcesdir})

    print()

    # Detect the scheduler: we need the scheduler to detect the partitions
    # OK, TESTED
    schedulers_found = []
    for sched_i in SCHEDULERS:
        try:
            scheduler = subprocess.run(
                ['which', f'{sched_i["cmd"]}'], 
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                check=True
            )
        except subprocess.CalledProcessError:
            pass
        else:
            schedulers_found.append(sched_i['name'])

    if not schedulers_found:
        # Set the scheduler to local if no other scheduler was detected
        print('No scheduler was detected')
        scheduler = 'local'
        print(f'The {bcolors.BOLD}{bcolors.UNDERLINE}' +
              f'scheduler{bcolors.ENDC}{bcolors.ENDC} ' +
              f'for the system {cluster_name} is set to ' +
              f'{bcolors.WARNING}{scheduler}{bcolors.ENDC}')
    else:
        print(f'The following schedulers were found: '+
              f'{", ".join(schedulers_found)}')
        if len(schedulers_found) == 1:
            scheduler = schedulers_found[0]
            print(f'The {bcolors.BOLD}{bcolors.UNDERLINE}' +
                  f'scheduler{bcolors.ENDC}{bcolors.ENDC} ' +
                  f'for the system {cluster_name} is set to ' + 
                  f'{bcolors.GREEN}{schedulers_found[0]}{bcolors.ENDC}')
        else:
            # Offer the different options for the schedulers
            print(RFM_DOCUMENTATION["schedulers"])
            scheduler = input("Please select a scheduler from the list above: ")
            while scheduler not in schedulers_found:
                scheduler = input("The scheduler was not recognized. Please check the syntax: ")
        print(f'The {bcolors.BOLD}{bcolors.UNDERLINE}' +
            f'scheduler{bcolors.ENDC}{bcolors.ENDC} ' +
            f'for the system {cluster_name} is set to ' + 
            f'{bcolors.GREEN}{scheduler}{bcolors.ENDC}')
    
    print()

    # Detect the parallel launcher
    launchers_found = []
    for launch_i in LAUNCHERS:
        try:
            launcher = subprocess.run(
                ['which', f'{launch_i["cmd"]}'], 
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                check=True
            )
        except subprocess.CalledProcessError:
            pass
        else:
            launchers_found.append(launch_i['name'])

    if not launchers_found:
        # Set the scheduler to local if no other scheduler was detected
        print('No parallel launcher was detected')
        launcher = 'local'
        print(f'The {bcolors.BOLD}{bcolors.UNDERLINE}' +
              f'launcher{bcolors.ENDC}{bcolors.ENDC} ' +
              f'for the partitions is set to {bcolors.WARNING}' +
              f'local{bcolors.ENDC}')
    else:
        print(f'The following launchers were found: ' +
              f'{", ".join(launchers_found)}')
        if len(launchers_found) == 1:
            launcher = launchers_found[0]
            print(f'The {bcolors.BOLD}{bcolors.UNDERLINE}' +
                  f'launcher{bcolors.ENDC}{bcolors.ENDC} ' +
                  f'for the partitions is set to {bcolors.GREEN}' +
                  f'{launchers_found[0]}{bcolors.ENDC}')
        else:
            # Offer the different options for the launchers
            launcher = input("Please select a launcher from the list above: ")
            while launcher not in launchers_found:
                launcher = input("The launcher was not recognized. Please check the syntax: ")
            print(f'The {bcolors.BOLD}{bcolors.UNDERLINE}' +
                f'launcher{bcolors.ENDC}{bcolors.ENDC} ' +
                f'for the partitions is set to ' + 
                f'{bcolors.GREEN}{launcher}{bcolors.ENDC}')

    print()

    # Detect container platforms
    #FIXME: The container platforms should be detected in the remote partitions
    # This part should be moved inside the partition creation
    containers_found = []
    for contain_i in CONTAINERS:
        try:
            container = subprocess.run(
                ['which', f'{contain_i["cmd"]}'], 
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                check=True
            )
        except subprocess.CalledProcessError:
            pass
        else:
            containers_found.append(contain_i['name'])

    if not containers_found:
        print('No container platforms were detected')
    else:
        print(f'The following containers were found: ' +
              f'{", ".join(containers_found)}')
        container_platforms = []
        for cp_i, cp in enumerate(containers_found):
            container_platforms.append({'type': cp})

            if module_system != "nomod":
                modules_list = []
                load_modules = input(f"Do you require any modules to be loaded to use {cp}?\n" +
                                    "If yes please write the modules names separated by commas\n" + 
                                    "If no please enter n\n")

                if load_modules.lower() == 'n':
                    print("No modules will be added.")
                elif module_system == "lmod":
                    modules_list = [mod.strip() for mod in load_modules.split(",")]
                    modules_valid = []
                    wrong_modules = len(modules_list)
                    index_remove = []
                    while wrong_modules != 0:
                        wrong_modules = len(modules_list)
                        for m_i, m in enumerate(modules_list):
                            m_output = subprocess.run(
                                f'module spider {m}', 
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                universal_newlines=True,
                                check=False,
                                shell=True
                                )
                            if "Versions" in m_output.stdout:
                                m_output = m_output.stdout.split("\n")
                                m_output = [m_i.strip() for m_i in m_output]
                                versions = []
                                v_i = m_output.index("Versions:")+1
                                all_versions = False
                                while not all_versions:
                                    versions.append(m_output[v_i])
                                    if "Other" in m_output[v_i+1]:
                                        v_i += 2
                                    elif not m_output[v_i+1]:
                                        all_versions = True
                                    else:
                                        v_i += 1
                                new_module = input(f"There are multiple versions of the module {versions}.\n" 
                                                f"Please select one (or enter n to remove it):")
                                while new_module not in versions and new_module.lower() != "n":
                                    new_module = input(f"Check the syntax please:")
                                if new_module.lower() != "n":
                                    modules_list[m_i] = new_module
                                    wrong_modules -= 1
                                else:
                                    index_remove.append(m_i) 
                                    wrong_modules -= 1
                            elif "error" in  m_output.stdout:
                                new_module = input(f"Module {modules_list[m_i]} not available.\n" 
                                                f"Specify the right one or enter n to remove it from the required modules:")
                                if new_module.lower() != "n":
                                    modules_list[m_i] = new_module
                                else:
                                    index_remove.append(m_i)
                                    wrong_modules -= 1
                            else:
                                wrong_modules -= 1
                        if index_remove:
                            for i in index_remove[::-1]:
                                modules_list.pop(i)
                        index_remove = []
                    print(f"Required {bcolors.UNDERLINE}{bcolors.BOLD}modules{bcolors.ENDC}" +
                          f"for container {cp}: {modules_list}")
                else:
                    modules_list = [mod.strip() for mod in load_modules.split(",")]
                    modules_valid = []
                    print(f"Required {bcolors.UNDERLINE}{bcolors.BOLD}modules{bcolors.ENDC}" +
                          f"for container {cp}: {modules_list}")
                    print(f"{bcolors.WARNING}WARNING: I won't check the syntax " +
                        f"and availability of the specified modules.{bcolors.ENDC}")

                if modules_list:
                    container_platforms[cp_i].update({"modules": modules_list})

    print()

    # Detect the group (to add it to the -A option for slurm)
    account = grp.getgrgid(os.getgid()).gr_name
    partition_name  = ""

    # Detecting the different types of nodes in the system (only form slurm)
    if scheduler == 'slurm' or scheduler == 'squeue':
        nodes = None
        print()
        print()
        print('Detecting partitions based on nodes features...')
        nodes_info = subprocess.run(
                        'scontrol show nodes -o | grep "ActiveFeatures"', 
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                        check=True,
                        shell=True
                        )
        nodes_info = nodes_info.stdout
        #DEBUG nodes_info+='ActiveFeatures=jaja,jeje\n'
        # Detect the default partition
        default_partition = subprocess.run(
                        'scontrol show partitions -o | grep "Default=YES"', 
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                        check=True,
                        shell=True
                        )
        try:
            # Detect the default partition
            default_partition = re.findall(r'PartitionName=([\w]+)', default_partition.stdout)[0]
            print(f"Detected default partition: {default_partition}")
            # Detect node types and the partitions they are assigned to
            nodes_features = re.findall(r'ActiveFeatures=([^ ]+) .*? Partitions=([^ ]+)', nodes_info)
            # Get the unique combinations
            nodes_features   = set(nodes_features)
            nodes_types = [[tuple(n[0].split(',')), tuple(n[1].split(','))] for n in nodes_features]
            # Retrieve the node types in the default partition 
            # (if more than 1, then access options are enforced to reach the exact node type)
            default_c = 0
            default_nodes = [] # Node type in the default partition
            nodes = [] # List of node types
            for n in nodes_types:
                nodes.append(n[0])
                if default_partition in n[1]:
                    default_nodes.append(n[0])
                    default_c += 1
            print(f"The number of node types in the default partition is: {default_c}: {default_nodes}")
            nodes = set(nodes)
            if default_c > 1:
                default_nodes = None
            print('Detected the following node types:')
            print(nodes)
        except:
            print('Unable to retrieve nodes features')
        
        print('Detecting gres...')
        reservations_info = subprocess.run(
                        'scontrol show nodes | grep "ReservationName"', 
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                        check=True,
                        shell=True
                        )
        reservations_info = reservations_info.stdout    

        print('Detecting partitions based on reservations...')
        reservations_info = subprocess.run(
                        'scontrol show res | grep "ReservationName"', 
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                        check=True,
                        shell=True
                        )
        reservations_info = reservations_info.stdout

        # Detecting the different types of nodes in the system
        reservations = None
        try:
            reservations = re.findall(r'ReservationName=([\w-]+)', reservations_info)
            print('Detected the following reservations:')
            print(reservations)
        except:
            print('Unable to retrieve reservations')

        print()
        print()

        partition_login = 0
        print('Initializing the partitions of the system...')
        login_partition = input("Do you want to create a partition for the login node? (y/n):")
        while login_partition != "y" and login_partition.lower() != "n":
            login_partition = input("Do you want to create a partition for the login node? (y/n):")
        if login_partition == "y":
            partition_login = 1
            print(f'Creating {bcolors.GREEN}login{bcolors.ENDC} ' +
                f'{bcolors.BOLD}{bcolors.UNDERLINE}partition' +
                f'{bcolors.ENDC}{bcolors.ENDC} with {bcolors.GREEN}' +
                f'local{bcolors.ENDC} scheduler...')
            system_config['systems'][0].update({'partitions': []})
            system_config['systems'][0]['partitions'].append(
                {'name':       'local', 
                'descr':      'Login nodes',
                'launcher':   'local',
                'time_limit':  TIME_LIMIT_LOGIN,
                'environs':   ['builtin'],
                'scheduler':  'local',
                'max_jobs':   MAX_JOBS_LOGIN}
            )

        if not nodes and not reservations:
            print(f'No information on node types and reservations could be retrieved.')
        if nodes:
            for n_i, n in enumerate(nodes):
                nodes_features = list(n)
                create_partition = input(f"Do you want to create a partition for the node with features {nodes_features}? (y/n):")
                while create_partition != "y" and create_partition.lower() != "n":
                    create_partition = input(f"Do you want to create a partition for the node with features {nodes_features}? (y/n):")
                if create_partition == "y":
                    partition_name = input(f"How do you want to name the partition?:")
                    maxjobs = input(f"Maximum number of forced local build or run jobs allowed?\n" +
                                               "(default is 100):")
                    if not maxjobs:
                        maxjobs = 100
                    integer_value = False
                    while not integer_value:
                        try:
                            maxjobs = int(maxjobs)
                            integer_value = True
                        except:
                            maxjobs = input(f"It must be an integer:")
                    time_limit = input(f"The time limit for the jobs submitted on this partition\n" +
                                                 "enter 'null' for no time limit (default is 10m):")
                    if not time_limit:
                        time_limit = "10m"
                    nodes_features.append('remote')
                    if system_config['systems'][0].get('partitions'):
                        pass
                    else:
                        system_config['systems'][0].update({'partitions': []})
                    system_config['systems'][0]['partitions'].append(
                        {'name':      partition_name, 
                        'scheduler': scheduler,
                        'time_limit': time_limit,
                        'environs':   ['builtin'],
                        'max_jobs':   maxjobs,
                        'resources':  resources,
                        'extras':     "#FIXME :"+RFM_DOCUMENTATION["extras"],
                        'env_vars':   "#FIXME :"+RFM_DOCUMENTATION["partition_envvars"],
                        'launcher':   launcher,  
                        'access':     [f'--account={account}'],
                        'features':   nodes_features}
                    )
                    if containers_found:
                        system_config['systems'][0]['partitions'][n_i+partition_login].update({'container_platforms': container_platforms})
                    print("Detecting the devices...")
                    devices = []
                    nodes_devices = subprocess.run(
                                    f'scontrol show nodes -o | grep "ActiveFeatures={",".join(nodes_features[0:-1])}"', 
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    universal_newlines=True,
                                    check=True,
                                    shell=True
                                    )
                    nodes_devices = re.findall(r'Gres=([\w,:()]+)', nodes_devices.stdout)
                    nodes_devices = set(nodes_devices)
                    print(nodes_devices)
                    if len(nodes_devices) != 1:
                        print(f"{bcolors.WARNING} Detected different devices in nodes with the same set of features. " +
                              f" Please check the devices option in the configuration file." + 
                              f"{RFM_DOCUMENTATION['devices']}")
                    elif "(null)" in list(nodes_devices):
                        print("No devices were found for this node type.")
                    else:
                        devices = []
                        for n_di, n_d in enumerate(nodes_devices):
                            n_d = n_d.split(":")
                            #FIXME: missing detection of device architecture (for gpus nvidia-smi)
                            devices.append({"type": n_d[0],
                                            "num_devices": n_d[1]})
                    if devices:
                        system_config['systems'][0]['partitions'][n_i+partition_login].update({"devices": devices})
                    if n not in default_nodes:
                        access_node = '&'.join(nodes_features)
                        system_config['systems'][0]['partitions'][n_i+partition_login]["access"].append(
                            f"--constraint={access_node}"
                        )
                        print("This node type is not the node type by default so I added the required constraints:" +
                              f"--constraints={access_node}.") 
                        access_custom = input("Do you need any additional ones? (if no, enter n):")
                        if access_custom.lower() != "n":
                            system_config['systems'][0]['partitions'][n_i+partition_login]["access"].append(
                            f"{access_custom}"
                        )
                    else: 
                        print("I have added the associated group found with the slurm option -A")
                        access_custom = input("Do you need any access options in slurm to access the node?\n" +
                                              f"(if no, enter n):")
                        if access_custom.lower() != "n":
                            system_config['systems'][0]['partitions'][n_i+partition_login]["access"].append(
                            f"{access_custom}"
                        )
                    print(f'Creating {bcolors.WARNING}{partition_name}{bcolors.ENDC} ' +
                        f'{bcolors.BOLD}{bcolors.UNDERLINE}partition{bcolors.ENDC}' +
                        f'{bcolors.ENDC} with {scheduler} scheduler and ' +
                        f'{bcolors.BOLD}{bcolors.UNDERLINE}features{bcolors.ENDC}' +
                        f'{bcolors.ENDC} = {nodes_features}')  

        # Creating an example of the reservation as partition

        if reservations:
            create_partition = input(f"Do you want to create a partition for any of the reservations {reservations}?\n" +
                                    f"(enter the reservation names separated by commas or n to skip):\n")
            if create_partition.lower() != "n":
                partitions_reservations = create_partition.split(",")
                wrong_p = len(partitions_reservations)
                index_remove = []
                while wrong_p != 0:
                    wrong_p = len(partitions_reservations)
                    for p_i, p_r in enumerate(partitions_reservations):
                        if p_r in reservations:
                            wrong_p -= 1
                        else:
                            new_partition = input(f"The reservation {p_r} is not in the system.\n" +
                                                  f"Please check the syntax or enter n to skip:")
                            if new_partition.lower() != "n":
                                partitions_reservations[p_i] = new_partition
                            else:
                                index_remove.append(p_i)
                                wrong_p -= 1
                    if index_remove:                    
                        for i in index_remove[::-1]:
                            partitions_reservations.pop(i)
                    index_remove = []
                for pr in partitions_reservations:
                    partition_name = input(f"How do you want to name the partition for reservation {pr}?:")
                    maxjobs = input(f"Maximum number of forced local build or run jobs allowed?\n" +
                                               "(default is 100):")
                    if not maxjobs:
                        maxjobs = 100
                    integer_value = False
                    while not integer_value:
                        try:
                            maxjobs = int(maxjobs)
                            integer_value = True
                        except:
                            maxjobs = input(f"It must be an integer:")
                    time_limit = input(f"The time limit for the jobs submitted on this partition\n" +
                                                 "enter 'null' for no time limit (default is 10m):")
                    if not time_limit:
                        time_limit = "10m"
                    system_config['systems'][0]['partitions'].append(
                        {'name':     partition_name, 
                        'scheduler': scheduler,
                        'time_limit': time_limit,
                        'environs':   ['builtin'],
                        'max_jobs':  maxjobs,
                        'launcher':   launcher,
                        'access':     [f'--reservation={pr}', f'--account={account}'],
                        'features':   ['remote']}
                    )
                    print(f'Creating {bcolors.WARNING}{partition_name}{bcolors.ENDC} ' +
                            f'{bcolors.BOLD}{bcolors.UNDERLINE}partition{bcolors.ENDC}' +
                            f'{bcolors.ENDC} with {scheduler} scheduler for ' +
                            f'{bcolors.BOLD}{bcolors.UNDERLINE}{pr}{bcolors.ENDC} ' +
                            'reservation')
    else:
        partition_login = 0
        print('Initializing the partitions of the system...')
        login_partition = input("Do you want to create a partition for the login node? (y/n):")
        while login_partition != "y" and login_partition.lower() != "n":
            login_partition = input("Do you want to create a partition for the login node? (y/n):")
        if login_partition == "y":
            partition_login = 1
            print(f'Creating {bcolors.GREEN}login{bcolors.ENDC} ' +
                f'{bcolors.BOLD}{bcolors.UNDERLINE}partition' +
                f'{bcolors.ENDC}{bcolors.ENDC} with {bcolors.GREEN}' +
                f'local{bcolors.ENDC} scheduler...')
            system_config['systems'][0].update({'partitions': []})
            system_config['systems'][0]['partitions'].append(
                {'name':       'local', 
                'descr':      'Login nodes',
                'launcher':   'local',
                'time_limit':  TIME_LIMIT_LOGIN,
                'environs':   ['builtin'],
                'scheduler':  'local',
                'max_jobs':   MAX_JOBS_LOGIN}
            )
        print("Automatic detection of partition is only possible with slurm")
        
    print()
    print()
    print(f'{bcolors.WARNING}For information about the environments check the links in the generated files{bcolors.ENDC}')
    # Creating an environment for reference
    system_config["environments"] = ["https://github.com/eth-cscs/cscs-reframe-tests/tree/alps/config/systems",
                                     "https://reframe-hpc.readthedocs.io/en/stable/config_reference.html#environment-configuration"]

    print()
    print()
    print(f'The following configuration files were generated:\n' +
          f"JSON: {cluster_name}_config.json\n" +
          f"PYTHON: {cluster_name}_config.py")

    # Set up Jinja2 environment and load the template
    template_loader = FileSystemLoader(searchpath="./") 
    env = Environment(loader=template_loader, trim_blocks=True, lstrip_blocks=True)
    rfm_config_template = env.get_template("reframe_config_template.j2")

    # Render the template with the gathered information
    organized_config = rfm_config_template.render(system_config['systems'][0])

    # Output filename for the generated configuration
    output_filename = f"{cluster_name}_config.py"

    # Write the rendered content to the output file
    with open(output_filename, "w") as output_file:
        output_file.write(organized_config)

    with open(f'{cluster_name}_config.json', 'w') as py_file:
        json.dump(system_config, py_file, indent=4)


if __name__ == '__main__':
    main()
