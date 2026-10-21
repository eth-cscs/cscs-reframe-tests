#!/bin/bash

set -e

podman build -t localhost/${USER}/reframe:release -f ./Containerfile-release .
mkdir -p "${SCRATCH}/reframe/ce-images"
rm -f "${SCRATCH}/reframe/ce-images/reframe-release.sqsh"

enroot import -x mount -o "${SCRATCH}/reframe/ce-images/reframe-release.sqsh" podman://localhost/${USER}/reframe:release

# Place a copy of the environment file next to the image so srun can load it
# with an absolute ${SCRATCH} path regardless of the submission cwd.
cp ./reframe.toml "${SCRATCH}/reframe/reframe.toml"

echo "==> Image created"
ls -lh "${SCRATCH}/reframe/ce-images/reframe-release.sqsh"
