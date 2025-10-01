+++
title = "Working with Syft JSON"
description = "Learn how to work with Syft's native JSON format including querying with jq, extracting metadata, and understanding the SBOM structure."
weight = 45
tags = ["syft", "sbom", "json", "jq"]
url = "docs/user-guides/sbom/syft-json"
+++

Syft's native JSON format contains the most complete information extracted during SBOM generation. This format captures all package metadata, file details, relationships, and source information that Syft discovers.

## Why use Syft JSON?

- **Complete data**: Contains all information Syft extracted, unlike standard formats that may omit some fields
- **Conversion source**: Best format to convert from when you need multiple SBOM formats
- **Automation-friendly**: Structured data ideal for CI/CD pipelines and custom tooling
- **Queryable**: Easy to filter and extract specific information using tools like `jq`

## Schema reference

The Syft JSON schema is versioned and available in the Syft repository:

- [Latest JSON schema](https://github.com/anchore/syft/blob/main/schema/json/schema-latest.json)
- [All schema versions](https://github.com/anchore/syft/tree/main/schema/json)

## Basic structure

A Syft JSON SBOM contains these main sections:

```json
{
  "artifacts": [],        // All discovered packages
  "files": [],           // File metadata (locations, digests)
  "secrets": [],         // Detected secrets (if enabled)
  "source": {},          // Information about what was scanned
  "distro": {},          // OS distribution details (if applicable)
  "descriptor": {},      // Syft version and configuration
  "schema": {}           // Schema version information
}
```

## Working with jq

[jq](https://jqlang.org/) is a command-line tool for querying and manipulating JSON. It's the most common way to work with Syft JSON output.

### Installation

{{< tabpane lang="bash">}}
{{% tab header="Platform:" disabled=true /%}}
{{< tab header="macOS" >}}brew install jq{{< /tab >}}
{{% tab header="Linux (Debian/Ubuntu)"%}}sudo apt-get install jq{{% /tab %}}
{{% tab header="Linux (RHEL/Fedora)"%}}sudo yum install jq{{% /tab %}}
{{< /tabpane >}}

For other platforms, see the [jq download page](https://jqlang.org/download/).

### Common queries

**List all package names:**

```bash
jq '.artifacts[].name' sbom.json
```

**Find packages by type:**

```bash
# Python packages only
jq '.artifacts[] | select(.type == "python") | {name, version}' sbom.json

# NPM packages only
jq '.artifacts[] | select(.type == "npm") | {name, version}' sbom.json
```

**Extract specific package details:**

```bash
# Get all package names and versions
jq '.artifacts[] | "\(.name)@\(.version)"' sbom.json

# Get packages with licenses
jq '.artifacts[] | select(.licenses != null) | {name, licenses}' sbom.json
```

**Filter by version patterns:**

```bash
# Find packages with specific version
jq '.artifacts[] | select(.version | startswith("1.2"))' sbom.json
```

**Count packages by type:**

```bash
jq '[.artifacts[].type] | group_by(.) | map({type: .[0], count: length})' sbom.json
```

**Extract CPEs:**

```bash
jq '.artifacts[] | select(.cpes != null) | {name, cpes}' sbom.json
```

**Get source information:**

```bash
# What was scanned
jq '.source' sbom.json

# Image metadata (if scanning a container)
jq '.source.metadata' sbom.json
```

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

## Converting to other formats

Syft JSON is the recommended source format when you need to generate multiple SBOM formats:

```bash
# Generate Syft JSON first
syft <source> -o json=sbom.json

# Convert to other formats as needed
syft convert sbom.json -o spdx-json=sbom.spdx.json
syft convert sbom.json -o cyclonedx-json=sbom.cdx.json
```

Learn more about [format conversion](/docs/user-guides/sbom/conversion/).

## CI/CD integration

Syft JSON works well in automated pipelines:

```yaml
# Example GitHub Actions workflow
- name: Generate SBOM
  run: syft . -o json=sbom.json

- name: Check for GPL licenses
  run: |
    if jq -e '.artifacts[] | select(.licenses[]?.value | contains("GPL"))' sbom.json; then
      echo "GPL license found!"
      exit 1
    fi

- name: Upload SBOM artifact
  uses: actions/upload-artifact@v3
  with:
    name: sbom
    path: sbom.json
```

## Next steps

- Explore [output formats](/docs/user-guides/sbom/formats/) to see all available SBOM formats
- Learn about [format conversion](/docs/user-guides/sbom/conversion/) to generate multiple formats efficiently
- Use [templates](/docs/user-guides/sbom/templates/) to create custom output formats
