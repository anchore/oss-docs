+++
title = "Format Conversion"
linkTitle = "Format Conversion"
description = "Convert existing SBOMs between different formats including SPDX and CycloneDX using Syft's experimental conversion capabilities."
weight = 70
tags = ["syft", "sbom", "formats", "spdx", "cyclonedx"]
url = "docs/guides/sbom/conversion"
+++

{{< alert color="warning" title="Experimental Feature" >}}
This feature is experimental and may change in future releases.
{{< /alert >}}

{{< alert title="TL;DR" color="primary" >}}

- Convert from Syft JSON to other SBOM formats: `syft convert <sbom-file> -o <format>`
- Best practice: keep Syft JSON as source, convert to SPDX/CycloneDX as needed
- Avoid chaining conversions (e.g., SPDX → CycloneDX)

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
Learn more about working with Syft's native format in the [Working with Syft JSON](/docs/guides/sbom/syft-json/) guide.
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

## FAQ

**Can I convert from SPDX to CycloneDX?**

Yes, but it's not recommended. Converting between non-Syft formats loses data with each conversion. If you have the original Syft JSON or can re-scan the source, that's a better approach.

**Why is some data missing after conversion?**

Different SBOM formats have different schemas with different capabilities. SPDX and CycloneDX can't represent all Syft metadata. Converting from Syft JSON to standard formats works best; converting between standard formats loses more data.

**Is conversion faster than re-scanning?**

Yes, significantly. Conversion takes milliseconds while scanning can take seconds to minutes depending on source size. This makes conversion ideal for CI/CD pipelines that need multiple formats.

**Can I convert back to Syft JSON from SPDX?**

Yes, but you'll lose Syft-specific metadata that doesn't exist in SPDX (like cataloger information, layer details, and file metadata). The result won't match the original Syft JSON.

**Which format versions are supported?**

See the [Output Formats](/docs/guides/sbom/formats/) guide for supported versions of each format. Syft converts to the latest version by default, but you can specify older versions (e.g., `-o spdx-json@2.2`).

## Next steps

{{< alert title="Continue the guide" color="success" url="/docs/guides/sbom/attestation/" >}}
**Next**: Explore [Attestation](/docs/guides/sbom/attestation/) to learn how to sign and verify your SBOMs for supply chain security.
{{< /alert >}}

Additional resources:

- **Source format**: See [Working with Syft JSON](/docs/guides/sbom/syft-json/) to understand the source format
- **Available formats**: Check [Output Formats](/docs/guides/sbom/formats/) for all supported SBOM formats
- **Direct generation**: Learn about generating formats directly in [Getting Started](/docs/guides/sbom/getting-started/)
