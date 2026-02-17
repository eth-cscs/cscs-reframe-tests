#!/bin/bash

podman build -t localhost/${USER}/reframe:release -f ./Containerfile-release .
enroot import -x mount -o ${SCRATCH}/ce-images/reframe-release.sqsh podman://localhost/${USER}/reframe:release
