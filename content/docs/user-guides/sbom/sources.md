+++
title = "Supported Sources"
description = "Explore the different sources Syft can analyze including container images, OCI registries, directories, files, and archives with syntax and options for each type."
weight = 20
tags = ["syft", "sbom"]
url = "docs/user-guides/sbom/sources"
+++

Syft can generate an SBOM from a variety of sources including images, files, directories, and archives. Syft will attempt to
determine the type of source based on provided input.:

Catalog a container image archive (from the result of `docker image save ...`, `podman save ...`, or `skopeo copy` commands):

```
syft path/to/image.tar
```

Catalog a Singularity Image Format (SIF) container:

```
syft path/to/image.sif
```

Catalog a directory:

```
syft path/to/dir
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

If a source is not provided and Syft identifies the input as a potential image reference, Syft will attempt to resolve it using the Docker, Podman, and Containerd daemons followed by direct registry access, in that order.

This default behavior can be overridden with the `default-image-pull-source` configuration option (See [Configuration](/docs/user-guides/sbom/configuration) for more details).


## caveats, assumptions, and behaviors

### container image references
- if no registry is provided in the image reference, we will assume docker.io
- for image references that are unspecific (a tag) or point to an index of multiple manifests (e.g. multi-arch images), we will analyze the linux:amd64 manifest by default. This can be changed / overridden with the `--platform` flag.

### files
- if the archive is a container image archive (e.g. from `docker save` or `skopeo copy`), we will treat it as a container image (see the cataloger selection)

#### archives
- we will attempt to unpack common archive formats (tar, zip, gzip, etc) and then catalog the contents (TODO enumerate all supported formats)


Supported archive formats:
- .zip
- .tar (uncompressed)
- .rar (read-only extraction)

Compressed tar variants:
- .tar.gz / .tgz
- .tar.bz2 / .tbz2
- .tar.br / .tbr (brotli)
- .tar.lz4 / .tlz4
- .tar.sz / .tsz (snappy)
- .tar.xz / .txz
- .tar.zst / .tzst (zstandard)

Standalone compression formats (extracted if containing tar):
- .gz (gzip)
- .bz2 (bzip2)
- .br (brotli)
- .lz4
- .sz (snappy)
- .xz
- .zst / .zstd (zstandard)


#### local container archive and directory sources
- we will attempt to detect the type of archive or directory structure (e.g. OCI layout, SIF, etc) and catalog accordingly
- OCI archives and layouts are useful in the sense that you can craete them at build time without pushing to a registry, allowing to catalog images / vuln scan them / any other check without requiring publishing. This is a powerful pattern for gating in CI.
- you can create an OCI archive from an image with: `skopeo copy docker://alpine:latest oci-archive:alpine_latest:latest`
- you can create an OCI layout directory from an image with: `skopeo copy docker://alpine:latest oci:alpine_oci:latest`
- you can create a container image archive from an image with: `docker save -o alpine_latest.tar alpine:latest`

### container daemons

- if the image does not exist locally in the daemon, we will attempt to pull it from the registry
- if the image is private, you must be logged in to the registry via the daemon (e.g. `docker login ...`) or have credentials configured for direct registry access (See [Authentication](/docs/user-guides/sbom/authentication) for more details).

- In terms of environment variables, syft respects the following variables for each container runtime:
  Docker 

   - DOCKER_HOST - Docker daemon socket/host address (supports ssh:// for remote connections)
   - DOCKER_TLS_VERIFY - Enable TLS verification (auto-sets DOCKER_CERT_PATH if not set)
   - DOCKER_CERT_PATH - Path to TLS certificates (defaults to ~/.docker if DOCKER_TLS_VERIFY is set)
   - DOCKER_CONFIG - Override default Docker config directory (mentioned at daemon_provider.go:191, used by Docker's
     config.Load())

  Podman

   - CONTAINER_HOST - Podman socket/host address (e.g., unix:///run/podman/podman.sock or ssh://user@host/path/to/socket)
   - CONTAINER_SSHKEY - SSH identity file path for remote Podman connections
   - CONTAINER_PASSPHRASE - Passphrase for the SSH key

  Containerd

   - CONTAINERD_ADDRESS - Containerd socket address (overrides default /run/containerd/containerd.sock)
   - CONTAINERD_NAMESPACE - Containerd namespace (defaults to default)

  Summary by Source

  | Source     | Environment Variables                                           |
    |------------|-----------------------------------------------------------------|
  | Docker     | DOCKER_HOST, DOCKER_TLS_VERIFY, DOCKER_CERT_PATH, DOCKER_CONFIG |
  | Podman     | CONTAINER_HOST, CONTAINER_SSHKEY, CONTAINER_PASSPHRASE          |
  | Containerd | CONTAINERD_ADDRESS, CONTAINERD_NAMESPACE                        |

#### podman

Daemon/Service Requirements

Yes, a Podman service/daemon needs to be running - unlike Docker Desktop which typically auto-starts, Podman users
must explicitly start the service:
- Rootless: podman system service --time=0 (runs as user, socket at $XDG_RUNTIME_DIR/podman/podman.sock)
- Rootful: Socket at /run/podman/podman.sock (typically root access required)

Connection Methods

The library tries two approaches (in order):

1. Unix Socket (primary) 
   - Checks CONTAINER_HOST env var first
   - Falls back to Podman config files
   - Finally tries default socket locations
2. SSH (fallback) 
   - Configured via CONTAINER_HOST, CONTAINER_SSHKEY, CONTAINER_PASSPHRASE env vars
   - For remote Podman instances



### direct registry access

- this bypasses any container runtime and pulls the image directly from the registry
- we attempt to use default docker credentials (e.g. `~/.docker/config.json`) if they exist
- otherwise, you can provide credentials via environment variables (See [Authentication](/docs/user-guides/sbom/authentication) for more details).
