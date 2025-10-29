#!/usr/bin/env python3
"""
Generate SBOM format examples by running Syft against a sample image.
Creates markdown files with code fences for each format.
"""

import sys
from pathlib import Path
from typing import cast

import click
from utils import config, log, markdown, output_manager, sbom, syft

# Format definitions: (format_name, file_extension, code_fence_language)
FORMATS = [
    ("table", "txt", ""),
    ("json", "json", "json"),
    ("purls", "txt", ""),
    ("cyclonedx-json", "json", "json"),
    ("cyclonedx-xml", "xml", "xml"),
    ("spdx-json", "json", "json"),
    ("spdx-tag-value", "txt", ""),
    ("github-json", "json", "json"),
    ("text", "txt", ""),
]


@click.command()
@click.option(
    "--image",
    default=config.docker_images.busybox_test,
    help=f"Container image to scan (default: {config.docker_images.busybox_test})",
)
@click.option(
    "--syft-image",
    default=config.docker_images.syft,
    help=f"Syft container image to use (default: {config.docker_images.syft})",
)
@click.option(
    "--output-dir",
    "-o",
    default=str(config.paths.format_examples_snippet_dir),
    help=f"Output directory for format examples (default: {config.paths.format_examples_snippet_dir})",
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
    image: str, syft_image: str, output_dir: str, update: bool, verbose: int
) -> None:
    """Generate SBOM format examples using Syft."""
    logger = log.setup(verbose, __file__)

    logger.info(f"Generating format examples for {image} using {syft_image}...")

    # Clean and prepare output directory
    output_path = Path(output_dir)
    output_manager.clean_directory(output_path, update=update, logger=logger)

    # use convention: cache is always sbom-cache subdirectory of template dir
    # the format examples are in snippets/format/examples, so we need to go up to data/sbom
    cache_dir = config.paths.sbom_data_dir / "format-examples" / "sbom-cache"
    output_manager.ensure_directory(cache_dir)

    # Generate or retrieve SBOM from cache
    sbom_file = cast(
        Path,
        sbom.get_or_generate(
            image=image,
            cache_dir=cache_dir,
            syft_image=syft_image,
            update=update,
        ),
    )

    # Generate examples for each format
    skipped_count = 0
    generated_count = 0

    for format_name, _, fence_lang in FORMATS:
        output_file = output_path / f"{format_name}.md"

        # Check if output needs regeneration
        if not output_manager.should_regenerate(
            output_file, [sbom_file], update=update
        ):
            logger.debug(f"  ⊚ Skipping {format_name}.md (up-to-date)")
            skipped_count += 1
            continue

        logger.debug(f"Generating {format_name} example...")
        try:
            generate_format_example(
                sbom_file=sbom_file,
                syft_image=syft_image,
                format_name=format_name,
                fence_lang=fence_lang,
                output_path=output_file,
            )
            logger.debug(f"  ✓ Generated {format_name}.md")
            generated_count += 1
        except Exception as e:
            logger.error(f"  ✗ Error generating {format_name}: {e}")
            sys.exit(1)

    # Log summary
    if skipped_count > 0:
        logger.info(
            f"Format examples: {generated_count} generated, {skipped_count} skipped (up-to-date)"
        )
    else:
        logger.info(
            f"Successfully generated {len(FORMATS)} format examples in {output_path}"
        )


def generate_format_example(
    sbom_file: Path,
    syft_image: str,
    format_name: str,
    fence_lang: str,
    output_path: Path,
) -> None:
    """Generate a single format example and write to markdown file."""
    # Use syft convert to generate the output format from cached SBOM
    output = syft.convert_format(
        sbom_file=sbom_file,
        output_format=format_name,
        syft_image=syft_image,
        env_vars={"SYFT_FORMAT_PRETTY": "true"},
    )

    if not output:
        raise RuntimeError(f"Failed to generate output for format '{format_name}'")

    # Create markdown content with code fence
    content = create_markdown_content(fence_lang, output)

    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)


def create_markdown_content(fence_lang: str, output: str) -> str:
    """Create markdown content with code fence."""
    # Add auto-generated comment
    comment = config.get_generated_comment(
        "scripts/generate_format_examples.py", "html"
    )

    # Use markdown utility for code fence
    content = comment + markdown.create_code_fence(output, fence_lang)

    return content


if __name__ == "__main__":
    main()
