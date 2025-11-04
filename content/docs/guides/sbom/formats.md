+++
title = "Output Formats"
description = "Choose from multiple SBOM output formats including SPDX, CycloneDX, and Syft's native JSON format."
weight = 40
tags = ["syft", "sbom", "formats", "spdx", "cyclonedx", "json"]
url = "docs/guides/sbom/formats"

+++

{{< alert title="TL;DR" color="primary" >}}

- **Choose a format** with `-o <format>`:
  - `table` (default)
  - `json` (complete data)
  - `spdx-json`/`spdx-tag-value`
  - `cyclonedx-json`/`cyclonedx-xml`
- **Write to file**: `-o json=sbom.json`
- Generate **multiple formats at once**: use multiple `-o` flags

{{< /alert >}}

Syft supports multiple output formats to fit different workflows and requirements by using the `-o` (or `--output`) flag:

```bash
syft <image> -o <format>
```

## Available formats

| `-o ARG`      | Description                                                                                                                                                                           |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `table`       | A columnar summary (default)                                                                                                                                                          |
| `json`        | Native output for Syft—use this to get as much information out of Syft as possible! (see the [JSON schema](https://github.com/anchore/syft/blob/main/schema/json/schema-latest.json)) |
| `purls`       | A line-separated list of [Package URLs (PURLs)](https://github.com/package-url/purl-spec) for all discovered packages                                                                 |
| `github-json` | A JSON report conforming to GitHub's dependency snapshot format                                                                                                                       |
| `template`    | Lets you specify a custom output format via Go templates (see [Templates](/docs/guides/sbom/templates/) for more detail)                                                              |
| `text`        | A row-oriented, human-and-machine-friendly output                                                                                                                                     |

### CycloneDX

[CycloneDX](https://cyclonedx.org/) is an OWASP-maintained industry standard SBOM format.

| `-o ARG`         | Description                                                                                              |
| ---------------- | -------------------------------------------------------------------------------------------------------- |
| `cyclonedx-json` | A JSON report conforming to the [CycloneDX specification](https://cyclonedx.org/specification/overview/) |
| `cyclonedx-xml`  | An XML report conforming to the [CycloneDX specification](https://cyclonedx.org/specification/overview/) |

### SPDX

[SPDX](https://spdx.dev/) (Software Package Data Exchange) is an ISO/IEC 5962:2021 industry standard SBOM format.

| `-o ARG`         | Description                                                                                                              |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `spdx-json`      | A JSON report conforming to the [SPDX JSON Schema](https://github.com/spdx/spdx-spec/blob/v2.3/schemas/spdx-schema.json) |
| `spdx-tag-value` | A tag-value formatted report conforming to the [SPDX specification](https://spdx.github.io/spdx-spec/v2.3/)              |

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
path="content/docs/guides/sbom/snippets/format/examples"
title="syft busybox:latest -o "
tabs="table|table.md,json|json.md,purls|purls.md,cyclonedx-json|cyclonedx-json.md,cyclonedx-xml|cyclonedx-xml.md,spdx-json|spdx-json.md,spdx-tag-value|spdx-tag-value.md,github-json|github-json.md" >}}

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
syft <source> \
  -o json=sbom.json \
  -o spdx-json=sbom.spdx.json
```

You can both display to terminal and write to file:

```bash
syft <source> \
  -o table \           # report to stdout
  -o json=sbom.json    # write to file
```

## FAQ

**Which format should I use?**

- **For human review**: Use `table` (default) for quick package lists
- **For automation and queries**: Use `json` to access all Syft data including file details, relationships, and metadata
- **For compliance and sharing**: Use `spdx-json` or `cyclonedx-json` - both are widely supported industry standards
- **For custom formats**: Use `template` to create your own output format

**Can I convert between formats?**

Yes! See the [Format Conversion](/docs/guides/sbom/conversion/) guide to convert existing SBOMs between formats without re-scanning.

**Do all formats contain the same information?**

No. Syft's native `json` format contains the most complete information. Standard formats (SPDX, CycloneDX) contain package data but may not include all file details or Syft-specific metadata. Some data may be omitted or transformed to fit the target schema.

**Which version should I use for SPDX or CycloneDX?**

Use the latest version (default) unless you need compatibility with specific tools that require older versions. Check your downstream tools' documentation for version requirements.

## Next steps

{{< alert title="Continue the guide" color="success" url="/docs/guides/sbom/syft-json/" >}}
**Next**: Explore [Working with Syft JSON](/docs/guides/sbom/syft-json/) to learn how to query and extract specific data from Syft's native format using jq.
{{< /alert >}}

Additional resources:

- **Custom formats**: Learn about [customizing output with templates](/docs/guides/sbom/templates) for specialized formats
- **Convert formats**: See [Format Conversion](/docs/guides/sbom/conversion/) to convert between different SBOM formats
- **Advanced settings**: Check [configuration options](/docs/reference/syft/configuration) for format-specific settings
