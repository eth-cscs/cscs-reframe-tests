# Configuration autodectection for new systems

The ReFrame configuration file can be automatically generated for a new system using ```generate_config.py```.

## Features

-   Detection of system name
-   Detection of hostname
-   Detection of module system 
-   Detection of scheduler
-   Detection of parallel launcher
-   Detection of partitions based on node types (node features from Slurm) [only when the scheduler is **Slurm**]
-   Detection of partitions based on reservations [only when the scheduler is **Slurm**]
-   Detection of available container platforms in remote partitions (and required modules when the module system is ```lmod```) [only when the scheduler is **Slurm**]
-   Detection of devices with architecture in the nodes (GRes from Slurm) [only when the scheduler is **Slurm**]

## Usage

### Install the Jinja2 python package

```sh
pip install jinja2
```

### Basic usage

```sh
python3 generate_config.py
```

The script is run in **interactive** mode. User input is used to detect and generate the final configuration of the system. The user input can be supressed by passing the ```--auto``` option.

## Available Arguments

| Argument                                            | Description                                                                 |
|-----------------------------------------------------|-----------------------------------------------------------------------------------------|
| `--auto`                                            | Disables user input. |
| `--no-remote-containers`                            | Disables the detection of containers in the remote partitions | 
| `--no-remote-devices`                               | Disables the detection of devices (slurm GRes) in the remote partitions |
| `--reservations=[list_reservations]`                | Allows the specification of the reservations in the system for which a partitions should be created |


```sh
python3 generate_config.py --auto
```

With this option, user input is not required to generate the configuration file. In the ```auto``` mode the following partitions are automatically created:

-   Login partition
-   Partition for each node type (based on Slurm AvailableFeatures)

If additional partitions for a specific reservations are required, the ```--auto``` option can be combined with ```--reservations=reserv_1,reserv_2``` in order to create partitions for ```reserv_1``` and ```reserv_2``` respectively.

```sh
python3 generate_config.py --auto --reservations=reserv_1,reserv_2
```

In the ```auto``` mode the detection of container platforms and devices is by default enabled. This requires the submission of a job per partition to detect these features. The script will wait until the job is completed. This job submission can be disabled through the options ```--no-remote-containers``` and ```--no-remote-devices``` respectively. Note that by default if no GRes is detected in a node, no device detection script will be submitted.

The options ```--no-remote-containers```, ```--no-remote-devices``` and ```--reservations=[list_reservations]``` are only used in the ```auto``` mode.

## Generated configuration files

The script generates a ```json``` and a ```py``` file with the system configuration

- json: ```<system_name>```_config.json
- .py: ```<system_name>```_config.py
