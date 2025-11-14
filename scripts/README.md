# Documentation Generation Scripts

This directory contains Python scripts that generate documentation content for Anchore's open source tools (Syft, Grype, Grant).

## Clean State Principle

Generation scripts follow a **clean state principle** to ensure no stale content remains when configurations change:

- Scripts using the `--update` flag trigger **conditional cleaning** via `output_manager.clean_directory()` (removes entire output directory)
- Capability scripts perform **selective cleaning** via `html_table.clean_owned_files()` (removes only script-owned files)

**Single Source of Truth:** All output paths are defined in `utils/config.py` via the `paths` dataclass. Scripts import these paths, ensuring path definitions exist in exactly one place.

## Generation Scripts

### SBOM Format Examples

**Script:** `generate_format_examples.py`
**Output:** `content/docs/guides/sbom/snippets/format/examples/`
**Purpose:** Generate example outputs for all supported SBOM formats (JSON, SPDX, CycloneDX, etc.)

```bash
uv run ./scripts/generate_format_examples.py [--update] [-v]
```

### SBOM Format Versions

**Script:** `generate_format_versions.py`
**Output:** `content/docs/guides/sbom/snippets/format/versions.md`
**Purpose:** Generate table showing supported versions for each SBOM format

```bash
uv run ./scripts/generate_format_versions.py [--update] [-v]
```

### JQ Query Examples

**Script:** `generate_jq_query_examples.py`
**Output:** `content/docs/guides/sbom/snippets/jq-queries/`
**Purpose:** Generate executable jq query examples with real outputs

```bash
uv run ./scripts/generate_jq_query_examples.py [--update] [-v]
```

### Template Examples

**Script:** `generate_template_examples.py`
**Output:** `content/docs/guides/sbom/snippets/templates/`
**Purpose:** Generate Syft template examples with rendered outputs

```bash
uv run ./scripts/generate_template_examples.py [--update] [-v]
```

### Package Capability Tables

**Script:** `generate_capability_package_tables.py`
**Output:** `content/docs/capabilities/snippets/`
**Purpose:** Generate tables showing Syft's package detection capabilities per ecosystem

```bash
uv run ./scripts/generate_capability_package_tables.py [--update] [-v]
```

### Vulnerability Capability Tables

**Script:** `generate_capability_vulnerability_tables.py`
**Output:** `content/docs/capabilities/snippets/`
**Purpose:** Generate tables showing Grype's vulnerability detection capabilities and OS support

```bash
uv run ./scripts/generate_capability_vulnerability_tables.py [--update] [-v]
```

### Reference Documentation

**Scripts:**
- `generate_reference_cli_docs.py` → CLI command reference
- `generate_reference_config_docs.py` → Configuration file reference

**Output:** `content/docs/reference/{tool}/`

```bash
uv run ./scripts/generate_reference_cli_docs.py anchore/syft:latest --output ./content/docs/reference/syft/cli.md --tool-name syft
uv run ./scripts/generate_reference_config_docs.py anchore/syft:latest --output ./content/docs/reference/syft/config.md --tool-name syft
```

### Syft JSON Schema Reference

**Script:** `generate_reference_syft_json_schema.py`
**Output:** `content/docs/reference/syft/json/`
**Purpose:** Generate reference documentation for Syft's JSON schema versions

```bash
uv run ./scripts/generate_reference_syft_json_schema.py [--schema-dir <path>] [--update] [-v]
```

Creates versioned schema documentation pages from Syft's JSON schema files.

## Utility Scripts

### Link Converter

**Script:** `convert_links_to_relref.py`
**Purpose:** Convert markdown links to Hugo relref shortcodes for build-time link validation

This is a one-time utility script for converting existing documentation links to Hugo's relref format.

### Hugo Validation

**Script:** `validate-hugo.sh`
**Purpose:** Run comprehensive Hugo validation checks for CI/testing

Validates:
- Successful Hugo build
- Front matter consistency
- Content structure
- Shortcode usage
- Menu weights

## How Scripts Clean Output

Scripts use two different cleaning strategies depending on their needs:

### Strategy 1: Conditional Directory Cleaning

Most generation scripts use `output_manager.clean_directory()` which **only cleans when `--update` is provided**:

```python
from utils.config import paths
from utils.output_manager import clean_directory

output_path = paths.format_examples_snippet_dir  # from single source of truth

# Cleans entire directory only if --update flag is set
clean_directory(output_path, update=args.update, logger=logger)
```

**Scripts using this strategy:**
- `generate_format_examples.py`
- `generate_jq_query_examples.py`
- `generate_template_examples.py`

### Strategy 2: Selective File Cleaning

Capability scripts use `html_table.clean_owned_files()` which **always removes script-owned files** (those with auto-generated markers):

```python
from utils.config import paths
from utils.html_table import clean_owned_files

# Remove only files owned by this script (unconditional)
clean_owned_files(paths.capabilities_snippet_dir, script_name, logger)
```

**Scripts using this strategy:**
- `generate_capability_package_tables.py` (cleans before all capability scripts)
- `generate_capability_vulnerability_tables.py`

### Output Path Definitions

All paths are defined in `scripts/utils/config.py`:

```python
@dataclass(frozen=True)
class Paths:
    # Snippet directories
    format_examples_snippet_dir: Path = snippets_dir / "format" / "examples"
    jq_queries_snippet_dir: Path = snippets_dir / "jq-queries"
    templates_snippet_dir: Path = snippets_dir / "templates"
    capabilities_snippet_dir: Path = docs_dir / "capabilities" / "snippets"
    # ... more paths
```

### Directory Ownership

| Script | Output Path Variable | Cleaning Strategy |
|--------|---------------------|-------------------|
| `generate_format_examples.py` | `paths.format_examples_snippet_dir` | Conditional (on `--update`) |
| `generate_jq_query_examples.py` | `paths.jq_queries_snippet_dir` | Conditional (on `--update`) |
| `generate_template_examples.py` | `paths.templates_snippet_dir` | Conditional (on `--update`) |
| `generate_format_versions.py` | `paths.format_versions_snippet` | Single file (overwrites) |
| `generate_capability_package_tables.py` | `paths.capabilities_snippet_dir` | Selective (always, owned files) |
| `generate_capability_vulnerability_tables.py` | `paths.capabilities_snippet_dir` | Selective (always, owned files) |
| `generate_reference_syft_json_schema.py` | `paths.syft_json_schema_reference_dir` | Creates versioned files |
| Reference CLI/config scripts | CLI args specify path | Single files (overwrite) |

## Task-Based Workflow

The recommended way to run generation is via Taskfile:

```bash
# Generate all documentation
task generate

# Generate with cache updates (triggers conditional cleaning)
task generate:update
```

The `generate` task runs all generation scripts in sequence. The `generate:update` variant passes `--update` to scripts, triggering conditional cleaning of output directories.

## Cache Management

Generation scripts use caches to avoid re-running expensive operations:

**Cache Location:** `data/{category}/*/sbom-cache/`
**Cache Control:** Use `--update` flag to regenerate caches

```bash
# Use existing caches
task generate

# Force cache updates
task generate:update
```

**Note:** Caches are gitignored via `data/.gitignore` (`**/sbom-cache/`)

## Benefits of This Approach

✅ **Single source of truth** - All paths defined in `utils/config.py`
✅ **Controlled cleaning** - Scripts clean output strategically (conditional or selective)
✅ **No duplication** - Taskfile doesn't know about paths
✅ **Self-contained scripts** - Each script manages its own outputs
✅ **Simple workflow** - `task generate` just runs scripts
✅ **Cache control** - Separate cache management via `--update` flag

## Auto-Generated Markers

All generated files include a header comment:

```html
<!-- AUTO-GENERATED by scripts/{script-name}.py -- DO NOT MANUALLY EDIT -->
```

This serves as both documentation and a marker for automated tooling.

## Maintenance Scripts

### Update OSS Adopters Page

The `/docs/about/adopters/` page can be regenerated periodically:

```bash
pip install requests packaging
./scripts/generate-adopters-info.sh
```

**Note:** Release notes generation has been removed from this repository. Release notes are now managed through a different process.

## Development

### Adding a New Generator

When creating a new generation script:

1. **Define output path in `utils/config.py`:**
   ```python
   @dataclass(frozen=True)
   class Paths:
       # Add your new path
       your_snippet_dir: Path = snippets_dir / "your-section"
   ```

2. **Add cleaning to script (choose strategy):**

   **Option A: Conditional directory cleaning** (for most scripts):
   ```python
   from utils.config import paths
   from utils.output_manager import clean_directory

   def main(update: bool, ...):
       # Clean only when --update is provided
       clean_directory(paths.your_snippet_dir, update=update, logger=logger)
   ```

   **Option B: Selective file cleaning** (for shared directories):
   ```python
   from utils.config import paths
   from utils.html_table import clean_owned_files

   def main(...):
       # Remove only files owned by this script (always)
       clean_owned_files(paths.your_snippet_dir, "your_script.py", logger)
   ```

3. **Add to Taskfile:**
   - Define command variable in `vars` section
   - Add command to `default` and `update` task lists

4. **Include generated marker:**
   ```python
   from utils.config import get_generated_comment

   comment = get_generated_comment("scripts/your_script.py", "html")
   ```

5. **Support cache updates:**
   - Add `--update` flag via Click
   - Pass to data-fetching functions

### Testing Generation

```bash
# Test individual script (with verbose output)
uv run ./scripts/generate_format_examples.py -vv

# Test individual script with cleaning
uv run ./scripts/generate_format_examples.py --update -vv

# Test full workflow
task generate -v

# Test full workflow with cleaning and cache updates
task generate:update -v

# Verify idempotency by running twice
task generate
git status  # Should show no changes after second run
```
