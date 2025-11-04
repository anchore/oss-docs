+++
title = "File Selection"
description = "Control which files and directories Syft includes or excludes when generating SBOMs."
weight = 55
tags = ["syft", "sbom"]
url = "docs/guides/sbom/file-selection"

+++

{{< alert title="TL;DR" color="primary" >}}

- By default, Syft includes information about files owned by packages into the SBOM
- **Select which files to include**: `file.metadata.selection` can be one of `all`, `none`, or `owned-by-package`
- **Exclude paths and globs**: `--exclude '**/node_modules/**'`

{{< /alert >}}

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

{{< alert title="Note" color="primary" >}}
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

## FAQ

**Why is my exclusion pattern not working?**

Common issues:

- **Missing quotes**: Wrap patterns in single quotes to prevent shell expansion (`'**/*.json'` not `**/*.json`)
- **Wrong path prefix**: Directory scans require `./`, `*/`, or `**/` prefix; absolute paths like `/etc` won't work
- **Pattern syntax**: Use glob syntax, not regex (e.g., `**/*.txt` not `.*\.txt`)

**What's the difference between `owned-by-package` and `all` file metadata?**

- **`owned-by-package`** (default): Only catalogs files that belong to discovered packages (e.g., files in an RPM's file manifest)
- **`all`**: Catalogs every file in the scan space, which significantly increases SBOM size and scan time

Use `all` when you need complete file listings for compliance or audit purposes.

**Can I exclude directories based on .gitignore?**

Not directly, but you can convert `.gitignore` patterns to `--exclude` flags. Note that `.gitignore` syntax differs from glob patterns, so you may need to adjust patterns (e.g., `node_modules/` becomes `**/node_modules/**`).

**Do exclusions affect package detection?**

Yes! If you exclude a file that a cataloger needs (like `package.json` or `requirements.txt`), Syft won't detect packages from that file. Exclude carefully to avoid missing dependencies.

## Next steps

{{< alert title="Continue the guide" color="success" url="/docs/guides/sbom/templates/" >}}
**Next**: Learn about [Using Templates](/docs/guides/sbom/templates/) to create custom SBOM output formats tailored to your specific needs.
{{< /alert >}}

Additional resources:

- **Configure catalogers**: See [Package Catalogers](/docs/guides/sbom/catalogers/) to control which package types are detected
- **Configuration file**: Use [Configuration](/docs/reference/syft/configuration) to set persistent exclusion patterns
- **Source types**: Review [Supported Sources](/docs/guides/sbom/sources/) to understand scanning behavior for different source types
