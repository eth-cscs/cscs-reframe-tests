#!/bin/bash

set -u

export CUDA_MPS_PIPE_DIRECTORY=/tmp/nvidia-mps
export CUDA_MPS_LOG_DIRECTORY=/tmp/nvidia-log
export CUDA_VISIBLE_DEVICES=$(( SLURM_LOCALID % 4 ))

if [ "${SLURM_LOCALID}" -eq 0 ]; then
    CUDA_VISIBLE_DEVICES=0,1,2,3 nvidia-cuda-mps-control -d
fi

sleep 5

exec "$@"

if [ "${SLURM_LOCALID}" -eq 0 ]; then
    echo quit | nvidia-cuda-mps-control
fi
