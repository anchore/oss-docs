#!/usr/bin/env python3
"""
Generate template example documentation with rendered outputs.
Runs Syft templates against a test image and creates markdown files.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate template example documentation"
    )
    parser.add_argument(
        "--template-dir",
        default="data/sbom/template-examples",
        help="Directory containing template files",
    )
    parser.add_argument(
        "--output-dir",
        default="content/docs/user-guides/sbom/snippets/templates",
        help="Output directory for generated examples",
    )
    parser.add_argument(
        "--image",
        default="alpine:3.9.2",
        help="Docker image to scan (default: alpine:3.9.2)",
    )
    parser.add_argument(
        "--syft-image",
        default="anchore/syft:latest",
        help="Syft Docker image to use (default: anchore/syft:latest)",
    )

    args = parser.parse_args()

    template_dir = Path(args.template_dir)
    output_dir = Path(args.output_dir)

    if not template_dir.exists():
        print(f"Error: Template directory not found: {template_dir}", file=sys.stderr)
        sys.exit(1)

    # Find all template files
    template_files = sorted(template_dir.glob("*.tmpl"))
    if not template_files:
        print(f"Error: No .tmpl files found in {template_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(template_files)} template(s) in {template_dir}")
    print(f"Scanning image: {args.image}")
    print(f"Using Syft image: {args.syft_image}")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process each template
    for template_file in template_files:
        example_name = template_file.stem  # filename without extension
        print(f"\nProcessing: {example_name}")

        try:
            generate_example(
                template_file=template_file,
                example_name=example_name,
                output_dir=output_dir,
                image=args.image,
                syft_image=args.syft_image,
            )
            print(f"  ✓ Generated {example_name}")
        except Exception as e:
            print(f"  ✗ Failed to generate {example_name}: {e}", file=sys.stderr)
            sys.exit(1)

    print(f"\n✓ All examples generated successfully in {output_dir}")


def generate_example(
    template_file: Path,
    example_name: str,
    output_dir: Path,
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
    template_md = f"```gotemplate\n{template_content}\n```\n"
    (example_dir / "template.md").write_text(template_md)

    # Run syft with the template to generate output
    output = run_syft_with_template(
        template_file=template_file,
        image=image,
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


def run_syft_with_template(
    template_file: Path, image: str, syft_image: str, timeout: int = 60
) -> str:
    """Run Syft with a template file and return the output."""
    # Get absolute path for the template file
    template_path = template_file.resolve()

    # Mount the template file and run syft
    docker_cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{template_path}:/template.tmpl:ro",
        syft_image,
        image,
        "-o",
        "template",
        "-t",
        "/template.tmpl",
    ]

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


if __name__ == "__main__":
    main()
