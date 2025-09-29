#!/usr/bin/env python3
"""
Generate command reference documentation from container images.
Supports Cobra-based CLIs (like Syft and Grype).
"""
import subprocess
import sys
import os
import argparse
from collections import deque


def run_docker_command(image, cmd_parts, timeout=10):
    """Run a command inside a Docker container."""
    docker_cmd = ['docker', 'run', '--rm', image] + cmd_parts
    try:
        result = subprocess.run(docker_cmd,
                              capture_output=True, text=True, timeout=timeout)
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1
    except Exception as e:
        return "", str(e), 1


def get_version_info(image, app_name):
    """Get version information from the app."""
    stdout, stderr, returncode = run_docker_command(image, ['version'])
    if returncode == 0:
        return stdout.strip()
    raise RuntimeError(f"Failed to retrieve version info from the image '{image}'.")


def get_subcommands(image, cmd_parts):
    """Extract subcommands from help output."""
    stdout, stderr, returncode = run_docker_command(image, cmd_parts + ['help'])

    if returncode != 0:
        return []

    lines = stdout.split('\n')
    in_commands_section = False
    commands = []

    for line in lines:
        if 'Available Commands:' in line:
            in_commands_section = True
            continue
        elif in_commands_section:
            if line.startswith('  ') and line.strip():
                cmd = line.strip().split()[0]
                if cmd not in ['help', 'completion', 'version']:
                    commands.append(cmd)
            elif line.strip() == '' or not line.startswith('  '):
                break

    return commands


def get_command_help(image, cmd_parts):
    """Get help output for a specific command."""
    print("   ...Getting help output for command:", ' '.join(cmd_parts) if cmd_parts else '(main help)')

    # Try both 'help' and '--help' patterns
    for help_flag in ['help', '--help']:
        if help_flag == 'help':
            full_cmd = cmd_parts + [help_flag]
        else:
            full_cmd = cmd_parts + [help_flag]

        stdout, stderr, returncode = run_docker_command(image, full_cmd)
        if returncode == 0 and stdout.strip():
            return stdout.strip()

    raise RuntimeError(f"Failed to retrieve help for command: {' '.join(cmd_parts)}")


def discover_all_commands(image, app_name):
    """Discover all commands recursively."""
    queue = deque([([], [])])  # Start with empty cmd_parts since container runs tool directly
    all_commands = []

    while queue:
        cmd_parts, path = queue.popleft()

        # Record current command path
        if path:
            all_commands.append(path.copy())

        # Get subcommands
        subcommands = get_subcommands(image, cmd_parts)

        # Add subcommands to queue
        for subcmd in subcommands:
            new_cmd_parts = cmd_parts + [subcmd]
            new_path = path + [subcmd]
            queue.append((new_cmd_parts, new_path))

    return all_commands


def generate_markdown_content(image, app_name, tool_name):
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

    # Add version information
    version_info = get_version_info(image, app_name)
    content += f"### `{app_name} version`\n\n```\n{version_info}\n```\n\n"

    # Add main help
    main_help = get_command_help(image, [])  # Empty cmd_parts for main help
    content += f"### `{app_name} help`\n\n```\n{main_help}\n```\n\n"

    # Discover and add all subcommands
    commands = discover_all_commands(image, app_name)

    # Sort commands to ensure consistent output
    commands.sort()

    for cmd_path in commands:
        cmd_string = ' '.join(cmd_path)

        help_output = get_command_help(image, cmd_path)  # Use cmd_path directly since container runs tool directly
        content += f"### `{app_name} {cmd_string}`\n\n```\n{help_output}\n```\n\n"

    return content


def main():
    parser = argparse.ArgumentParser(description='Generate command reference documentation')
    parser.add_argument('image', help='Container image (e.g., anchore/syft:latest)')
    parser.add_argument('--output', '-o', required=True, help='Output markdown file path')
    parser.add_argument('--tool-name', help='Tool name for documentation (auto-detected if not provided)')
    parser.add_argument('--app-name', help='App binary name (auto-detected if not provided)')
    parser.add_argument('--mock', action='store_true', help='Generate mock documentation for testing')

    args = parser.parse_args()

    # Auto-detect tool and app names if not provided
    if not args.tool_name:
        # Extract tool name from image name (e.g., anchore/syft:latest -> syft)
        image_parts = args.image.split('/')
        if len(image_parts) > 1:
            tool_part = image_parts[-1].split(':')[0]
        else:
            tool_part = args.image.split(':')[0]
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
        content = generate_markdown_content(args.image, args.app_name, args.tool_name)

        # Write to file
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"CLI docs generated successfully: {args.output}")

    except Exception as e:
        print(f"Error generating documentation: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()