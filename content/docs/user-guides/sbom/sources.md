+++
title = "Supported Sources"
description = "Explore the different sources Syft can analyze including container images, OCI registries, directories, files, and archives with syntax and options for each type."
weight = 20
tags = ["syft", "sbom"]
url = "docs/user-guides/sbom/sources"
+++

Syft can generate an SBOM from a variety of sources including container images, directories, files, and archives. In most cases, you can simply point Syft at what you want to analyze and it will automatically detect the source type.

Catalog a container image from your local daemon or a remote registry:

```bash
syft alpine:latest
```

Catalog a directory (useful for analyzing source code or installed applications):

```bash
syft /path/to/project
```

Catalog a container image archive:

```bash
syft image.tar
```

Catalog a Singularity Image Format (SIF) container:

```bash
syft container.sif
```

To explicitly specify the source behavior, use the `--from` flag. Allowable options are:

- `docker`: use images from the Docker daemon
- `podman`: use images from the Podman daemon
- `containerd`: use images from the Containerd daemon
- `docker-archive`: use a tarball from disk for archives created from `docker save`
- `oci-archive`: use a tarball from disk for [OCI archives](https://specs.opencontainers.org/image-spec/image-layout/?v=v1.0.1) (from Skopeo or otherwise)
- `oci-dir`: read directly from a path on disk for [OCI layout directories](https://specs.opencontainers.org/image-spec/image-layout/?v=v1.0.1) (from Skopeo or otherwise)
- `singularity`: read directly from a [Singularity Image Format (SIF)](https://github.com/sylabs/sif) container file on disk
- `dir`: read directly from a path on disk (any directory)
- `file`: read directly from a path on disk (any single file)
- `registry`: pull image directly from a registry (no container runtime required)

## Source-Specific Behaviors

### Container Image References

When working with container images, Syft applies the following defaults and behaviors:

- **Registry**: If no registry is specified in the image reference (e.g. `alpine:latest` instead of `docker.io/alpine:latest`), Syft assumes `docker.io`
- **Platform**: For unspecific image references (tags) or multi-arch images pointing to a manifest index, Syft analyzes the `linux/amd64` manifest by default. Use the `--platform` flag to target a different platform.

When you provide an image reference without specifying a source type (no `--from` flag), Syft attempts to resolve the image using the following sources in order:

1. Docker daemon
2. Podman daemon
3. Containerd daemon
4. Direct registry access

For example, when you run `syft alpine:latest`, Syft will first check your local Docker daemon for the image. If Docker isn't available, it tries Podman, then Containerd, and finally attempts to pull directly from the registry.

You can override this default behavior with the `default-image-pull-source` configuration option to always prefer a specific source. See [Configuration](/docs/user-guides/sbom/configuration) for more details.

### Filesystems

Syft works best (fastest) when cataloging a pre-indexed filesystem. The first step for almost any input is to index the filesystem to enable the efficient search for packages and other artifacts.

#### Directories

When you point Syft at a directory (especially system directories like `/`), it automatically skips certain filesystem types to improve scan performance and avoid indexing areas that don't contain installed software packages.

**Filesystems always skipped:**

- `proc` / `procfs` - Virtual filesystem for process information
- `sysfs` - Virtual filesystem for kernel and device information
- `devfs` / `devtmpfs` / `udev` - Device filesystems

**Filesystems conditionally skipped:**

`tmpfs` filesystems are only skipped when mounted at these specific locations:

- `/dev` - Device files
- `/sys` - System information
- `/run` and `/var/run` - Runtime data and process IDs
- `/var/lock` - Lock files

These paths are excluded because they contain virtual or temporary runtime data rather than installed software packages. Skipping them significantly improves scan performance and enables you to catalog entire system root directories without getting stuck scanning thousands of irrelevant entries.

Syft identifies these filesystems by reading your system's mount table (`/proc/self/mountinfo` on Linux). When a directory matches one of these criteria, the entire directory tree under that mount point is skipped.

**File types excluded:**

These file types are never indexed during directory scans:

- Character devices
- Block devices
- Sockets
- FIFOs (named pipes)
- Irregular files

Regular files, directories, and symbolic links are always processed.


#### Archive Detection

Syft automatically detects and unpacks common archive formats, then catalogs their contents. If an archive is a container image archive (from `docker save` or `skopeo copy`), Syft treats it as a container image.

**Supported archive formats:**

Standard archives:
- `.zip`
- `.tar` (uncompressed)
- `.rar` (read-only extraction)

Compressed tar variants:
- `.tar.gz` / `.tgz`
- `.tar.bz2` / `.tbz2`
- `.tar.br` / `.tbr` (brotli)
- `.tar.lz4` / `.tlz4`
- `.tar.sz` / `.tsz` (snappy)
- `.tar.xz` / `.txz`
- `.tar.zst` / `.tzst` (zstandard)

Standalone compression formats (extracted if containing tar):
- `.gz` (gzip)
- `.bz2` (bzip2)
- `.br` (brotli)
- `.lz4`
- `.sz` (snappy)
- `.xz`
- `.zst` / `.zstd` (zstandard)

#### OCI Archives and Layouts

Syft automatically detects OCI archive and directory structures (including OCI layouts and SIF files) and catalogs them accordingly.

OCI archives and layouts are particularly useful for CI/CD pipelines, as they allow you to catalog images, scan for vulnerabilities, or perform other checks without publishing to a registry. This provides a powerful pattern for build-time gating.

**Create OCI sources without a registry:**

OCI archive from an image:
```bash
skopeo copy docker://alpine@sha256:eafc1edb577d2e9b458664a15f23ea1c370214193226069eb22921169fc7e43f oci-archive:alpine.tar
```

OCI layout directory from an image:
```bash
skopeo copy docker://alpine@sha256:eafc1edb577d2e9b458664a15f23ea1c370214193226069eb22921169fc7e43f oci:alpine 
```

Container image archive from an image:
```bash
docker save -o alpine.tar alpine:latest
```

## Container Daemon Configuration

### Image Availability and Authentication

When using container daemon sources (Docker, Podman, or Containerd):

- **Missing images**: If an image doesn't exist locally in the daemon, Syft attempts to pull it from the registry
- **Private images**: You must be logged in to the registry via the daemon (e.g., `docker login`) or have credentials configured for direct registry access. See [Authentication](/docs/user-guides/sbom/authentication) for more details.

### Environment Variables

Syft respects the following environment variables for each container runtime:

| Source | Environment Variables | Description |
|--------|----------------------|-------------|
| **Docker** | `DOCKER_HOST` | Docker daemon socket/host address (supports `ssh://` for remote connections) |
| | `DOCKER_TLS_VERIFY` | Enable TLS verification (auto-sets `DOCKER_CERT_PATH` if not set) |
| | `DOCKER_CERT_PATH` | Path to TLS certificates (defaults to `~/.docker` if `DOCKER_TLS_VERIFY` is set) |
| | `DOCKER_CONFIG` | Override default Docker config directory |
| **Podman** | `CONTAINER_HOST` | Podman socket/host address (e.g., `unix:///run/podman/podman.sock` or `ssh://user@host/path/to/socket`) |
| | `CONTAINER_SSHKEY` | SSH identity file path for remote Podman connections |
| | `CONTAINER_PASSPHRASE` | Passphrase for the SSH key |
| **Containerd** | `CONTAINERD_ADDRESS` | Containerd socket address (overrides default `/run/containerd/containerd.sock`) |
| | `CONTAINERD_NAMESPACE` | Containerd namespace (defaults to `default`) |

### Podman Daemon Requirements

Unlike Docker Desktop, which typically auto-starts, Podman requires explicitly starting the service:

**Rootless mode:**
```bash
podman system service --time=0
```
Socket location: `$XDG_RUNTIME_DIR/podman/podman.sock`

**Rootful mode:**
Socket location: `/run/podman/podman.sock` (typically requires root access)

**Connection methods:**

Syft attempts to connect to Podman using the following methods in order:

1. **Unix Socket** (primary)
   - Checks `CONTAINER_HOST` environment variable first
   - Falls back to Podman config files
   - Finally tries default socket locations

2. **SSH** (fallback)
   - Configured via `CONTAINER_HOST`, `CONTAINER_SSHKEY`, and `CONTAINER_PASSPHRASE` environment variables
   - Used for remote Podman instances

## Direct Registry Access

The `registry` source bypasses container runtimes entirely and pulls images directly from the registry.

**Credential resolution:**

- Syft first attempts to use default Docker credentials from `~/.docker/config.json` if they exist
- If default credentials are not available, you can provide credentials via environment variables. See [Authentication](/docs/user-guides/sbom/authentication) for more details.

