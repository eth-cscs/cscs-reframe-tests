#!/bin/bash

set -eu

export ROCR_VISIBLE_DEVICES=$SLURM_LOCALID

exec "$@"
