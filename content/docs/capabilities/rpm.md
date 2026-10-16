+++
title = "RPM"
description = "Red Hat Package Manager format used by Red Hat-based Linux distributions"
weight = 270
type = "docs"
menu_group = "os"

[params]
sidebar_badge = "redhat+"
+++

## Package analysis

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/rpm/package.md" >}}

## Vulnerability scanning

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/rpm/vulnerability.md" >}}

### Operating systems

CBL-Mariner was renamed Azure Linux with the 3.0 release. Both use the
`mariner` Vunnel provider, but Azure Linux 3.0 and CBL-Mariner 1.0/2.0 use
different OVAL feeds, as reflected in the data source links below.

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/rpm/os.md" >}}

## Next steps

- [Syft package analysis]({{< ref "docs/guides/sbom/getting-started" >}})
- [Grype vulnerability scanning]({{< ref "docs/guides/vulnerability/getting-started" >}})
