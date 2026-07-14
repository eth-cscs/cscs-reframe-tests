#!/bin/bash

#SBATCH --account=csstaff
#SBATCH --job-name=test-reframe
#SBATCH --time=00:10:00
#SBATCH --nodes=1

srun --environment=./reframe.toml reframe -C /opt/cscs-reframe-tests/config/cscs.py -c /opt/cscs-reframe-tests/checks/ --system daint:normal -n SlurmGPUGresTest -r
