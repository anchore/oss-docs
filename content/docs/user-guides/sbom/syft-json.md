+++
title = "Working with Syft JSON"
description = "Learn how to work with Syft's native JSON format including querying with jq, extracting metadata, and understanding the SBOM structure."
weight = 45
tags = ["syft", "sbom", "json", "jq"]
url = "docs/user-guides/sbom/syft-json"
+++

Syft's native JSON format contains the most complete information extracted when discovering software components.
This format captures all package metadata, file details, relationships, and source information that Syft discovers.

Since Syft can [convert from its native JSON format to other SBOM formats](/docs/user-guides/sbom/conversion/), it's
often a good idea to at least capture your SBOM in the native Syft JSON format, allowing you to generate any other
SBOM format for your compliance needs.

## Basic structure

A Syft JSON output contains these main sections:

```json
{
  "artifacts": [], // All discovered package nodes (names, versions, licenses, purls, cpes, etc.)
  "files": [], // All discovered file nodes (locations, digests, mime types, etc.)
  "relationships": [], // Qualified edges between packages, files, and the source nodes
  "source": {}, // Information about what was scanned (e.g. container image details)
  "distro": {}, // OS distribution details (if applicable)
  "descriptor": {}, // Syft version and configuration
  "schema": {} // Schema version information
}
```

The Syft JSON schema is versioned and available in the Syft repository:

- [Latest JSON schema](https://github.com/anchore/syft/blob/main/schema/json/schema-latest.json)
- [All schema versions](https://github.com/anchore/syft/tree/main/schema/json)

## JQ Recipes

[jq](https://jqlang.org/) is a command-line tool for querying and manipulating JSON.
The following examples demonstrate practical queries for working with Syft JSON output.

Each example includes the jq query and its output when run against a real SBOM.

**Find packages by name pattern:**

Uses regex pattern matching to find security-critical packages

{{< file-tabs
title=""
path="content/docs/user-guides/sbom/snippets/jq-queries/find-package-versions"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Location of all JARs:**

Shows Java packages with their primary installation paths

{{< file-tabs
title=""
path="content/docs/user-guides/sbom/snippets/jq-queries/java-archives-with-paths"
tabs="query|query.md,example|example.md,output|output.md" >}}

**All executable files:**

Lists all binary files with their format and entry point status

{{< file-tabs
title=""
path="content/docs/user-guides/sbom/snippets/jq-queries/all-executables"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Binaries not owned by packages:**

Uses set operations on relationships to identify untracked binaries that might indicate supply chain issues

{{< file-tabs
title=""
path="content/docs/user-guides/sbom/snippets/jq-queries/binaries-not-owned"
tabs="query|query.md,example|example.md,config|config.md,output|output.md" >}}

**Binary file digests:**

Useful for verifying binary integrity and detecting tampering

{{< file-tabs
title=""
path="content/docs/user-guides/sbom/snippets/jq-queries/binary-digests"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Binaries with security features:**

Analyzes ELF security hardening features extracted during SBOM generation

{{< file-tabs
title=""
path="content/docs/user-guides/sbom/snippets/jq-queries/binaries-with-security-features"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Binaries importing specific libraries:**

Identifies which binaries depend on specific shared libraries for security audits

{{< file-tabs
title=""
path="content/docs/user-guides/sbom/snippets/jq-queries/binary-imports"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Extract Package URLs (PURLs):**

Extracts Package URLs for cross-tool SBOM correlation and vulnerability matching

{{< file-tabs
title=""
path="content/docs/user-guides/sbom/snippets/jq-queries/all-purls"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Group packages by language:**

Groups and counts packages by programming language

{{< file-tabs
title=""
path="content/docs/user-guides/sbom/snippets/jq-queries/packages-by-language"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Count packages by type:**

Provides a summary count of packages per ecosystem

{{< file-tabs
title=""
path="content/docs/user-guides/sbom/snippets/jq-queries/count-packages-by-type"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Package locations:**

Maps packages to their filesystem locations

{{< file-tabs
title=""
path="content/docs/user-guides/sbom/snippets/jq-queries/package-locations"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Files by MIME type:**

Filters files by MIME type, useful for finding specific file types

{{< file-tabs
title=""
path="content/docs/user-guides/sbom/snippets/jq-queries/files-by-mime-type"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Dependency relationships:**

Traverses package dependency graph using relationships

{{< file-tabs
title=""
path="content/docs/user-guides/sbom/snippets/jq-queries/dependency-relationships"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Files without packages:**

Finds orphaned files not associated with any package

{{< file-tabs
title=""
path="content/docs/user-guides/sbom/snippets/jq-queries/files-without-packages"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Largest files:**

Identifies the top 10 largest files by size

{{< file-tabs
title=""
path="content/docs/user-guides/sbom/snippets/jq-queries/large-files"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Extract CPEs:**

Lists Common Platform Enumeration identifiers for vulnerability scanning

{{< file-tabs
title=""
path="content/docs/user-guides/sbom/snippets/jq-queries/all-cpes"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Packages without licenses:**

Identifies packages missing license information for compliance audits

{{< file-tabs
title=""
path="content/docs/user-guides/sbom/snippets/jq-queries/packages-without-licenses"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Packages with CPE identifiers:**

Lists packages with CPE identifiers indicating potential CVE matches

{{< file-tabs
title=""
path="content/docs/user-guides/sbom/snippets/jq-queries/packages-with-cves"
tabs="query|query.md,example|example.md,output|output.md" >}}

## Example workflow

Here's a complete example of generating and querying a Syft JSON SBOM:

```bash
# Generate Syft JSON
syft alpine:latest -o json=alpine.json

# Prettify the output for readability
jq '.' alpine.json > alpine-pretty.json

# List all packages
jq -r '.artifacts[] | "\(.name) \(.version)"' alpine.json

# Find security-related packages
jq '.artifacts[] | select(.name | contains("ssl") or contains("crypto"))' alpine.json

# Export to CSV
jq -r '.artifacts[] | [.name, .version, .type] | @csv' alpine.json > packages.csv
```

## Next steps

- Explore [output formats](/docs/user-guides/sbom/formats/) to see all available SBOM formats
- Learn about [format conversion](/docs/user-guides/sbom/conversion/) to generate multiple formats efficiently
- Use [templates](/docs/user-guides/sbom/templates/) to create custom output formats
