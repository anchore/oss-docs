#!/usr/bin/env python3
"""
Generate format version information from Syft output.

This script runs Syft with an invalid format to capture the list of available
formats and their supported versions, then generates:
1. A JSON data file with format-to-versions mapping
2. A markdown snippet showing formats with multiple versions
"""

import json
import re
import subprocess
import sys
from pathlib import Path

import click
from utils.config import docker_images, paths, timeouts


def extract_format_versions():
    """
    run Syft with a fake format to capture available formats output

    returns: dict mapping format names to lists of supported versions
    """
    try:
        # run syft with an invalid format to trigger the error message
        result = subprocess.run(
            ["syft", docker_images.busybox_test, "-o", "fake"],
            capture_output=True,
            text=True,
            timeout=timeouts.syft_format_version_check,
        )

        # the format list will be in stderr
        output = result.stderr

        # parse the format list
        # looking for lines like: "   - cyclonedx-json @ 1.2, 1.3, 1.4, 1.5, 1.6"
        format_pattern = re.compile(
            r"^\s*-\s+([a-z0-9-]+)(?:\s+@\s+([\d.,\s]+))?$", re.MULTILINE
        )

        formats = {}
        for match in format_pattern.finditer(output):
            format_name = match.group(1)
            versions_str = match.group(2)

            if versions_str:
                # parse versions
                versions = [v.strip() for v in versions_str.split(",")]
                formats[format_name] = versions
            else:
                # no versions specified, format has no version variants
                formats[format_name] = []

        return formats

    except subprocess.TimeoutExpired:
        print("Error: Syft command timed out", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error running Syft: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(
            "Error: Syft command not found. Please ensure Syft is installed.",
            file=sys.stderr,
        )
        sys.exit(1)


def save_json_data(formats, output_path: Path) -> None:
    """save format versions to JSON file"""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(formats, f, indent=2)

    print(f"Generated {output_path}")


def generate_markdown_snippet(formats, output_path: Path) -> None:
    """
    generate markdown snippet showing formats with multiple versions

    only includes formats that have 2+ versions
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # filter to only formats with multiple versions
    multi_version_formats = {k: v for k, v in formats.items() if len(v) > 1}

    if not multi_version_formats:
        print("No formats with multiple versions found", file=sys.stderr)
        return

    # generate markdown list only
    lines = []

    # sort formats alphabetically
    for format_name in sorted(multi_version_formats.keys()):
        versions = multi_version_formats[format_name]
        versions_str = ", ".join([f"`{v}`" for v in versions])
        lines.append(f"- **{format_name}**: {versions_str}")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))
        f.write("\n")

    print(f"Generated {output_path}")


def load_existing_formats(json_path: Path):
    """load existing format data from JSON file"""
    try:
        with open(json_path) as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        print(f"Warning: Invalid JSON in {json_path}: {e}", file=sys.stderr)
        return None


@click.command()
@click.option(
    "--update",
    is_flag=True,
    help="Update the JSON file even if it already exists",
)
def main(update: bool) -> None:
    """Generate format version information from Syft output."""
    # define output paths from config
    json_output = paths.format_versions_json
    md_output = paths.format_versions_snippet

    # check if JSON file already exists
    if json_output.exists() and not update:
        print(f"Using existing {json_output}")
        formats = load_existing_formats(json_output)
        if formats is None:
            print("Error: Could not load existing JSON file", file=sys.stderr)
            sys.exit(1)
    else:
        # extract format information
        print("Extracting format versions from Syft...")
        formats = extract_format_versions()

        if not formats:
            print("Error: No formats found", file=sys.stderr)
            sys.exit(1)

        print(f"Found {len(formats)} formats")

        # save JSON data
        save_json_data(formats, json_output)

    # generate markdown snippet
    generate_markdown_snippet(formats, md_output)


if __name__ == "__main__":
    main()
