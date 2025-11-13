#!/usr/bin/env python3
"""
Generate configuration documentation from container images.
Supports tools that have a 'config' subcommand (like Syft and Grype).
"""

import os
import sys
from pathlib import Path

import click
from utils import cache, config, log, markdown, syft, version


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
    logger = log.setup(verbose, __file__)

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

    # Check if output is up-to-date
    if is_output_up_to_date(output, tool_name, update):
        logger.info(f"Configuration docs are up-to-date, skipping generation: {output}")
        return

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

    # Generate front matter using utility
    weight = config.reference_weights.get_weight(tool_name, "config")
    content = markdown.generate_front_matter(
        title=f"{tool_display} Configuration Reference",
        link_title="Configuration",
        weight=weight,
        tags=[tool_name.lower()],
        categories=["reference"],
        menu_group=tool_name,
        url=f"docs/reference/{tool_name.lower()}/configuration",
    )

    # Add auto-generated comment
    content += config.get_generated_comment(
        "scripts/generate_reference_config_docs.py", "html"
    )

    # Get version information
    app_version = get_app_version(image, tool_name, update)
    if not app_version:
        app_version = "unknown"

    # Add version header
    content += f"""{{{{< alert title="Note" >}}}}
This documentation was generated with {tool_display} version `{app_version}`.
{{{{< /alert >}}}}

"""

    # Add configuration search locations section
    content += get_config_locations_section(app_name, tool_display)

    # Get configuration output
    config_output = get_config_output(image, tool_name, update)

    if config_output:
        content += markdown.create_code_fence(config_output, "yaml") + "\n"
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
    cache_dir = config.paths.reference_cache_dir / tool_name / command_type
    return cache_dir / "output.txt"


def is_output_up_to_date(output_path: str, tool_name: str, update: bool) -> bool:
    """
    check if output file is up-to-date relative to cache files.

    Args:
        output_path: path to output markdown file
        tool_name: tool name (e.g., "syft", "grype")
        update: if true, always return False to force regeneration

    Returns:
        True if output exists and is newer than all cache files
    """
    # if updating, always regenerate
    if update:
        return False

    # check if output exists
    output_file = Path(output_path)
    if not output_file.exists():
        return False

    # get output modification time
    output_mtime = output_file.stat().st_mtime

    # check version cache
    version_cache = get_cache_path(tool_name, "version")
    if version_cache.exists():
        if version_cache.stat().st_mtime > output_mtime:
            return False

    # check config cache
    config_cache = get_cache_path(tool_name, "config")
    if config_cache.exists():
        if config_cache.stat().st_mtime > output_mtime:
            return False

    # output is up-to-date
    return True


def get_config_locations_section(app_name: str, tool_display: str) -> str:
    """Generate markdown section describing configuration file search locations."""
    return f"""
{tool_display} searches for configuration files in the following locations, in order:

1. `./.{app_name}.yaml` - current working directory
2. `./.{app_name}/config.yaml` - app subdirectory in current working directory
3. `~/.{app_name}.yaml` - home directory
4. `$XDG_CONFIG_HOME/{app_name}/config.yaml` - [XDG config directory](https://github.com/adrg/xdg?tab=readme-ov-file#default-locations)

The configuration file can use either `.yaml` or `.yml` extensions. The first configuration file found will be used.

For general information about how config and environment variables are handled, see the [Configuration Reference]({{{{< relref "/docs/reference/configuration" >}}}}) section.

"""


def get_app_version(image: str, tool_name: str, update: bool = False) -> str | None:
    """Get the application version from the image."""
    cache_path = get_cache_path(tool_name, "version")
    return version.get_app_version(image, tool_name, cache_path, update)


def get_config_output(image: str, tool_name: str, update: bool = False) -> str | None:
    """Get configuration output from the app."""
    # check cache first
    cache_path = get_cache_path(tool_name, "config")
    cached = cache.get_output(cache_path, update)

    if cached is not None:
        return cached.strip()

    # run command
    stdout, stderr, returncode = syft.run(
        syft_image=image,
        args=["config"],
    )

    if returncode == 0:
        # save to cache
        cache.save(cache_path, stdout)
        return stdout.strip()
    return None


if __name__ == "__main__":
    main()
