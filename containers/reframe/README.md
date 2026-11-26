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

If `firecrest id` fails against the lys deployment (CLI 3.7.x reports
`Operation failed: 'group'`, a CLI/server schema mismatch), export the remote
user explicitly:

```bash
export FIRECREST_REMOTE_USER=<remote user>
```

lys also requires an explicit Slurm account for (transfer-based) uploads:

```bash
export FIRECREST_ACCOUNT=<default Slurm account, e.g. chuv>
```

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

## lys container notes (host hook stack since 2026-10-02)

The lys host hook stack (enroot `CSCS_2026_05_1`, installed 2026-10-02 in
`/etc/enroot/hooks.d/`) is templated for CSCS Alps and breaks container
starts for images without matching OCI annotations:

- `10-netstack.sh` (enabled by default) mounts a netstack from
  `/capstor/store/cscs/cscs/public/containers/netstack/...`, which is not
  mounted on lys at all. Its version/name fallbacks are baked-in literals
  and cannot be overridden via the environment.
- `89-libfabric-cxi.sh` (enabled by default) mounts
  `/opt/cray/libfabric/host/lib64/libfabric.so.1` for
  `netstack source=host`; that Alps path layout does not exist on lys
  (lys has `/opt/cray/libfabric/<version>/`).
- `90-aws-ofi-nccl.sh` and `91-dcgm.sh` are opt-in (no annotation, no
  effect).

### Smoke test (no Slingshot needed)

`submit-reframe-lys-firecrest.sh` exports the two annotation overrides
before `srun`, which makes the offending hooks exit cleanly:

```bash
export OCI_ANNOTATION_com__hooks__netstack__source=host
export OCI_ANNOTATION_com__hooks__cxi__enabled=false
```

This skips CXI/libfabric injection entirely - fine for Slurm-level checks.

### MPI containers (Slingshot via the host stack)

Checks that need MPI over Slingshot inside a container can use the **host
libfabric** instead of the netstack injection. Verified on lys with
`OMB_MBW_MR_FullTopology` (23.4 GB/s aggregate over 2 switch groups,
matching the daint N=2 baseline):

1. Keep the two annotation overrides above (`netstack source=host`,
   `cxi enabled=false`). They can be set as EDF annotations
   (`[annotations.com.hooks]`) or as job-environment exports; both reach
   the hooks.
2. Bind-mount the host libfabric stack at paths the container's loader
   already searches. Two lys-specific traps:
   - `/usr/lib64` is not in the Ubuntu container's library search path.
   - `LD_LIBRARY_PATH` set in the job environment is overridden by the
     image environment inside the container (pyxis/enroot), so it cannot
     be used to select the host libfabric.
   For the CE-MPICH OSU image (`omb:7.5.2-mpich4.3.2-ofi1.22-cuda12.8.1`)
   the working mount set is:

   ```toml
   mounts = [
       "<stagedir>:/rfm_workdir",
       "/opt/cray/libfabric/2.3.1/lib64:/opt/cray/libfabric/2.3.1/lib64",
       "/opt/cray/libfabric/2.3.1/lib64/libfabric.so.1:/lib/libfabric.so.1",
       "/opt/cray/libfabric/2.3.1/lib64/libfabric.so.1:/usr/lib/libfabric.so.1",
       "/usr/lib64/libcxi.so.1:/usr/lib/libcxi.so.1",
       # + the remaining host deps of libfabric (libcurl, libjson-c,
       # libssl.so.3, libcrypto.so.3, libkrb5, ...) mounted as
       # "/usr/lib64/<lib>:/usr/lib/<lib>"
   ]
   ```

   The dependency list is exactly what
   `ldd /opt/cray/libfabric/2.3.1/lib64/libfabric.so.1` reports, minus
   glibc libraries. Mounting over `/lib/libfabric.so.1` replaces the
   image's own libfabric (which has no `cxi` provider); the remaining
   host libs go to `/usr/lib/`, which the container loader searches by
   default.

3. `/dev/cxi*` is exposed into containers by enroot defaults; no device
   mounts are needed.

4. If a check selects nodes via switch topology, be aware that lys has a
   single-digit node count with one node (`nid007671`) permanently held by
   the `lys-image-update` maintenance reservation, and that node states
   flap for a while after jobs end (including FirecREST's own transfer
   jobs). IDLE-only node selection is fragile at this scale; prefer
   selecting from all schedulable nodes and letting Slurm queue the job.

Reported to the lys administrators on 2026-11; if the hooks are fixed
upstream, the exports can be dropped and the standard annotations used.
