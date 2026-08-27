#!/bin/bash

# Fallback local driver script (runs on clariden) that uploads a pre-built
# enroot sqsh image from clariden to lys via FirecREST/S3 staging.

set -euo pipefail

# PRE-REQ: Load FirecREST environment and CLI.


export FIRECREST_SYSTEM=lys

# Derive remote user and scratch path from FirecREST.
REMOTE_USER=$(firecrest id | awk -F'[()]' '{print $2}')
REMOTE_SCRATCH=$(firecrest systems | jq -r '.[0].fileSystems[] | select(.dataType=="scratch") | .path')
REMOTE_DIR="${REMOTE_SCRATCH}/${REMOTE_USER}/reframe"
LOCAL_IMAGE="${SCRATCH}/reframe/ce-images/reframe-release.sqsh"

echo "==> Checking local image"
if [[ ! -f "${LOCAL_IMAGE}" ]]; then
    echo "ERROR: local image not found: ${LOCAL_IMAGE}" >&2
    echo "Build it first with: ./build-release.sh" >&2
    exit 1
fi
ls -lh "${LOCAL_IMAGE}"

echo "==> Creating remote image directory ${REMOTE_DIR}/ce-images"
firecrest mkdir -p "${REMOTE_DIR}/ce-images"

echo "==> Uploading image to ${REMOTE_DIR}/ce-images/"
firecrest upload "${LOCAL_IMAGE}" "${REMOTE_DIR}/ce-images" reframe-release.sqsh

echo "==> Verifying uploaded image"
firecrest stat "${REMOTE_DIR}/ce-images/reframe-release.sqsh"
firecrest ls "${REMOTE_DIR}/ce-images"

echo "==> Image deployed to lys: ${REMOTE_DIR}/ce-images/reframe-release.sqsh"
