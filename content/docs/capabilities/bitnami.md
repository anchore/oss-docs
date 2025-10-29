+++
title = "Bitnami"
description = "Bitnami package analysis and vulnerability scanning capabilities"
weight = 40
type = "docs"
menu_group = "other"
+++

## Package analysis

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/bitnami/package.md" >}}

Since all package data is gathered from SPDX SBOMs, the quality of the package analysis is dependent on the quality of the provided SBOMs.

## Vulnerability scanning

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/bitnami/vulnerability.md" >}}

## Next steps

- [Syft package analysis]({{< ref "docs/guides/sbom" >}})
- [Grype vulnerability scanning]({{< ref "docs/guides/vulnerability" >}})
