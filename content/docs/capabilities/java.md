+++
title = "Java"
description = "Java package analysis and vulnerability scanning capabilities"
weight = 160
type = "docs"
menu_group = "language"
+++

## Package analysis

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/java/package.md" >}}

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/java/syft-app-config.md" >}}

### Archives

When scanning a Java archive (e.g. `jar`, `war`, `ear`, ...), Syft will look for `maven` project evidence within the archive recursively.
This means that if a `jar` file contains other `jar` files, Syft will also look for `pom.xml` files within those nested `jar` files to identify packages (such as with [shaded jars](https://maven.apache.org/plugins/maven-shade-plugin/)).

Additionally, if opted-in via configuration, Syft will scan non-java archive files (e.g., `zip`, `tar`, `tar.gz`, ...) for Java package evidence as well.

## Vulnerability scanning

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/java/vulnerability.md" >}}

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/java/grype-app-config.md" >}}

## Next steps

- [Syft package analysis]({{< ref "docs/guides/sbom/getting-started" >}})
- [Grype vulnerability scanning]({{< ref "docs/guides/vulnerability/getting-started" >}})
