#!/bin/bash

# NOTE: no hardcoded --account. The `csstaff` account is no longer valid
# for all lys users ("Invalid account or account/partition combination"
# as of 2026-11); sbatch then uses the user's default account (e.g.
# `chuv`). Pass an account via `firecrest submit --account <name>` if
# needed.
#SBATCH --job-name=test-reframe-lys
#SBATCH --time=00:10:00
#SBATCH --nodes=1

# The lys host hook stack (enroot CSCS_2026_05_1, installed 2026-10-02)
# defaults to an "artifact" netstack stored under /capstor, which is not
# mounted on lys, and to an Alps-style libfabric path. Both hooks fail at
# container start for images without matching OCI annotations. Disable
# them for this smoke test (SlurmGPUGresTest runs natively in the
# container and does not need the Slingshot injection).
# See README.md "lys container notes".
export OCI_ANNOTATION_com__hooks__netstack__source=host
export OCI_ANNOTATION_com__hooks__cxi__enabled=false

mkdir -p "${SCRATCH}/reframe/.reframe"

srun --environment="${SCRATCH}/reframe/reframe.toml" \
    reframe -C /opt/cscs-reframe-tests/config/cscs.py \
    -c /opt/cscs-reframe-tests/checks/ \
    --system lys:normal \
    -n SlurmGPUGresTest \
    -r
