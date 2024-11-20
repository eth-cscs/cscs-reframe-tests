#!/bin/bash
GPUS=(3 2 1 0)
let lrank=$SLURM_LOCALID%8
export CUDA_VISIBLE_DEVICES=${GPUS[lrank]}
# echo "SLURM_LOCALID=$SLURM_LOCALID CUDA_VISIBLE_DEVICES=${GPUS[lrank]}"
exec $*
