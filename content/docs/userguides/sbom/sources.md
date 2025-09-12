+++
title = "Supported Sources"
description = "SBOM Generation Supported Sources"
weight = 20
tags = ["syft", "sbom"]
url = "docs/userguides/sbom/sources"
+++

## Supported sources

Syft can generate an SBOM from a variety of sources including images, files, directories, and archives. Syft will attempt to
determine the type of source based on provided input, for example:

```
# catalog a container image archive (from the result of `docker image save ...`, `podman save ...`, or `skopeo copy` commands)
syft path/to/image.tar

# catalog a Singularity Image Format (SIF) container
syft path/to/image.sif

# catalog a directory
syft path/to/dir
```

To explicitly specify the source behavior, use the `--from` flag. Allowable options are:

```
docker             use images from the Docker daemon
podman             use images from the Podman daemon
containerd         use images from the Containerd daemon
docker-archive     use a tarball from disk for archives created from "docker save"
oci-archive        use a tarball from disk for OCI archives (from Skopeo or otherwise)
oci-dir            read directly from a path on disk for OCI layout directories (from Skopeo or otherwise)
singularity        read directly from a Singularity Image Format (SIF) container on disk
dir                read directly from a path on disk (any directory)
file               read directly from a path on disk (any single file)
registry           pull image directly from a registry (no container runtime required)
```
If a source is not provided and Syft identifies the input as a potential image reference, Syft will attempt to resolve it using:
the Docker, Podman, and Containerd daemons followed by direct registry access, in that order.

<!-- TODO(alex): broken link locally -->
This default behavior can be overridden with the `default-image-pull-source` configuration option (See [Configuration](configuration) for more details).
