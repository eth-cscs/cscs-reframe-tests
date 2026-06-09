#! /usr/bin/env bash

export GPUID=$(( SLURM_LOCALID % 4 ))
export NUMAID=$GPUID

export ROCR_VISIBLE_DEVICES=$GPUID

numactl --cpunodebind=$NUMAID --membind=$NUMAID "$@"
