# Copyright 2016-2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import argparse
import fnmatch
import grp
from jinja2 import Environment, FileSystemLoader
import json
import os
import re
import shutil
import socket
import subprocess
import tempfile
from utilities.constants import *
from utils import *

system_config   = {}

# Configure the logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(CustomFormatter())
logger.addHandler(console_handler)

# Create an ArgumentParser object
parser = argparse.ArgumentParser()

# Define the '--auto' flag
parser.add_argument('--auto', action='store_true', help='Turn off interactive mode')
# Define the '--no-remote-containers' flag
parser.add_argument('--no-remote-containers', action='store_true', help='Disable container platform detection in remote partition')
# Define the '--no-remote-devices' flag
parser.add_argument('--no-remote-devices', action='store_true', help='Disable devices detection in remote partition')
# Define the '--reservations' flag
parser.add_argument('--reservations', nargs='?', help='Specify the reservations that you want to create partitions for.')
# Define the '--exclude' flag
parser.add_argument('--exclude', nargs='?', help='Exclude the certain node features for the detection of node types')

args = parser.parse_args()

user_input = not args.auto

containers_search = 'y'
if args.no_remote_containers:
    containers_search = 'n'

devices_search = 'y'
if args.no_remote_devices:
    devices_search = 'n'

if args.reservations:
    reservations_based = args.reservations.split(',')
else:
    reservations_based = False

if args.exclude:
    exclude_feat = args.exclude.split(',')
else:
    exclude_feat = []

user_input = not args.auto

temp_dir = tempfile.mkdtemp(prefix='reframe_config_detection_', dir=os.getenv('SCRATCH'))

def main(user_input, containers_search, devices_search, reservations_based, exclude_feat):

    system_config['systems']   = []
    keep_tmpdir = False

    # Get the system name
    cluster_name = os.getenv('CLUSTER_NAME')
    if cluster_name:
        logger.info(f'System name is {cluster_name}\n')
    else:
        cluster_name = 'cluster'
        logger.warning(f'System name not found set to "{cluster_name}\n"')

    system_config['systems'].append({'name': cluster_name})

    # Get the hostname
    try:
        hostname = socket.gethostname() # Same method reframe uses
    except Exception as e:
        hostname = '<hostname>'
        logger.error('Hostname not found')
        logger.debug(f'Trying to retrieve the hostname raised:\n{e}\n')
    else:
        hostname = hostname.strip()
        hostname = re.search(r'(^\w+)', hostname)
        hostname = hostname.group(0)
        logger.info(f'Hostname is {hostname}\n')

    if hostname != '<hostname>' and cluster_name != 'cluster':
        if hostname != cluster_name:
            logger.warning('Detected hostname and '
                           'systemname are different\n')

    system_config['systems'][0].update({'hostnames': [hostname]})

    # Get the modules system
    module_system = 'nomod'
    # Detect lmod and tmod
    module_info = os.getenv('LMOD_CMD')
    if not module_info:
        try:
            module_info = subprocess.run(['modulecmd','-V'],
                stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                universal_newlines=True
            )
        except FileNotFoundError:
            try:
                module_info = subprocess.run(['spack','-V'],
                    stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                    universal_newlines=True
                )
            except FileNotFoundError:
                pass
            else:
                module_system = 'spack'
        else:
            version_tmod = re.search(r'^VERSION=(\S+)', module_info.stdout,
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
                    module_system = 'tmod4'
                elif ver_major >= 3 and ver_minor >= 2:
                    module_system = 'tmod32'
                elif ver_major >= 3 and ver_minor >= 1:
                    module_system = 'tmod31'
                else:
                    logger.warning('Detected unsupported '
                                   f'TMod version: {version}\n')
    else:
        module_system = 'lmod'

    if module_system != 'nomod':
        logger.info(f'The module system for the system {cluster_name} '
                    f' is set to {module_system}\n')
    else:
        logger.warning('No valid module system was detected.'
                       'Set to nomod.\n')

    system_config['systems'][0].update({'modules_system': module_system})

    # Ask for modules to be loaded (if user_input required)
    if module_system != 'nomod' and user_input:
        logger.debug('You can require some modules to be loaded every time reframe is run on this system')
        modules_list = []
        load_modules = input('Do you require any modules to be loaded?\n'
                             'If yes please write the modules names separated by commas\n'
                             'If no please enter n\n')

        if load_modules.lower() == 'n':
            logger.debug('No modules will be added.\n')
        elif module_system == 'lmod':
            modules_list = [mod.strip() for mod in load_modules.split(',')]
            wrong_modules = len(modules_list)
            index_remove = []
            while wrong_modules != 0:
                wrong_modules = len(modules_list)
                for m_i, m in enumerate(modules_list):
                    m_output = subprocess.run(f'module spider {m}',
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                        universal_newlines=True, check=False, shell=True
                        )
                    if 'Versions' in m_output.stdout:
                        m_output = m_output.stdout.split('\n')
                        m_output = [m_i.strip() for m_i in m_output]
                        versions = []
                        v_i = m_output.index('Versions:')+1
                        all_versions = False
                        while not all_versions:
                            versions.append(m_output[v_i])
                            if 'Other' in m_output[v_i+1]:
                                v_i += 2
                            elif not m_output[v_i+1]:
                                all_versions = True
                            else:
                                v_i += 1
                        new_module = input(f'There are multiple versions of the module {versions}.\n'
                                           'Please select one (or enter n to remove it):')
                        while new_module not in versions and new_module.lower() != 'n':
                            new_module = input(f'Check the syntax please:')
                        if new_module.lower() != 'n':
                            modules_list[m_i] = new_module
                            wrong_modules -= 1
                        else:
                            index_remove.append(m_i)
                            wrong_modules -= 1
                    elif 'error' in  m_output.stdout:
                        new_module = input(f'Module {modules_list[m_i]} not available.\n'
                                           'Specify the right one or enter n to remove it from the required modules:')
                        if new_module.lower() != 'n':
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
            if modules_list:
                logger.debug(f'Required modules: {modules_list}\n')
            else:
                logger.debug('No modules will be added.\n')
        else:
            modules_list = [mod.strip() for mod in load_modules.split(',')]
            logger.debug(f'Required modules: {modules_list}')
            logger.warning('WARNING: I will not check the syntax '
                           'and availability of the specified modules.\n')

        if modules_list:
            system_config['systems'][0].update({'modules': modules_list})

    elif module_system != 'nomod':
        # If user input is disabled and a module system was detected set it to empty list (default reframe)
        # The link to the reframe documentation is printed
        system_config['systems'][0].update({'modules': []})

    # Additional fields that must be manually configured
    if user_input:
        resourcesdir = input('Do you want to add a resources directory for the system?\n'
                             'Directory prefix where external test resources (e.g., large input files) are stored.\n'
                             'If no just enter n.\n')
        if resourcesdir.lower() != 'n':
            while not os.path.exists(resourcesdir):
                resourcesdir = input('The specified directory does not exist.\n'
                                     'Please enter a valid directory (or n):\n')
                if resourcesdir.lower() == 'n':
                    break
    else:
        # If no user input, set it to the default reframe
        resourcesdir = '.'

        if resourcesdir.lower() != 'n':
            system_config['systems'][0].update({'resourcesdir': resourcesdir})

    # Detect the scheduler: we need the scheduler to detect the partitions
    schedulers_found = []
    for sched_i in SCHEDULERS:
        try:
            scheduler = subprocess.run(['which', f'{sched_i["cmd"]}'],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                universal_newlines=True, check=True
            )
        except subprocess.CalledProcessError:
            pass
        else:
            schedulers_found.append(sched_i['name'])

    if not schedulers_found:
        # Set the scheduler to local if no other scheduler was detected
        logger.debug('No scheduler was detected')
        scheduler = 'local'
        logger.warning(f'The scheduler for the system is set to {scheduler}\n')
    else:
        logger.debug('The following schedulers were found: '
                     f'{", ".join(schedulers_found)}')
        if len(schedulers_found) == 1:
            scheduler = schedulers_found[0]
            logger.info(f'The scheduler for the system {cluster_name}'
                        f' is set to {schedulers_found[0]}\n')
        elif user_input:
            # Offer the different options for the schedulers
            logger.debug(RFM_DOCUMENTATION['schedulers'])
            scheduler = input('Please select a scheduler from the list above: ')
            while scheduler not in schedulers_found:
                scheduler = input('The scheduler was not recognized. Please check the syntax: ')
            logger.info(f'The scheduler for the system {cluster_name}'
                        f' is set to {scheduler}\n')
        else:
            # Select the last one detected (this will choose slurm over squeue
            # if both are detected in the system)
            #FIXME put the list in the jinja template
            scheduler = schedulers_found[-1]
            logger.warning(f'The scheduler for the system {cluster_name}'
                           f' is set to {scheduler}')
            logger.debug(f'Check {cluster_name}_config.json to select'
                         ' a different one\n')

    # Detect the parallel launcher
    launchers_found = []
    for launch_i in LAUNCHERS:
        try:
            launcher = subprocess.run(['which', f'{launch_i["cmd"]}'],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                universal_newlines=True, check=True
            )
        except subprocess.CalledProcessError:
            pass
        else:
            launchers_found.append(launch_i['name'])

    if not launchers_found:
        # Set the scheduler to local if no other scheduler was detected
        logger.debug('No parallel launcher was detected')
        launcher = 'local'
        logger.warning(f'The launcher for the partitions '
                       f'is set to {launcher}\n')
    else:
        logger.debug(f'The following launchers were found: '
                     f'{", ".join(launchers_found)}')
        if len(launchers_found) == 1:
            launcher = launchers_found[0]
            logger.info(f'The launcher for the partitions '
                        f'is set to {launcher}\n')
        elif user_input:
            # Offer the different options for the launchers
            launcher = input('Please select a launcher from the list above: ')
            while launcher not in launchers_found:
                launcher = input('The launcher was not recognized. Please check the syntax: ')
            logger.info('The launcher for the partitions '
                        f'is set to {launcher}\n')
        else:
            # Select the last one detected
            #FIXME put the list in the jinja template
            launcher = launchers_found[-1]
            logger.warning(f'The launcher for the system {cluster_name}'
                           f' is set to {launcher}')
            logger.debug(f'Check {cluster_name}_config.json to select'
                         ' a different one\n')

    # Detect the group (to add it to the -A option for slurm)
    account = grp.getgrgid(os.getgid()).gr_name
    partition_name  = ''

    # Detecting the different types of nodes in the system (only form slurm)
    if scheduler == 'slurm' or scheduler == 'squeue':
        nodes = None
        #FIXME : nodes detection always on, can be disabled from command line
        logger.debug('Detecting partitions based on nodes features...')
        nodes_info = subprocess.run('scontrol show nodes -o | grep "ActiveFeatures"',
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                        universal_newlines=True, check=True, shell=True
                        )
        nodes_info = nodes_info.stdout
        # Detect the default partition
        default_partition = subprocess.run('scontrol show partitions -o | grep "Default=YES"',
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                        universal_newlines=True, check=True, shell=True
                        )
        try:
            # Detect the default partition
            default_partition = re.findall(r'PartitionName=([\w]+)', default_partition.stdout)[0]
            logger.debug(f'Detected default partition: {default_partition}')
            # Detect node types and the partitions they are assigned to
            nodes_features = re.findall(r'ActiveFeatures=([^ ]+) .*? Partitions=([^ ]+)', nodes_info)
            # Get the unique combinations
            nodes_features   = set(nodes_features)
            nodes_types = [[tuple(n[0].split(',')), tuple(n[1].split(','))] for n in nodes_features]
            # Retrieve the node types in the default partition
            # (if more than 1, then access options are enforced to reach the exact node type)
            default_nodes = [] # Node type in the default partition
            nodes = [] # List of node types
            for n in nodes_types:
                node_f = []
                for feat in list(n[0]):
                    feat_valid = not any([fnmatch.fnmatch(feat, pattern) for pattern in exclude_feat])
                    if feat_valid:
                        node_f.append(feat)
                if node_f:
                    nodes.append(tuple(node_f))
                if default_partition in n[1]:
                    default_nodes.append(tuple(node_f))
            default_nodes = set(default_nodes)
            nodes = set(nodes)
            default_c = len(default_nodes)
            logger.debug(f'The number of node types in the default partition is: {default_c}: {default_nodes}')
            nodes = set(nodes)
            if default_c > 1:
                default_nodes = []
            logger.debug('Detected the following node types:')
            logger.debug(f'{nodes}\n')
        except:
            logger.warning('Unable to retrieve nodes features\n')

        if reservations_based or user_input:
            # Only search for reservations if the option is required
            logger.debug('Detecting partitions based on reservations...')
            reservations_info = subprocess.run('scontrol show res | grep "ReservationName"',
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, check=True, shell=True
                            )
            reservations_info = reservations_info.stdout

            # Detecting the different types of nodes in the system
            reservations = None
            try:
                reservations = re.findall(r'ReservationName=([\w-]+)', reservations_info)
                logger.debug('Detected the following reservations:')
                logger.debug(f'{reservations}\n')
            except:
                logger.warning('Unable to retrieve reservations\n')

        # Create login partition
        p_login = 0
        logger.debug('Initializing the partitions of the system...\n')
        if user_input:
            login_partition = input('Do you want to create a partition for the login node? (y/n):')
            while login_partition != 'y' and login_partition.lower() != 'n':
                login_partition = input('Do you want to create a partition for the login node? (y/n):')
            if login_partition == 'y':
                p_login = 1
                maxjobs = input('Maximum number of forced local build or run jobs allowed?\n'
                                '(default is 4 for login):')
                if not maxjobs:
                    maxjobs = 4
                integer_value = False
                while not integer_value:
                    try:
                        maxjobs = int(maxjobs)
                        integer_value = True
                    except:
                        maxjobs = input('It must be an integer:')
                time_limit = input('The time limit for the jobs submitted on this partition\n'
                                   'enter "null" for no time limit (default is 2m for login):')
                if not time_limit:
                    time_limit = '2m'
                system_config['systems'][0].update({'partitions': []})
                system_config['systems'][0]['partitions'].append(
                    {'name':      'login',
                    'descr':      'Login nodes',
                    'launcher':   'local',
                    'time_limit':  time_limit,
                    'environs':   ['builtin'],
                    'scheduler':  'local',
                    'max_jobs':   maxjobs}
                )
                logger.info('Created login partition with local scheduler\n')
        else:
            p_login = 1
            system_config['systems'][0].update({'partitions': []})
            system_config['systems'][0]['partitions'].append(
                {'name':      'local',
                'descr':      'Login nodes',
                'launcher':   'local',
                'time_limit':  '2m',
                'environs':   ['builtin'],
                'scheduler':  'local',
                'max_jobs':   '4'}
            )
            logger.info('Created login partition with local scheduler\n')

        if not nodes and not reservations:
            logger.warning('No information is available for the creation of the partition.\n')
        nodes_p = 0
        if nodes:
            for n in nodes:
                nodes_features = list(n)
                if user_input:
                    create_partition = input(f'Do you want to create a partition for the node with features {nodes_features}? (y/n):')
                    while create_partition != 'y' and create_partition.lower() != 'n':
                        create_partition = input(f'Do you want to create a partition for the node with features {nodes_features}? (y/n):')
                    if create_partition == 'y':
                        nodes_p += 1
                        partition_name = input('How do you want to name the partition?:')
                        maxjobs = input('Maximum number of forced local build or run jobs allowed?\n'
                                        '(default is 100):')
                        if not maxjobs:
                            maxjobs = 100
                        integer_value = False
                        while not integer_value:
                            try:
                                maxjobs = int(maxjobs)
                                integer_value = True
                            except:
                                maxjobs = input('It must be an integer:')
                        time_limit = input('The time limit for the jobs submitted on this partition\n'
                                           'enter "null" for no time limit (default is 10m):')
                        if not time_limit:
                            time_limit = '10m'
                        nodes_features.append('remote')
                        if system_config['systems'][0].get('partitions'):
                            pass
                        else:
                            system_config['systems'][0].update({'partitions': []})
                        system_config['systems'][0]['partitions'].append(
                            {'name':      partition_name,
                            'scheduler':  scheduler,
                            'time_limit': time_limit,
                            'environs':   ['builtin'],
                            'max_jobs':   maxjobs,
                            'resources':  resources,
                            'extras':     {},
                            'env_vars':   [],
                            'launcher':   launcher,
                            'access':     [f'--account={account}'],
                            'features':   nodes_features}
                        )
                        # Get additional access options
                        logger.debug('I have added the associated group found with the slurm option -A')
                        if n not in default_nodes:
                            access_node = '&'.join(nodes_features[0:-1])
                            system_config['systems'][0]['partitions'][nodes_p+p_login-1]["access"].append(
                                f'--constraint="{access_node}"'
                            )
                            logger.debug('This node type is not the node type by default so I added the required constraints:'
                                         f'--constraint="{access_node}".')
                            access_custom = input('Do you need any additional ones? (if no, enter n):')
                            if not access_custom:
                                pass
                            elif access_custom.lower() != 'n':
                                system_config['systems'][0]['partitions'][nodes_p+p_login-1]['access'].append(
                                f"{access_custom}"
                            )
                        else:
                            access_custom = input('Do you need any access options in slurm to access the node?\n'
                                                  '(if no, enter n):')
                            if not access_custom:
                                pass
                            elif access_custom.lower() != 'n':
                                system_config['systems'][0]['partitions'][nodes_p+p_login-1]['access'].append(
                                f'{access_custom}'
                            )
                        # Detect the containers in remote partition
                        containers_search = input('Do you require automatic detection of container platforms in this partition? (y/n):')
                        while containers_search != 'n' and containers_search != 'y':
                            containers_search = input('Do you require automatic detection of container platforms in this partition? (y/n):')

                        # cn_memory_search = input("Do you require information about the total memory in the nodes of this partition? (y/n):")
                        # while cn_memory_search != "n" and cn_memory_search != "y":
                        #     cn_memory_search = input("Do you require automatic detection of container platforms in this partition? (y/n):")

                        logger.info(f'Creating {partition_name} partition '
                                    f'with {scheduler} scheduler and features = {nodes_features}\n')
                else:
                    create_partition = 'y'
                    nodes_p += 1
                    logger.info(f'Creating partition for node with features {nodes_features}: partition_{nodes_p}\n')
                    if system_config['systems'][0].get('partitions'):
                        pass
                    else:
                        system_config['systems'][0].update({'partitions': []})
                    nodes_features.append('remote')
                    system_config['systems'][0]['partitions'].append(
                        {'name':      f'partition_{nodes_p}',
                        'scheduler':  scheduler,
                        'time_limit': '10m',
                        'environs':   ['builtin'],
                        'max_jobs':   '100',
                        'resources':  resources,
                        'extras':     {},
                        'env_vars':   [],
                        'launcher':   launcher,
                        'access':     [f'--account={account}'],
                        'features':   nodes_features}
                    )
                    if n not in default_nodes:
                        access_node = '&'.join(nodes_features[0:-1])
                        system_config['systems'][0]['partitions'][nodes_p+p_login-1]['access'].append(
                            f'--constraint="{access_node}"'
                        )
                        # To prevent job submission failing in eiger
                    elif hostname == 'eiger':
                        system_config['systems'][0]['partitions'][nodes_p+p_login-1]['access'].append('-Cmc')

                if create_partition == 'y':
                    devices_search_n = 'n'
                    if devices_search == 'y':
                        logger.debug('Detecting devices...')
                        devices = []
                        nodes_devices = subprocess.run(f'scontrol show nodes -o | grep "ActiveFeatures=.*{".*,.*".join(nodes_features[0:-1])}.*"',
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        universal_newlines=True, check=True, shell=True
                                        )
                        nodes_devices = re.findall(r'Gres=([\w,:()]+)', nodes_devices.stdout)
                        nodes_devices = set(nodes_devices)
                        if len(nodes_devices) != 1:
                            logger.warning('Detected different devices in nodes with the same set of features.\n'
                                            'Please check the devices option in the configuration file.'
                                            f'{RFM_DOCUMENTATION["devices"]}\n')
                        #FIXME : deal with nodes with different devices configurations
                        elif '(null)' in list(nodes_devices) or 'gpu' not in next(iter(nodes_devices)):
                            logger.debug('No devices were found for this node type.\n')
                        else:
                            # Devices search is limited to gpus
                            devices_search_n = 'y'

                    if containers_search == 'y' or devices_search_n == 'y':
                        keep_tmpdir = True
                        logger.debug(temp_dir)
                        with change_dir(temp_dir):
                            generate_submission_file(containers_search == 'y', devices_search_n == 'y', False,
                                            system_config['systems'][0]['partitions'][nodes_p+p_login-1]['name'],
                                            system_config['systems'][0]['partitions'][nodes_p+p_login-1]['access'])
                            job_submitted = submit_autodetection(system_config['systems'][0]['partitions'][nodes_p+p_login-1]['name'])
                            if job_submitted:
                                containers_found, devices_found, _ = extract_info(containers_search == 'y', devices_search_n == 'y', False,
                                                        system_config['systems'][0]['partitions'][nodes_p+p_login-1]['name'])
                                if containers_found:
                                    if module_system != 'lmod':
                                        logger.warning('Container platforms were detected but the automatic detection '
                                                       f'of required modules is not possible with {module_system}.\n')
                                    for cp_i, cp in enumerate(containers_found):
                                        logger.debug(f'Detected container platform: {cp["type"]}')
                                        system_config['systems'][0]['partitions'][nodes_p+p_login-1]['features'].append(cp['type'].lower())

                                    system_config['systems'][0]['partitions'][nodes_p+p_login-1].update({'container_platforms': containers_found})
                                else:
                                    logger.debug('No container platforms were detected\n')

                                if devices_found:
                                    gpus_count_slurm = 0
                                    for n_di, n_d in enumerate(nodes_devices):
                                        n_d = n_d.split(':')
                                        if n_d[0] == 'gpu':
                                            gpus_count_slurm += n_d[1]
                                    gpus_count_detect = 0
                                    for model, number in devices_found['NVIDIA'].items():
                                        devices.append({'type': 'gpu',
                                                        'arch': nvidia_gpu_architecture.get(model),
                                                        'num_devices': number})
                                        gpus_count_detect += number
                                    if gpus_count_detect != gpus_count_slurm:
                                        logger.warning(f'The number of detected GPUs ({gpus_count_detect}) '
                                                       f'differs from the one in GRes from slurm ({gpus_count_slurm}).\n')
                                    system_config['systems'][0]['partitions'][nodes_p+p_login-1].update({'devices': devices})
                            else:
                                logger.warning('The autodetection script could not be submitted, please check the sbatch options.\n')

        # Creating an example of the reservation as partition (only when --reservations or user_input)
        reservations_p = 0
        if reservations_based or user_input:
            if user_input:
                create_partition = input(f'Do you want to create a partition for any of the reservations {reservations}?\n' +
                                         f'(enter the reservation names separated by commas or n to skip):\n')
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
                                new_partition = input(f'The reservation {p_r} is not in the system.\n'
                                                      'Please check the syntax or enter n to skip:')
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
                        reservations_p += 1
                        partition_name = input(f'How do you want to name the partition for reservation {pr}?:')
                        maxjobs = input('Maximum number of forced local build or run jobs allowed?\n'
                                        '(default is 100):')
                        if not maxjobs:
                            maxjobs = 100
                        integer_value = False
                        while not integer_value:
                            try:
                                maxjobs = int(maxjobs)
                                integer_value = True
                            except:
                                maxjobs = input(f'It must be an integer:')
                        time_limit = input('The time limit for the jobs submitted on this partition\n'
                                           'enter "null" for no time limit (default is 10m):')
                        if not time_limit:
                            time_limit = '10m'
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
                        logger.debug(f'I have added the associated group found with the slurm option -A and the --reservation={pr}')
                        access_custom = input('Do you need any access options in slurm to access this reservation?\n'
                                              '(if no, enter n):')
                        if not access_custom:
                            pass
                        elif access_custom.lower() != 'n':
                            system_config['systems'][0]['partitions'][nodes_p+p_login+reservations_p-1]['access'].append(
                            f"{access_custom}"
                        )
                        logger.info(f'Created {partition_name} partition with {scheduler} '
                                    f'scheduler for {pr} reservation\n')

            else:
                for res in reservations_based:
                    if res in reservations:
                        reservations_p += 1
                        system_config['systems'][0]['partitions'].append(
                            {'name':     f'{res}',
                            'scheduler':  scheduler,
                            'time_limit': '10m',
                            'environs':   ['builtin'],
                            'max_jobs':   100,
                            'launcher':   launcher,
                            'access':     [f'--reservation={res}', f'--account={account}'],
                            'features':   ['remote']}
                        )
                        if hostname == 'eiger':
                            system_config['systems'][0]['partitions'][nodes_p+p_login+reservations_p-1]['access'].append('-Cmc')

                        logger.info(f'Created {partition_name} partition with {scheduler} '
                                    f'scheduler for {res} reservation\n')
                    else:
                        logger.warning(f'Reservation {res} not found in the system, skipping...\n')

    else:
        nodes_p = 0
        reservations_p = 0
        p_login = 0
        if user_input:
            login_partition = input('Do you want to create a partition for the login node? (y/n):')
            while login_partition != 'y' and login_partition.lower() != 'n':
                login_partition = input('Do you want to create a partition for the login node? (y/n):')
            if login_partition == 'y':
                p_login = 1
                maxjobs = input('Maximum number of forced local build or run jobs allowed?\n'
                                '(default is 4 for login):')
                if not maxjobs:
                    maxjobs = 4
                integer_value = False
                while not integer_value:
                    try:
                        maxjobs = int(maxjobs)
                        integer_value = True
                    except:
                        maxjobs = input('It must be an integer:')
                time_limit = input('The time limit for the jobs submitted on this partition\n'
                                   'enter "null" for no time limit (default is 2m for login):')
                if not time_limit:
                    time_limit = '2m'
                system_config['systems'][0].update({'partitions': []})
                system_config['systems'][0]['partitions'].append(
                    {'name':      'local',
                    'descr':      'Login nodes',
                    'launcher':   'local',
                    'time_limit':  time_limit,
                    'environs':   ['builtin'],
                    'scheduler':  'local',
                    'max_jobs':   maxjobs}
                )
                logger.info('Created login partition with local scheduler\n')
        else:
            system_config['systems'][0].update({'partitions': []})
            system_config['systems'][0]['partitions'].append(
                {'name':      'local',
                'descr':      'Login nodes',
                'launcher':   'local',
                'time_limit':  '2m',
                'environs':   ['builtin'],
                'scheduler':  'local',
                'max_jobs':   4}
            )
            logger.info('Created login partition with local scheduler\n')
        logger.warning('Automatic detection of partition is only possible with slurm\n')

    # If no partitions were created raise an error message
    if nodes_p + reservations_p + p_login == 0:
        logger.error('\nNo partitions were created. ReFrame requires at least 1 partition defintion to run.\n')

    logger.warning('\n\nFor information about the environments check the links in the generated files\n\n')
    # Creating an environment for reference
    system_config["environments"] = ['https://github.com/eth-cscs/cscs-reframe-tests/tree/alps/config/systems',
                                     'https://reframe-hpc.readthedocs.io/en/stable/config_reference.html#environment-configuration']

    if keep_tmpdir:
        logger.debug(f'You can check the job submissions in {temp_dir}.\n')

    logger.debug(f'The following configuration files were generated:\n'
                 f'JSON: {cluster_name}_config.json\n'
                 f'PYTHON: {cluster_name}_config.py')

    # Write the Json config file
    with open(f'{cluster_name}_config.json', 'w') as py_file:
        json.dump(system_config, py_file, indent=4)

    # Set up Jinja2 environment and load the template
    template_loader = FileSystemLoader(searchpath='./')
    env = Environment(loader=template_loader, trim_blocks=True, lstrip_blocks=True)
    rfm_config_template = env.get_template('reframe_config_template.j2')

    # Render the template with the gathered information
    organized_config = rfm_config_template.render(system_config['systems'][0])

    # Output filename for the generated configuration
    output_filename = f'{cluster_name}_config.py'

    # Write the rendered content to the output file
    with open(output_filename, 'w') as output_file:
        output_file.write(organized_config)

    if not keep_tmpdir:
        shutil.rmtree(temp_dir)

if __name__ == '__main__':
    main(user_input, containers_search, devices_search, reservations_based, exclude_feat)
