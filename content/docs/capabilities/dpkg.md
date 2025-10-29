+++
title = "DPKG"
description = "Debian package format used by Debian-based Linux distributions"
weight = 80
type = "docs"
menu_group = "os"
[params]
sidebar_badge = "debian+"
+++

## Package analysis

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/dpkg/package.md" >}}

There is additional functionality for:

- the detection of [OpenWrt's](https://openwrt.org/) [OPKG packages](https://openwrt.org/docs/guide-user/additional-software/opkg)
- the detection of [Google Distroless image](https://github.com/GoogleContainerTools/distroless) debian-based packages

## Vulnerability scanning

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/dpkg/vulnerability.md" >}}

### Operating systems

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/dpkg/os.md" >}}

## Next steps

- [Syft package analysis]({{< ref "docs/guides/sbom" >}})
- [Grype vulnerability scanning]({{< ref "docs/guides/vulnerability" >}})
