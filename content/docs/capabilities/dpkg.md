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


### Operating systems

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/dpkg/os.md" >}}

## Next steps

- [Syft package analysis]({{< ref "/docs/guides/sbom" >}})
- [Grype vulnerability scanning]({{< ref "/docs/guides/vulnerability" >}})
