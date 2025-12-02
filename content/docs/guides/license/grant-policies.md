+++
title = "Grant Policies"
description = "Configure license compliance policies to automatically enforce allowed licenses and flag violations in your software supply chain."
weight = 30
tags = ["grant", "licenses"]
+++

Grant policies let you define which licenses are acceptable in your projects and automatically flag violations. This is essential for organizations managing legal risk across their software supply chain.

## How policies work

By default, Grant uses a **deny-all policy**. Any license found triggers a violation. You customize this by specifying allowed licenses in a configuration file.

When you run `grant check`, Grant:

1. Scans the target for all packages and their licenses
2. Compares each license against your allow list
3. Reports violations and exits with code 1 if any are found

## Create a policy file

Generate a sample configuration file:

```bash
grant config
```

This creates `.grant.yaml` in your current directory. Grant searches for configuration in these locations (in order):

1. `./.grant.yaml`
2. `./.grant/config.yaml`
3. `~/.grant.yaml`
4. `$XDG_CONFIG_HOME/grant/config.yaml`

## Basic policy configuration

A minimal policy specifies allowed licenses:

```yaml
allow:
  - MIT
  - Apache-2.0
  - BSD-2-Clause
  - BSD-3-Clause
  - ISC
```

With this configuration, `grant check` passes only if all detected licenses match the allow list.

## Allow license patterns

Use glob patterns to allow families of licenses:

```yaml
allow:
  - MIT
  - Apache-*       # Matches Apache-1.0, Apache-1.1, Apache-2.0
  - BSD-*-Clause   # Matches BSD-2-Clause, BSD-3-Clause
  - CC0-*          # Matches CC0-1.0
```

## Ignore specific packages

Some packages may have licenses you can't change but have determined are acceptable for your use case. Ignore them by package name:

```yaml
allow:
  - MIT
  - Apache-2.0

ignore-packages:
  - "github.com/internal/*"    # Internal packages
  - "legacy-component"          # Known acceptable exception
```

## Require license presence

Packages without detected licenses can indicate missing metadata or proprietary code. Configure how Grant handles these:

```yaml
# Fail if any package has no license detected
require-license: true

# Fail if license isn't a recognized SPDX identifier
require-known-license: false
```

Setting `require-license: true` ensures you don't accidentally include packages with unclear licensing.

## Example: Permissive-only policy

A common enterprise policy allows only permissive licenses:

```yaml
# .grant.yaml - Permissive licenses only
allow:
  - MIT
  - Apache-2.0
  - BSD-2-Clause
  - BSD-3-Clause
  - ISC
  - Unlicense
  - CC0-1.0
  - 0BSD

require-license: true

ignore-packages:
  - "internal/*"
```

## Example: Allow weak copyleft

Some organizations permit weak copyleft for dynamically linked libraries:

```yaml
# .grant.yaml - Permissive + weak copyleft
allow:
  # Permissive
  - MIT
  - Apache-2.0
  - BSD-*-Clause
  - ISC

  # Weak copyleft (acceptable for dynamic linking)
  - LGPL-*
  - MPL-2.0
  - EPL-*

require-license: true
require-known-license: true
```

## Run compliance checks

Check a container image against your policy:

```bash
grant check alpine:latest
```

Check an SBOM file:

```bash
grant check sbom.spdx.json
```

Pipe from Syft for a combined workflow:

```bash
syft alpine:latest -o json | grant check
```

## Interpret results

`grant check` exits with:

- **Exit code 0:** All licenses comply with policy
- **Exit code 1:** Violations found or an error occurred

For detailed violation information, use verbose output:

```bash
grant check alpine:latest --verbose
```

Or output as JSON for programmatic processing:

```bash
grant check alpine:latest -o json
```

## CI/CD integration

Add license compliance to your pipeline:

```yaml
# GitHub Actions example
- name: Check license compliance
  run: |
    syft ${{ env.IMAGE }} -o json > sbom.json
    grant check sbom.json
```

```yaml
# GitLab CI example
license-check:
  script:
    - syft ${CI_REGISTRY_IMAGE}:${CI_COMMIT_SHA} -o json > sbom.json
    - grant check sbom.json
```

The non-zero exit code fails the pipeline when violations are detected.

## Find unlicensed packages

Identify packages missing license information:

```bash
grant list alpine:latest --unlicensed
```

Or in check mode:

```bash
grant check alpine:latest --unlicensed
```

This helps you track down packages that need license clarification.

## Show only non-SPDX licenses

Find packages with unrecognized license identifiers:

```bash
grant list alpine:latest --non-spdx
```

These may need manual review to determine the actual license.

## FAQ

**How do I start with a new policy?**

Begin with permissive-only licenses and add more as needed. It's easier to relax restrictions than to enumerate all problematic licenses upfront.

**Should I document package exceptions?**

Yes. When adding packages to `ignore-packages`, document why they're acceptable in comments or a separate document for future reference.

**How often should I review my policy?**

Review periodically since license metadata changes. Audit your allow list and ignored packages at least quarterly.

**When should I run compliance checks?**

Integrate `grant check` into CI/CD pipelines to catch issues before they reach production. Use `grant list` during development for visibility.

## Next steps

- [Types of Licenses]({{< relref "types-of-licenses" >}}) - Understand license categories and risk levels
- [Getting Started]({{< relref "getting-started" >}}) - Basic Grant usage
- [Configuration Reference]({{< relref "/docs/reference/grant/configuration" >}}) - Full configuration options
