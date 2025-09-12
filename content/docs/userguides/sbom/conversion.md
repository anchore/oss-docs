+++
title = "Format Conversion (experimental)"
linkTitle = "Format Conversion"
description = "SBOM Generation Format Conversion (experimental)"
weight = 70
tags = ["syft", "sbom", "formats", "spdx", "cyclonedx"]
url = "docs/userguides/sbom/conversion"
+++

## Format Conversion (experimental)

The ability to convert existing SBOMs means you can create SBOMs in different formats quickly, without the need to regenerate the SBOM from scratch, which may take significantly more time.

```
syft convert <ORIGINAL-SBOM-FILE> -o <NEW-SBOM-FORMAT>[=<NEW-SBOM-FILE>]
```

This feature is experimental and data might be lost when converting formats. Packages are the main SBOM component easily transferable across formats, whereas files and relationships, as well as other information Syft doesn't support, are more likely to be lost.

We support formats with wide community usage AND good encode/decode support by Syft. The supported formats are:
- Syft JSON (```-o syft-json```)
- SPDX 2.2 JSON (```-o spdx-json```)
- SPDX 2.2 tag-value (```-o spdx-tag-value```)
- CycloneDX 1.4 JSON (```-o cyclonedx-json```)
- CycloneDX 1.4 XML (```-o cyclonedx-xml```)

Conversion example:

```sh
syft alpine:latest -o syft-json=sbom.syft.json # generate a syft SBOM
syft convert sbom.syft.json -o cyclonedx-json=sbom.cdx.json  # convert it to CycloneDX
```
