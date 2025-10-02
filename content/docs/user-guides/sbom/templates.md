+++
title = "Using Templates"
description = "Create custom SBOM output formats using Go templates with available data fields to build tailored reports for specific tooling or compliance requirements."
weight = 60
tags = ["syft", "sbom", "templates"]
url = "docs/user-guides/sbom/templates"
+++

Syft lets you define custom output formats using [Go templates](https://pkg.go.dev/text/template). This is useful for generating custom reports, integrating with specific tools, or extracting only the data you need.

## How to use templates

Set the output format to `template` and specify the template file path:

```bash
syft <image> -o template -t ./path/to/custom.tmpl
```

You can also configure the template path in your [configuration file](/docs/reference/commands/syft-config/):

```yaml
#.syft.yaml
format:
  template:
    path: "/path/to/template.tmpl"
```

## Available fields

Templates receive the same data structure as the `syft-json` output format. The [Syft JSON schema](https://github.com/anchore/syft/blob/main/schema/json/schema-latest.json) is the source of truth for all available fields and their structure.

To see what data is available:

```bash
# View the full JSON structure
syft <image> -o json

# Explore specific fields
syft <image> -o json | jq '.artifacts[0]'
```

Key fields commonly used in templates:

- `.artifacts` - Array of discovered packages
- `.files` - Array of discovered files
- `.source` - Information about what was scanned
- `.distro` - Detected Linux distribution (if applicable)
- `.descriptor` - Syft version and configuration

Common package (artifact) fields:

- `.name`, `.version`, `.type` - Basic package info
- `.licenses` - License information (array)
- `.purl` - Package URL
- `.cpes` - Common Platform Enumerations
- `.locations` - Where the package was found

## Template functions

Syft templates support:

- **Go template built-ins** - See the [Go template documentation](https://pkg.go.dev/text/template#hdr-Functions)
- **Sprig functions** - Additional helpers from [Sprig](http://masterminds.github.io/sprig/)
- **Syft-specific functions:**

| Function       | Arguments      | Description                                                                      |
| -------------- | -------------- | -------------------------------------------------------------------------------- |
| `getLastIndex` | `collection`   | Returns the last index of a slice (length - 1), useful for comma-separated lists |
| `hasField`     | `obj`, `field` | Checks if a field exists on an object, returns boolean                           |

## Examples

The following examples show template source code and the rendered output when run against `alpine:3.9.2`:

### CSV output

{{< file-tabs
title=""
path="content/docs/user-guides/sbom/snippets/templates/csv"
tabs="template|template.md,output|output.md" >}}

### Filter by package type

{{< file-tabs
title=""
path="content/docs/user-guides/sbom/snippets/templates/filter-package-type"
tabs="template|template.md,output|output.md" >}}

### Markdown report

{{< file-tabs
title=""
path="content/docs/user-guides/sbom/snippets/templates/markdown-report"
tabs="template|template.md,output|output.md" >}}

### License compliance

{{< file-tabs
title=""
path="content/docs/user-guides/sbom/snippets/templates/license-compliance"
tabs="template|template.md,output|output.md" >}}

### Custom JSON subset

{{< file-tabs
title=""
path="content/docs/user-guides/sbom/snippets/templates/json-subset"
tabs="template|template.md,output|output.md" >}}

### Executable file digests

{{< file-tabs
title=""
path="content/docs/user-guides/sbom/snippets/templates/executable-digests"
tabs="template|template.md,output|output.md" >}}

### Find binaries importing a library

{{< file-tabs
title=""
path="content/docs/user-guides/sbom/snippets/templates/libcrypto-imports"
tabs="template|template.md,output|output.md" >}}

## Troubleshooting

**"can't evaluate field" errors:** The field doesn't exist or is misspelled. Check field names with `syft <image> -o json | jq`.

**Empty output:** Verify your field paths are correct. Use `syft <image> -o json` to see the actual data structure.

**Template syntax errors:** Refer to the [Go template documentation](https://pkg.go.dev/text/template) for syntax help.

{{< alert title="Note" color="info" >}}
If you have templates from before Syft v0.102.0 that no longer work, set `format.template.legacy: true` in your configuration. This uses internal Go structs instead of the JSON output schema.

Long-term support for this legacy option is not guaranteed.
{{< /alert >}}

## Additional resources

- [Go template documentation](https://pkg.go.dev/text/template) - Template syntax reference
- [Sprig function documentation](http://masterminds.github.io/sprig/) - Helper functions
- [Output formats](/docs/user-guides/sbom/formats/) - Other output format options
- [Configuration options](/docs/reference/commands/syft-config/) - Advanced settings
