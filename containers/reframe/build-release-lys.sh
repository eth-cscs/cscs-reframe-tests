#!/bin/bash

#SBATCH --account=csstaff
#SBATCH --job-name=reframe-build-lys
#SBATCH --time=01:00:00
#SBATCH --nodes=1

set -e

# Single scratch prefix for this workflow.  HOST HOME and SCRATCH are left at
# their host defaults; on lys they resolve to /users/<user> and
# /vast/scratch/<user> respectively.
export RFM_LYS_WORKDIR=${SCRATCH}/reframe

# Podman's image storage must be on a local filesystem that supports xattrs;
# /vast/scratch is a network filesystem and does not.  Use /tmp (tmpfs) for the
# container storage and runtime files, and keep only the final sqsh on scratch.
export XDG_RUNTIME_DIR=/tmp/podman-run-${USER}
export XDG_DATA_HOME=/tmp/podman-data-${USER}
export XDG_CONFIG_HOME=${RFM_LYS_WORKDIR}/containers/config

mkdir -p "${RFM_LYS_WORKDIR}/.reframe" "${XDG_RUNTIME_DIR}" "${XDG_DATA_HOME}" "${XDG_CONFIG_HOME}"

# Silence the systemd cgroup warning and avoid relying on a user systemd bus.
mkdir -p "${XDG_CONFIG_HOME}/containers"
cat > "${XDG_CONFIG_HOME}/containers/containers.conf" <<'EOF'
[engine]
cgroup_manager = "cgroupfs"
EOF

echo "==> Build environment"
echo "USER=${USER}"
echo "HOME=${HOME}"
echo "SCRATCH=${SCRATCH}"
echo "RFM_LYS_WORKDIR=${RFM_LYS_WORKDIR}"
echo "XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR}"
echo "XDG_DATA_HOME=${XDG_DATA_HOME}"
echo "XDG_CONFIG_HOME=${XDG_CONFIG_HOME}"

echo "==> Checking for container tools"
which podman >/dev/null || { echo "ERROR: podman not available on this node"; exit 1; }
which enroot >/dev/null || { echo "ERROR: enroot not available on this node"; exit 1; }

echo "==> Building container image"
podman build -t localhost/${USER}/reframe:release -f ./Containerfile-release .

echo "==> Importing image to enroot sqsh"
mkdir -p "${RFM_LYS_WORKDIR}/ce-images"
rm -f "${RFM_LYS_WORKDIR}/ce-images/reframe-release.sqsh"

# On lys enroot import exits with code 1 even after successfully creating the
# squashfs image.  Capture the code and verify the artifact explicitly.
set +e
enroot import -x mount -o "${RFM_LYS_WORKDIR}/ce-images/reframe-release.sqsh" podman://localhost/${USER}/reframe:release
ENROOT_EC=$?
set -e

if [[ ${ENROOT_EC} -ne 0 ]]; then
    echo "WARNING: enroot import returned exit code ${ENROOT_EC}; verifying artifact" >&2
fi

if [[ ! -s "${RFM_LYS_WORKDIR}/ce-images/reframe-release.sqsh" ]]; then
    echo "ERROR: ${RFM_LYS_WORKDIR}/ce-images/reframe-release.sqsh is missing or empty" >&2
    exit 1
fi

echo "==> Image created"
ls -lh "${RFM_LYS_WORKDIR}/ce-images/reframe-release.sqsh"
