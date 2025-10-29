#!/usr/bin/env python3
"""
Generate command reference documentation from container images.
Supports Cobra-based CLIs (like Syft and Grype).
"""

import os
import sys
from collections import deque
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
    "--include-all-cmds",
    is_flag=True,
    help="Include all commands including parent commands that have subcommands (default: only leaf commands)",
)
@click.option(
    "--include-cmd",
    multiple=True,
    help="Include specific commands even if they are parent commands (can be used multiple times)",
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
    include_all_cmds: bool,
    include_cmd: tuple[str, ...],
    update: bool,
    verbose: int,
) -> None:
    """Generate command reference documentation.

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

    logger.info(f"Generating CLI docs for {tool_name} using image {image}...")

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Check if output is up-to-date
    if is_output_up_to_date(output, tool_name, update):
        logger.info(f"CLI docs are up-to-date, skipping generation: {output}")
        return

    # Generate markdown content
    try:
        content = generate_markdown_content(
            image,
            app_name,
            tool_name,
            include_all_cmds,
            list(include_cmd) if include_cmd else None,
            update,
        )

        # Write to file
        with open(output, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"CLI docs generated successfully: {output}")

    except Exception as e:
        logger.error(f"Error generating documentation: {e}")
        sys.exit(1)


def generate_markdown_content(
    image: str,
    app_name: str,
    tool_name: str,
    include_all_cmds: bool = False,
    include_specific_cmds: list[str] | None = None,
    update: bool = False,
) -> str:
    """Generate the complete markdown content."""
    # Prepare tool name for display
    tool_display = tool_name.title()

    # Generate front matter using utility
    weight = config.reference_weights.get_weight(tool_name, "cli")
    content = markdown.generate_front_matter(
        title=f"{tool_display} Command Line Reference",
        link_title=f"{tool_display} CLI",
        weight=weight,
        tags=[tool_name.lower()],
        categories=["reference"],
        url=f"docs/reference/{tool_name.lower()}/cli",
    )

    # Add auto-generated comment
    content += config.get_generated_comment(
        "scripts/generate_reference_cli_docs.py", "html"
    )

    # Add version info block at the top
    version_info = get_version_info(image, app_name, tool_name, update)
    # Extract version using utility function
    app_version = version.extract_from_output(version_info, tool_name=tool_name)

    content += f"""{{{{< alert title="Note" >}}}}
This documentation was generated with {tool_display} version `{app_version}`.
{{{{< /alert >}}}}

"""

    # Add main help at the top without header (entire output in code block)
    main_help = get_command_help(
        image, [], tool_name, update
    )  # Empty cmd_parts for main help
    content += markdown.create_code_fence(main_help, "") + "\n"

    # Discover and add all subcommands
    all_commands, leaf_commands = discover_all_commands(
        image, app_name, tool_name, update
    )

    # Choose which commands to include based on flags
    if include_all_cmds:
        # Include all commands
        commands = all_commands
    else:
        # Start with leaf commands
        commands = leaf_commands.copy()

        # Add any specifically requested commands
        if include_specific_cmds:
            for specific_cmd in include_specific_cmds:
                # Parse the specific command into a list (e.g., "db search" -> ["db", "search"])
                cmd_parts = specific_cmd.strip().split()

                # Check if this command exists in all_commands
                for cmd_path in all_commands:
                    if cmd_path == cmd_parts and cmd_path not in commands:
                        commands.append(cmd_path)

    # Sort commands to ensure consistent output
    commands.sort()

    for cmd_path in commands:
        cmd_string = " ".join(cmd_path)

        help_output = get_command_help(
            image, cmd_path, tool_name, update
        )  # Use cmd_path directly since container runs tool directly
        description, command_details = split_help_output(
            help_output, is_main_help=False
        )

        content += f"### `{app_name} {cmd_string}`\n\n"
        if description:
            content += f"{description}\n\n"
        content += markdown.create_code_fence(command_details, "") + "\n"

    return content


def get_cache_path_for_cli(tool_name: str, cmd_parts: list[str]) -> Path:
    """
    get cache file path for a CLI command output.

    Args:
        tool_name: tool name (e.g., "syft", "grype")
        cmd_parts: command parts (e.g., ["db", "search"] or [] for main help)

    Returns:
        Path to cache file
    """
    if not cmd_parts:
        # main help
        cache_dir = config.paths.reference_cache_dir / tool_name / "cli" / "main"
    else:
        # subcommand help - use command path as directory structure
        cache_dir = (
            config.paths.reference_cache_dir / tool_name / "cli" / "/".join(cmd_parts)
        )

    return cache_dir / "output.txt"


def discover_all_commands(
    image: str, app_name: str, tool_name: str, update: bool = False
):
    """Discover all commands recursively.

    Returns a tuple of (all_commands, leaf_commands) where:
    - all_commands: list of all command paths
    - leaf_commands: list of command paths that have no subcommands (leaf nodes)
    """
    queue = deque(
        [([], [])]
    )  # Start with empty cmd_parts since container runs tool directly
    all_commands = []
    commands_with_subcommands = set()

    while queue:
        cmd_parts, path = queue.popleft()

        # Record current command path
        if path:
            all_commands.append(path.copy())

        # Get subcommands
        subcommands = get_subcommands(image, cmd_parts, tool_name, update)

        # If this command has subcommands, mark it as a parent
        if subcommands and path:
            commands_with_subcommands.add(tuple(path))

        # Add subcommands to queue
        for subcmd in subcommands:
            new_cmd_parts = cmd_parts + [subcmd]
            new_path = path + [subcmd]
            queue.append((new_cmd_parts, new_path))

    # Determine leaf commands (commands that are not in commands_with_subcommands)
    leaf_commands = [
        cmd for cmd in all_commands if tuple(cmd) not in commands_with_subcommands
    ]

    return all_commands, leaf_commands


def get_subcommands(image: str, cmd_parts, tool_name: str, update: bool = False):
    """Extract subcommands from help output."""
    # check cache first
    cache_path = get_cache_path_for_cli(tool_name, cmd_parts + ["help"])
    cached = cache.get_output(cache_path, update)

    if cached is not None:
        lines = cached.split("\n")
    else:
        # run command
        stdout, stderr, returncode = syft.run(
            syft_image=image,
            args=cmd_parts + ["help"],
        )

        if returncode != 0:
            return []

        # save to cache
        cache.save(cache_path, stdout)
        lines = stdout.split("\n")
    in_commands_section = False
    commands = []

    for line in lines:
        if "Available Commands:" in line:
            in_commands_section = True
            continue
        elif in_commands_section:
            if line.startswith("  ") and line.strip():
                cmd = line.strip().split()[0]
                if cmd not in ["help", "completion"]:
                    commands.append(cmd)
            elif line.strip() == "" or not line.startswith("  "):
                break

    return commands


def get_version_info(
    image: str, app_name: str, tool_name: str, update: bool = False
) -> str:
    """Get version information from the app."""
    # check cache first
    cache_path = get_cache_path_for_cli(tool_name, ["version"])
    cached = cache.get_output(cache_path, update)

    if cached is not None:
        return cached.strip()

    # run command
    stdout, stderr, returncode = syft.run(
        syft_image=image,
        args=["version"],
    )

    if returncode == 0:
        # save to cache
        cache.save(cache_path, stdout)
        return stdout.strip()

    raise RuntimeError(f"Failed to retrieve version info from the image '{image}'.")


def get_command_help(
    image: str, cmd_parts, tool_name: str, update: bool = False
) -> str:
    """Get help output for a specific command."""
    import logging

    logger = logging.getLogger(__name__)

    # check cache first
    cache_path = get_cache_path_for_cli(tool_name, cmd_parts)
    cached = cache.get_output(cache_path, update)

    if cached is not None:
        return cached.strip()

    logger.debug(
        f"Getting help output for command: {' '.join(cmd_parts) if cmd_parts else '(main help)'}"
    )

    for help_flag in ["--help"]:
        if help_flag == "help":
            full_cmd = cmd_parts + [help_flag]
        else:
            full_cmd = cmd_parts + [help_flag]

        stdout, stderr, returncode = syft.run(
            syft_image=image,
            args=full_cmd,
        )
        if returncode == 0 and stdout.strip():
            # save to cache
            cache.save(cache_path, stdout)
            return stdout.strip()

    raise RuntimeError(f"Failed to retrieve help for command: {' '.join(cmd_parts)}")


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

    # find all cache files for this tool
    cache_base = config.paths.reference_cache_dir / tool_name / "cli"
    if not cache_base.exists():
        # no cache exists, output is stale
        return False

    # check all cache files recursively
    for cache_file in cache_base.rglob("output.txt"):
        cache_mtime = cache_file.stat().st_mtime
        if cache_mtime > output_mtime:
            # cache is newer than output, output is stale
            return False

    # output is up-to-date
    return True


def split_help_output(help_output: str, is_main_help=False) -> tuple[str, str]:
    """Split help output into description and command details.

    Returns a tuple of (description, command_details).
    Description contains text before 'Usage:' line.
    Command details contain everything from 'Usage:' onwards.
    For non-main help, truncates content after 'Global Flags:'.
    """
    lines = help_output.split("\n")
    description_lines = []
    usage_index = -1

    # Find the "Usage:" line and collect description lines preserving paragraph breaks
    for i, line in enumerate(lines):
        if line.startswith("Usage:"):
            usage_index = i
            break
        # Collect all lines before Usage: (including empty lines for paragraph breaks)
        description_lines.append(line.rstrip())

    if usage_index == -1:
        # No Usage: found, return full output as command details with empty description
        return "", help_output

    # Process description lines to create proper markdown paragraphs
    if description_lines:
        # Remove trailing empty lines
        while description_lines and not description_lines[-1].strip():
            description_lines.pop()

        # Treat each non-empty line as a separate paragraph for proper markdown formatting
        description_parts = []

        for line in description_lines:
            if line.strip():
                description_parts.append(line.strip())

        # Join paragraphs with double newlines for proper markdown
        description = "\n\n".join(description_parts)

        if description:
            # Capitalize the first letter
            description = (
                description[0].upper() + description[1:]
                if len(description) > 1
                else description.upper()
            )
            # Ensure it ends with a period
            if not description.endswith("."):
                description += "."
    else:
        description = ""

    # Get everything from Usage: onwards
    command_details_lines = lines[usage_index:]

    # For non-main help, truncate before "Global Flags:"
    if not is_main_help:
        truncated_lines = []
        for line in command_details_lines:
            if line.strip().startswith("Global Flags:"):
                break
            truncated_lines.append(line)
        command_details_lines = truncated_lines

    command_details = "\n".join(command_details_lines)

    return description, command_details


if __name__ == "__main__":
    main()
