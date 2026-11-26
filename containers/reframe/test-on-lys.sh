#!/bin/bash

# Local driver script (runs on clariden) that runs the ReFrame smoke test
# inside the container on lys via FirecREST.

set -euo pipefail

# PRE-REQ: Load FirecREST environment and CLI.

export FIRECREST_SYSTEM=lys

# Derive remote user and scratch path from FirecREST.
#
# `firecrest id` fails against the lys deployment with CLI 3.7.x ("Operation
# failed: 'group'": the server returns `groups` as a list and no singular
# `group` key). Fall back to FIRECREST_REMOTE_USER in that case.
REMOTE_USER="${FIRECREST_REMOTE_USER:-$(firecrest id 2>/dev/null | awk -F'[()]' '{print $2}')}"
if [[ -z "${REMOTE_USER}" ]]; then
    echo "ERROR: could not determine the remote user." >&2
    echo "       'firecrest id' failed and FIRECREST_REMOTE_USER is unset." >&2
    exit 1
fi
REMOTE_SCRATCH=$(firecrest systems | jq -r '.[0].fileSystems[] | select(.dataType=="scratch") | .path')
REMOTE_DIR="${REMOTE_SCRATCH}/${REMOTE_USER}/reframe"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# lys requires an explicit account for (transfer-based) uploads; set
# FIRECREST_ACCOUNT to the user's default Slurm account, e.g. `chuv`.
ACCOUNT_ARGS=()
if [[ -n "${FIRECREST_ACCOUNT:-}" ]]; then
    ACCOUNT_ARGS=(--account "${FIRECREST_ACCOUNT}")
fi

echo "==> Ensuring remote working directory ${REMOTE_DIR} exists"
firecrest mkdir -p "${REMOTE_DIR}"

echo "==> Uploading test scripts to ${REMOTE_DIR}"
firecrest upload "${ACCOUNT_ARGS[@]}" "${SCRIPT_DIR}/reframe.toml" "${REMOTE_DIR}" reframe.toml
firecrest upload "${ACCOUNT_ARGS[@]}" "${SCRIPT_DIR}/submit-reframe-lys-firecrest.sh" "${REMOTE_DIR}" submit-reframe-lys-firecrest.sh

echo "==> Making remote test script executable"
firecrest chmod "${REMOTE_DIR}/submit-reframe-lys-firecrest.sh" 755

echo "==> Submitting remote test job"
SUBMIT_OUT=$(firecrest submit --working-dir "${REMOTE_DIR}" "remote://${REMOTE_DIR}/submit-reframe-lys-firecrest.sh")
echo "${SUBMIT_OUT}"

JOBID=$(echo "${SUBMIT_OUT}" | jq -r '.jobId')
if [[ -z "${JOBID}" || "${JOBID}" == "null" ]]; then
    echo "ERROR: failed to extract job ID from submit response" >&2
    exit 1
fi

echo "==> Waiting for test job ${JOBID}"
firecrest wait-for-job "${JOBID}"

echo "==> Downloading test output"
firecrest download "${REMOTE_DIR}/slurm-${JOBID}.out" "${SCRIPT_DIR}/slurm-${JOBID}.out"
echo "Test log saved to: ${SCRIPT_DIR}/slurm-${JOBID}.out"
