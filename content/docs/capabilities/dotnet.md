+++
title = ".NET"
description = ".NET package analysis and vulnerability scanning capabilities"
weight = 90
type = "docs"
menu_group = "language"
+++

## Package analysis

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/dotnet/package.md" >}}

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/dotnet/syft-app-config.md" >}}

When scanning a .NET application evidence from deps.json (compiler output) as well as any built binaries are used together to identify packages.
This way we can enrich missing data from any one source and synthesize a more complete and accurate package graph.

## Vulnerability scanning

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/dotnet/vulnerability.md" >}}

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/dotnet/grype-app-config.md" >}}

## Next steps

- [Syft package analysis]({{< ref "docs/guides/sbom/getting-started" >}})
- [Grype vulnerability scanning]({{< ref "docs/guides/vulnerability/getting-started" >}})
