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
from logging import Logger
from pathlib import Path

import click

from utils import config, log, syft


@click.command()
@click.option(
    "--syft-image",
    type=str,
    default=config.docker_images.syft,
    help="Syft Docker image to use",
)
@click.option(
    "--update",
    is_flag=True,
    help="Update the JSON file even if it already exists",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity (use -v for info, -vv for debug)",
)
def main(syft_image: str, update: bool, verbose: int) -> None:
    """Generate format version information from Syft output."""
    logger = log.setup(verbose, __file__)

    # define output paths from config
    json_output = config.paths.format_versions_json
    md_output = config.paths.format_versions_snippet

    # check if JSON file already exists
    if json_output.exists() and not update:
        logger.info(f"Using existing {json_output}")
        formats = load_existing_formats(json_output)
        if formats is None:
            logger.error("Could not load existing JSON file")
            sys.exit(1)
    else:
        # extract format information
        logger.info("Extracting format versions from Syft...")
        formats = extract_format_versions(syft_image)

        if not formats:
            logger.error("No formats found")
            sys.exit(1)

        logger.info(f"Found {len(formats)} formats")

        # save JSON data
        save_json_data(formats, json_output, logger)

    # generate markdown snippet
    generate_markdown_snippet(formats, md_output, logger)


def extract_format_versions(syft_image: str):
    """
    run Syft with a fake format to capture available formats output.

    Args:
        syft_image: Syft Docker image to use

    Returns:
        dict mapping format names to lists of supported versions
    """
    try:
        # run syft with an invalid format to trigger the error message
        stdout, stderr, returncode = syft.run(
            syft_image=syft_image,
            args=[config.docker_images.busybox_test, "-o", "fake"],
            timeout=config.timeouts.syft_format_version_check,
        )

        # the format list will be in stderr
        output = stderr

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
        import logging

        logger = logging.getLogger(__name__)
        logger.error("Syft command timed out")
        sys.exit(1)


def save_json_data(formats, output_path: Path, logger: Logger) -> None:
    """save format versions to JSON file"""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # add auto-generated comment as a special field
    comment = config.get_generated_comment(__file__, "json")
    data = {"_comment": comment, **formats}

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info(f"Generated {output_path}")


def generate_markdown_snippet(formats, output_path: Path, logger: Logger) -> None:
    """
    generate markdown snippet showing formats with multiple versions

    only includes formats that have 2+ versions
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # filter to only formats with multiple versions
    multi_version_formats = {k: v for k, v in formats.items() if len(v) > 1}

    if not multi_version_formats:
        logger.warning("No formats with multiple versions found")
        return

    # add auto-generated comment
    comment = config.get_generated_comment(__file__, "html")

    # generate markdown list only
    lines = []

    # sort formats alphabetically
    for format_name in sorted(multi_version_formats.keys()):
        versions = multi_version_formats[format_name]
        versions_str = ", ".join([f"`{v}`" for v in versions])
        lines.append(f"- **{format_name}**: {versions_str}")

    with open(output_path, "w") as f:
        f.write(comment)
        f.write("\n".join(lines))
        f.write("\n")

    logger.info(f"Generated {output_path}")


def load_existing_formats(json_path: Path):
    """load existing format data from JSON file"""
    try:
        with open(json_path) as f:
            data = json.load(f)
            # filter out the _comment field if present
            return {k: v for k, v in data.items() if k != "_comment"}
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"Invalid JSON in {json_path}: {e}")
        return None


if __name__ == "__main__":
    main()
