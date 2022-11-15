#!/bin/bash

IFS=$'\n'
export CUDA_VISIBLE_DEVICES=$SLURM_LOCALID
exec $*
