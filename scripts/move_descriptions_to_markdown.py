#!/usr/bin/env python3
"""Move descriptions from file-tabs title to markdown text."""

import re
from pathlib import Path

# Read the current markdown file
md_path = Path("content/docs/user-guides/sbom/syft-json.md")
content = md_path.read_text()

# Pattern to match: **Title:**\n\n{{< file-tabs\ntitle="description"\npath=...
pattern = r'\*\*([^*]+):\*\*\n\n{{< file-tabs\ntitle="([^"]+)"\npath="([^"]+)"\ntabs="([^"]+)" >}}'

def replace_shortcode(match):
    title = match.group(1)
    description = match.group(2)
    path = match.group(3)
    tabs = match.group(4)

    return f'**{title}:**\n\n{description}\n\n{{{{< file-tabs\ntitle=""\npath="{path}"\ntabs="{tabs}" >}}}}'

# Replace all occurrences
new_content = re.sub(pattern, replace_shortcode, content)

# Write back to file
md_path.write_text(new_content)

print("✓ Moved descriptions from title to markdown text")
