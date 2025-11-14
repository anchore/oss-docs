# Scripts

> **Note:** Python scripts have been moved to the `src/` directory following Python packaging conventions. See `../src/README.md` for documentation generation scripts.

This directory contains shell scripts for automation tasks related to the documentation site.

## Shell Scripts

### Hugo Validation

**Script:** `validate-hugo.sh`
**Purpose:** Run comprehensive Hugo validation checks for CI/testing

Validates:
- Successful Hugo build
- Front matter consistency
- Content structure
- Shortcode usage
- Menu weights

```bash
./scripts/validate-hugo.sh
```

### Update OSS Adopters Page

**Script:** `generate-adopters-info.sh`
**Purpose:** Generate the `/docs/about/adopters/` page with organizations using Anchore OSS tools

The adopters page can be regenerated periodically:

```bash
pip install requests packaging
./scripts/generate-adopters-info.sh
```

This script uses the `github-dependents-info` tool to find repositories that depend on Anchore's open source projects and generates a Hugo-compatible markdown page.
