#!/bin/bash

# Local driver script (runs on clariden) that builds the ReFrame container
# image natively on lys via FirecREST.

set -euo pipefail

# PRE-REQ: Load FirecREST environment and CLI.


export FIRECREST_SYSTEM=lys

# Derive remote user and scratch path from FirecREST.
REMOTE_USER=$(firecrest id | awk -F'[()]' '{print $2}')
REMOTE_SCRATCH=$(firecrest systems | jq -r '.[0].fileSystems[] | select(.dataType=="scratch") | .path')
REMOTE_DIR="${REMOTE_SCRATCH}/${REMOTE_USER}/reframe"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Creating remote working directory ${REMOTE_DIR}"
firecrest mkdir -p "${REMOTE_DIR}"

echo "==> Uploading build context to ${REMOTE_DIR}"
firecrest upload "${SCRIPT_DIR}/Containerfile-release" "${REMOTE_DIR}" Containerfile-release
firecrest mkdir -p "${REMOTE_DIR}/apt-workaround"
firecrest upload "${SCRIPT_DIR}/apt-workaround/ubuntu.sources" "${REMOTE_DIR}/apt-workaround" ubuntu.sources
firecrest upload "${SCRIPT_DIR}/apt-workaround/99-jfrog-proxy" "${REMOTE_DIR}/apt-workaround" 99-jfrog-proxy
firecrest upload "${SCRIPT_DIR}/build-release-lys.sh" "${REMOTE_DIR}" build-release-lys.sh

echo "==> Making remote build script executable"
firecrest chmod "${REMOTE_DIR}/build-release-lys.sh" 755

echo "==> Submitting remote build job"
SUBMIT_OUT=$(firecrest submit --working-dir "${REMOTE_DIR}" "remote://${REMOTE_DIR}/build-release-lys.sh")
echo "${SUBMIT_OUT}"

JOBID=$(echo "${SUBMIT_OUT}" | jq -r '.jobId')
if [[ -z "${JOBID}" || "${JOBID}" == "null" ]]; then
    echo "ERROR: failed to extract job ID from submit response" >&2
    exit 1
fi

echo "==> Waiting for build job ${JOBID}"
firecrest wait-for-job "${JOBID}"

echo "==> Downloading build output"
firecrest download "${REMOTE_DIR}/slurm-${JOBID}.out" "${SCRIPT_DIR}/slurm-${JOBID}.out"
echo "Build log saved to: ${SCRIPT_DIR}/slurm-${JOBID}.out"

echo "==> Checking for generated image on ${REMOTE_DIR}/ce-images/reframe-release.sqsh"
firecrest stat "${REMOTE_DIR}/ce-images/reframe-release.sqsh"
