+++
title = "Capabilities"
description = "Summary of package analysis and vulnerability scanning capabilities across ecosystems"
weight = 11
type = "docs"
+++

Anchore's open source tools provide comprehensive package analysis and vulnerability scanning across many programming languages, operating systems, and package formats. This section documents what Syft can catalog and what Grype can scan for each ecosystem.

## What are capabilities?

Capabilities describe the **cross-cutting features** available across Anchore's tools:

- **Package analysis**: What Syft can catalog from package manifests, lock files, and installed packages
- **Vulnerability scanning**: What Grype can detect using vulnerability databases and matching rules

These capabilities are ecosystem-specific. For example, Python's capabilities differ from Go's, and Ubuntu's capabilities differ from Alpine's.

## Ecosystem capabilities

The table below shows which ecosystems support package analysis and vulnerability scanning.

{{< readfile file="/content/docs/capabilities/snippets/overview/package.md" >}}

**Legend**:
- ✅ = Supported by default
- ⚙️ = Conditionally supported (requires configuration)
- \- = Not supported

## Operating system version support

Grype maintains vulnerability data for specific operating system versions. The table below shows which OS versions are supported and where the data comes from.

{{< readfile file="/content/docs/capabilities/snippets/overview/os.md" >}}

## Next steps

- Explore capabilities for specific ecosystems using the navigation menu
- Learn about [Syft package analysis]({{< ref "/docs/guides/sbom" >}})
- Learn about [Grype vulnerability scanning]({{< ref "/docs/guides/vulnerability" >}})
