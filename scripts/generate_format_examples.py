#!/usr/bin/env python3
"""
Generate SBOM format examples by running Syft against a sample image.
Creates markdown files with code fences for each format.
"""

import sys
from pathlib import Path

import click
from utils.config import docker_images, paths, timeouts
from utils.syft import run_syft_convert_format, run_syft_scan

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
def main(image: str, syft_image: str, output_dir: str) -> None:
    """Generate SBOM format examples using Syft."""
    print(f"Generating format examples for {image} using {syft_image}...")

    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # use convention: cache is always sbom-cache subdirectory of template dir
    # the format examples are in snippets/format/examples, so we need to go up to data/sbom
    cache_dir = paths.sbom_data_dir / "format-examples" / "sbom-cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Generate or retrieve SBOM from cache
    sbom_file = get_or_generate_sbom(
        image=image,
        cache_dir=cache_dir,
        syft_image=syft_image,
    )

    # Generate examples for each format
    for format_name, _, fence_lang in FORMATS:
        print(f"Generating {format_name} example...")
        try:
            generate_format_example(
                sbom_file=sbom_file,
                syft_image=syft_image,
                format_name=format_name,
                fence_lang=fence_lang,
                output_path=output_path / f"{format_name}.md",
            )
            print(f"  ✓ Generated {format_name}.md")
        except Exception as e:
            print(f"  ✗ Error generating {format_name}: {e}", file=sys.stderr)
            sys.exit(1)

    print(f"\nSuccessfully generated {len(FORMATS)} format examples in {output_path}")


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
    # Build the code fence opening
    if fence_lang:
        fence_start = f"```{fence_lang}"
    else:
        fence_start = "```"

    content = f"""{fence_start}
{output}
```
"""
    return content


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
