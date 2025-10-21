+++
title = "DPKG"
description = "Debian package format used by Debian-based Linux distributions"
weight = 80
type = "docs"
[params]
sidebar_badge = "debian+"
+++

## Package analysis

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/dpkg/package.md" >}}

**Notable capabilities:**

- **OPKG compatibility**: Syft supports OpenWrt's OPKG package manager format using the same cataloger.
- **Distroless images**: Syft automatically detects and supports Google distroless images that use `/var/lib/dpkg/status.d/`.

## Vulnerability scanning

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/dpkg/vulnerability.md" >}}

### Source and binary package matching

Grype matches vulnerabilities against both binary package names and source package names. You'll receive matches regardless of which name the security advisory uses. Matches found via source package names are marked as indirect matches in the output.

### Fix availability tracking

The vulnerability database tracks multiple fix states for DPKG packages:

- **Fixed**: A fix version is available and specified in the constraint
- **NotFixed**: The vulnerability is known but no fix has been released yet
- **WontFix**: The vendor has determined no advisory will be issued (common for ignored vulnerabilities in end-of-life releases)

Debian Security Advisories (DSAs) and Ubuntu Security Notices (USNs) are correlated with CVEs when available, providing links to official vendor advisories in Grype's output.

### Operating systems

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/dpkg/os.md" >}}

## Next steps

- [Syft package analysis]({{< ref "/docs/guides/sbom" >}})
- [Grype vulnerability scanning]({{< ref "/docs/guides/vulnerability" >}})
