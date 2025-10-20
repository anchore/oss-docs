#!/usr/bin/env python3
"""
Generate configuration documentation from container images.
Supports tools that have a 'config' subcommand (like Syft and Grype).
"""

import os
import sys
from pathlib import Path

import click
from utils.cache import get_cached_output, save_to_cache
from utils.config import get_generated_comment, paths
from utils.logging import setup_logging
from utils.syft import run_syft


@click.command()
@click.argument("image")
@click.option(
    "--output",
    "-o",
    required=True,
    help="Output markdown file path",
)
@click.option(
    "--tool-name",
    help="Tool name for documentation (auto-detected if not provided)",
)
@click.option(
    "--app-name",
    help="App binary name (auto-detected if not provided)",
)
@click.option(
    "--update",
    is_flag=True,
    help="Update the cache even if it already exists",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity (use -v for info, -vv for debug)",
)
def main(
    image: str,
    output: str,
    tool_name: str | None,
    app_name: str | None,
    update: bool,
    verbose: int,
) -> None:
    """Generate configuration reference documentation.

    IMAGE: Container image (e.g., anchore/syft:latest)
    """
    logger = setup_logging(verbose, __file__)

    # Auto-detect tool and app names if not provided
    if not tool_name:
        # Extract tool name from image name (e.g., anchore/syft:latest -> syft)
        image_parts = image.split("/")
        if len(image_parts) > 1:
            tool_part = image_parts[-1].split(":")[0]
        else:
            tool_part = image.split(":")[0]
        tool_name = tool_part

    if not app_name:
        app_name = tool_name

    logger.info(f"Generating configuration docs for {tool_name} using image {image}...")

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Generate markdown content
    try:
        content = generate_markdown_content(image, app_name, tool_name, update)

        # Write to file
        with open(output, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Configuration docs generated successfully: {output}")

    except Exception as e:
        logger.error(f"Error generating configuration documentation: {e}")
        sys.exit(1)


def generate_markdown_content(
    image: str, app_name: str, tool_name: str, update: bool = False
) -> str:
    """Generate the complete markdown content for config documentation."""
    # Prepare tool name for display
    tool_display = tool_name.title()

    # Generate front matter
    content = f"""+++
title = "{tool_display} Default Configuration"
linkTitle = "{tool_display} Default Config"
weight = 25
tags = ['{tool_name.lower()}']
categories = ['reference']
url = "docs/reference/{tool_name.lower()}/configuration"
+++

"""

    # Add auto-generated comment
    content += get_generated_comment(
        "scripts/generate_reference_config_docs.py", "html"
    )

    # Get version information
    app_version = get_app_version(image, tool_name, update)
    if not app_version:
        app_version = "unknown"

    # Add version header
    content += f"""{{{{< alert title="Note" >}}}}
This documentation was generated from {tool_display} version `{app_version}`.
{{{{< /alert >}}}}

"""

    # Add configuration search locations section
    content += get_config_locations_section(app_name, tool_display)

    # Get configuration output
    config_output = get_config_output(image, tool_name, update)

    if config_output:
        content += f"```yaml\n{config_output}\n```\n\n"
    else:
        raise RuntimeError(
            f"Failed to retrieve configuration from the image '{image}'."
        )

    return content


def get_cache_path(tool_name: str, command_type: str) -> Path:
    """
    get cache file path for a command output.

    Args:
        tool_name: tool name (e.g., "syft", "grype")
        command_type: type of command ("version" or "config")

    Returns:
        Path to cache file
    """
    cache_dir = paths.reference_cache_dir / tool_name / command_type
    return cache_dir / "output.txt"


def get_config_locations_section(app_name: str, tool_display: str) -> str:
    """Generate markdown section describing configuration file search locations."""
    return f"""
{tool_display} searches for configuration files in the following locations, in order:

1. `./.{app_name}.yaml` - current working directory
2. `./.{app_name}/config.yaml` - app subdirectory in current working directory
3. `~/.{app_name}.yaml` - home directory
4. `$XDG_CONFIG_HOME/{app_name}/config.yaml` - [XDG config directory](https://github.com/adrg/xdg?tab=readme-ov-file#default-locations)

The configuration file can use either `.yaml` or `.yml` extensions. The first configuration file found will be used.

"""


def get_app_version(image: str, tool_name: str, update: bool = False) -> str | None:
    """Get the application version from the image."""
    # check cache first
    cache_path = get_cache_path(tool_name, "version")
    cached = get_cached_output(cache_path, update)

    if cached is not None:
        # parse cached output
        for line in cached.splitlines():
            if line.startswith("Version:"):
                return line.split(":", 1)[1].strip()
        return None

    # run command
    stdout, stderr, returncode = run_syft(
        syft_image=image,
        args=["version"],
    )

    if returncode == 0:
        # save to cache
        save_to_cache(cache_path, stdout)

        # parse output
        for line in stdout.splitlines():
            if line.startswith("Version:"):
                return line.split(":", 1)[1].strip()
    return None


def get_config_output(image: str, tool_name: str, update: bool = False) -> str | None:
    """Get configuration output from the app."""
    # check cache first
    cache_path = get_cache_path(tool_name, "config")
    cached = get_cached_output(cache_path, update)

    if cached is not None:
        return cached.strip()

    # run command
    stdout, stderr, returncode = run_syft(
        syft_image=image,
        args=["config"],
    )

    if returncode == 0:
        # save to cache
        save_to_cache(cache_path, stdout)
        return stdout.strip()
    return None


if __name__ == "__main__":
    main()
