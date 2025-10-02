#!/usr/bin/env python3
"""
Generate SBOM format examples by running Syft against a sample image.
Creates markdown files with code fences for each format.
"""

import argparse
import subprocess
import sys
from pathlib import Path

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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate SBOM format examples using Syft"
    )
    parser.add_argument(
        "--image",
        default="busybox:latest",
        help="Container image to scan (default: busybox:latest)",
    )
    parser.add_argument(
        "--syft-image",
        default="anchore/syft:latest",
        help="Syft container image to use (default: anchore/syft:latest)",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default="content/docs/user-guides/sbom/snippets/format/examples",
        help="Output directory for format examples (default: content/docs/user-guides/sbom/snippets/format/examples)",
    )

    args = parser.parse_args()

    print(f"Generating format examples for {args.image} using {args.syft_image}...")

    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate examples for each format
    for format_name, _, fence_lang in FORMATS:
        print(f"Generating {format_name} example...")
        try:
            generate_format_example(
                args.image,
                args.syft_image,
                format_name,
                fence_lang,
                output_dir / f"{format_name}.md",
            )
            print(f"  ✓ Generated {format_name}.md")
        except Exception as e:
            print(f"  ✗ Error generating {format_name}: {e}", file=sys.stderr)
            sys.exit(1)

    print(f"\nSuccessfully generated {len(FORMATS)} format examples in {output_dir}")


def generate_format_example(
    target_image: str,
    syft_image: str,
    format_name: str,
    fence_lang: str,
    output_path: Path,
) -> None:
    """Generate a single format example and write to markdown file."""
    # Run syft to generate the output
    output = run_syft(target_image, syft_image, format_name)

    if not output:
        raise RuntimeError(f"Failed to generate output for format '{format_name}'")

    # Create markdown content with code fence
    content = create_markdown_content(target_image, format_name, fence_lang, output)

    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)


def create_markdown_content(
    target_image: str, format_name: str, fence_lang: str, output: str
) -> str:
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


def run_syft(target_image: str, syft_image: str, format_name: str) -> str | None:
    """Run Syft in a container and return the output."""
    docker_cmd = [
        "docker",
        "run",
        "--rm",
        "-e",
        "SYFT_FORMAT_PRETTY=true",
        "-e",
        "SYFT_FILE_METADATA_SELECTION=none",
        syft_image,
        target_image,
        "-o",
        format_name,
    ]

    try:
        result = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(
                f"Syft command failed with exit code {result.returncode}",
                file=sys.stderr,
            )
            print(f"stderr: {result.stderr}", file=sys.stderr)
            return None
    except subprocess.TimeoutExpired:
        print("Syft command timed out", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error running Syft: {e}", file=sys.stderr)
        return None


if __name__ == "__main__":
    main()
