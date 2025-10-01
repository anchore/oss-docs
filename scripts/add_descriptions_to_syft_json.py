#!/usr/bin/env python3
"""Add descriptions to syft-json.md file-tabs shortcodes."""

import re
from pathlib import Path

# Read the current markdown file
md_path = Path("content/docs/user-guides/sbom/syft-json.md")
content = md_path.read_text()

# Pattern to match file-tabs shortcodes
pattern = r'{{< file-tabs\s+title=""\s+path="([^"]+)"\s+tabs="([^"]+)" >}}'


def replace_shortcode(match):
    path = match.group(1)
    tabs = match.group(2)

    # Read the description file
    desc_path = Path(path) / "description.md"
    if desc_path.exists():
        description = desc_path.read_text().strip()
        # Escape any quotes in the description
        description = description.replace('"', '\\"')
        return f'{{{{< file-tabs\ntitle="{description}"\npath="{path}"\ntabs="{tabs}" >}}}}'
    else:
        print(f"Warning: No description found at {desc_path}")
        return match.group(0)


# Replace all occurrences
new_content = re.sub(pattern, replace_shortcode, content)

# Write back to file
md_path.write_text(new_content)

print("✓ Updated syft-json.md with descriptions")
