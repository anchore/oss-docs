#!/usr/bin/env python3
"""
Generate configuration documentation from container images.
Supports tools that have a 'config' subcommand (like Syft and Grype).
"""

import argparse
import os
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate configuration reference documentation"
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

    print(
        f"Generating configuration docs for {args.tool_name} using image {args.image}..."
    )

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Generate markdown content
    try:
        content = generate_markdown_content(args.image, args.app_name, args.tool_name)

        # Write to file
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Configuration docs generated successfully: {args.output}")

    except Exception as e:
        print(f"Error generating configuration documentation: {e}", file=sys.stderr)
        sys.exit(1)


def generate_markdown_content(image, app_name, tool_name) -> str:
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

    # Get configuration output
    config_output = get_config_output(image)

    if config_output:
        content += f"```yaml\n{config_output}\n```\n\n"
    else:
        raise RuntimeError(
            f"Failed to retrieve configuration from the image '{image}'."
        )

    return content


def get_config_output(image) -> str | None:
    """Get configuration output from the app."""
    stdout, stderr, returncode = run_docker_command(image, ["config"])
    if returncode == 0:
        return stdout.strip()
    return None


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
