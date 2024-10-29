
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

nvidia_gpu_architecture = {
                            "Tesla K20": "sm_35",
                            "Tesla K40": "sm_35",
                            "Tesla P100": "sm_60",
                            "Tesla V100": "sm_70",
                            "Tesla T4": "sm_75",
                            "Tesla A100": "sm_80",
                            "Quadro RTX 8000": "sm_75",
                            "Quadro RTX 6000": "sm_75",
                            "Quadro P6000": "sm_61",
                            "Quadro GV100": "sm_70",
                            "GeForce GTX 1080": "sm_61",
                            "GeForce GTX 1080 Ti": "sm_61",
                            "GeForce GTX 1070": "sm_61",
                            "GeForce GTX 1060": "sm_61",
                            "GeForce GTX 1050": "sm_61",
                            "GeForce RTX 2060": "sm_75",
                            "GeForce RTX 2070": "sm_75",
                            "GeForce RTX 2080": "sm_75",
                            "GeForce RTX 2080 Ti": "sm_75",
                            "GeForce RTX 3060": "sm_86",
                            "GeForce RTX 3070": "sm_86",
                            "GeForce RTX 3080": "sm_86",
                            "GeForce RTX 3090": "sm_86",
                            "GeForce RTX 4060": "sm_89",
                            "GeForce RTX 4070": "sm_89",
                            "GeForce RTX 4080": "sm_89",
                            "GeForce RTX 4090": "sm_89",
                            "A100": "sm_80",
                            "H100": "sm_90",
                            "H100 PCIe": "sm_90",
                            "H100 SXM": "sm_90",
                            "Titan V": "sm_70",
                            "Titan RTX": "sm_75"
                        }

containers_detect_bash = '''
# List of containers to check
CONTAINERS=(
    "Sarus:sarus"
    "Apptainer:apptainer"
    "Docker:docker"
    "Singularity:singularity"
    "Shifter:shifter"
)

# Array to hold installed containers
installed=()

# Function to check for module existence (with lmod)
check_module_spider() {
    output=$(module spider "$1" 2>&1)
    if echo $output | grep -q "error"; then
        return 1
    else
        return 0
    fi
}

# Function to check for module existence (with tmod)
check_module_avail() {
    output=$(module avail "$1" 2>&1)
    if echo $output | grep -q "$1"; then
        return 0
    else
        return 1
    fi
}

check_lmod() {
    if [[ -n "$LMOD_CMD" ]]; then
        return 0
    else
        return 1
    fi
}

check_tmod() {
    if [[ -n "modulecmd -V" ]]; then
        return 0
    else
        return 1
    fi
}

# Check each container command
for container in "${CONTAINERS[@]}"; do
    IFS=":" read -r name cmd <<< "$container"

    # Check if the command exists via 'which'
    found_via_command=false
    found_via_module=false

    if which "$cmd" > /dev/null 2>&1; then
        found_via_command=true
    fi

    if check_lmod; then
        # Check if it's available as a module, regardless of 'which' result
        if check_module_spider "$cmd"; then
            output=$(module spider "$cmd" 2>&1)
            modules_load=$(echo $output | grep -oP '(?<=available to load.).*?(?= Help)')
            found_via_module=true
        fi
    fi

    if check_tmod; then
        # Check if it's available as a module, regardless of 'which' result
        if check_module_avail "$cmd"; then
            output=$(module avail "$cmd" 2>&1)
            modules_load=""
            found_via_module=true
        fi
    fi

    # Determine the status of the container
    if $found_via_command && $found_via_module; then
        installed+=("$name modules: $modules_load")
    elif $found_via_command; then
        installed+=("$name")
    elif $found_via_module; then
        installed+=("$name modules: $modules_load")
    else
        echo "$name is not installed."
    fi
done

# Output installed containers
echo "Installed containers:"
for name in "${installed[@]}"; do
    echo "$name"
done
'''

devices_detect_bash = '''
# Check for NVIDIA GPUs
if command -v nvidia-smi > /dev/null 2>&1; then
    echo "Checking for NVIDIA GPUs..."
    gpu_info=$(nvidia-smi --query-gpu=name --format=csv,noheader)

    if [ -z "$gpu_info" ]; then
        echo "No NVIDIA GPU found."
    else
        echo "NVIDIA GPUs installed:"
        echo "$gpu_info"
    fi
else
    echo "No NVIDIA GPU found or nvidia-smi command is not available."
fi

# Check for AMD GPUs (if applicable)
if command -v lspci > /dev/null 2>&1; then
    echo -e "\nChecking for AMD GPUs:"
    if lspci | grep -i 'amd\|radeon'; then
        lspci | grep -i 'amd\|radeon'
    else
        echo "No AMD GPU found."
    fi
else
    echo "lspci command is not available."
fi
'''

cn_memory_bash = '''
#!/bin/bash

# Execute the free -h command and capture the output
output=$(free -h)

# Extract the total memory value from the output (second column of the "Mem:" row)
total_memory=$(echo "$output" | grep -i "mem:" | awk '{print $2}')

# Output the total memory
echo "Total memory: $total_memory"
                '''

slurm_submission_header = '''#!/bin/bash
#SBATCH --job-name="Config_autodetection"
#SBATCH --ntasks=1
#SBATCH --output=config_autodetection_{partition_name}.out
#SBATCH --error=config_autodetection_{partition_name}.out
#SBATCH --time=0:2:0
'''
