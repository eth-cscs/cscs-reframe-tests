#!/bin/bash

CUDA_VISIBLE_DEVICES=$SLURM_LOCALID

eval "$@"
