---
name: airgap-image-transfer
description: Export OCI/Docker container images to files and move them from an internet-connected machine to an airgapped one, using skopeo or regctl instead of `docker save`. Use whenever the task is to bundle, transfer, mirror, or air-gap a container image (for a flash drive, an internal registry, JFrog Artifactory, or an OpenShift cluster with no internet), or when `docker save` produces a tiny/broken tarball with missing layers. Covers why `docker save` silently drops layer blobs under the containerd image store, the skopeo/regctl commands that avoid it, checksum verification, and loading/pushing on the airgapped side.
---

# Airgapped container image transfer (skopeo / regctl)

Moving a container image from an internet-connected machine to an airgapped one is a
pull → export-to-file → carry → load/push workflow. The reliable tools for the
export step are **skopeo** or **regctl** — not `docker save`. This skill explains
why, and gives the exact commands for both ends.

## TL;DR

```bash
# On the internet machine — pull straight from the registry to a docker-load-able archive:
skopeo copy --override-os linux --override-arch amd64 \
  docker://ghcr.io/org/image:1.2.3 \
  docker-archive:image_1.2.3_amd64.tar:org/image:1.2.3
gzip image_1.2.3_amd64.tar
sha256sum image_1.2.3_amd64.tar.gz > image_1.2.3_amd64.tar.gz.sha256

# --- carry the .tar.gz + .sha256 across the airgap (flash drive) ---

# On the airgapped machine — verify, then load or push:
sha256sum -c image_1.2.3_amd64.tar.gz.sha256
gunzip image_1.2.3_amd64.tar.gz
docker load -i image_1.2.3_amd64.tar        # or: podman load -i ...
```

## Why not `docker save`

Docker Engine stores images two ways:

- the classic **graph-driver store** (overlay2), and
- the newer **containerd image store** (containerd snapshotter).

Check which is active:

```bash
docker info | grep -iE "storage driver|driver-type"
# driver-type: io.containerd.snapshotter.v1  → containerd image store is ON
```

**The failure:** registry images are usually multi-arch **manifest lists**. With the
containerd image store, `docker save <name:tag>` of such an image writes the index +
per-arch manifests + config blobs but **omits the actual layer blobs** — you get a
tiny (tens-of-KB) tarball that looks valid but contains no filesystem. Adding
`--platform` often fails outright with *"no suitable export target found: … does not
provide the specified platform"*. Symptoms to recognize:

- `docker save` output is kilobytes when the image is hundreds of MB;
- `tar tf out.tar` shows `index.json`, `manifest.json`, `oci-layout` and only a few
  small `blobs/sha256/*` entries;
- `docker load` on the other side errors or produces an unusable image.

This is a known interaction between `docker save` and the containerd image store for
manifest-list images. Don't fight it — use skopeo or regctl, which bypass the daemon
export path entirely.

## Why skopeo / regctl are better here

- **Daemon-independent.** `skopeo copy docker://…` pulls directly from the registry to
  a file; it never touches the local containerd store, so the blob-dropping bug can't
  occur. (regctl works the same way.)
- **Deterministic platform selection** via `--override-os/--override-arch` (skopeo) or
  `--platform` (regctl) — critical when the airgapped target is a fixed arch (e.g.
  linux/amd64 for most OpenShift/Ubuntu, linux/arm64 for Graviton/ARM nodes).
- **Registry-to-registry mirroring** in one command — no local docker load needed.
- **Digest-pinning and signature handling** for reproducible, verifiable transfers.
- Works with **Podman/OpenShift** environments where a Docker daemon may not even be
  present.

## Export options (internet machine)

Pick the archive format by how you'll consume it on the other side.

**skopeo → `docker load`-able archive** (most common):
```bash
skopeo copy --override-os linux --override-arch amd64 \
  docker://<registry>/<repo>:<tag> \
  docker-archive:<file>.tar:<repo>:<tag>
```

**skopeo → OCI layout archive** (for tooling that wants OCI, or multi-image):
```bash
skopeo copy docker://<registry>/<repo>:<tag> oci-archive:<file>.oci.tar:<tag>
```

**regctl → archive** (alternative if skopeo isn't installed):
```bash
regctl image export --platform linux/amd64 <registry>/<repo>:<tag> <file>.tar
```

**Pin by digest** for reproducibility (recommended for anything you'll audit):
```bash
skopeo copy docker://<registry>/<repo>@sha256:<digest> docker-archive:<file>.tar:<repo>:<tag>
```

Always follow with `gzip` + a `sha256sum` sidecar so integrity is checkable after the
flash-drive hop.

## Import options (airgapped machine)

**Load into a local engine:**
```bash
docker load -i <file>.tar        # Docker
podman load -i <file>.tar        # Podman / OpenShift nodes
```

**Push straight into an internal registry** (JFrog Artifactory Docker repo, OpenShift
internal registry) — skopeo can do this without a local daemon:
```bash
skopeo copy docker-archive:<file>.tar \
  docker://artifactory.internal.example.com/docker-local/<repo>:<tag> \
  --dest-creds <user>:<token>
```
Then reference that internal image from your Deployment/Pod specs.

## Gotchas

- **Match the arch to the target**, not to the export machine. If unsure, export both
  `amd64` and `arm64`, or copy the full manifest list to your internal registry.
- **Private CA / self-signed registries:** add the CA to the OS trust store, or use
  `--src-tlsverify=false` / `--dest-tlsverify=false` (skopeo) / `--host` regctl config
  for the internal registry.
- **Multi-arch in one file:** use `oci-archive` (or `skopeo copy --all …` to a
  registry). `docker-archive` is single-image/single-platform by design.
- **Fixing `docker save` itself** (only if you must use it): disable the containerd
  image store in `/etc/docker/daemon.json` with
  `{ "features": { "containerd-snapshotter": false } }` and restart Docker — reverts
  to the overlay2 store where `docker save` behaves classically, but you lose native
  multi-arch/lazy-pull and must re-pull existing images. Prefer skopeo/regctl instead.
- **Install (internet side):** `skopeo` and `regctl` are single tools; on Debian/Ubuntu
  `apt install skopeo`, or grab static binaries. If you need them airgapped too,
  transfer their binaries the same way you'd transfer any other CLI.
