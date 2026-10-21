#!/bin/bash

#SBATCH --account=csstaff
#SBATCH --job-name=test-reframe
#SBATCH --time=00:30:00
#SBATCH --nodes=1

mkdir -p "${SCRATCH}/reframe/.reframe"

srun --environment="${SCRATCH}/reframe/reframe.toml" \
    reframe -C /opt/cscs-reframe-tests/config/cscs.py \
    -c /opt/cscs-reframe-tests/checks/ \
    --system clariden:normal \
    -n SlurmGPUGresTest \
    -n NCCLTestsCE \
    -n CudaNodeBurnGemmCE \
    -r
