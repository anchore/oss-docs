+++
title = "ALPM"
description = "ALPM package format used by Arch-based Linux distributions"
weight = 10
type = "docs"
menu_group = "os"
[params]
sidebar_badge = "arch"
+++

## Package analysis

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/alpm/package.md" >}}

## Vulnerability scanning

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/alpm/vulnerability.md" >}}

### Operating systems

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/alpm/os.md" >}}

#### Contributing

**Interested in contributing vulnerability scanning support?**

Feel free to add a new vunnel provider for Arch-based distributions.
See the [existing issue](https://github.com/anchore/vunnel/issues/907) in the Vunnel repository.

## Next steps

- [Syft package analysis]({{< ref "docs/guides/sbom" >}})
- [Grype vulnerability scanning]({{< ref "docs/guides/vulnerability" >}})
