#!/usr/bin/env python3
"""
Generate configuration documentation from container images.
Supports tools that have a 'config' subcommand (like Syft and Grype).
"""

import os
import sys

import click
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
def main(
    image: str,
    output: str,
    tool_name: str | None,
    app_name: str | None,
) -> None:
    """Generate configuration reference documentation.

    IMAGE: Container image (e.g., anchore/syft:latest)
    """
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

    print(f"Generating configuration docs for {tool_name} using image {image}...")

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Generate markdown content
    try:
        content = generate_markdown_content(image, app_name, tool_name)

        # Write to file
        with open(output, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Configuration docs generated successfully: {output}")

    except Exception as e:
        print(f"Error generating configuration documentation: {e}", file=sys.stderr)
        sys.exit(1)


def generate_markdown_content(image: str, app_name: str, tool_name: str) -> str:
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
url = "docs/reference/commands/{tool_name.lower()}-config"
+++

"""

    # Get version information
    app_version = get_app_version(image)
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
    config_output = get_config_output(image)

    if config_output:
        content += f"```yaml\n{config_output}\n```\n\n"
    else:
        raise RuntimeError(
            f"Failed to retrieve configuration from the image '{image}'."
        )

    return content


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


def get_app_version(image: str) -> str | None:
    """Get the application version from the image."""
    stdout, stderr, returncode = run_syft(
        syft_image=image,
        args=["version"],
    )
    if returncode == 0:
        for line in stdout.splitlines():
            if line.startswith("Version:"):
                return line.split(":", 1)[1].strip()
    return None


def get_config_output(image: str) -> str | None:
    """Get configuration output from the app."""
    stdout, stderr, returncode = run_syft(
        syft_image=image,
        args=["config"],
    )
    if returncode == 0:
        return stdout.strip()
    return None


if __name__ == "__main__":
    main()
