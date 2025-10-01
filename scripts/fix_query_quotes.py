#!/usr/bin/env python3
"""Remove surrounding quotes from jq queries in YAML files."""

from pathlib import Path

def fix_yaml_file(file_path):
    """Remove leading and trailing quotes from query."""
    with open(file_path) as f:
        content = f.read()

    lines = content.split('\n')
    in_query = False
    result = []

    for line in lines:
        if line.startswith('query: |'):
            in_query = True
            result.append(line)
        elif in_query and line and not line.startswith(' '):
            # end of query block
            in_query = False
            result.append(line)
        elif in_query and line.strip():
            # remove leading quote and trailing quote
            stripped = line.lstrip()
            if stripped.startswith("'"):
                stripped = stripped[1:]
            if stripped.endswith("'"):
                stripped = stripped[:-1]
            # preserve indentation
            indent = len(line) - len(line.lstrip())
            result.append(' ' * indent + stripped)
        else:
            result.append(line)

    with open(file_path, 'w') as f:
        f.write('\n'.join(result))

def main():
    examples_dir = Path('data/sbom/jq-query-examples')
    yaml_files = sorted(examples_dir.glob('*.yaml'))

    for yaml_file in yaml_files:
        fix_yaml_file(yaml_file)
        print(f"Fixed: {yaml_file.name}")

if __name__ == '__main__':
    main()
