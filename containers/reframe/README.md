# ReFrame container workflow for clariden and lys

This directory contains the container image and job scripts used to build and
run the CSCS ReFrame test suite inside an enroot/Pyxis container on **clariden**
and on **lys** (via FirecREST, no SSH required).

The workflow uses a single shared container environment file
(`reframe.toml`) that resolves `${SCRATCH}` to the correct scratch path on each
system.

## Prerequisites

- Clariden/Daint
  -  `podman` and `enroot` available on a compute node.
- Lys:
  - FirecREST CLI configured. 
     - pyfirecrest and credentials
- `jq` installed (used by the lys driver scripts to parse `firecrest systems`).

## File summary

| File | Purpose |
|---|---|
| `Containerfile-release` | Container definition for the release image (Ubuntu 24.04 + ReFrame 4.10.1 + CSCS checks). |
| `Containerfile-develop` | Alternative container definition for development. |
| `apt-workaround/` | Internal CSCS Ubuntu mirror configuration injected into the container build. |
| `reframe.toml` | Shared Pyxis environment file. Image, mounts and workdir are based on `${SCRATCH}/reframe`. |
| `build-release.sh` | Build the image **locally on clariden** and export it to `${SCRATCH}/reframe/ce-images/...`. |
| `build-release-lys.sh` | Batch recipe that builds the image **natively on a lys compute node**. |
| `build-on-lys.sh` | Clariden driver that uploads the build context to lys and submits `build-release-lys.sh` via FirecREST. |
| `test-on-lys.sh` | Clariden driver that uploads the test scripts to lys and submits the ReFrame smoke test via FirecREST. |
| `submit-reframe-clariden.sh` | Batch script to run the ReFrame tests inside the container on clariden. |
| `submit-reframe-lys-firecrest.sh` | Batch script to run the ReFrame smoke test inside the container on lys. |
| `submit-reframe-daint.sh` | Batch script for running the tests on daint. |
| `deploy-image-to-lys.sh` | Fallback driver: upload a pre-built sqsh image from clariden to lys via FirecREST. |

## Usage

### clariden

Run from a compute node in this directory:

```bash
./build-release.sh
sbatch submit-reframe-clariden.sh
```

The image is written to `${SCRATCH}/reframe/ce-images/reframe-release.sqsh`.
`submit-reframe-clariden.sh` loads the environment from
`${SCRATCH}/reframe/reframe.toml`.

### lys (via FirecREST from clariden)

Build the image natively on lys:

```bash
./build-on-lys.sh
```

Run the smoke test:

```bash
./test-on-lys.sh
```

Both scripts derive the remote user and scratch path from FirecREST, upload the
necessary files, submit the batch job, wait for completion and download the
Slurm output log.

### Fallback: upload a pre-built image to lys

If the native lys build does not work, build on clariden and upload:

```bash
./build-release.sh
./deploy-image-to-lys.sh
```

Then run the test as usual:

```bash
./test-on-lys.sh
```

## Notes

- `reframe.toml` is shared between clariden and lys. Each system expands
  `${SCRATCH}` to its own scratch filesystem, and the `.reframe` directory is
  kept under `${SCRATCH}/reframe/.reframe` while being mounted at
  `${HOME}/.reframe` inside the container.

- On lys, compute nodes have no systemd user session, so `/run/user/<uid>`
  does not exist and podman cannot use the default systemd cgroup manager.
  `build-release-lys.sh` works around this by setting
  `XDG_RUNTIME_DIR=/tmp/podman-run-${USER}` and writing a `containers.conf`
  with `cgroup_manager = "cgroupfs"`.

- On lys, `/vast/scratch` is a network filesystem that does not support the
  extended attributes required by podman's overlay storage driver.
  `build-release-lys.sh` keeps podman's image layers on local tmpfs by setting
  `XDG_DATA_HOME=/tmp/podman-data-${USER}`.

- On lys, `enroot import` may return exit code 1 even after successfully
  creating the sqsh image; `build-release-lys.sh` captures the code and
  verifies the artifact explicitly.

- On lys, GID mismatch (transient / not reproduced): the job was observed running
  with group `workspace36` while `/etc/passwd` listed `workspace39`, causing
  `newuidmap` to reject rootless user namespaces. This has not been reproduced
  recently. If needed, wrap podman and enroot calls with `sg workspace39`.
