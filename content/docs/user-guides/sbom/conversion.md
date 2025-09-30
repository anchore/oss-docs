+++
title = "Format Conversion"
linkTitle = "Format Conversion"
description = "Convert existing SBOMs between different formats including SPDX and CycloneDX using Syft's experimental conversion capabilities."
weight = 70
tags = ["syft", "sbom", "formats", "spdx", "cyclonedx"]
url = "docs/user-guides/sbom/conversion"
+++

{{< alert color="warning" title="Experimental Feature" >}}
This feature is experimental and data might be lost when converting formats. Packages are the main SBOM component easily transferable across formats, whereas files and relationships, as well as other information Syft doesn't support, are more likely to be lost.
{{< /alert >}}

The ability to convert existing SBOMs means you can create SBOMs in different formats quickly, without the need to regenerate the SBOM from scratch, which may take significantly more time.

```
syft convert <ORIGINAL-SBOM-FILE> -o <NEW-SBOM-FORMAT>[=<NEW-SBOM-FILE>]
```

We support formats with wide community usage AND good encode/decode support by Syft. The supported formats are:

- Syft JSON (`-o syft-json`)
- SPDX 2.2 JSON (`-o spdx-json`)
- SPDX 2.2 tag-value (`-o spdx-tag-value`)
- CycloneDX 1.4 JSON (`-o cyclonedx-json`)
- CycloneDX 1.4 XML (`-o cyclonedx-xml`)

Conversion example:

```sh
syft alpine:latest -o syft-json=sbom.syft.json # generate a syft SBOM
syft convert sbom.syft.json -o cyclonedx-json=sbom.cdx.json  # convert it to CycloneDX
```
