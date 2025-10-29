+++
title = "C/C++"
description = "C/C++ package analysis and vulnerability scanning capabilities"
weight = 60
type = "docs"
menu_group = "language"
+++

## Package analysis

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/c++/package.md" >}}

We support package detection for [v1](https://docs.conan.io/1/versioning/lockfiles.html#lockfiles) and [v2](https://docs.conan.io/2/tutorial/versioning/lockfiles.html) formatted `conan.lock` files.

## Vulnerability scanning

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/c++/vulnerability.md" >}}

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/c++/grype-app-config.md" >}}

## Next steps

- [Syft package analysis]({{< ref "docs/guides/sbom" >}})
- [Grype vulnerability scanning]({{< ref "docs/guides/vulnerability" >}})
