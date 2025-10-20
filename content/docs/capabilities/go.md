+++
title = "Go"
description = "Go package analysis and vulnerability scanning capabilities"
weight = 130
type = "docs"
+++

## Package analysis

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/go/package.md" >}}


{{< readfile file="/content/docs/capabilities/snippets/ecosystem/go/syft-app-config.md" >}}


## Vulnerability scanning

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/go/vulnerability.md" >}}

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/go/grype-app-config.md" >}}


### Main module filtering

Grype skips vulnerability matching for packages that match all these conditions:

- Package name equals the main module name (from the SBOM metadata)
- Package version is unreliable:
  - When `allow-main-module-pseudo-version-comparison` is `false` (default): version starts with `v0.0.0-` or is `(devel)`
  - When `allow-main-module-pseudo-version-comparison` is `true`: version is `(devel)` only

This filtering exists because Go doesn't have a standard way to embed the main module's version into compiled binaries (see [golang/go#50603](https://github.com/golang/go/issues/50603)). Pseudo-versions in compiled binaries are often unreliable for vulnerability matching.

You can disable this filtering with the `allow-main-module-pseudo-version-comparison` configuration option.

### Troubleshooting

#### No vulnerabilities found for main module

**Cause:** The main module has a pseudo-version (`v0.0.0-*`) or `(devel)`, which Grype filters by default.

**Solution:** Enable pseudo-version matching in your Grype configuration:

```yaml
match:
  golang:
    allow-main-module-pseudo-version-comparison: true
```

{{< alert color="primary" title="Note" >}}
This may produce false positives. Use properly versioned builds when possible.
{{< /alert >}}

#### No vulnerabilities found for stdlib

**Possible causes:**

- **Missing CPEs:** Verify Syft generates CPEs with `generate-cpes: true` in `.syft.yaml`
- **CPE matching disabled:** Ensure `always-use-cpe-for-stdlib: true` in Grype config (default)
- **Incorrect version format:** Stdlib version should be `go1.18.3`, not `v1.18.3` (file a Syft bug if incorrect)


## Next steps

- [Syft package analysis]({{< ref "/docs/guides/sbom" >}})
- [Grype vulnerability scanning]({{< ref "/docs/guides/vulnerability" >}})
