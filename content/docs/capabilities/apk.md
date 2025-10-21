+++
title = "APK"
description = "APK package format analysis and vulnerability scanning capabilities"
weight = 20
type = "docs"
[params]
sidebar_badge = "alpine+"
+++

## Package analysis

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/apk/package.md" >}}

## Vulnerability scanning

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/apk/vulnerability.md" >}}


### Operating systems

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/apk/os.md" >}}

The APK vulnerability database (a.k.a. "SecDB") includes data from the Alpine Security Tracker, which provides detailed information on vulnerabilities affecting Alpine Linux packages.
This database only includes vulnerabilities that have fixes available and does not track unfixed vulnerabilities.
The maintainers of the SecDB intend for the primary source of truth for disclosures to be the [National Vulnerability Database](https://nvd.nist.gov/developers/vulnerabilities) (NVD).

This is true of other APK vulnerability data sources as well (such as Chainguard, Wolfi, and MinimOS).


## Next steps

- [Syft package analysis]({{< ref "/docs/guides/sbom" >}})
- [Grype vulnerability scanning]({{< ref "/docs/guides/vulnerability" >}})
- [Alpine Linux](https://alpinelinux.org/)
- [Wolfi](https://wolfi.dev/)
- [Chainguard Images](https://www.chainguard.dev/chainguard-images)
