#!/usr/bin/env python3
"""
Generate jq query example documentation with real outputs.
Runs Syft to generate SBOMs, then executes jq queries and creates markdown files.
"""

import subprocess
import sys
from pathlib import Path
from typing import cast

import click
import yaml
from utils import config, log, markdown, output_manager, sbom


@click.command()
@click.option(
    "--examples-dir",
    default=str(config.paths.jq_query_examples_dir),
    help=f"Directory containing YAML example definitions (default: {config.paths.jq_query_examples_dir})",
)
@click.option(
    "--output-dir",
    default=str(config.paths.jq_queries_snippet_dir),
    help=f"Output directory for generated examples (default: {config.paths.jq_queries_snippet_dir})",
)
@click.option(
    "--syft-image",
    default=config.docker_images.syft,
    help=f"Syft Docker image to use (default: {config.docker_images.syft})",
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
    logger = log.setup(verbose, __file__)

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

    # Clean and prepare directories
    output_manager.clean_directory(output_path, update=update, logger=logger)
    output_manager.ensure_directory(cache_dir)

    # Process each example
    skipped_count = 0
    generated_count = 0

    for example_file in example_files:
        example_name = example_file.stem
        logger.debug(f"Processing: {example_name}")

        try:
            was_generated = generate_example(
                example_file=example_file,
                example_name=example_name,
                output_dir=output_path,
                cache_dir=cache_dir,
                syft_image=syft_image,
                update=update,
            )
            if was_generated:
                logger.debug(f"  ✓ Generated {example_name}")
                generated_count += 1
            else:
                logger.debug(f"  ⊚ Skipping {example_name} (up-to-date)")
                skipped_count += 1
        except Exception as e:
            logger.error(f"  ✗ Failed to generate {example_name}: {e}")
            sys.exit(1)

    # Log summary
    if skipped_count > 0:
        logger.info(
            f"JQ query examples: {generated_count} generated, {skipped_count} skipped (up-to-date)"
        )
    else:
        logger.info(f"All examples generated successfully in {output_path}")


def generate_example(
    example_file: Path,
    example_name: str,
    output_dir: Path,
    cache_dir: Path,
    syft_image: str,
    update: bool = False,
) -> bool:
    """
    Generate markdown files for a single jq query example.

    Returns:
        True if example was generated, False if skipped (up-to-date)
    """
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
    output_manager.ensure_directory(example_dir)

    # Define output files
    query_md = example_dir / "query.md"
    example_md = example_dir / "example.md"
    output_md = example_dir / "output.md"

    # Build list of source files
    config_file = example_file.parent / config if config else None
    cache_key = output_manager.get_cache_key(image, config_file)
    sbom_cache = cache_dir / f"{cache_key}.json"

    source_files = [example_file, sbom_cache]
    if config_file and config_file.exists():
        source_files.append(config_file)

    # Check if outputs need regeneration
    if not output_manager.should_regenerate_multiple(
        [query_md, example_md, output_md], source_files, update
    ):
        return False

    # Import sbom utility for SBOM generation

    # Generate or retrieve SBOM
    sbom_json = cast(
        str,
        sbom.get_or_generate(
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
    query_md = markdown.create_code_fence(query, "python")
    (example_dir / "query.md").write_text(query_md)

    # Generate example.md - full copy-pastable command using piped input
    # Strip comments from query for the example command
    query_no_comments = strip_comments(query)
    example_md = markdown.create_code_fence(
        f"syft {image} -o json | \\\n  jq '{query_no_comments}'", "bash"
    )
    (example_dir / "example.md").write_text(example_md)

    # Generate config.md if a config is specified
    if config:
        config_path = example_file.parent / config
        if config_path.exists():
            config_content = config_path.read_text()
            config_md = markdown.create_code_fence(
                f"# .syft.yaml\n{config_content}", "yaml"
            )
            (example_dir / "config.md").write_text(config_md)

    # Run jq query and generate output.md
    output = run_jq_query(sbom_json, query)

    # Truncate output if it exceeds 200 lines
    output_lines = output.split("\n")
    if len(output_lines) > 200:
        output = "\n".join(output_lines[:200]) + "\n...\n"

    # detect output format
    output_format = markdown.detect_format(output)

    output_md = markdown.create_code_fence(output, output_format)
    (example_dir / "output.md").write_text(output_md)

    return True


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
            timeout=config.timeouts.jq_query,
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
            f"jq command timed out after {config.timeouts.jq_query} seconds"
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


if __name__ == "__main__":
    main()
