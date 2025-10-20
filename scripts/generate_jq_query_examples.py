#!/usr/bin/env python3
"""
Generate jq query example documentation with real outputs.
Runs Syft to generate SBOMs, then executes jq queries and creates markdown files.
"""

import shutil
import subprocess
import sys
from pathlib import Path
from typing import cast

import click
import yaml
from utils.config import docker_images, paths, timeouts
from utils.logging import setup_logging
from utils.sbom import get_or_generate_sbom


@click.command()
@click.option(
    "--examples-dir",
    default=str(paths.jq_query_examples_dir),
    help=f"Directory containing YAML example definitions (default: {paths.jq_query_examples_dir})",
)
@click.option(
    "--output-dir",
    default=str(paths.jq_queries_snippet_dir),
    help=f"Output directory for generated examples (default: {paths.jq_queries_snippet_dir})",
)
@click.option(
    "--syft-image",
    default=docker_images.syft,
    help=f"Syft Docker image to use (default: {docker_images.syft})",
)
@click.option(
    "--update",
    is_flag=True,
    help="Update the SBOM cache even if it already exists",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity (use -v for info, -vv for debug)",
)
def main(
    examples_dir: str,
    output_dir: str,
    syft_image: str,
    update: bool,
    verbose: int,
) -> None:
    """Generate jq query example documentation."""
    logger = setup_logging(verbose, __file__)

    examples_path = Path(examples_dir)
    output_path = Path(output_dir)

    # use convention: cache is always sbom-cache subdirectory of examples dir
    cache_dir = examples_path / "sbom-cache"

    if not examples_path.exists():
        logger.error(f"Examples directory not found: {examples_path}")
        sys.exit(1)

    # Find all YAML example files
    example_files = sorted(examples_path.glob("*.yaml"))
    if not example_files:
        logger.error(f"No .yaml files found in {examples_path}")
        sys.exit(1)

    logger.info(f"Found {len(example_files)} example(s) in {examples_path}")
    logger.debug(f"Using Syft image: {syft_image}")

    # Clean output directory to remove stale examples
    if output_path.exists():
        logger.debug(f"Cleaning output directory: {output_path}")
        shutil.rmtree(output_path)

    # Create output and cache directories
    output_path.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Process each example
    for example_file in example_files:
        example_name = example_file.stem
        logger.debug(f"Processing: {example_name}")

        try:
            generate_example(
                example_file=example_file,
                example_name=example_name,
                output_dir=output_path,
                cache_dir=cache_dir,
                syft_image=syft_image,
                update=update,
            )
            logger.debug(f"  ✓ Generated {example_name}")
        except Exception as e:
            logger.error(f"  ✗ Failed to generate {example_name}: {e}")
            sys.exit(1)

    logger.info(f"All examples generated successfully in {output_path}")


def generate_example(
    example_file: Path,
    example_name: str,
    output_dir: Path,
    cache_dir: Path,
    syft_image: str,
    update: bool = False,
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
    config_file = example_file.parent / config if config else None
    sbom_json = cast(
        str,
        get_or_generate_sbom(
            image=image,
            cache_dir=cache_dir,
            syft_image=syft_image,
            update=update,
            config_file=config_file,
            return_content=True,
        ),
    )

    # Generate query.md - just the jq expression
    # there is no jq support... python is the closest (see https://gohugo.io/content-management/syntax-highlighting/#languages)
    query_md = f"```python\n{query}\n```\n"
    (example_dir / "query.md").write_text(query_md)

    # Generate example.md - full copy-pastable command using piped input
    # Strip comments from query for the example command
    query_no_comments = strip_comments(query)
    example_md = (
        f"```bash\nsyft {image} -o json | \\\n  jq '{query_no_comments}'\n```\n"
    )
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
            timeout=timeouts.jq_query,
        )

        if result.returncode != 0:
            raise RuntimeError(f"jq command failed: {result.stderr}")

        output = result.stdout.strip()

        # if output is empty, return a message
        if not output:
            return "(no results)"

        return output

    except subprocess.TimeoutExpired as e:
        raise RuntimeError(
            f"jq command timed out after {timeouts.jq_query} seconds"
        ) from e
    except FileNotFoundError as e:
        raise RuntimeError("jq not found. Please install jq to run this script.") from e
    except Exception as e:
        raise RuntimeError(f"Failed to run jq: {e}") from e


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
