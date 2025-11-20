#!/usr/bin/env bash

set -x

export ROCR_VISIBLE_DEVICES="$SLURM_LOCALID"

"$@"
