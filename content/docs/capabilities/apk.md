+++
title = "APK"
description = "APK package format analysis and vulnerability scanning capabilities"
weight = 20
type = "docs"
menu_group = "os"
[params]
sidebar_badge = "alpine+"
+++

## Package analysis

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/apk/package.md" >}}

## Vulnerability scanning

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/apk/vulnerability.md" >}}

The APK vulnerability matcher searches all data sources for upstream packages, including NVD.

### Operating systems

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/apk/os.md" >}}

The APK vulnerability database (a.k.a. "SecDB") includes data from the Alpine Security Tracker, which provides fix information for known vulnerabilities that affect Alpine Linux packages.
This database only includes vulnerabilities that have fixes available and does not track unfixed vulnerabilities.
The maintainers of the SecDB intend for the primary source of truth for disclosures to be the [National Vulnerability Database](https://nvd.nist.gov/developers/vulnerabilities) (NVD).

This is true of other APK vulnerability data sources as well (such as Chainguard, Wolfi, and MinimOS).

## Next steps

- [Syft package analysis]({{< ref "docs/guides/sbom/getting-started" >}})
- [Grype vulnerability scanning]({{< ref "docs/guides/vulnerability/getting-started" >}})
- [Alpine Linux](https://alpinelinux.org/)
- [Wolfi](https://wolfi.dev/)
- [Chainguard Images](https://www.chainguard.dev/chainguard-images)
