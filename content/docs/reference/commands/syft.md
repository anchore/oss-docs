+++
title = "Syft Command Line Reference"
linkTitle = "Syft CLI"
weight = 10
tags = ['syft']
categories = ['reference']
url = "docs/reference/commands/syft"
+++

### `syft version`

```
Application: syft
Version:    1.24.0
BuildDate:  2025-05-14T14:51:30Z
GitCommit:  3c7018a853ab7b311db9ff70e1cf3113b46d9c0c
GitDescription: v1.24.0
Platform:   darwin/arm64
GoVersion:  go1.24.3
Compiler:   gc
```

### `syft help`

```
Generate a packaged-based Software Bill Of Materials (SBOM) from container images and filesystems

Usage:
  syft [SOURCE] [flags]
  syft [command]

Examples:
  syft scan alpine:latest                                a summary of discovered packages
  syft scan alpine:latest -o json                        show all possible cataloging details
  syft scan alpine:latest -o cyclonedx                   show a CycloneDX formatted SBOM
  syft scan alpine:latest -o cyclonedx-json              show a CycloneDX JSON formatted SBOM
  syft scan alpine:latest -o spdx                        show a SPDX 2.3 Tag-Value formatted SBOM
  syft scan alpine:latest -o spdx@2.2                    show a SPDX 2.2 Tag-Value formatted SBOM
  syft scan alpine:latest -o spdx-json                   show a SPDX 2.3 JSON formatted SBOM
  syft scan alpine:latest -o spdx-json@2.2               show a SPDX 2.2 JSON formatted SBOM
  syft scan alpine:latest -vv                            show verbose debug information
  syft scan alpine:latest -o template -t my_format.tmpl  show a SBOM formatted according to given template file

  Supports the following image sources:
    syft scan yourrepo/yourimage:tag     defaults to using images from a Docker daemon. If Docker is not present, the image is pulled directly from the registry.
    syft scan path/to/a/file/or/dir      a Docker tar, OCI tar, OCI directory, SIF container, or generic filesystem directory

  You can also explicitly specify the scheme to use:
    syft scan docker:yourrepo/yourimage:tag            explicitly use the Docker daemon
    syft scan podman:yourrepo/yourimage:tag            explicitly use the Podman daemon
    syft scan registry:yourrepo/yourimage:tag          pull image directly from a registry (no container runtime required)
    syft scan docker-archive:path/to/yourimage.tar     use a tarball from disk for archives created from "docker save"
    syft scan oci-archive:path/to/yourimage.tar        use a tarball from disk for OCI archives (from Skopeo or otherwise)
    syft scan oci-dir:path/to/yourimage                read directly from a path on disk for OCI layout directories (from Skopeo or otherwise)
    syft scan singularity:path/to/yourimage.sif        read directly from a Singularity Image Format (SIF) container on disk
    syft scan dir:path/to/yourproject                  read directly from a path on disk (any directory)
    syft scan file:path/to/yourproject/file            read directly from a path on disk (any single file)


Available Commands:
  attest      Generate an SBOM as an attestation for the given [SOURCE] container image
  cataloger   Show available catalogers and configuration
  completion  Generate the autocompletion script for the specified shell
  config      show the syft configuration
  convert     Convert between SBOM formats
  help        Help about any command
  login       Log in to a registry
  scan        Generate an SBOM
  version     show version information

Flags:
      --base-path string                          base directory for scanning, no links will be followed above this directory, and all paths will be reported relative to this directory
  -c, --config stringArray                        syft configuration file(s) to use
      --enrich stringArray                        enable package data enrichment from local and online sources (options: all, golang, java, javascript)
      --exclude stringArray                       exclude paths from being scanned using a glob expression
      --file string                               file to write the default report output to (default is STDOUT) (DEPRECATED: use: --output FORMAT=PATH)
      --from stringArray                          specify the source behavior to use (e.g. docker, registry, oci-dir, ...)
  -h, --help                                      help for syft
  -o, --output stringArray                        report output format (<format>=<file> to output to a file), formats=[cyclonedx-json cyclonedx-xml github-json purls spdx-json spdx-tag-value syft-json syft-table syft-text template] (default [syft-table])
      --override-default-catalogers stringArray   set the base set of catalogers to use (defaults to 'image' or 'directory' depending on the scan source)
      --parallelism int                           number of cataloger workers to run in parallel
      --platform string                           an optional platform specifier for container image sources (e.g. 'linux/arm64', 'linux/arm64/v8', 'arm64', 'linux')
      --profile stringArray                       configuration profiles to use
  -q, --quiet                                     suppress all logging output
  -s, --scope string                              selection of layers to catalog, options=[squashed all-layers deep-squashed] (default "squashed")
      --select-catalogers stringArray             add, remove, and filter the catalogers to be used
      --source-name string                        set the name of the target being analyzed
      --source-version string                     set the version of the target being analyzed
  -t, --template string                           specify the path to a Go template file
  -v, --verbose count                             increase verbosity (-v = info, -vv = debug)
      --version                                   version for syft

Use "syft [command] --help" for more information about a command.
```

### `syft scan`

```
Generate a packaged-based Software Bill Of Materials (SBOM) from container images and filesystems

Usage:
  syft scan [SOURCE] [flags]

Examples:
  syft scan alpine:latest                                a summary of discovered packages
  syft scan alpine:latest -o json                        show all possible cataloging details
  syft scan alpine:latest -o cyclonedx                   show a CycloneDX formatted SBOM
  syft scan alpine:latest -o cyclonedx-json              show a CycloneDX JSON formatted SBOM
  syft scan alpine:latest -o spdx                        show a SPDX 2.3 Tag-Value formatted SBOM
  syft scan alpine:latest -o spdx@2.2                    show a SPDX 2.2 Tag-Value formatted SBOM
  syft scan alpine:latest -o spdx-json                   show a SPDX 2.3 JSON formatted SBOM
  syft scan alpine:latest -o spdx-json@2.2               show a SPDX 2.2 JSON formatted SBOM
  syft scan alpine:latest -vv                            show verbose debug information
  syft scan alpine:latest -o template -t my_format.tmpl  show a SBOM formatted according to given template file

  Supports the following image sources:
    syft scan yourrepo/yourimage:tag     defaults to using images from a Docker daemon. If Docker is not present, the image is pulled directly from the registry.
    syft scan path/to/a/file/or/dir      a Docker tar, OCI tar, OCI directory, SIF container, or generic filesystem directory

  You can also explicitly specify the scheme to use:
    syft scan docker:yourrepo/yourimage:tag            explicitly use the Docker daemon
    syft scan podman:yourrepo/yourimage:tag            explicitly use the Podman daemon
    syft scan registry:yourrepo/yourimage:tag          pull image directly from a registry (no container runtime required)
    syft scan docker-archive:path/to/yourimage.tar     use a tarball from disk for archives created from "docker save"
    syft scan oci-archive:path/to/yourimage.tar        use a tarball from disk for OCI archives (from Skopeo or otherwise)
    syft scan oci-dir:path/to/yourimage                read directly from a path on disk for OCI layout directories (from Skopeo or otherwise)
    syft scan singularity:path/to/yourimage.sif        read directly from a Singularity Image Format (SIF) container on disk
    syft scan dir:path/to/yourproject                  read directly from a path on disk (any directory)
    syft scan file:path/to/yourproject/file            read directly from a path on disk (any single file)


Flags:
      --base-path string                          base directory for scanning, no links will be followed above this directory, and all paths will be reported relative to this directory
      --enrich stringArray                        enable package data enrichment from local and online sources (options: all, golang, java, javascript)
      --exclude stringArray                       exclude paths from being scanned using a glob expression
      --file string                               file to write the default report output to (default is STDOUT) (DEPRECATED: use: --output FORMAT=PATH)
      --from stringArray                          specify the source behavior to use (e.g. docker, registry, oci-dir, ...)
  -h, --help                                      help for scan
  -o, --output stringArray                        report output format (<format>=<file> to output to a file), formats=[cyclonedx-json cyclonedx-xml github-json purls spdx-json spdx-tag-value syft-json syft-table syft-text template] (default [syft-table])
      --override-default-catalogers stringArray   set the base set of catalogers to use (defaults to 'image' or 'directory' depending on the scan source)
      --parallelism int                           number of cataloger workers to run in parallel
      --platform string                           an optional platform specifier for container image sources (e.g. 'linux/arm64', 'linux/arm64/v8', 'arm64', 'linux')
  -s, --scope string                              selection of layers to catalog, options=[squashed all-layers deep-squashed] (default "squashed")
      --select-catalogers stringArray             add, remove, and filter the catalogers to be used
      --source-name string                        set the name of the target being analyzed
      --source-version string                     set the version of the target being analyzed
  -t, --template string                           specify the path to a Go template file

Global Flags:
  -c, --config stringArray    syft configuration file(s) to use
      --profile stringArray   configuration profiles to use
  -q, --quiet                 suppress all logging output
  -v, --verbose count         increase verbosity (-v = info, -vv = debug)
```

### `syft convert`

```
[Experimental] Convert SBOM files to, and from, SPDX, CycloneDX and Syft's format. For more info about data loss between formats see https://github.com/anchore/syft/wiki/format-conversion

Usage:
  syft convert [SOURCE-SBOM] -o [FORMAT] [flags]

Examples:
  syft convert img.syft.json -o spdx-json                      convert a syft SBOM to spdx-json, output goes to stdout
  syft convert img.syft.json -o cyclonedx-json=img.cdx.json    convert a syft SBOM to CycloneDX, output is written to the file "img.cdx.json"
  syft convert - -o spdx-json                                  convert an SBOM from STDIN to spdx-json


Flags:
      --file string          file to write the default report output to (default is STDOUT) (DEPRECATED: use: --output FORMAT=PATH)
  -h, --help                 help for convert
  -o, --output stringArray   report output format (<format>=<file> to output to a file), formats=[cyclonedx-json cyclonedx-xml github-json purls spdx-json spdx-tag-value syft-json syft-table syft-text template] (default [syft-table])
  -t, --template string      specify the path to a Go template file

Global Flags:
  -c, --config stringArray    syft configuration file(s) to use
      --profile stringArray   configuration profiles to use
  -q, --quiet                 suppress all logging output
  -v, --verbose count         increase verbosity (-v = info, -vv = debug)
```
