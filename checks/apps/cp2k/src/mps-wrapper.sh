#!/bin/bash

set -eu

export CUDA_DEVICE_MAX_COPY_CONNECTIONS=8
export CUDA_DEVICE_MAX_CONNECTIONS=8

export CUDA_MPS_PIPE_DIRECTORY=/tmp/nvidia-mps-$((SLURM_LOCALID % 4))
export CUDA_MPS_LOG_DIRECTORY=/tmp/nvidia-log-$((SLURM_LOCALID % 4))-$(id -un)

export HWLOC_KEEP_NVIDIA_GPU_NUMA_NODES=0
numa_nodes=$(hwloc-calc --physical --intersect NUMAnode $(hwloc-bind --get --taskset)) # do not set CUDA_VISIBLE_DEVICES, enough to set it for the daemon

# Launch MPS from a single rank per GPU
if [[ $SLURM_LOCALID -lt 4 ]]; then
    mkdir -p ${CUDA_MPS_PIPE_DIRECTORY}
    mkdir -p ${CUDA_MPS_LOG_DIRECTORY}
    CUDA_VISIBLE_DEVICES=$((SLURM_LOCALID % 4)) nvidia-cuda-mps-control -d
fi

# Wait for MPS to start
sleep 1

# Run the command
"$@"
result=$?

# Quit MPS control daemon before exiting
if [[ $SLURM_LOCALID -lt 4 ]]; then
    echo quit | nvidia-cuda-mps-control
fi

exit $result
