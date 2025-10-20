+++
title = "Go"
description = "Go package analysis and vulnerability scanning capabilities"
weight = 130
type = "docs"
+++

## Package analysis

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/go/package.md" >}}

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/go/syft-app-config.md" >}}

### Version detection for binaries

When Syft scans a Go binary, the main module often has version `(devel)` because Go doesn't embed version information by default.
Syft attempts to detect the actual version using three strategies (configurable via `golang.main-module-version.*`):

1. **From ldflags** (enabled by default): Looks for version strings passed during build like `-ldflags="-X main.version=v1.2.3"`. Supports common patterns: `*.version=`, `*.gitTag=`, `*.release=`, etc.

2. **From build settings** (enabled by default): Uses VCS metadata (commit hash and timestamp) embedded by Go 1.18+ to generate a pseudo-version like `v0.0.0-20230101120000-abcdef123456`.

3. **From contents** (disabled by default): Scans binary contents for version string patterns. Can produce false positives.

**Best practice**: Use `-ldflags` when building to embed your version explicitly.

**Example:**

```bash
go build -ldflags="-X main.version=v1.2.3"
```

This ensures Syft (and Grype) can accurately identify your application version for vulnerability matching.

### Standard library

Syft automatically creates a `stdlib` package for each Go binary, representing the Go standard library version used to compile it.
The version is extracted from the binary's build metadata (e.g., `go1.22.2`).
This enables Grype to check for vulnerabilities reported against the go standard library.

**Why this matters:** Vulnerabilities in the Go compiler (like CVEs affecting the crypto library or net/http) can affect your application even if your code doesn't directly use those packages.

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
