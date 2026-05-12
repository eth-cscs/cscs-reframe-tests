#! /usr/bin/env bash

export GPUID=$(( SLURM_LOCALID % 8))

export ROCR_VISIBLE_DEVICES=$GPUID

"$@"

