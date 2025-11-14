#!/usr/bin/env python3
"""
Generate template example documentation with rendered outputs.
Runs Syft templates against a test image and creates markdown files.
"""

import sys
from pathlib import Path
from typing import cast

import click

from utils import config, log, markdown, output_manager, sbom, syft


@click.command()
@click.option(
    "--template-dir",
    default=str(config.paths.template_examples_dir),
    help=f"Directory containing template files (default: {config.paths.template_examples_dir})",
)
@click.option(
    "--output-dir",
    default=str(config.paths.templates_snippet_dir),
    help=f"Output directory for generated examples (default: {config.paths.templates_snippet_dir})",
)
@click.option(
    "--image",
    default=config.docker_images.alpine_test,
    help=f"Docker image to scan (default: {config.docker_images.alpine_test})",
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
    template_dir: str,
    output_dir: str,
    image: str,
    syft_image: str,
    update: bool,
    verbose: int,
) -> None:
    """Generate template example documentation."""
    logger = log.setup(verbose, __file__)

    template_path = Path(template_dir)
    output_path = Path(output_dir)

    # use convention: cache is always sbom-cache subdirectory of template dir
    cache_dir = template_path / "sbom-cache"

    if not template_path.exists():
        logger.error(f"Template directory not found: {template_path}")
        sys.exit(1)

    # Find all template files
    template_files = sorted(template_path.glob("*.tmpl"))
    if not template_files:
        logger.error(f"No .tmpl files found in {template_path}")
        sys.exit(1)

    logger.info(f"Found {len(template_files)} template(s) in {template_path}")
    logger.info(f"Scanning image: {image}")
    logger.debug(f"Using Syft image: {syft_image}")

    # Clean and prepare directories
    output_manager.clean_directory(output_path, update=update, logger=logger)
    output_manager.ensure_directory(cache_dir)

    # Process each template
    skipped_count = 0
    generated_count = 0

    for template_file in template_files:
        example_name = template_file.stem  # filename without extension
        logger.debug(f"Processing: {example_name}")

        try:
            was_generated = generate_example(
                template_file=template_file,
                example_name=example_name,
                output_dir=output_path,
                cache_dir=cache_dir,
                image=image,
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
            f"Template examples: {generated_count} generated, {skipped_count} skipped (up-to-date)"
        )
    else:
        logger.info(f"All examples generated successfully in {output_path}")


def generate_example(
    template_file: Path,
    example_name: str,
    output_dir: Path,
    cache_dir: Path,
    image: str,
    syft_image: str,
    update: bool = False,
) -> bool:
    """
    Generate markdown files for a single template example.

    Returns:
        True if example was generated, False if skipped (up-to-date)
    """
    # Create example directory
    example_dir = output_dir / example_name
    output_manager.ensure_directory(example_dir)

    # Define output files
    template_md = example_dir / "template.md"
    output_md = example_dir / "output.md"

    # Check if outputs need regeneration
    if not output_manager.should_regenerate_multiple(
        [template_md, output_md], [template_file], update
    ):
        return False

    # Read template content
    template_content = template_file.read_text()

    # Generate template.md
    # see the language support: https://gohugo.io/content-management/syntax-highlighting/#languages
    template_md_content = markdown.create_code_fence(
        template_content, "go-text-template"
    )
    (example_dir / "template.md").write_text(template_md_content)

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

    # Use syft convert to apply template to cached SBOM
    output = syft.convert(
        sbom_file=sbom_file,
        template_file=template_file,
        syft_image=syft_image,
    )

    # Determine output format based on template
    if example_name == "csv":
        output_format = "csv"
    elif example_name.startswith("json"):
        output_format = "json"
    elif example_name.startswith("markdown"):
        output_format = "markdown"
    else:
        output_format = "text"

    # Generate output.md
    output_md_content = markdown.create_code_fence(output, output_format)
    (example_dir / "output.md").write_text(output_md_content)

    return True


if __name__ == "__main__":
    main()
