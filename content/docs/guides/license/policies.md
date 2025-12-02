+++
title = "Policies"
description = "Configure license compliance policies to automatically enforce allowed licenses and flag violations in your software supply chain."
weight = 30
tags = ["grant", "licenses"]
+++

Grant policies let you define which licenses are acceptable in your projects and automatically flag violations when running `grant check`.

**Default behavior:**

- **Deny all licenses** except those explicitly permitted in the `allow` list
- **Deny packages without licenses** when `require-license` is `true` (the default)
- **Allow non-SPDX licenses** when `require-known-license` is `false` (the default)

You customize this behavior by specifying allowed licenses and other options in a configuration file.

Grant categorizes licenses by risk level based on their copyleft strength:

| Risk       | License type    | Examples             | Implication                   |
| ---------- | --------------- | -------------------- | ----------------------------- |
| **High**   | Strong copyleft | GPL-3.0, AGPL-3.0    | May require source disclosure |
| **Medium** | Weak copyleft   | LGPL-2.1, MPL-2.0    | Obligations for modifications |
| **Low**    | Permissive      | MIT, Apache-2.0, BSD | Attribution only              |

License types affect how software can be used, modified, and distributed. Understanding these categories helps you create effective compliance policies:

- **Strong copyleft** (also called "reciprocal" or "restrictive") licenses require that derivative works are distributed under the same license.
  Any modifications or software that incorporates the code must have its source code made available.
- **Weak copyleft** licenses balance permissive and restrictive terms. They allow linking to open source libraries with limited obligations, making them practical for library code.
- **Permissive** licenses have minimal restrictions on how you can modify or redistribute software. They typically only require you to retain copyright notices and attribution.

## Create a policy file

Grant searches for configuration in this order:

1. File specified with `-c` or `--config` flag
2. Current directory: `grant.yaml`, `.grant.yaml`
3. XDG config: `~/.config/grant/grant.yaml`
4. Home directory: `~/.grant.yaml`

If no configuration is found, Grant uses a deny-all default.

## Policy options

| Option                  | Type       | Default | Description                   |
| ----------------------- | ---------- | ------- | ----------------------------- |
| `allow`                 | `string[]` | `[]`    | License patterns to permit    |
| `ignore-packages`       | `string[]` | `[]`    | Package patterns to skip      |
| `require-license`       | `bool`     | `true`  | Deny packages with no license |
| `require-known-license` | `bool`     | `false` | Deny non-SPDX licenses        |

### `allow`

Specifies which licenses pass compliance checks. Supports glob patterns with `*` as a wildcard. Matching is **case-sensitive**.

```yaml
allow:
  - MIT # Exact match
  - Apache-* # Matches Apache-1.0, Apache-1.1, Apache-2.0
  - BSD-*-Clause # Matches BSD-2-Clause, BSD-3-Clause
  - CC0-* # Matches CC0-1.0
```

A package passes if **any** of its licenses matches the allow list. With an empty allow list, all licenses are denied.

### `ignore-packages`

Skips license evaluation for specific packages. Use this for internal packages or known exceptions you've reviewed. Supports glob patterns with `*`:

```yaml
ignore-packages:
  - "internal-*" # Packages starting with internal-
  - "legacy-component" # Exact match
```

Ignored packages appear with status "ignore" in output and don't affect the exit code.

### `require-license`

When `true` (the default), packages with no detected license are denied. This catches packages with missing metadata that may need investigation.

```yaml
require-license: true
```

Set to `false` if you want to allow packages without license information.

### `require-known-license`

When `true`, only SPDX-recognized license identifiers pass. Custom or unrecognized license strings are denied.

```yaml
require-known-license: true
```

This catches packages with unusual license declarations like "See LICENSE file" or custom proprietary licenses that need review.

## Example policies

### Permissive-only for commercial software

For a SaaS product where you want to avoid any copyleft obligations:

```yaml
# .grant.yaml
allow:
  - MIT
  - Apache-2.0
  - BSD-2-Clause
  - BSD-3-Clause
  - ISC
  - 0BSD
  - Unlicense
  - CC0-1.0

require-license: true
require-known-license: true # Catch unexpected license strings
```

This policy ensures all dependencies use permissive licenses with no source disclosure requirements.

### Internal tooling with exceptions

For internal tools that aren't distributed, you can allow weak copyleft and ignore internal packages:

```yaml
# .grant.yaml
allow:
  # Permissive
  - MIT
  - Apache-2.0
  - BSD-*-Clause
  - ISC

  # Weak copyleft (OK for internal use)
  - LGPL-*
  - MPL-2.0
  - EPL-*

ignore-packages:
  - "github.com/yourcompany/*"
  - "@yourorg/*"

require-license: true
```

## Next steps

- [Getting Started]({{< relref "getting-started" >}}) - Basic Grant usage
- [Configuration Reference]({{< relref "/docs/reference/grant/configuration" >}}) - Full Grant CLI options
- [Open Source Licenses](https://opensource.org/licenses) - License details and OSI approval status
- [Choose a License](https://choosealicense.com/licenses/) - License comparison and selection guide
