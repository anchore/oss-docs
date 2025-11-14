#!/usr/bin/env python3
"""
Convert hardcoded markdown links to Hugo relref shortcodes.

This script finds internal documentation links in markdown files and converts them
to use Hugo's relref feature for build-time link validation.
"""

import re
import sys
from pathlib import Path


def convert_absolute_link(match) -> str:
    """Convert absolute /docs/ links to relref syntax."""
    link_text = match.group(1)
    link_path = match.group(2)

    # If path ends with /, it's likely an _index.md file
    # If it has an anchor, we need to be more explicit
    if "#" in link_path:
        path_part, anchor = link_path.split("#", 1)
        # Add .md extension if not pointing to a directory
        if path_part.endswith("/"):
            # It's an _index.md file
            path_part = path_part.rstrip("/") + "/_index.md"
        elif not path_part.endswith(".md"):
            path_part = path_part + ".md"
        converted = f'[{link_text}]({{{{< relref "{path_part}#{anchor}" >}}}})'
    else:
        converted = f'[{link_text}]({{{{< relref "{link_path}" >}}}})'

    return converted


def convert_relative_link(match):
    """Convert relative ../ links to relref syntax with absolute paths."""
    link_text = match.group(1)
    relative_path = match.group(2)

    # We're in /docs/guides/vulnerability/, so ../ goes to /docs/guides/
    # Convert relative path to absolute
    if relative_path.startswith("../"):
        # Remove ../ prefix
        remaining = relative_path[3:]

        # Determine the absolute path based on context
        # Since we're in vulnerability guide, ../ means /docs/guides/
        if "#" in remaining:
            # Has anchor
            if "/" in remaining:
                # Format: ../other-section/...#anchor
                path_part, anchor = remaining.split("#", 1)
                abs_path = f"/docs/guides/{path_part}"
                if not abs_path.endswith(".md") and not abs_path.endswith("/"):
                    abs_path = abs_path + ".md"
                converted = f'[{link_text}]({{{{< relref "{abs_path}#{anchor}" >}}}})'
            else:
                # Format: ../#anchor (links to parent _index.md)
                anchor = remaining.split("#", 1)[1]
                converted = f'[{link_text}]({{{{< relref "/docs/guides/_index.md#{anchor}" >}}}})'
        else:
            # No anchor
            abs_path = f"/docs/guides/{remaining}"
            converted = f'[{link_text}]({{{{< relref "{abs_path}" >}}}})'
    else:
        # Handle other relative patterns if needed
        converted = match.group(0)  # Return unchanged

    return converted


def process_file(filepath: str) -> bool:
    """Process a markdown file and convert hardcoded links to relref."""
    content = Path(filepath).read_text()
    original_content = content

    # Pattern 1: Absolute internal documentation links [text](/docs/...)
    # Match: [link text](/docs/path/to/file)
    absolute_pattern = r"\[([^\]]+)\]\((/docs/[^)]+)\)"
    content = re.sub(absolute_pattern, convert_absolute_link, content)

    # Pattern 2: Relative links [text](../)
    # Match: [link text](../path/to/file)
    relative_pattern = r"\[([^\]]+)\]\((\.\.\/[^)]+)\)"
    content = re.sub(relative_pattern, convert_relative_link, content)

    # Check if any changes were made
    if content != original_content:
        Path(filepath).write_text(content)
        print(f"✓ Updated {filepath}")
        return True
    else:
        print(f"- No changes needed for {filepath}")
        return False


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: python convert_links_to_relref.py <markdown-file> [<markdown-file> ...]"
        )
        sys.exit(1)

    files_updated = 0
    for filepath in sys.argv[1:]:
        if process_file(filepath):
            files_updated += 1

    print(f"\nSummary: Updated {files_updated} of {len(sys.argv) - 1} files")


if __name__ == "__main__":
    main()
