+++
title = "Output Formats"
description = "SBOM Generation Output Formats"
weight = 40
tags = ["syft", "sbom", "formats", "spdx", "cyclonedx"]
url = "docs/userguides/sbom/formats"

+++

## Output formats

The output format for Syft is configurable as well using the
`-o` (or `--output`) option:

```
syft <image> -o <format>
```

Where the `formats` available are:
- `syft-json`: Use this to get as much information out of Syft as possible!
- `syft-text`: A row-oriented, human-and-machine-friendly output.
- `cyclonedx-xml`: A XML report conforming to the [CycloneDX 1.6 specification](https://cyclonedx.org/specification/overview/).
- `cyclonedx-json`: A JSON report conforming to the [CycloneDX 1.6 specification](https://cyclonedx.org/specification/overview/).
- `spdx-tag-value`: A tag-value formatted report conforming to the [SPDX 2.3 specification](https://spdx.github.io/spdx-spec/v2.3/).
- `spdx-tag-value@2.2`: A tag-value formatted report conforming to the [SPDX 2.2 specification](https://spdx.github.io/spdx-spec/v2.2.2/).
- `spdx-json`: A JSON report conforming to the [SPDX 2.3 JSON Schema](https://github.com/spdx/spdx-spec/blob/v2.3/schemas/spdx-schema.json).
- `spdx-json@2.2`: A JSON report conforming to the [SPDX 2.2 JSON Schema](https://github.com/spdx/spdx-spec/blob/v2.2/schemas/spdx-schema.json).
- `github-json`: A JSON report conforming to GitHub's dependency snapshot format.
- `syft-table`: A columnar summary (default).
- `template`: Lets the user specify the output format. See ["Using templates"](#using-templates) below.

## Multiple Outputs

Syft can also output multiple files in differing formats by appending `=<file>` to the option, for example to output Syft JSON and SPDX JSON:

```
syft <image> -o syft-json=sbom.syft.json -o spdx-json=sbom.spdx.json
```