# jq Query Examples

This directory contains YAML definition files for jq query examples used in the documentation.

## File Format

Each `.yaml` file defines a single query example with the following structure:

```yaml
description: "Human-readable description of what the query does"
image: "docker-image:tag"  # Docker image to scan with Syft
config: null  # Optional: path to Syft config file (relative to repo root)
query: 'jq query expression'
```

## Generating Documentation

To generate the documentation snippets from these examples:

```bash
python3 src/generate_jq_query_examples.py
```

This script will:
1. Generate SBOMs for each unique image using Syft (running in Docker)
2. Cache SBOMs in `.cache/sboms/` for reuse
3. Execute each jq query against the appropriate SBOM
4. Generate markdown files in `content/docs/guides/sbom/snippets/jq-queries/`

Each example creates a subdirectory with:
- `description.md` - Human-readable explanation (if provided)
- `query.md` - The jq query in a bash code fence
- `output.md` - Real output from running the query

## Adding New Examples

1. Create a new `.yaml` file in this directory
2. Fill in the required fields (`image` and `query` are required)
3. Run the generation script
4. Add a reference to the new example in `content/docs/guides/sbom/json.md` using the `file-tabs` shortcode

Example:

```markdown
**My new query:**

{{< file-tabs
title=""
path="content/docs/guides/sbom/snippets/jq-queries/my-new-query"
tabs="query|query.md,output|output.md" >}}
```

## Notes

- The script uses Docker to run Syft, ensuring consistent results
- SBOMs are cached to speed up regeneration
- If you need to regenerate with fresh SBOMs, delete the `.cache/sboms/` directory
- Complex jq queries that reference the root document should use `. as $root` pattern
- Query output is automatically formatted as JSON, CSV, or text based on content
