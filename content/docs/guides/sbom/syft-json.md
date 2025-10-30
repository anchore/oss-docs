+++
title = "Working with Syft JSON"
description = "Learn how to work with Syft's native JSON format including querying with jq, extracting metadata, and understanding the SBOM structure."
weight = 45
tags = ["syft", "sbom", "json", "jq"]
url = "docs/guides/sbom/syft-json"
+++

Syft's native JSON format provides the most comprehensive view of discovered software components, capturing all package metadata, file details, relationships, and source information.

Since Syft can [convert from its native JSON format to standard SBOM formats](/docs/guides/sbom/conversion/),
capturing your SBOM in Syft JSON format lets you generate any SBOM format as needed for compliance requirements.

{{< alert title="JSON Schema Reference" color="primary" >}}
For the complete, detailed JSON schema specification, see the [Syft JSON Schema Reference](/docs/reference/syft/json/latest).
{{< /alert >}}

## Data Shapes

A Syft JSON output contains these main sections:

```json
{
  "artifacts": [], // Package nodes discovered
  "artifactRelationships": [], // Edges between packages and files
  "files": [], // File nodes discovered
  "source": {}, // What was scanned (the image, directory, etc.)
  "distro": {}, // Linux distribution discovered
  "descriptor": {}, // Syft version and configuration that captured this SBOM
  "schema": {} // Schema version
}
```

### Package (artifacts)

A software package discovered by Syft (library, application, OS package, etc.).

```json
{
  "id": "74d9294c42941b37", // Unique identifier for this package that is content addressable
  "name": "openssl",
  "version": "1.1.1k",
  "type": "apk", // Package ecosystem (apk, deb, npm, etc.)
  "foundBy": "apk-cataloger",
  "locations": [
    // Paths used to populate information on this package object
    {
      "path": "/lib/apk/db/installed", // Always the real-path
      "layerID": "sha256:...",
      "accessPath": "/lib/apk/db/installed", // How Syft accessed the file (may be a symlink)
      "annotations": {
        "evidence": "primary" // Qualifies the kind of evidence extracted from this location (primary, supporting)
      }
    }
  ],
  "licenses": [
    {
      "value": "Apache-2.0", // Raw value discovered
      "spdxExpression": "Apache-2.0", // Normalized SPDX expression of the discovered value
      "type": "declared", // "declared", "concluded", or "observed"
      "urls": ["https://..."],
      "locations": [] // Where license was found
    }
  ],
  "language": "c",
  "cpes": [
    {
      "cpe": "cpe:2.3:a:openssl:openssl:1.1.1k:*:*:*:*:*:*:*",
      "source": "nvd-dictionary" // Where the CPE was derived from (nvd-dictionary or syft-generated)
    }
  ],
  "purl": "pkg:apk/alpine/openssl@1.1.1k",
  "metadata": {} // Ecosystem-specific fields (varies by type)
}
```

### File

A file found on disk or referenced in package manager metadata.

```json
{
  "id": "def456",
  "location": {
    "path": "/usr/bin/example",
    "layerID": "sha256:..." // For container images
  },
  "metadata": {
    "mode": 493, // File permissions in octal
    "type": "RegularFile",
    "mimeType": "application/x-executable",
    "size": 12345 // Size in bytes
  },
  "digests": [
    {
      "algorithm": "sha256",
      "value": "abc123..."
    }
  ],
  "licenses": [
    {
      "value": "Apache-2.0", // Raw value discovered
      "spdxExpression": "Apache-2.0", // Normalized SPDX expression of the discovered value
      "type": "declared", // "declared", "concluded", or "observed"
      "evidence": {
        "confidence": 100,
        "offset": 1234, // Byte offset in file
        "extent": 567 // Length of match
      }
    }
  ],
  "executable": {
    "format": "elf", // "elf", "pe", or "macho"
    "hasExports": true,
    "hasEntrypoint": true,
    "importedLibraries": [
      // Shared library dependencies
      "libc.so.6",
      "libssl.so.1.1"
    ],
    "elfSecurityFeatures": {
      // ELF binaries only
      "symbolTableStripped": false,
      "stackCanary": true, // Stack protection
      "nx": true, // No-Execute bit
      "relRO": "full", // Relocation Read-Only
      "pie": true // Position Independent Executable
    }
  }
}
```

### Relationship

Connects any two nodes (package, file, or source) with a typed relationship.

```json
{
  "parent": "package-id", // Package, file, or source ID
  "child": "file-id",
  "type": "contains" // contains, dependency-of, etc.
}
```

### Source

Information about what was scanned (container image, directory, file, etc.).

```json
{
  "id": "sha256:...",
  "name": "alpine:3.9.2", // User input
  "version": "sha256:...",
  "type": "image", // image, directory, file
  "metadata": {
    "imageID": "sha256:...",
    "manifestDigest": "sha256:...",
    "mediaType": "application/vnd.docker...",
    "tags": ["alpine:3.9.2"],
    "repoDigests": []
  }
}
```

### Distribution

Linux distribution details from `/etc/os-release` or similar sources.

```json
{
  "name": "alpine",
  "version": "3.9.2",
  "idLike": ["alpine"] // Related distributions
}
```

### Location

Describes where a package or file was found.

```json
{
  "path": "/lib/apk/db/installed",
  "layerID": "sha256:...",
  "accessPath": "/var/lib/apk/installed",
  "annotations": {
    "evidence": "primary"
  }
}
```

The `path` field always contains the real path after resolving symlinks, while `accessPath` shows how Syft accessed the file (which may be through a symlink).

The `evidence` annotation indicates whether this location was used to discover the package (`primary`) or contains only auxiliary information (`supporting`).

### Descriptor

Syft version and configuration used to generate this SBOM.

```json
{
  "name": "syft",
  "version": "1.0.0",
  "configuration": {} // Syft configuration used
}
```

The Syft JSON schema is versioned and available in the Syft repository:

- [Latest JSON schema](https://github.com/anchore/syft/blob/main/schema/json/schema-latest.json)
- [All schema versions](https://github.com/anchore/syft/tree/main/schema/json)

## JQ Recipes

[jq](https://jqlang.org/) is a command-line tool for querying and manipulating JSON.
The following examples demonstrate practical queries for working with Syft JSON output.

**Find packages by name pattern:**

Uses regex pattern matching to find security-critical packages

{{< file-tabs
title=""
path="content/docs/guides/sbom/snippets/jq-queries/find-package-versions"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Location of all JARs:**

Shows Java packages with their primary installation paths

{{< file-tabs
title=""
path="content/docs/guides/sbom/snippets/jq-queries/java-archives-with-paths"
tabs="query|query.md,example|example.md,output|output.md" >}}

**All executable files:**

Lists all binary files with their format and entry point status

{{< file-tabs
title=""
path="content/docs/guides/sbom/snippets/jq-queries/all-executables"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Binaries not owned by packages:**

Uses set operations on relationships to identify untracked binaries that might indicate supply chain issues

{{< file-tabs
title=""
path="content/docs/guides/sbom/snippets/jq-queries/binaries-not-owned"
tabs="query|query.md,example|example.md,config|config.md,output|output.md" >}}

**Binary file digests:**

Useful for verifying binary integrity and detecting tampering

{{< file-tabs
title=""
path="content/docs/guides/sbom/snippets/jq-queries/binary-digests"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Binaries with security features:**

Analyzes ELF security hardening features extracted during SBOM generation

{{< file-tabs
title=""
path="content/docs/guides/sbom/snippets/jq-queries/binaries-with-security-features"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Binaries importing specific libraries:**

Identifies which binaries depend on specific shared libraries for security audits

{{< file-tabs
title=""
path="content/docs/guides/sbom/snippets/jq-queries/binary-imports"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Extract Package URLs (PURLs):**

Extracts Package URLs for cross-tool SBOM correlation and vulnerability matching

{{< file-tabs
title=""
path="content/docs/guides/sbom/snippets/jq-queries/all-purls"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Group packages by language:**

Groups and counts packages by programming language

{{< file-tabs
title=""
path="content/docs/guides/sbom/snippets/jq-queries/packages-by-language"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Count packages by type:**

Provides a summary count of packages per ecosystem

{{< file-tabs
title=""
path="content/docs/guides/sbom/snippets/jq-queries/count-packages-by-type"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Package locations:**

Maps packages to their filesystem locations

{{< file-tabs
title=""
path="content/docs/guides/sbom/snippets/jq-queries/package-locations"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Files by MIME type:**

Filters files by MIME type, useful for finding specific file types

{{< file-tabs
title=""
path="content/docs/guides/sbom/snippets/jq-queries/files-by-mime-type"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Dependency relationships:**

Traverses package dependency graph using relationships

{{< file-tabs
title=""
path="content/docs/guides/sbom/snippets/jq-queries/dependency-relationships"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Files without packages:**

Finds orphaned files not associated with any package

{{< file-tabs
title=""
path="content/docs/guides/sbom/snippets/jq-queries/files-without-packages"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Largest files:**

Identifies the top 10 largest files by size

{{< file-tabs
title=""
path="content/docs/guides/sbom/snippets/jq-queries/large-files"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Extract CPEs:**

Lists Common Platform Enumeration identifiers for vulnerability scanning

{{< file-tabs
title=""
path="content/docs/guides/sbom/snippets/jq-queries/all-cpes"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Packages without licenses:**

Identifies packages missing license information for compliance audits

{{< file-tabs
title=""
path="content/docs/guides/sbom/snippets/jq-queries/packages-without-licenses"
tabs="query|query.md,example|example.md,output|output.md" >}}

**Packages with CPE identifiers:**

Lists packages with CPE identifiers indicating potential CVE matches

{{< file-tabs
title=""
path="content/docs/guides/sbom/snippets/jq-queries/packages-with-cves"
tabs="query|query.md,example|example.md,output|output.md" >}}

## Troubleshooting

### jq command not found

Install jq to query JSON output:

- **macOS**: `brew install jq`
- **Ubuntu/Debian**: `apt-get install jq`
- **Fedora/RHEL**: `dnf install jq`
- **Windows**: Download from [jqlang.org](https://jqlang.org/)

### Empty or unexpected query results

Common jq query issues:

- **Wrong field path**: Use `jq 'keys'` to list available top-level keys, then explore nested structures
- **Missing select filter**: Remember to use `select()` when filtering (e.g., `.artifacts[] | select(.type=="apk")`)
- **String vs array**: Some fields like licenses are arrays; use `.[0]` or iterate with `.[]`

### Query works in terminal but not in scripts

When using jq in shell scripts:

- **Quote properly**: Single quotes prevent shell variable expansion (e.g., `jq '.artifacts'` not `jq ".artifacts"`)
- **Escape for heredocs**: Use different quotes or escape when embedding jq in heredocs
- **Pipe errors**: Add `set -o pipefail` to catch jq errors in pipelines

### Performance issues with large SBOMs

For very large JSON files:

- **Stream processing**: Use jq's `--stream` flag for memory-efficient processing
- **Filter early**: Apply filters as early as possible in the pipeline to reduce data volume
- **Use specific queries**: Avoid `.[]` on large arrays; be specific about what you need

## Next steps

{{< alert title="Continue the guide" color="success" >}}
**Next**: Dive into [Package Catalogers](/docs/guides/sbom/catalogers/) to understand how Syft discovers different types of software packages.
{{< /alert >}}

Additional resources:

- **Other formats**: Explore [output formats](/docs/guides/sbom/formats/) to see all available SBOM formats
- **Convert formats**: Learn about [format conversion](/docs/guides/sbom/conversion/) to generate multiple formats efficiently
- **Custom output**: Use [templates](/docs/guides/sbom/templates/) to create custom output formats
- **Syft JSON Schema**: Review the [Syft JSON Schema Reference](/docs/reference/syft/json/latest) for detailed field definitions
