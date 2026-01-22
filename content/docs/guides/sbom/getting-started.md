+++
title = "Getting Started"
description = "Use Syft to generate your first SBOM from container images, directories, or archives."
weight = 10
tags = ["syft", "sbom"]
+++

## What is an SBOM?

A **Software Bill of Materials** (SBOM) is a **detailed list of all libraries and components** that make up software.

- **For developers**, it's crucial for tracking dependencies, identifying vulnerabilities, and ensuring license compliance.

- **For organizations**, it provides transparency into the software supply chain to assess security risks.

**[Syft](https://github.com/anchore/syft)** is a CLI tool for generating an SBOM from container images and filesystems.

## Installation

Syft is provided as a single compiled executable and requires no external dependencies to run.
Run the command for your platform to download the latest release.

{{< tabpane lang="bash">}}
{{% tab header="Platform:" disabled=true /%}}
{{< tab header="Linux (and macOS)" >}}
curl -sSfL https://get.anchore.io/syft | sudo sh -s -- -b /usr/local/bin
{{< /tab >}}
{{% tab header="macOS"%}}brew install syft{{% /tab %}}
{{% tab header="Windows"%}}winget install Anchore.Syft{{% /tab %}}
{{< /tabpane >}}

Check out [installation guide]({{< relref "/docs/installation/syft" >}}) for full list of official and community-maintained packaging options.

## Find packages within a container image

Run `syft` against a small container image; the output will be a simple human-readable table of the installed packages found:

```
syft alpine:latest
```

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
Syft supports more than just containers. Learn more about [Supported Scan Targets]({{< relref "/docs/guides/sbom/scan-targets/" >}})
{{< /alert >}}

## Create an industry-standard SBOM

This command will display the human-readable table _and_ write SBOMs in both **[SPDX](https://spdx.dev/)** and **[CycloneDX](https://cyclonedx.org/)** formats, the two primary industry standards.

```bash
syft alpine:latest \                 # what we're scanning
  -o table \                         # a human-readable table to stdout
  -o spdx-json=alpine.spdx.json \    # SPDX-JSON formatted SBOM to a file
  -o cyclonedx-json=alpine.cdx.json  # CycloneDX-JSON formatted SBOM to a file
```

The same table will be displayed, and two SBOM files will be created in the current directory.

{{< alert title="Learn more" color="primary" >}}
Syft supports multiple SBOM output formats, find out more about [Output Formats]({{< relref "/docs/guides/sbom/formats/" >}}).
{{< /alert >}}

### Examine the SBOM file contents

We can use [`jq`](https://jqlang.org/) to extract specific package data from the SBOM files (by default Syft outputs JSON on a single line,
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

{{% alert title="More JSON examples" color="primary" %}}
For more examples of working with Syft's JSON output using jq, see the [jq recipes]({{< relref "/docs/guides/sbom/json/#jq-recipes" >}}).
{{% /alert %}}

## FAQ

**Does Syft need internet access?**

Only for downloading container images. By default, scanning works offline, but Syft can download supplemental
information from online sources when enabled with the `--enrich` option.

**What about private container registries?**

Syft supports authentication for private registries. See [Private Registries]({{< relref "/docs/guides/private-registries/" >}}).

**Can I use Syft in CI/CD pipelines?**

Absolutely! Syft is designed for automation. Generate SBOMs during builds and scan them for vulnerabilities.

**What data does Syft send externally?**

Nothing. Syft runs entirely locally and doesn't send any data to external services.

## Next steps

{{< alert title="Continue the guide" color="success" url="/docs/guides/sbom/scan-targets/" >}}
**Next**: Learn about all the different [Supported Scan Targets]({{< relref "/docs/guides/sbom/scan-targets/" >}}) Syft can analyze --from container images to local directories and archives.
{{< /alert >}}

Now that you've generated your first SBOM, here are additional resources:

- **Scan for vulnerabilities**: Use [Grype]({{< relref "/docs/guides/vulnerability/getting-started/" >}}) to find security issues in your SBOMs
- **Check licenses**: Learn about [License Scanning]({{< relref "/docs/guides/license/getting-started/" >}}) to understand dependency licenses
- **Customize output**: Explore different [Output Formats]({{< relref "/docs/guides/sbom/formats/" >}}) for various tools and workflows
- **Query SBOM data**: Master [Working with Syft JSON]({{< relref "/docs/guides/sbom/json/" >}}) for advanced data extraction
