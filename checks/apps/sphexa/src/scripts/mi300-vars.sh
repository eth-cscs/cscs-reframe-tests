#!/bin/bash

export LOCAL_RANK=$SLURM_LOCALID
export GLOBAL_RANK=$SLURM_PROCID
export GPUS=(0 1 2 3)
export NUMA_NODE=$(echo "$LOCAL_RANK % 4" | bc)
export HIP_VISIBLE_DEVICES=${GPUS[$NUMA_NODE]}

#echo $GLOBAL_RANK/$LOCAL_RANK sees $CUDA_VISIBLE_DEVICES

export MPICH_GPU_SUPPORT_ENABLED=1

numactl --cpunodebind=$NUMA_NODE --membind=$NUMA_NODE "$@"
