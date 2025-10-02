+++
title = "Format Conversion"
linkTitle = "Format Conversion"
description = "Convert existing SBOMs between different formats including SPDX and CycloneDX using Syft's experimental conversion capabilities."
weight = 70
tags = ["syft", "sbom", "formats", "spdx", "cyclonedx"]
url = "docs/user-guides/sbom/conversion"
+++

{{< alert color="warning" title="Experimental Feature" >}}
This feature is experimental and may change in future releases.
{{< /alert >}}

The ability to convert existing SBOMs means you can create SBOMs in different formats quickly, without the need to regenerate the SBOM from scratch, which may take significantly more time.

```
syft convert <ORIGINAL-SBOM-FILE> -o <NEW-SBOM-FORMAT>[=<NEW-SBOM-FILE>]
```

We support formats with wide community usage AND good encode/decode support by Syft. The supported formats are:

- Syft JSON (`-o json`)
- SPDX JSON (`-o spdx-json`)
- SPDX tag-value (`-o spdx-tag-value`)
- CycloneDX JSON (`-o cyclonedx-json`)
- CycloneDX XML (`-o cyclonedx-xml`)

Conversion example:

```sh
syft alpine:latest -o syft-json=sbom.syft.json # generate a syft SBOM
syft convert sbom.syft.json -o cyclonedx-json=sbom.cdx.json  # convert it to CycloneDX
```

## Best practices

### Use Syft JSON as the source format

Generate and keep Syft JSON as your primary SBOM. Convert from it to other formats as needed:

```bash
# Generate Syft JSON (native format with complete data)
syft <source> -o json=sbom.json

# Convert to other formats
syft convert sbom.json -o spdx-json=sbom.spdx.json
syft convert sbom.json -o cyclonedx-json=sbom.cdx.json
```

Converting between non-Syft formats loses data. Syft JSON contains all information Syft extracted, while other formats use different schemas that can't represent the same fields.

{{< alert title="Learn more" color="primary" >}}
Learn more about working with Syft's native format in the [Working with Syft JSON](/docs/user-guides/sbom/syft-json/) guide.
{{< /alert >}}

### What gets preserved

{{< alert color="warning" title="Data Loss During Conversion" >}}
Converting between formats may lose data. Packages (names, versions, licenses) transfer reliably, while tool metadata, source details, and format-specific fields may not. Use Syft JSON as the source format to minimize data loss.
{{< /alert >}}

Conversions from Syft JSON to SPDX or CycloneDX preserve all standard SBOM fields. Converted output matches directly-generated output (only timestamps and IDs differ).

Avoid chaining conversions (e.g., SPDX → CycloneDX). Each step may lose format-specific data.

**Reliably preserved across conversions:**

- Package names, versions, and PURLs
- License information
- CPEs and external references
- Package relationships

**May be lost in conversions:**

- Tool configuration and cataloger information
- Source metadata (image manifests, layers, container config)
- File location details and layer attribution
- Package-manager-specific metadata (git commits, checksums, provides/dependencies)
- Distribution details

### When to convert vs regenerate

**Convert from Syft JSON when:**

- You need multiple formats for different tools
- The original source is unavailable
- Scanning takes significant time

**Regenerate from source when:**

- You need complete format-specific data
- Conversion output is missing critical information
