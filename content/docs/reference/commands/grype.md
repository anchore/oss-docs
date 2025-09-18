+++
title = "Grype Command Line Reference"
linkTitle = "Grype CLI"
weight = 20
tags = ['grype']
categories = ['reference']
url = "docs/reference/commands/grype"
+++

### `grype version`

```
Application:         grype
Version:             0.91.2
BuildDate:           2025-04-25T17:20:02Z
GitCommit:           7e6ba817350bdb922f35e4437aa01869cf0a8be0
GitDescription:      v0.91.2
Platform:            darwin/arm64
GoVersion:           go1.24.2
Compiler:            gc
Syft Version:        v1.23.1
Supported DB Schema: 6
```

### `grype help`

```
A vulnerability scanner for container images, filesystems, and SBOMs.

Supports the following image sources:
    grype yourrepo/yourimage:tag             defaults to using images from a Docker daemon
    grype path/to/yourproject                a Docker tar, OCI tar, OCI directory, SIF container, or generic filesystem directory

You can also explicitly specify the scheme to use:
    grype podman:yourrepo/yourimage:tag          explicitly use the Podman daemon
    grype docker:yourrepo/yourimage:tag          explicitly use the Docker daemon
    grype docker-archive:path/to/yourimage.tar   use a tarball from disk for archives created from "docker save"
    grype oci-archive:path/to/yourimage.tar      use a tarball from disk for OCI archives (from Podman or otherwise)
    grype oci-dir:path/to/yourimage              read directly from a path on disk for OCI layout directories (from Skopeo or otherwise)
    grype singularity:path/to/yourimage.sif      read directly from a Singularity Image Format (SIF) container on disk
    grype dir:path/to/yourproject                read directly from a path on disk (any directory)
    grype file:path/to/yourfile                  read directly from a file on disk
    grype sbom:path/to/syft.json                 read Syft JSON from path on disk
    grype registry:yourrepo/yourimage:tag        pull image directly from a registry (no container runtime required)
    grype purl:path/to/purl/file                 read a newline separated file of package URLs from a path on disk
    grype PURL                                   read a single package PURL directly (e.g. pkg:apk/openssl@3.2.1?distro=alpine-3.20.3)

You can also pipe in Syft JSON directly:
        syft yourimage:tag -o json | grype

Usage:
  grype [IMAGE] [flags]
  grype [command]

Available Commands:
  completion  Generate a shell completion for Grype (listing local docker images)
  config      show the grype configuration
  db          vulnerability database operations
  explain     Ask grype to explain a set of findings
  help        Help about any command
  version     show version information

Flags:
      --add-cpes-if-none       generate CPEs for packages with no CPE data
      --by-cve                 orient results by CVE instead of the original vulnerability ID when possible
  -c, --config stringArray     grype configuration file(s) to use
      --distro string          distro to match against in the format: <distro>:<version>
      --exclude stringArray    exclude paths from being scanned using a glob expression
  -f, --fail-on string         set the return code to 1 if a vulnerability is found with a severity >= the given severity, options=[negligible low medium high critical]
      --file string            file to write the default report output to (default is STDOUT)
  -h, --help                   help for grype
      --ignore-states string   ignore matches for vulnerabilities with specified comma separated fix states, options=[fixed not-fixed unknown wont-fix]
      --name string            set the name of the target being analyzed
      --only-fixed             ignore matches for vulnerabilities that are not fixed
      --only-notfixed          ignore matches for vulnerabilities that are fixed
  -o, --output stringArray     report output formatter, formats=[json table cyclonedx cyclonedx-json sarif template], deprecated formats=[embedded-cyclonedx-vex-json embedded-cyclonedx-vex-xml]
      --platform string        an optional platform specifier for container image sources (e.g. 'linux/arm64', 'linux/arm64/v8', 'arm64', 'linux')
      --profile stringArray    configuration profiles to use
  -q, --quiet                  suppress all logging output
  -s, --scope string           selection of layers to analyze, options=[squashed all-layers] (default "squashed")
      --show-suppressed        show suppressed/ignored vulnerabilities in the output (only supported with table output format)
  -t, --template string        specify the path to a Go template file (requires 'template' output to be selected)
  -v, --verbose count          increase verbosity (-v = info, -vv = debug)
      --version                version for grype
      --vex stringArray        a list of VEX documents to consider when producing scanning results

Use "grype [command] --help" for more information about a command.
```

### `grype db update`

```
 ✔ Vulnerability DB                [updated]
Vulnerability database updated to latest version!
```
