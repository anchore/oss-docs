#!/usr/bin/env python3
"""
Generate SBOM format examples by running Syft against a sample image.
Creates markdown files with code fences for each format.
"""

import shutil
import sys
from pathlib import Path
from typing import cast

import click
from utils.config import docker_images, get_generated_comment, paths
from utils.logging import setup_logging
from utils.sbom import get_or_generate_sbom
from utils.syft import run_syft_convert_format

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
    default=docker_images.busybox_test,
    help=f"Container image to scan (default: {docker_images.busybox_test})",
)
@click.option(
    "--syft-image",
    default=docker_images.syft,
    help=f"Syft container image to use (default: {docker_images.syft})",
)
@click.option(
    "--output-dir",
    "-o",
    default=str(paths.format_examples_snippet_dir),
    help=f"Output directory for format examples (default: {paths.format_examples_snippet_dir})",
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
    logger = setup_logging(verbose, __file__)

    logger.info(f"Generating format examples for {image} using {syft_image}...")

    # Clean output directory to ensure no stale content
    output_path = Path(output_dir)
    if output_path.exists():
        logger.debug(f"Cleaning output directory: {output_path}")
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    # use convention: cache is always sbom-cache subdirectory of template dir
    # the format examples are in snippets/format/examples, so we need to go up to data/sbom
    cache_dir = paths.sbom_data_dir / "format-examples" / "sbom-cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Generate or retrieve SBOM from cache
    sbom_file = cast(
        Path,
        get_or_generate_sbom(
            image=image,
            cache_dir=cache_dir,
            syft_image=syft_image,
            update=update,
        ),
    )

    # Generate examples for each format
    for format_name, _, fence_lang in FORMATS:
        logger.debug(f"Generating {format_name} example...")
        try:
            generate_format_example(
                sbom_file=sbom_file,
                syft_image=syft_image,
                format_name=format_name,
                fence_lang=fence_lang,
                output_path=output_path / f"{format_name}.md",
            )
            logger.debug(f"  ✓ Generated {format_name}.md")
        except Exception as e:
            logger.error(f"  ✗ Error generating {format_name}: {e}")
            sys.exit(1)

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
    output = run_syft_convert_format(
        sbom_file=sbom_file,
        output_format=format_name,
        syft_image=syft_image,
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
    comment = get_generated_comment("scripts/generate_format_examples.py", "html")

    # Build the code fence opening
    if fence_lang:
        fence_start = f"```{fence_lang}"
    else:
        fence_start = "```"

    content = f"""{comment}{fence_start}
{output}
```
"""
    return content


if __name__ == "__main__":
    main()
