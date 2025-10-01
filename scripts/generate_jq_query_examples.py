#!/usr/bin/env python3
"""
Generate jq query example documentation with real outputs.
Runs Syft to generate SBOMs, then executes jq queries and creates markdown files.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate jq query example documentation"
    )
    parser.add_argument(
        "--examples-dir",
        default="data/sbom/jq-query-examples",
        help="Directory containing YAML example definitions",
    )
    parser.add_argument(
        "--output-dir",
        default="content/docs/user-guides/sbom/snippets/jq-queries",
        help="Output directory for generated examples",
    )
    parser.add_argument(
        "--syft-image",
        default="anchore/syft:latest",
        help="Syft Docker image to use (default: anchore/syft:latest)",
    )
    parser.add_argument(
        "--cache-dir",
        default="data/sbom/jq-query-examples/sbom-cache",
        help="Directory to cache generated SBOMs",
    )

    args = parser.parse_args()

    examples_dir = Path(args.examples_dir)
    output_dir = Path(args.output_dir)
    cache_dir = Path(args.cache_dir)

    if not examples_dir.exists():
        print(f"Error: Examples directory not found: {examples_dir}", file=sys.stderr)
        sys.exit(1)

    # Find all YAML example files
    example_files = sorted(examples_dir.glob("*.yaml"))
    if not example_files:
        print(f"Error: No .yaml files found in {examples_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(example_files)} example(s) in {examples_dir}")
    print(f"Using Syft image: {args.syft_image}")

    # Clean output directory to remove stale examples
    if output_dir.exists():
        print(f"Cleaning output directory: {output_dir}")
        shutil.rmtree(output_dir)

    # Create output and cache directories
    output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Process each example
    for example_file in example_files:
        example_name = example_file.stem
        print(f"\nProcessing: {example_name}")

        try:
            generate_example(
                example_file=example_file,
                example_name=example_name,
                output_dir=output_dir,
                cache_dir=cache_dir,
                syft_image=args.syft_image,
            )
            print(f"  ✓ Generated {example_name}")
        except Exception as e:
            print(f"  ✗ Failed to generate {example_name}: {e}", file=sys.stderr)
            sys.exit(1)

    print(f"\n✓ All examples generated successfully in {output_dir}")


def generate_example(
    example_file: Path,
    example_name: str,
    output_dir: Path,
    cache_dir: Path,
    syft_image: str,
) -> None:
    """Generate markdown files for a single jq query example."""
    # Load example definition
    with open(example_file) as f:
        example = yaml.safe_load(f)

    image = example.get("image")
    config = example.get("config")
    query = example.get("query")

    if not image:
        raise ValueError(f"Missing 'image' in {example_file}")
    if not query:
        raise ValueError(f"Missing 'query' in {example_file}")

    # Create example directory
    example_dir = output_dir / example_name
    example_dir.mkdir(parents=True, exist_ok=True)

    # Generate or retrieve SBOM
    sbom_json = get_or_generate_sbom(
        image=image,
        config=config,
        cache_dir=cache_dir,
        syft_image=syft_image,
        examples_dir=example_file.parent,
    )

    # Generate query.md - just the jq expression
    # there is no jq support... python is the closest (see https://gohugo.io/content-management/syntax-highlighting/#languages)
    query_md = f"```python\n{query}\n```\n"
    (example_dir / "query.md").write_text(query_md)

    # Generate example.md - full copy-pastable command using piped input
    # Strip comments from query for the example command
    query_no_comments = strip_comments(query)
    example_md = f"```bash\nsyft {image} -o json | \\\n  jq '{query_no_comments}'\n```\n"
    (example_dir / "example.md").write_text(example_md)

    # Generate config.md if a config is specified
    if config:
        config_path = example_file.parent / config
        if config_path.exists():
            config_content = config_path.read_text()
            config_md = f"```yaml\n# .syft.yaml\n{config_content}```\n"
            (example_dir / "config.md").write_text(config_md)

    # Run jq query and generate output.md
    output = run_jq_query(sbom_json, query)

    # Truncate output if it exceeds 200 lines
    output_lines = output.split("\n")
    if len(output_lines) > 200:
        output = "\n".join(output_lines[:200]) + "\n...\n"

    # try to detect output format
    output_format = detect_output_format(output)

    output_md = f"```{output_format}\n{output}\n```\n"
    (example_dir / "output.md").write_text(output_md)


def get_or_generate_sbom(
    image: str,
    config: str | None,
    cache_dir: Path,
    syft_image: str,
    examples_dir: Path = Path("data/sbom/jq-query-examples"),
) -> str:
    """Get SBOM from cache or generate it using Syft."""
    # create cache key from image and config
    cache_key = f"{image.replace(':', '_').replace('/', '_')}"
    if config:
        cache_key += f"_{Path(config).stem}"
    cache_file = cache_dir / f"{cache_key}.json"

    # check cache
    if cache_file.exists():
        print(f"  Using cached SBOM: {cache_file}")
        return cache_file.read_text()

    # generate SBOM
    print(f"  Generating SBOM for: {image}")
    sbom_json = run_syft(image, config, syft_image, examples_dir)

    # save to cache
    cache_file.write_text(sbom_json)
    print(f"  Cached SBOM to: {cache_file}")

    return sbom_json


def run_syft(image: str, config: str | None, syft_image: str, examples_dir: Path, timeout: int = 120) -> str:
    """Run Syft to generate an SBOM in JSON format."""
    docker_cmd = ["docker", "run", "--rm"]

    # mount config if provided
    if config:
        config_path = (examples_dir / config).resolve()
        if not config_path.exists():
            raise ValueError(f"Config file not found: {config_path}")
        docker_cmd.extend(["-v", f"{config_path}:/config.yaml:ro"])

    docker_cmd.extend([syft_image, image, "-o", "syft-json"])

    if config:
        docker_cmd.extend(["-c", "/config.yaml"])

    try:
        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Syft command failed: {result.stderr or result.stdout}"
            )

        return result.stdout.strip()

    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Syft command timed out after {timeout} seconds")
    except Exception as e:
        raise RuntimeError(f"Failed to run Syft: {e}")


def run_jq_query(sbom_json: str, query: str) -> str:
    """Execute a jq query against SBOM JSON and return the output."""
    # extract just the jq expression from the query (strip jq command and sbom.json)
    # the query from YAML might be formatted like:
    # jq '.artifacts[] | \n    select(...) | \n    ...' \n    sbom.json
    # we need to extract just the jq expression
    jq_expr = extract_jq_expression(query)

    try:
        result = subprocess.run(
            ["jq", jq_expr],
            input=sbom_json,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            raise RuntimeError(f"jq command failed: {result.stderr}")

        output = result.stdout.strip()

        # if output is empty, return a message
        if not output:
            return "(no results)"

        return output

    except subprocess.TimeoutExpired:
        raise RuntimeError("jq command timed out after 30 seconds")
    except FileNotFoundError:
        raise RuntimeError("jq not found. Please install jq to run this script.")
    except Exception as e:
        raise RuntimeError(f"Failed to run jq: {e}")


def strip_comments(query: str) -> str:
    """Remove comments from a jq query for copy-pastable examples."""
    lines = query.split("\n")
    cleaned_lines = []
    for line in lines:
        # Remove comments (everything after #)
        # But be careful with # inside strings
        comment_pos = line.find("#")
        if comment_pos != -1:
            # Simple heuristic: if there's a quote before the #, it might be in a string
            # For now, just strip everything after # (we can make this smarter if needed)
            line = line[:comment_pos].rstrip()
        if line.strip():  # Only include non-empty lines
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def extract_jq_expression(query: str) -> str:
    """Extract the jq expression, handling various formats.

    The query from YAML is just the jq expression without wrapping.
    """
    # Strip comments for execution
    return strip_comments(query).strip()


def detect_output_format(output: str) -> str:
    """Detect the output format for syntax highlighting."""
    if output == "(no results)":
        return "text"

    # try to parse as JSON (if starts with { or [)... we can't parse it since it might be truncated
    if output.startswith("{") or output.startswith("["):
        return "json"

    # check if it looks like CSV
    lines = output.split("\n")
    if len(lines) > 1 and all("," in line for line in lines[:3]):
        return "csv"

    # default to text
    return "text"


if __name__ == "__main__":
    main()
