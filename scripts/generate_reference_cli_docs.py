#!/usr/bin/env python3
"""
Generate command reference documentation from container images.
Supports Cobra-based CLIs (like Syft and Grype).
"""

import argparse
import os
import subprocess
import sys
from collections import deque


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate command reference documentation"
    )
    parser.add_argument("image", help="Container image (e.g., anchore/syft:latest)")
    parser.add_argument(
        "--output", "-o", required=True, help="Output markdown file path"
    )
    parser.add_argument(
        "--tool-name",
        help="Tool name for documentation (auto-detected if not provided)",
    )
    parser.add_argument(
        "--app-name", help="App binary name (auto-detected if not provided)"
    )
    parser.add_argument(
        "--include-all-cmds",
        action="store_true",
        help="Include all commands including parent commands that have subcommands (default: only leaf commands)",
    )
    parser.add_argument(
        "--include-cmd",
        action="append",
        help="Include specific commands even if they are parent commands (can be used multiple times)",
    )

    args = parser.parse_args()

    # Auto-detect tool and app names if not provided
    if not args.tool_name:
        # Extract tool name from image name (e.g., anchore/syft:latest -> syft)
        image_parts = args.image.split("/")
        if len(image_parts) > 1:
            tool_part = image_parts[-1].split(":")[0]
        else:
            tool_part = args.image.split(":")[0]
        args.tool_name = tool_part

    if not args.app_name:
        args.app_name = args.tool_name

    print(f"Generating CLI docs for {args.tool_name} using image {args.image}...")

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Generate markdown content
    try:
        content = generate_markdown_content(
            args.image,
            args.app_name,
            args.tool_name,
            args.include_all_cmds,
            args.include_cmd,
        )

        # Write to file
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"CLI docs generated successfully: {args.output}")

    except Exception as e:
        print(f"Error generating documentation: {e}", file=sys.stderr)
        sys.exit(1)


def generate_markdown_content(
    image,
    app_name,
    tool_name,
    include_all_cmds: bool = False,
    include_specific_cmds=None,
) -> str:
    """Generate the complete markdown content."""
    # Prepare tool name for display
    tool_display = tool_name.title()

    # Generate front matter
    content = f"""+++
title = "{tool_display} Command Line Reference"
linkTitle = "{tool_display} CLI"
weight = 20
tags = ['{tool_name.lower()}']
categories = ['reference']
url = "docs/reference/commands/{tool_name.lower()}"
+++

"""

    # Add version info block at the top
    version_info = get_version_info(image, app_name)
    # Extract just the version line for the info block
    version_lines = version_info.split("\n")
    app_version = "unknown"
    for line in version_lines:
        if line.startswith("Version:") or line.startswith("version:"):
            app_version = line.split(":", 1)[1].strip()
            break
        elif line.startswith(f"{tool_display}:") or line.startswith(f"{tool_name}:"):
            app_version = line.split(":", 1)[1].strip()
            break
        elif "version" in line.lower() and ":" in line:
            parts = line.split(":", 1)
            if len(parts) == 2:
                app_version = parts[1].strip()
                break

    content += f"""{{{{< alert title="Note" >}}}}
This documentation was generated from {tool_display} version `{app_version}`.
{{{{< /alert >}}}}

"""

    # Add main help at the top without header (entire output in code block)
    main_help = get_command_help(image, [])  # Empty cmd_parts for main help
    content += f"```\n{main_help}\n```\n\n"

    # Discover and add all subcommands
    all_commands, leaf_commands = discover_all_commands(image, app_name)

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
            image, cmd_path
        )  # Use cmd_path directly since container runs tool directly
        description, command_details = split_help_output(
            help_output, is_main_help=False
        )

        content += f"### `{app_name} {cmd_string}`\n\n"
        if description:
            content += f"{description}\n\n"
        content += f"```\n{command_details}\n```\n\n"

    return content


def discover_all_commands(image, app_name):
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
        subcommands = get_subcommands(image, cmd_parts)

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


def get_subcommands(image, cmd_parts):
    """Extract subcommands from help output."""
    stdout, stderr, returncode = run_docker_command(image, cmd_parts + ["help"])

    if returncode != 0:
        return []

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


def get_version_info(image, app_name) -> str:
    """Get version information from the app."""
    stdout, stderr, returncode = run_docker_command(image, ["version"])
    if returncode == 0:
        return stdout.strip()
    raise RuntimeError(f"Failed to retrieve version info from the image '{image}'.")


def get_command_help(image, cmd_parts) -> str:
    """Get help output for a specific command."""
    print(
        "   ...Getting help output for command:",
        " ".join(cmd_parts) if cmd_parts else "(main help)",
    )

    for help_flag in ["--help"]:
        if help_flag == "help":
            full_cmd = cmd_parts + [help_flag]
        else:
            full_cmd = cmd_parts + [help_flag]

        stdout, stderr, returncode = run_docker_command(image, full_cmd)
        if returncode == 0 and stdout.strip():
            return stdout.strip()

    raise RuntimeError(f"Failed to retrieve help for command: {' '.join(cmd_parts)}")


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


def run_docker_command(image, cmd_parts: list[str], timeout=10) -> tuple[str, str, int]:
    """Run a command inside a Docker container."""
    docker_cmd = ["docker", "run", "--rm", image] + cmd_parts
    try:
        result = subprocess.run(
            docker_cmd, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1
    except Exception as e:
        return "", str(e), 1


if __name__ == "__main__":
    main()
