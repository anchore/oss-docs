# Documentation Generation Scripts

This directory contains Python scripts that generate documentation content for Anchore's open source tools (Syft, Grype, Grant).

## Clean State Principle

All generation follows a **clean state principle**: scripts automatically clean their output directories before regeneration to ensure no stale content remains when script configurations change.

**Single Source of Truth:** All output paths are defined in `utils/config.py` via the `paths` dataclass. Scripts import these paths and self-clean, ensuring path definitions exist in exactly one place.

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

## How Scripts Self-Clean

Each script cleans its output directory automatically at startup:

```python
from utils.config import paths

# Every script uses paths from single source of truth
output_path = paths.format_examples_snippet_dir  # or whatever path it needs

# Clean before generation
if output_path.exists():
    logger.debug(f"Cleaning output directory: {output_path}")
    shutil.rmtree(output_path)
output_path.mkdir(parents=True, exist_ok=True)
```

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

| Script | Output Path Variable | Notes |
|--------|---------------------|-------|
| `generate_format_examples.py` | `paths.format_examples_snippet_dir` | Self-cleans |
| `generate_jq_query_examples.py` | `paths.jq_queries_snippet_dir` | Self-cleans |
| `generate_template_examples.py` | `paths.templates_snippet_dir` | Self-cleans |
| `generate_capability_package_tables.py` | `paths.capabilities_snippet_dir` | Cleans (runs first) |
| `generate_capability_vulnerability_tables.py` | `paths.capabilities_snippet_dir` | Shared dir (relies on package script) |
| `generate_format_versions.py` | `paths.format_versions_snippet` | Single file (overwrites) |
| Reference scripts | CLI args specify path | Single files (overwrite) |

## Task-Based Workflow

The recommended way to run generation is via Taskfile:

```bash
# Generate all documentation (scripts auto-clean)
task generate

# Generate with cache updates
task generate:update
```

The `generate` task runs all generation scripts in sequence. Each script automatically cleans its output directory before generating new content.

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
✅ **No stale content** - Scripts auto-clean before generation
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

### Generate Release Notes

Pull release notes for all open source repos:

```bash
scripts/generate-release-notes.sh
```

Or for individual repos:

```bash
python scripts/release-to-hugo.py --repo syft --output-dir content/docs/releases/syft --weight 10
```

The `--weight` parameter controls menu positioning (lower = higher in menu).

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

2. **Add self-cleaning to script:**
   ```python
   from utils.config import paths

   def main(...):
       # Clean output directory at startup
       if paths.your_snippet_dir.exists():
           shutil.rmtree(paths.your_snippet_dir)
       paths.your_snippet_dir.mkdir(parents=True, exist_ok=True)
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
# Test individual script (auto-cleans its output)
uv run ./scripts/generate_format_examples.py -vv

# Test full workflow (each script auto-cleans)
task generate -v

# Verify clean state by running twice
task generate
git status  # Should show no changes after second run
```
