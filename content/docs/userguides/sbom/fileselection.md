+++
title = "File Selection"
description = "SBOM Generation File Selection"
weight = 30
tags = ["syft", "sbom"]
url = "docs/userguides/sbom/fileselection"

+++

## File selection

By default, Syft will catalog file details and digests for files that are owned by discovered packages. You can change this behavior by using the `SYFT_FILE_METADATA_SELECTION` environment variable or the `file.metadata.selection` configuration option. The options are:

- `all`: capture all files from the search space
- `owned-by-package`: capture only files owned by packages (default)
- `none`: disable capturing any file information

## Excluding file paths

Syft can exclude files and paths from being scanned within a source by using glob expressions
with one or more `--exclude` parameters:

```
syft <source> --exclude './out/**/*.json' --exclude /etc
```

**Note:** in the case of _image scanning_, since the entire filesystem is scanned it is
possible to use absolute paths like `/etc` or `/usr/**/*.txt` whereas _directory scans_
exclude files _relative to the specified directory_. For example: scanning `/usr/foo` with
`--exclude ./package.json` would exclude `/usr/foo/package.json` and `--exclude '**/package.json'`
would exclude all `package.json` files under `/usr/foo`. For _directory scans_,
it is required to begin path expressions with `./`, `*/`, or `**/`, all of which
will be resolved _relative to the specified scan directory_. Keep in mind, your shell
may attempt to expand wildcards, so put those parameters in single quotes, like:
`'**/*.json'`.