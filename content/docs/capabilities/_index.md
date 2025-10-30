+++
title = "Capabilities"
description = "Summary of package analysis and vulnerability scanning capabilities across ecosystems"
weight = 13
type = "docs"
+++

Capabilities describe the **cross-cutting features** available across Anchore's tools:

- **Package analysis**: What Syft can catalog from package manifests, lock files, and installed packages
- **Vulnerability scanning**: What Grype can detect using vulnerability databases and matching rules

These capabilities are _ecosystem-specific_.
For example, Python's capabilities differ from Go's, and Ubuntu's capabilities differ from Alpine's.

Default capabilities do not require to be online or have special configuration (other than having a vulnerability DB downloaded).
Some capabilities may be conditionally supported, requiring additional configuration or online access to function.

## Vulnerability scanning capabilities

### Operating system support

Syft and Grype support several operating systems for package cataloging and vulnerability detection.
The table below shows which OS versions are supported and where Grype's vulnerability data comes from.

{{< readfile file="/content/docs/capabilities/snippets/overview/os.md" >}}

### Data sources

Vulnerability data sources vary in the information they provide. Grype uses these capabilities when available to provide more accurate and comprehensive vulnerability detection:

- **Independent Disclosure**: Whether the advisory discloses the vulnerability regardless of fix availability. Sources with this capability report vulnerabilities even when no fix is available yet.

- **Disclosure Date**: Whether the data source provides the date when a vulnerability was first publicly disclosed. This helps you understand the timeline of vulnerability exposure.

- **Fix Versions**: Whether the data source specifies which package versions contain fixes for a vulnerability. This allows Grype to determine if an installed package version is vulnerable or fixed.

- **Fix Date**: Whether the advisory includes a date when the fix was made available. This helps you understand the timeline of vulnerability remediation.

## Package analysis capabilities

The table below shows which ecosystems support package analysis and vulnerability scanning.

{{< readfile file="/content/docs/capabilities/snippets/overview/package.md" >}}

## Legend

- <svg class="capability-icon"><use href="#icon-check"/> : Supported by default
- <svg class="capability-icon"><use href="#icon-gear"/> : Conditionally supported (requires configuration)
- _(empty)_ : Not supported

### Dependencies

We describe Syft's ability to capture dependency information in the following dimentions:

- **Depth**: How far into the true dependency graph we are able to discover package nodes.
  - `direct`: only captures dependencies explicitly declared by the project, but not necessarily dependencies of those dependencies

  - `transitive`: all possible depths of dependencies are captured

- **Edges**: Whether we are able to capture relationships between packages, and if so, describe the topology of those relationships.
  - `flat`: we can capture the root package relative to all other dependencies, but are unaware of relationships between dependencies (a simple star topology, where all dependencies point to the root package)

  - `complete`: all possible relationships between packages are captured (the full dependency graph)

- **Kinds**: The types of dependencies we are able to capture.
  - `runtime`: dependencies required for the package to function at runtime

  - `dev`: dependencies required for development

### Licenses

Indicates whether Syft can detect and catalog license information from package metadata. When supported, Syft extracts license declarations from package manifests, metadata files, or installed package databases.

### Package manager features

Syft can extract various package manager metadata beyond basic package information:

- **Files**: Whether Syft can catalog the list of files that are part of a package installation. This provides visibility into all files installed by the package manager.

- **Digests**: Whether Syft can capture file checksums (digests/hashes) for individual files within a package. This enables integrity verification of installed files. Note: this is not necessarily the actual hash of the file, but instead the claims made by the package manager about those files. We capture actual file hashes in the files section of the SBOM.

- **Integrity Hash**: Whether Syft can capture a single package-level integrity hash used by package managers to verify the package archive itself (for example, the <https://go.dev/ref/mod#go-sum-files> for go packages).

## Next steps

- Explore capabilities for specific ecosystems using the navigation menu
- Learn about [Syft package analysis]({{< ref "docs/guides/sbom" >}})
- Learn about [Grype vulnerability scanning]({{< ref "docs/guides/vulnerability" >}})
