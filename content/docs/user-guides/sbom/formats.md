+++
title = "Output Formats"
description = "Choose from multiple SBOM output formats including SPDX, CycloneDX, and Syft's native JSON format with format capabilities and version support for different use cases."
weight = 40
tags = ["syft", "sbom", "formats", "spdx", "cyclonedx"]
url = "docs/user-guides/sbom/formats"

+++

Syft supports multiple output formats to fit different workflows and requirements. Configure the output format using the `-o` (or `--output`) option:

```bash
syft <image> -o <format>
```

## Available formats

### Syft-native formats

- `table`: A columnar summary (default).
- `json`: Use this to get as much information out of Syft as possible!
- `purls`: A line-separated list of [Package URLs (PURLs)](https://github.com/package-url/purl-spec) for all discovered packages.
- `github-json`: A JSON report conforming to GitHub's dependency snapshot format.
- `template`: Lets the user specify a custom output format via go templates (see [Templates](/docs/user-guides/sbom/templates/) for more detail).
- `text`: A row-oriented, human-and-machine-friendly output.

### CycloneDX

CycloneDX is an OWASP-maintained industry standard SBOM format.

- `cyclonedx-json`: A JSON report conforming to the [CycloneDX specification](https://cyclonedx.org/specification/overview/).
- `cyclonedx-xml`: A XML report conforming to the [CycloneDX specification](https://cyclonedx.org/specification/overview/).

### SPDX

SPDX (Software Package Data Exchange) is an ISO/IEC 5962:2021 industry standard SBOM format.

- `spdx-json`: A JSON report conforming to the [SPDX JSON Schema](https://github.com/spdx/spdx-spec/blob/v2.3/schemas/spdx-schema.json).
- `spdx-tag-value`: A tag-value formatted report conforming to the [SPDX specification](https://spdx.github.io/spdx-spec/v2.3/).

## Format versions

Some output formats support multiple schema versions. Specify a version by appending `@<version>` to the format name:

```bash
syft <source> -o <format>@<version>
```

**Examples:**

```bash
# Use CycloneDX JSON version 1.4
syft <source> -o cyclonedx-json@1.4

# Use SPDX JSON version 2.2
syft <source> -o spdx-json@2.2

# Default to latest version if not specified
syft <source> -o cyclonedx-json
```

Formats with version support:

{{% readfile "snippets/format/versions.md" %}}

When no version is specified, Syft uses the latest supported version of the format.

## Format examples

{{< file-tabs
path="content/docs/user-guides/sbom/snippets/format/examples"
title="syft busybox:latest -o "
tabs="table|table.md,json|json.md,cyclonedx-json|cyclonedx-json.md,cyclonedx-xml|cyclonedx-xml.md,spdx-json|spdx-json.md,spdx-tag-value|spdx-tag-value.md,github-json|github-json.md" >}}

## Writing output to files

Direct Syft output to a file instead of stdout by appending `=<file>` to the format option:

```bash
# Write JSON to a file
syft <source> -o json=sbom.json

# Write to stdout (default behavior)
syft <source> -o json
```

## Multiple outputs

Generate multiple SBOM formats in a single run by specifying multiple `-o` flags:

```bash
syft <source> -o json=sbom.json -o spdx-json=sbom.spdx.json
```

**Examples:**

Generate multiple formats:

```bash
syft <source> \
  -o cyclonedx-json=sbom.cdx.json \
  -o spdx-json=sbom.spdx.json
```

Display to terminal and write to file:

```bash
syft <source> \
  -o table \
  -o json=sbom.json
```

Organize by directory:

```bash
syft <source> \
  -o cyclonedx-json=security/sbom.cdx.json \
  -o spdx-json=compliance/sbom.spdx.json \
  -o json=automation/sbom.json
```

## Next steps

- Learn about [customizing output with templates](/docs/user-guides/sbom/templates) for specialized formats
- Explore [supported sources](/docs/user-guides/sbom/sources) to understand what Syft can analyze
- See [configuration options](/docs/user-guides/sbom/configuration) for advanced format settings
