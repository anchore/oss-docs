#!/usr/bin/env python3
"""Remove description field from all YAML files."""

from pathlib import Path

import yaml

yaml_dir = Path("data/sbom/jq-query-examples")

for yaml_file in yaml_dir.glob("*.yaml"):
    with open(yaml_file) as f:
        data = yaml.safe_load(f)

    # Remove description field
    if "description" in data:
        del data["description"]

    # Write back
    with open(yaml_file, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"✓ Removed description from {yaml_file.name}")

print("\n✓ All descriptions removed from YAML files")
