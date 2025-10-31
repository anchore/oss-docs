+++
title = "Package Catalogers"
description = "Configure which package catalogers Syft uses to discover software components including language-specific and file-based catalogers."
weight = 50
tags = ["syft", "sbom", "catalogers"]
url = "docs/guides/sbom/catalogers"

+++

{{< alert title="TL;DR" color="primary" >}}

- **Syft automatically picks the right catalogers for you** (recommended for most users)
- **Scanning a container image?** Finds installed packages (like Python packages in `site-packages`)
- **Scanning a directory?** Finds both installed packages and declared dependencies (like `requirements.txt`)
- **Want to customize?** Use `--select-catalogers` to filter, add, or remove catalogers
- **Need complete control?** Use `--override-default-catalogers` to replace all defaults

{{< /alert >}}

Catalogers are Syft's detection modules that identify software packages in your projects.
Each cataloger specializes in finding specific types of packages—for example, `python-package-cataloger` finds Python dependencies declared in `requirements.txt`,
while `python-installed-package-cataloger` finds Python packages that have already been installed.

Syft includes dozens of catalogers covering languages like Python, Java, Go, JavaScript, Ruby, Rust, and more, as well as OS packages (APK, RPM, DEB) and binary formats.

## Default Behavior

Syft uses different cataloger sets depending on what you're scanning:

| Scan Type           | Default Catalogers            | What They Find                             | Example                                                   |
| ------------------- | ----------------------------- | ------------------------------------------ | --------------------------------------------------------- |
| **Container Image** | Image-specific catalogers     | Installed packages only                    | Python packages in `site-packages`                        |
| **Directory**       | Directory-specific catalogers | Installed packages + declared dependencies | Python packages in `site-packages` AND `requirements.txt` |

This behavior ensures accurate results across different contexts. When you scan an image, Syft assumes installation steps
have completed --this way you are getting results for software that is positively present.
When you scan a directory (like a source code repository), Syft looks for both what's installed and what's declared as
a dependency --this way you are getting results for not only what's installed but also what you intend to install.

### Why use different catalogers for different sources?

Most of the time, files that hint at the intent to install software do not have enough information in them to determine the exact version of the package that would be installed.
For example, a `requirements.txt` file might specify a package without a version, or with a version range.
By looking at installed packages in an image, after any build tooling has been invoked, Syft can provide more accurate version information.

### Example: Python Package Detection

Scanning an image:

```bash
$ syft <container-image> --select-catalogers python
# Uses: python-installed-package-cataloger
# Finds: Packages in site-packages directories
```

Scanning a directory:

```bash
$ syft <source-directory> --select-catalogers python
# Uses: python-installed-package-cataloger, python-package-cataloger
# Finds: Packages in site-packages + requirements.txt, setup.py, Pipfile, etc.
```

## Viewing Active Catalogers

The most reliable way to see which catalogers Syft used is to check the SBOM itself. Every SBOM captures both the catalogers that were requested and those that actually ran:

```bash
syft busybox:latest -o json | jq '.descriptor.configuration.catalogers'
```

Output:

```json
{
  "requested": {
    "default": [
      "image",
      "file"
    ]
  },
  "used": [
    "alpm-db-cataloger",
    "apk-db-cataloger",
    "binary-classifier-cataloger",
    "bitnami-cataloger",
    "cargo-auditable-binary-cataloger",
    "conan-info-cataloger",
    "dotnet-deps-binary-cataloger",
    "dotnet-packages-lock-cataloger",
    "dpkg-db-cataloger",
    "elf-binary-package-cataloger",
    ...
  ]
}
```

This shows what catalogers were **attempted**, not just what found packages. The `requested` field shows your cataloger selection strategy, while `used` lists every cataloger that ran.

You can also see cataloger activity in real-time using verbose logging, though this is less comprehensive and not as direct.

## Exploring Available Catalogers

Use the `syft cataloger list` command to see all available catalogers, their tags, and test selection expressions.

### List all catalogers

```bash
syft cataloger list
```

Output shows file and package catalogers with their tags:

```
┌───────────────────────────┬───────────────────────┐
│ FILE CATALOGER            │ TAGS                  │
├───────────────────────────┼───────────────────────┤
│ file-content-cataloger    │ content, file         │
│ file-digest-cataloger     │ digest, file          │
│ file-executable-cataloger │ binary-metadata, file │
│ file-metadata-cataloger   │ file, file-metadata   │
└───────────────────────────┴───────────────────────┘
┌────────────────────────────────────┬────────────────────────────────────────────────────────┐
│ PACKAGE CATALOGER                  │ TAGS                                                   │
├────────────────────────────────────┼────────────────────────────────────────────────────────┤
│ python-installed-package-cataloger │ directory, image, installed, language, package, python │
│ python-package-cataloger           │ declared, directory, language, package, python         │
│ java-archive-cataloger             │ directory, image, installed, java, language, maven     │
│ go-module-binary-cataloger         │ binary, directory, go, golang, image, installed        │
│ ...                                │                                                        │
└────────────────────────────────────┴────────────────────────────────────────────────────────┘
```

### Test cataloger selection

Preview which catalogers a selection expression would use:

```bash
$ syft cataloger list --select-catalogers python
Default selections: 1
  • 'all'
Selection expressions: 1
  • 'python' (intersect)

┌────────────────────────────────────┬────────────────────────────────────────────────────────┐
│ PACKAGE CATALOGER                  │ TAGS                                                   │
├────────────────────────────────────┼────────────────────────────────────────────────────────┤
│ python-installed-package-cataloger │ directory, image, installed, language, package, python │
│ python-package-cataloger           │ declared, directory, language, package, python         │
└────────────────────────────────────┴────────────────────────────────────────────────────────┘
```

This shows exactly which catalogers your selection expression will use, helping you verify your configuration before running a scan.

### Output formats

Get cataloger information in different formats:

```bash
# Table format (default)
$ syft cataloger list

# JSON format (useful for automation)
$ syft cataloger list -o json
```

## Cataloger References

You can refer to catalogers in two ways:

- **By name**: The exact cataloger identifier (e.g., `java-pom-cataloger`, `go-module-binary-cataloger`)
- **By tag**: A group label for related catalogers (e.g., `java`, `python`, `image`, `directory`)

Common tags include:

- **Language tags**: `python`, `java`, `go`, `javascript`, `ruby`, `rust`, etc.
- **Scan type tags**: `image`, `directory`
- **Installation state tags**: `installed`, `declared`
- **Ecosystem tags**: `maven`, `npm`, `cargo`, `composer`, etc.

## Customizing Cataloger Selection

Syft provides two flags for controlling catalogers:

### `--select-catalogers`: Modify Defaults

Use this flag to adjust the default cataloger set. This is the recommended approach for most use cases.

**Syntax:**

| Operation   | Syntax                 | Example                                           | Description                                |
| ----------- | ---------------------- | ------------------------------------------------- | ------------------------------------------ |
| **Filter**  | `<tag>`                | `--select-catalogers java`                        | Use only Java catalogers from the defaults |
| **Add**     | `+<name>`              | `--select-catalogers +sbom-cataloger`             | Add a specific cataloger to defaults       |
| **Remove**  | `-<name-or-tag>`       | `--select-catalogers -rpm`                        | Remove catalogers by name or tag           |
| **Combine** | `<tag>,+<name>,-<tag>` | `--select-catalogers java,+sbom-cataloger,-maven` | Multiple operations together               |

**Selection Logic:**

1. Start with default catalogers (image or directory based)
2. If tags provided (without `+` or `-`), filter to only those tagged catalogers
3. Remove any catalogers matching `-<name-or-tag>`
4. Add any catalogers specified with `+<name>`

{{< alert title="Note" color="primary" >}}
Added catalogers (prefixed with `+`) are always included, regardless of other filters or removals.
{{< /alert >}}

### `--override-default-catalogers`: Replace Defaults

Use this flag to completely replace Syft's default cataloger selection. This bypasses the automatic image vs. directory behavior.

**Syntax:**

```bash
--override-default-catalogers <comma-separated-names-or-tags>
```

**When to use:**

- You need catalogers from both image and directory sets
- You want to use catalogers that aren't in the default set
- You need precise control regardless of scan type

{{< alert title="Warning" color="warning" >}}
Overriding defaults can lead to incomplete or inaccurate results if you don't include all necessary catalogers. Use `--select-catalogers` for most cases.
{{< /alert >}}

## Examples by Use Case

### Filtering to Specific Languages

Scan for only Python packages using defaults for your scan type:

```bash
syft <target> --select-catalogers python
```

Scan for only Java and Go packages:

```bash
syft <target> --select-catalogers java,go
```

### Adding Catalogers

Use defaults and also include the SBOM cataloger (which finds embedded SBOMs):

```bash
syft <target> --select-catalogers +sbom-cataloger
```

Scan with defaults plus both SBOM and binary catalogers:

```bash
syft <target> --select-catalogers +sbom-cataloger,+binary-cataloger
```

### Removing Catalogers

Use defaults but exclude all RPM-related catalogers:

```bash
syft <target> --select-catalogers -rpm
```

Scan with defaults but remove Java JAR cataloger specifically:

```bash
syft <target> --select-catalogers -java-archive-cataloger
```

### Combining Operations

Scan for Go packages, always include SBOM cataloger, but exclude binary analysis:

```bash
$ syft <container-image> --select-catalogers go,+sbom-cataloger,-binary
# Result: go-module-binary-cataloger, sbom-cataloger
# (binary cataloger excluded even though it's in go tag)
```

Filter to Java, add POM cataloger, remove Gradle:

```bash
syft <directory> --select-catalogers java,+java-pom-cataloger,-gradle
```

### Complete Override Examples

Use only binary analysis catalogers regardless of scan type:

```bash
$ syft <target> --override-default-catalogers binary
# Result: binary-cataloger, cargo-auditable-binary-cataloger,
#         dotnet-portable-executable-cataloger, go-module-binary-cataloger
```

Use exactly two specific catalogers:

```bash
syft <target> --override-default-catalogers go-module-binary-cataloger,go-module-file-cataloger
```

Use all directory catalogers even when scanning an image:

```bash
syft <container-image> --override-default-catalogers directory
```

## Troubleshooting

### My language isn't being detected

Check which catalogers ran and whether they found packages:

```bash
# See which catalogers were used
$ syft <target> -o json | jq '.descriptor.configuration.catalogers.used'

# See which catalogers found packages
$ syft <target> -o json | jq '.artifacts[].foundBy'

# See packages found by a specific cataloger
$ syft <target> -o json | jq '.artifacts[] | select(.foundBy == "python-package-cataloger") | .name'
```

If your expected cataloger isn't in the `used` list:

1. **Verify the cataloger exists for your scan type**: Use `syft cataloger list --select-catalogers <tag>` to preview
2. **Check your selection expressions**: You may have excluded it with `-` or not included it in your filter
3. **Check file locations**: Some catalogers look for specific paths (e.g., `site-packages` for Python)

If the cataloger ran but found nothing, check that:

- Package files exist in the scanned source
- Files are properly formatted
- Files are in the expected locations for that cataloger

### How do I know if I'm using image or directory defaults?

Check the SBOM's cataloger configuration:

```bash
syft <target> -o json | jq '.descriptor.configuration.catalogers.requested'
```

This shows the selection strategy used:

- `"default": ["image", "file"]` indicates image defaults
- `"default": ["directory", "file"]` indicates directory defaults

### What's the difference between a name and a tag?

- **Name**: The unique identifier for a single cataloger (e.g., `python-package-cataloger`)
- **Tag**: A label that groups multiple catalogers (e.g., `python` includes both `python-package-cataloger` and `python-installed-package-cataloger`)

Use tags when you want to downselect from the default catalogers, and names when you need to target a specific cataloger.

### Why use --select-catalogers vs --override-default-catalogers?

- **`--select-catalogers`**: Respects Syft's automatic image/directory behavior, safer for most use cases
- **`--override-default-catalogers`**: Ignores scan type, gives complete control, requires more knowledge

When in doubt, use `--select-catalogers`.

## Technical Reference

For reference, here's the formal logic Syft uses for cataloger selection:

```text
image_catalogers = all_catalogers AND catalogers_tagged("image")

directory_catalogers = all_catalogers AND catalogers_tagged("directory")

default_catalogers = image_catalogers OR directory_catalogers

sub_selected_catalogers = default_catalogers INTERSECT catalogers_tagged(TAG) [ UNION sub_selected_catalogers ... ]

base_catalogers = default_catalogers OR sub_selected_catalogers

final_set = (base_catalogers SUBTRACT removed_catalogers) UNION added_catalogers
```

This logic applies when using `--select-catalogers`. The `--override-default-catalogers` flag bypasses the default cataloger selection entirely and starts with the specified catalogers instead.

## Next steps

{{< alert title="Continue the guide" color="success" >}}
**Next**: Learn about [File Selection](/docs/guides/sbom/file-selection/) to control which files and directories Syft scans during cataloging.
{{< /alert >}}

Additional resources:

- **Reference**: See the [ecosystem capabilities](/docs/capabilities/) for detailed information about package detection and vulnerability matching
- **Configuration**: Check [configuration options](/docs/reference/syft/configuration) for persistent cataloger settings
- **Filter files**: Use [File Selection](/docs/guides/sbom/file-selection) to exclude irrelevant paths before cataloging
