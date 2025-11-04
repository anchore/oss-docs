+++
title = "Supported Sources"
description = "Explore the different sources Syft can analyze including container images, OCI registries, directories, files, and archives."
weight = 20
tags = ["syft", "sbom"]
url = "docs/guides/sbom/sources"
+++

{{< alert title="TL;DR" color="primary" >}}

- Syft automatically detects source type, simply pass it as an argument: `syft <target>`
- Supports **container images** (Docker/Podman/Containerd/registries), **directories**, **files**, and **archives**
- Use `--from <type>` to explicitly specify source (e.g., `--from registry` to bypass local daemons)

{{< /alert >}}

Syft can generate an SBOM from a variety of sources including container images, directories, files, and archives.
In most cases, you can simply point Syft at what you want to analyze and it will automatically detect and catalog it correctly.

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

To explicitly specify the source, use the `--from` flag:

| `--from ARG`     | Description                                                                                                                                                   |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docker`         | Use images from the Docker daemon                                                                                                                             |
| `podman`         | Use images from the Podman daemon                                                                                                                             |
| `containerd`     | Use images from the Containerd daemon                                                                                                                         |
| `docker-archive` | Use a tarball from disk for archives created from `docker save`                                                                                               |
| `oci-archive`    | Use a tarball from disk for [OCI archives](https://specs.opencontainers.org/image-spec/image-layout/?v=v1.0.1) (from Skopeo or otherwise)                     |
| `oci-dir`        | Read directly from a path on disk for [OCI layout directories](https://specs.opencontainers.org/image-spec/image-layout/?v=v1.0.1) (from Skopeo or otherwise) |
| `singularity`    | Read directly from a [Singularity Image Format (SIF)](https://github.com/sylabs/sif) container file on disk                                                   |
| `dir`            | Read directly from a path on disk (any directory)                                                                                                             |
| `file`           | Read directly from a path on disk (any single file)                                                                                                           |
| `registry`       | Pull image directly from a registry (bypass any container runtimes)                                                                                           |

## Source-Specific Behaviors

### Container Image Sources

When working with container images, Syft applies the following defaults and behaviors:

- **Registry**: If no registry is specified in the image reference (e.g. `alpine:latest` instead of `docker.io/alpine:latest`), Syft assumes `docker.io`
- **Platform**: For unspecific image references (tags) or multi-arch images pointing to an index (not a manifest), Syft analyzes the `linux/amd64` manifest by default.
  Use the `--platform` flag to target a different platform.

When you provide an image reference without specifying a source type (i.e. no `--from` flag), Syft attempts to resolve the image using the following sources in order:

1. Docker daemon
2. Podman daemon
3. Containerd daemon
4. Direct registry access

For example, when you run `syft alpine:latest`, Syft will first check your local Docker daemon for the image.
If Docker isn't available, it tries Podman, then Containerd, and finally attempts to pull directly from the registry.

You can override this default behavior with the `default-image-pull-source` configuration option to always prefer a specific source.
See [Configuration](/docs/reference/syft/configuration) for more details.

### Directory Sources

When you provide a directory path as the source, Syft recursively scans the directory tree to catalog installed software packages and files.

When you point Syft at a directory (especially system directories like `/`), it automatically skips certain filesystem types to improve
scan performance and avoid indexing areas that don't contain installed software packages.

#### Filesystems always skipped

- `proc` / `procfs` - Virtual filesystem for process information
- `sysfs` - Virtual filesystem for kernel and device information
- `devfs` / `devtmpfs` / `udev` - Device filesystems

#### Filesystems conditionally skipped

`tmpfs` filesystems are only skipped when mounted at these specific locations:

- `/dev` - Device files
- `/sys` - System information
- `/run` and `/var/run` - Runtime data and process IDs
- `/var/lock` - Lock files

These paths are excluded because they contain virtual or temporary runtime data rather than installed software packages.
Skipping them significantly improves scan performance and enables you to catalog entire system root directories without getting stuck scanning thousands of irrelevant entries.

Syft identifies these filesystems by reading your system's mount table (`/proc/self/mountinfo` on Linux).
When a directory matches one of these criteria, the entire directory tree under that mount point is skipped.

#### File types excluded

These file types are never indexed during directory scans:

- Character devices
- Block devices
- Sockets
- FIFOs (named pipes)
- Irregular files

Regular files, directories, and symbolic links are always processed.

### Archive Sources

Syft automatically detects and unpacks common archive formats, then catalogs their contents.
If an archive is a container image archive (from `docker save` or `skopeo copy`), Syft treats it as a container image.

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

### OCI Archives and Layout Sources

Syft automatically detects OCI archive and directory structures (including OCI layouts and SIF files) and catalogs them accordingly.

OCI archives and layouts are particularly useful for CI/CD pipelines, as they allow you to catalog images, scan for vulnerabilities, or perform other checks without publishing to a registry. This provides a powerful pattern for build-time gating.

#### Create OCI sources without a registry

OCI archive from an image:

```bash
skopeo copy \
  docker://alpine@sha256:eafc1edb577d2e9b458664a15f23ea1c370214193226069eb22921169fc7e43f \
  oci-archive:alpine.tar
```

OCI layout directory from an image:

```bash
skopeo copy \
  docker://alpine@sha256:eafc1edb577d2e9b458664a15f23ea1c370214193226069eb22921169fc7e43f \
  oci:alpine
```

Container image archive from an image:

```bash
docker save -o alpine.tar alpine:latest
```

## Container Runtime Configuration

### Image Availability and Authentication

When using container runtime sources (Docker, Podman, or Containerd):

- **Missing images**: If an image doesn't exist locally in the container runtime, Syft attempts to pull it from the registry via the runtime
- **Private images**: You must be logged in to the registry via the container runtime (e.g., `docker login`) or have credentials configured for direct registry access. See [Authentication with Private Registries](/docs/guides/private-registries) for more details.

### Environment Variables

Syft respects the following environment variables for each container runtime:

| Source         | Environment Variables  | Description                                                                                             |
| -------------- | ---------------------- | ------------------------------------------------------------------------------------------------------- |
| **Docker**     | `DOCKER_HOST`          | Docker daemon socket/host address (supports `ssh://` for remote connections)                            |
|                | `DOCKER_TLS_VERIFY`    | Enable TLS verification (auto-sets `DOCKER_CERT_PATH` if not set)                                       |
|                | `DOCKER_CERT_PATH`     | Path to TLS certificates (defaults to `~/.docker` if `DOCKER_TLS_VERIFY` is set)                        |
|                | `DOCKER_CONFIG`        | Override default Docker config directory                                                                |
| **Podman**     | `CONTAINER_HOST`       | Podman socket/host address (e.g., `unix:///run/podman/podman.sock` or `ssh://user@host/path/to/socket`) |
|                | `CONTAINER_SSHKEY`     | SSH identity file path for remote Podman connections                                                    |
|                | `CONTAINER_PASSPHRASE` | Passphrase for the SSH key                                                                              |
| **Containerd** | `CONTAINERD_ADDRESS`   | Containerd socket address (overrides default `/run/containerd/containerd.sock`)                         |
|                | `CONTAINERD_NAMESPACE` | Containerd namespace (defaults to `default`)                                                            |

### Podman Daemon Requirements

Unlike Docker Desktop, which typically auto-starts, Podman requires explicitly starting the service.

Syft attempts to connect to Podman using the following methods in order:

1. **Unix Socket** (primary)
   - Checks `CONTAINER_HOST` environment variable first
   - Falls back to Podman config files
   - Finally tries default socket locations ($XDG_RUNTIME_DIR/podman/podman.sock`and`/run/podman/podman.sock`)

2. **SSH** (fallback)
   - Configured via `CONTAINER_HOST`, `CONTAINER_SSHKEY`, and `CONTAINER_PASSPHRASE` environment variables
   - Used for remote Podman instances

## Direct Registry Access

The `registry` source bypasses container runtimes entirely and pulls images directly from the registry.

Credentials are resolved in the following order:

- Syft first attempts to use default Docker credentials from `~/.docker/config.json` if they exist
- If default credentials are not available, you can provide credentials via environment variables. See [Authentication with Private Registries](/docs/guides/private-registries) for more details.

## Troubleshooting

### Image not found in local daemon

If Syft reports an image doesn't exist but you know it's available:

- **Check which daemon has the image**: Run `docker images`, `podman images`, or `nerdctl images` to see where the image exists
- **Specify the source explicitly**: Use `--from docker`, `--from podman`, or `--from containerd` to target the correct daemon
- **Pull from registry**: Use `--from registry` to bypass local daemons and pull directly

### Authentication failures with private registries

If you get authentication errors when scanning private images:

- **For daemon sources**: Ensure you're logged in via the daemon (e.g., `docker login registry.example.com`)
- **For registry source**: Configure credentials in `~/.docker/config.json` or use environment variables (see [Private Registries](/docs/guides/private-registries))
- **Verify credentials**: Check that your credentials haven't expired and have appropriate permissions

### Podman connection issues

If Syft can't connect to Podman:

- **Start the service**: Run `podman system service` to start the Podman socket
- **Check socket location**: Verify the socket exists at `$XDG_RUNTIME_DIR/podman/podman.sock` or `/run/podman/podman.sock`
- **Use environment variable**: Set `CONTAINER_HOST` to point to your Podman socket location

### Slow directory scans

If scanning a directory takes too long:

- **Exclude unnecessary paths**: Use file selection options to skip build artifacts, caches, or virtual environments (see [File Selection](/docs/guides/sbom/file-selection))
- **Avoid system directories**: Scanning `/` includes all mounted filesystems; consider scanning specific application directories instead
- **Check mount points**: Ensure you're not accidentally scanning network mounts or remote filesystems

## Next steps

{{< alert title="Continue the guide" color="success" url="/docs/guides/sbom/formats/" >}}
**Next**: Learn about [Output Formats](/docs/guides/sbom/formats/) to understand how to generate SBOMs in different standard formats like SPDX and CycloneDX.
{{< /alert >}}

Additional resources:

- **Authenticate with registries**: Set up [Private Registry Authentication](/docs/guides/private-registries) for scanning private images
- **Control what gets scanned**: Use [File Selection](/docs/guides/sbom/file-selection) to include or exclude specific files
- **Configure defaults**: See [Configuration](/docs/reference/syft/configuration) for setting default source preferences
