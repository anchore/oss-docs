#!/usr/bin/env python3
"""
Generate template example documentation with rendered outputs.
Runs Syft templates against a test image and creates markdown files.
"""

import sys
from pathlib import Path

import click
from utils.config import docker_images, paths, timeouts
from utils.syft import run_syft_convert, run_syft_scan


@click.command()
@click.option(
    "--template-dir",
    default=str(paths.template_examples_dir),
    help=f"Directory containing template files (default: {paths.template_examples_dir})",
)
@click.option(
    "--output-dir",
    default=str(paths.templates_snippet_dir),
    help=f"Output directory for generated examples (default: {paths.templates_snippet_dir})",
)
@click.option(
    "--image",
    default=docker_images.alpine_test,
    help=f"Docker image to scan (default: {docker_images.alpine_test})",
)
@click.option(
    "--syft-image",
    default=docker_images.syft,
    help=f"Syft Docker image to use (default: {docker_images.syft})",
)
def main(
    template_dir: str,
    output_dir: str,
    image: str,
    syft_image: str,
) -> None:
    """Generate template example documentation."""
    template_path = Path(template_dir)
    output_path = Path(output_dir)

    # use convention: cache is always sbom-cache subdirectory of template dir
    cache_dir = template_path / "sbom-cache"

    if not template_path.exists():
        print(f"Error: Template directory not found: {template_path}", file=sys.stderr)
        sys.exit(1)

    # Find all template files
    template_files = sorted(template_path.glob("*.tmpl"))
    if not template_files:
        print(f"Error: No .tmpl files found in {template_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(template_files)} template(s) in {template_path}")
    print(f"Scanning image: {image}")
    print(f"Using Syft image: {syft_image}")

    # Create output and cache directories
    output_path.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Process each template
    for template_file in template_files:
        example_name = template_file.stem  # filename without extension
        print(f"\nProcessing: {example_name}")

        try:
            generate_example(
                template_file=template_file,
                example_name=example_name,
                output_dir=output_path,
                cache_dir=cache_dir,
                image=image,
                syft_image=syft_image,
            )
            print(f"  ✓ Generated {example_name}")
        except Exception as e:
            print(f"  ✗ Failed to generate {example_name}: {e}", file=sys.stderr)
            sys.exit(1)

    print(f"\n✓ All examples generated successfully in {output_path}")


def generate_example(
    template_file: Path,
    example_name: str,
    output_dir: Path,
    cache_dir: Path,
    image: str,
    syft_image: str,
) -> None:
    """Generate markdown files for a single template example."""
    # Create example directory
    example_dir = output_dir / example_name
    example_dir.mkdir(parents=True, exist_ok=True)

    # Read template content
    template_content = template_file.read_text()

    # Generate template.md
    # see the language support: https://gohugo.io/content-management/syntax-highlighting/#languages
    template_md = f"```go-text-template\n{template_content}\n```\n"
    (example_dir / "template.md").write_text(template_md)

    # Generate or retrieve SBOM from cache
    sbom_file = get_or_generate_sbom(
        image=image,
        cache_dir=cache_dir,
        syft_image=syft_image,
    )

    # Use syft convert to apply template to cached SBOM
    output = run_syft_convert(
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
    output_md = f"```{output_format}\n{output}\n```\n"
    (example_dir / "output.md").write_text(output_md)


def get_or_generate_sbom(
    image: str,
    cache_dir: Path,
    syft_image: str,
) -> Path:
    """Get SBOM from cache or generate it using Syft."""
    # create cache key from image name
    cache_key = image.replace(":", "_").replace("/", "_")
    cache_file = cache_dir / f"{cache_key}.json"

    # check cache
    if cache_file.exists():
        print(f"  Using cached SBOM: {cache_file}")
        return cache_file

    # generate SBOM
    print(f"  Generating SBOM for: {image}")
    sbom_json = run_syft_scan(
        target_image=image,
        syft_image=syft_image,
        output_format="syft-json",
        timeout=timeouts.syft_scan_default,
    )

    # save to cache
    cache_file.write_text(sbom_json)
    print(f"  Cached SBOM to: {cache_file}")

    return cache_file


if __name__ == "__main__":
    main()
