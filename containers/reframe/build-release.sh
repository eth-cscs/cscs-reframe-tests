#!/bin/bash

podman build -t localhost/${USER}/reframe:release -f ./Containerfile-release .
rm -f ${SCRATCH}/ce-images/reframe-release.sqfs
enroot import -x mount -o ${SCRATCH}/ce-images/reframe-release.sqfs podman://localhost/${USER}/reframe:release
