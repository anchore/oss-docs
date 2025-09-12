+++
title = "Getting Started"
description = "SBOM Generation Getting Started"
weight = 10
tags = ["syft", "sbom"]
url = "docs/userguides/sbom/getstarted"
+++

### Introduction

Syft is our CLI tool for generating a Software Bill of Materials (SBOM) from container images and filesystems.

### Install the latest Syft release

Syft is provided as a single compiled executable. Issue the command for your platform to download the latest release of Syft. The full list of official and community maintained packages can be found on the [installation](/docs/installation/syft) page.

{{< tabpane lang="bash">}}
  {{% tab header="Platform:" disabled=true /%}}
  {{% tab header="Linux (and macOS)" %}}curl -sSfL https://get.anchore.io/syft | sudo sh -s -- -b /usr/local/bin{{% /tab %}}
  {{% tab header="macOS"%}}brew install syft{{% /tab %}}
  {{% tab header="Windows"%}}nuget install Anchore.Syft{{% /tab %}}
{{< /tabpane >}}

Once installed, ensure the `syft` binary is in the `PATH` for your system.

### Create an SBOM with Syft

Generate an SBOM for a container image:

```
syft <image>
```

### Display the contents of a public container image

Run `syft` with default options against a small container, which will be pulled from DockerHub. The output will be a simple human-readable table.

{{% alert title="Learn more" color="primary" %}}
Syft supports more than just containers, find out more about [Supported Sources](/docs/userguides/sbom/sources/)
{{% /alert %}}

```
syft alpine:latest
```

The output will look similar to the following table.

```
 ✔ Pulled image
 ✔ Loaded image alpine:latest
 ✔ Parsed image sha256:8d591b0b7dea080ea3be9e12ae563eebf9…
 ✔ Cataloged contents 058c92d86112aa6f641b01ed238a07a3885…
   ├── ✔ Packages                        [15 packages]
   ├── ✔ File metadata                   [82 locations]
   ├── ✔ File digests                    [82 files]
   └── ✔ Executables                     [17 executables]
NAME                    VERSION      TYPE
alpine-baselayout       3.6.8-r1     apk
alpine-baselayout-data  3.6.8-r1     apk
alpine-keys             2.5-r0       apk
alpine-release          3.21.3-r0    apk
apk-tools               2.14.6-r3    apk
busybox                 1.37.0-r12   apk
busybox-binsh           1.37.0-r12   apk
ca-certificates-bundle  20241121-r1  apk
libcrypto3              3.3.3-r0     apk
libssl3                 3.3.3-r0     apk
musl                    1.2.5-r9     apk
musl-utils              1.2.5-r9     apk
scanelf                 1.3.8-r1     apk
ssl_client              1.37.0-r12   apk
zlib                    1.3.1-r2     apk
```

### Create an SPDX formatted SBOM

The next command will display the human-readable table, *and* write an SBOM in an industry-standard format, SPDX.

```
syft alpine:latest -o table -o spdx-json=alpine_latest-spdx.json
```

The same table will be displayed, but there will also be an SBOM in the current directory.

{{% alert title="Learn more" color="primary" %}}
Syft supports multiple SBOM output formats, find out more about [Output Formats](/docs/userguides/sbom/formats/).
{{% /alert %}}

### Examine the SPDX file contents

The JSON output by Syft is long, but compressed down to one line. We can use `jq` to prettify it, and extract some package data.

{{% alert title="Note" color="primary" %}}
jq is an third-party command-line utility for manipulating JSON documents, find out more about jq on the <i class="fa-solid fa-arrow-up-right-from-square"></i> [jqlang](https://jqlang.org/) website.
{{% /alert %}}

```
jq '.packages[].name' < alpine_latest-spdx.json
```

The output will show a list of packages that Syft found in the container.

```text
"alpine-baselayout"
"alpine-baselayout-data"
"alpine-keys"
"alpine-release"
"apk-tools"
"busybox"
"busybox-binsh"
"ca-certificates-bundle"
"libcrypto3"
"libssl3"
"musl"
"musl-utils"
"scanelf"
"ssl_client"
"zlib"
"alpine"
```

The above output includes only software that is visible in the container (i.e., the squashed representation of the image). To include software from all image layers in the SBOM, regardless of its presence in the final image, provide `--scope all-layers`:

```
syft <image> --scope all-layers
```

{{% alert title="Next steps" color="primary" %}}
* Try running Syft against other containers, or an application directory on your workstation.
* Find out more about [Supported Sources](/docs/userguides/sbom/sources/) and [Output Formats](/docs/userguides/sbom/formats/).
* Learn about [Vulnerability Scanning](/docs/userguides/vuln/getstarted/) and [License Scaanning](/docs/userguides/license/getstarted/) your SBOMs.
{{% /alert %}}