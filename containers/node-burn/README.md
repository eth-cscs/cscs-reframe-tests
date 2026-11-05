# Node-burn container images (multi-arch)

This directory builds the node-burn container image used by the Container
Engine (CE) ReFrame tests in
`checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py`.  The image is
published to the CSCS jfrog registry (`jfrog.svc.cscs.ch/reframe-oci/node-burn`)
as a **multi-arch OCI index** with `amd64` and `arm64` entries, because the
tests run on both x86_64 (eiger/pilatus) and aarch64 (GH200 vclusters:
daint/starlex/clariden/santis).  The Container Engine resolves the index
per-arch and caches the squashed per-arch images in
`$SCRATCH/.edf_imagestore/`.

## Architecture split

| arch | build on | BLAS path |
|---|---|---|
| `arm64` | starlex login node | NVPL via apt (NVIDIA CUDA repo) |
| `amd64` | eiger/pilatus login node | OpenBLAS 0.3.30 built from source |

The `Containerfile` selects the path automatically with `uname -m`; the same
file is used on both architectures.  `ARG NODEBURN_COMMIT_ID` pins the
node-burn source commit — keep it in sync with the tag name.

## Procedure (full rebuild + republish)

### 1. Build on each architecture

From the repository root, on the login node of the matching architecture:

```bash
podman build -t jfrog.svc.cscs.ch/reframe-oci/node-burn:<tag> containers/node-burn/
```

e.g. `<tag> = cuda-12.4_nb-c22ac2f-openmp` for `NODEBURN_COMMIT_ID=c22ac2f`.
The build log must show `HEAD is now at <commit>` — if it does not, the pin
is not being honored (see gotcha 1).

### 2. Push each arch under an arch-specific temporary tag

On the **arm64** machine (e.g. starlex):

```bash
podman tag jfrog.svc.cscs.ch/reframe-oci/node-burn:<tag> \
           jfrog.svc.cscs.ch/reframe-oci/node-burn:<tag>-arm64
podman push jfrog.svc.cscs.ch/reframe-oci/node-burn:<tag>-arm64
```

On the **amd64** machine (e.g. eiger):

```bash
podman tag jfrog.svc.cscs.ch/reframe-oci/node-burn:<tag> \
           jfrog.svc.cscs.ch/reframe-oci/node-burn:<tag>-amd64
podman push jfrog.svc.cscs.ch/reframe-oci/node-burn:<tag>-amd64
```

> ⚠️ **Never push a single-arch image under the final `<tag>`** — it would
> *replace* the multi-arch index with a single-arch manifest and break pulls
> on the other architecture ("no matching manifest for linux/arm64" or
> "linux/amd64").  Always push arch-specific temporary tags and assemble the
> index as in step 3.

### 3. Assemble the multi-arch index (on any one machine)

The example assumes the arm64 image is local (built or tagged on this
machine) and the amd64 image is on the registry under `<tag>-amd64`:

```bash
# Pull the foreign-arch image with an explicit platform:
podman pull --platform linux/amd64 jfrog.svc.cscs.ch/reframe-oci/node-burn:<tag>-amd64

# Free the final tag (the image survives under its -arm64 tag):
podman rmi jfrog.svc.cscs.ch/reframe-oci/node-burn:<tag>

# Create the index and add both arches (all images local by now):
podman manifest create jfrog.svc.cscs.ch/reframe-oci/node-burn:<tag>
podman manifest add jfrog.svc.cscs.ch/reframe-oci/node-burn:<tag> \
    jfrog.svc.cscs.ch/reframe-oci/node-burn:<tag>-arm64
podman manifest add jfrog.svc.cscs.ch/reframe-oci/node-burn:<tag> \
    jfrog.svc.cscs.ch/reframe-oci/node-burn:<tag>-amd64

# Push the index (--all pushes the referenced manifests too, default true):
podman manifest push jfrog.svc.cscs.ch/reframe-oci/node-burn:<tag>
```

### 4. Verify the registry tag

Using the credentials from `podman login jfrog.svc.cscs.ch`:

```bash
curl -s -u '<user>:<token>' \
  'https://jfrog.svc.cscs.ch/v2/reframe-oci/node-burn/manifests/<tag>' \
  -H 'Accept: application/vnd.oci.image.index.v1+json' \
  | grep -o '"architecture":"[^"]*"'
```

Expected output: `"architecture":"amd64"` and `"architecture":"arm64"`.
If the response is a plain manifest instead of an index, the tag was
overwritten by a single-arch push (see the warning in step 2).

### 5. Update the test's image tag

`checks/microbenchmarks/cpu_gpu/node_burn/node-burn-ce.py` sets
`image_tag` on the `NodeBurnCE` base class — update it to the new `<tag>`
in the same PR, otherwise the tests keep pulling the old image.

## Gotchas

1. **`$(VAR)` is not `${VAR}`** — Dockerfile `ARG`s are interpolated by the
   builder only in `${VAR}`/`$VAR` form.  `$(VAR)` passes through to the
   shell, which treats it as *command substitution*: `NODEBURN_COMMIT_ID`
   is not an executable, so the substitution silently expands to empty and
   `git checkout` becomes a no-op — the image is then built from the
   default branch HEAD instead of the pinned commit.  This is why the
   pre-fix image tagged `nb-be4f759-openmp` actually contained `c22ac2f`
   code (see PR #670).  Always grep the build log for
   `HEAD is now at <pinned commit>`.
2. **Single-arch push overwrites the index** — see the warning in step 2.
3. **`manifest create` needs a free tag** — if the tag already points at a
   local image, `podman rmi <tag>` first; the image survives via its other
   tags (that is what the `-arm64`/`-amd64` tags are for).
4. **Foreign-arch pull needs `--platform`** — e.g. `--platform linux/amd64`
   when pulling the amd64 image on an aarch64 login node, otherwise the
   platform negotiation may refuse the mismatched manifest.
5. **Reference values are content-calibrated** — the performance references
   in `node-burn-ce.py` were measured against a specific image content.
   Changing the pinned commit (and thus the image content) without
   re-validating the references invalidates the performance checks.
6. **First CE pull per account is slow** — the Container Engine caches the
   squashed images in `$SCRATCH/.edf_imagestore/`; the first pull can take
   20–30 minutes, subsequent runs complete in under a minute.
