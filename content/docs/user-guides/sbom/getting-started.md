+++
title = "Getting Started"
description = "Use Syft to generate your first SBOM from container images, directories, or archives."
weight = 10
tags = ["syft", "sbom"]
url = "docs/user-guides/sbom/getting-started"
+++

Syft is a CLI tool for generating a Software Bill of Materials (SBOM) from container images and filesystems.

## Installation

Syft is provided as a single compiled executable. Run the command for your platform to download the latest release. The full list of official and community maintained packages can be found on the [installation](/docs/installation/syft) page.

{{< tabpane lang="bash">}}
{{% tab header="Platform:" disabled=true /%}}
{{< tab header="Linux (and macOS)" >}}
curl -sSfL <https://get.anchore.io/syft> | sudo sh -s -- -b /usr/local/bin
{{< /tab >}}
{{% tab header="macOS"%}}brew install syft{{% /tab %}}
{{% tab header="Windows"%}}nuget install Anchore.Syft{{% /tab %}}
{{< /tabpane >}}

See the [installation guide](/docs/installation/syft) for more options including package managers and manual installation.

## Display the contents of a public container image

Run `syft` against a small container image, which will be pulled from DockerHub. The output will be a simple human-readable table.

```
syft alpine:latest
```

The output will look similar to the following table.

```
NAME                    VERSION      TYPE
alpine-baselayout       3.6.8-r1     apk
alpine-baselayout-data  3.6.8-r1     apk
alpine-keys             2.5-r0       apk
alpine-release          3.21.3-r0    apk
apk-tools               2.14.6-r3    apk
busybox                 1.37.0-r12   apk
busybox-binsh           1.37.0-r12   apk
...
```

{{< alert title="Learn more" color="primary" >}}
Syft supports more than just containers. Learn more about [Supported Sources](/docs/user-guides/sbom/sources/)
{{< /alert >}}

## Create an industry-standard SBOM

This command will display the human-readable table _and_ write SBOMs in both SPDX and CycloneDX formats, the two primary industry standards.

```bash
syft alpine:latest -o table -o spdx-json=alpine.spdx.json -o cyclonedx-json=alpine.cdx.json
```

The same table will be displayed, and two SBOM files will be created in the current directory.

{{< alert title="Learn more" color="primary" >}}
Syft supports multiple SBOM output formats, find out more about [Output Formats](/docs/user-guides/sbom/formats/).
{{< /alert >}}

### Examine the SBOM file contents

We can use [`jq`](https://jqlang.org/) to extract specific package data from the SBOM files (note: by default Syft outputs JSON on a single line,
but you can enable pretty-printing with the `SYFT_FORMAT_PRETTY=true` environment variable).
Both formats structure package information differently:

**SPDX format:**

```bash
jq '.packages[].name' alpine.spdx.json
```

**CycloneDX format:**

```bash
jq '.components[].name' alpine.cdx.json
```

Both commands show the packages that Syft found in the container image:

```text
"alpine-baselayout"
"alpine-baselayout-data"
"alpine-keys"
"alpine-release"
"apk-tools"
"busybox"
"busybox-binsh"
...
```

By default, Syft shows only software visible in the final container image (the "squashed" representation).
To include software from all image layers, regardless of its presence in the final image, use `--scope all-layers`:

```bash
syft <image> --scope all-layers
```

## FAQ

**Does Syft need internet access?**

Only for downloading container images. By default, scanning works offline.

**What about private container registries?**

Syft supports authentication for private registries. See [Private Registries](/docs/user-guides/private-registries/).

**Can I use Syft in CI/CD pipelines?**

Absolutely! Syft is designed for automation. Generate SBOMs during builds and scan them for vulnerabilities.

**What data does Syft send externally?**

Nothing. Syft runs entirely locally and doesn't send any data to external services.

## Next steps

Now that you've generated your first SBOM, here's what you can do next:

- **Scan for vulnerabilities**: Use [Grype](/docs/user-guides/vulnerability/getting-started/) to find security issues in your SBOMs
- **Check licenses**: Learn about [License Scanning](/docs/user-guides/license/getting-started/) to understand dependency licenses
- **Customize output**: Explore different [Output Formats](/docs/user-guides/sbom/formats/) for various tools and workflows
- **Scan different sources**: Discover all [Supported Sources](/docs/user-guides/sbom/sources/) Syft can analyze
- **Query SBOM data**: Master [Working with Syft JSON](/docs/user-guides/sbom/syft-json/) for advanced data extraction
