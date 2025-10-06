+++
title = "File Selection"
description = "Control which files and directories Syft includes or excludes when generating SBOMs."
weight = 55
tags = ["syft", "sbom"]
url = "docs/guides/sbom/file-selection"

+++

By default, Syft catalogs file details and digests for files owned by discovered packages. You can change this behavior using the `SYFT_FILE_METADATA_SELECTION` environment variable or the `file.metadata.selection` configuration option.

**Available options:**

- `all`: capture all files from the search space
- `owned-by-package`: capture only files owned by packages _(default)_
- `none`: disable file information capture

## Excluding file paths

You can exclude specific files and paths from scanning using glob patterns with the `--exclude` parameter. Use multiple `--exclude` flags to specify multiple patterns.

```bash
# Exclude a specific directory
syft <source> --exclude /etc

# Exclude files by pattern
syft <source> --exclude './out/**/*.json'

# Combine multiple exclusions
syft <source> --exclude './out/**/*.json' --exclude /etc --exclude '**/*.log'
```

{{< alert title="Tip" color="primary" >}}
Always wrap glob patterns in single quotes to prevent your shell from expanding wildcards:

```bash
syft <source> --exclude '**/*.json'  # Correct
syft <source> --exclude **/*.json    # May not work as expected
```

{{< /alert >}}

### Exclusion behavior by source type

How Syft interprets exclusion patterns depends on whether you're scanning an image or a directory.

#### Image scanning

When scanning container images, Syft scans the entire filesystem. Use absolute paths for exclusions:

```bash
# Exclude system directories
syft alpine:latest --exclude /etc --exclude /var

# Exclude files by pattern across entire filesystem
syft alpine:latest --exclude '/usr/**/*.txt'
```

#### Directory scanning

When scanning directories, Syft resolves exclusion patterns relative to the specified directory. All exclusion patterns must begin with `./`, `*/`, or `**/`.

```bash
# Scanning /usr/foo
syft /usr/foo --exclude ./package.json        # Excludes /usr/foo/package.json
syft /usr/foo --exclude '**/package.json'     # Excludes all package.json files under /usr/foo
syft /usr/foo --exclude './out/**'            # Excludes everything under /usr/foo/out
```

**Path prefix requirements for directory scans:**

| Pattern | Meaning                         | Example           |
| ------- | ------------------------------- | ----------------- |
| `./`    | Relative to scan directory root | `./config.json`   |
| `*/`    | One level of directories        | `*/temp`          |
| `**/`   | Any depth of directories        | `**/node_modules` |

{{< alert title="Note" color="info" >}}
When scanning directories, you cannot use absolute paths like `/etc` or `/usr/**/*.txt`. The pattern must begin with `./`, `*/`, or `**/` to be resolved relative to your specified scan directory.
{{< /alert >}}

### Common exclusion patterns

```bash
# Exclude all JSON files
syft <source> --exclude '**/*.json'

# Exclude build output directories
syft <source> --exclude '**/dist/**' --exclude '**/build/**'

# Exclude dependency directories
syft <source> --exclude '**/node_modules/**' --exclude '**/vendor/**'

# Exclude test files
syft <source> --exclude '**/*_test.go' --exclude '**/test/**'
```
