# Configuration autodetection for new systems

The ReFrame configuration file can be automatically generated for a new system using ```generate.py```.

## Features

-   Detection of system name
-   Detection of hostname
-   Detection of module system
-   Detection of scheduler
-   Detection of parallel launcher
-   Detection of partitions based on node types (node features from Slurm) [only when the scheduler is **Slurm**]
-   Detection of partitions based on reservations [only when the scheduler is **Slurm**]
-   Detection of available container platforms in remote partitions (and required modules when the modules system is ```lmod``` or ```tmod```) [only when the scheduler is **Slurm**]
-   Detection of devices with architecture in the nodes (GRes from Slurm) [only when the scheduler is **Slurm**]

## Usage

### Install Jinja2 and autopep8 python packages

```sh
pip install jinja2
pip install autopep8
```

### Basic usage

```sh
python3 generate.py
```

The script is run in **interactive** mode. User input is used to detect and generate the final configuration of the system. The user input can be supressed by passing the ```--auto``` option.

## Available Arguments

| Argument                                            | Description                                                                 |
|-----------------------------------------------------|-----------------------------------------------------------------------------------------|
| `--auto`                                            | Disables user input. |
| `--exclude=[list_of_features]`                      | List of features to be excluded in the detection of node types |
| `--no-remote-containers`                            | Disables the detection of containers in the remote partitions |
| `--no-remote-devices`                               | Disables the detection of devices (slurm GRes) in the remote partitions |
| `--reservations=[list_reservations]`                | Allows the specification of the reservations in the system for which a partitions should be created |
| `--prefix`                                          | Shared directory where the jobs for remote detection will be created and submitted |
| `--access`                                          | Additional access options that must be included for the sbatch submission |
| `-v`                                                | Adjust the verbosity level to debug in ```auto``` mode. The option is only effective if combined with ```--auto```. |

```sh
python3 generate.py --auto
```

With this option, user input is not required to generate the configuration file. In the ```auto``` mode the following partitions are automatically created:

-   Login partition
-   Partition for each node type (based on Slurm AvailableFeatures)

If additional partitions for a specific reservations are required, the ```--auto``` option can be combined with ```--reservations=reserv_1,reserv_2``` in order to create partitions for ```reserv_1``` and ```reserv_2``` respectively.

```sh
python3 generate.py --auto --reservations=reserv_1,reserv_2
```

In the ```auto``` mode the detection of container platforms and devices is by default enabled. This requires the submission of a job per partition to detect these features. The script will wait until the job is completed. This job submission can be disabled through the options ```--no-remote-containers``` and ```--no-remote-devices``` respectively. Note that by default if no Gres is detected in a node, no device detection script will be submitted.

The options ```--no-remote-containers``` and ```--reservations=[list_reservations]``` are only used in the ```auto``` mode. The option ```--no-remote-devices``` is valid for both interactive and ```auto``` modes.

**Excluding node features from the node types filtering**

In order to exclude some features from the detection of the different node types, these can be passed to the script in the command line using the option ```--exclude=[list_of_features]```. Patterns can also be specified in this option using ```*```.

*Usage example:*

```sh
python3 generate.py --exclude=group*,c*,r*
```

Running this will ignore the node features that match those patterns. Node A with features ```(gpu,group2,column43,row9)``` and Node B ```(gpu,group8,column1,row75)``` will be identified as the same node type and included in the same partition.

**Specifying additional access options**

Additional access options can be passed to the script through the ```--access``` command line option.

*Usage example:*

```sh
python3 generate.py --access=-Cgpu
```

This option will add ```-Cgpu``` to the access options for the remote partitions in the configuration file and use it submit the remote detection jobs for container platforms and devices.

## Generated configuration files

The script generates a ```py``` file with the system configuration

- .py: ```<system_name>```_config.py
