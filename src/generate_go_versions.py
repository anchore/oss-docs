#!/usr/bin/env python3
"""
Generate the minimum Go version for each Go tool from its upstream go.mod.

Writes a Hugo data file consumed by the `go-min-version` shortcode on the
contributing pages.
"""

import json
import re

import click
import requests

from utils import config, log

TOOLS = ["syft", "grype", "grant"]

GO_MOD_URL = "https://raw.githubusercontent.com/anchore/{tool}/main/go.mod"


def fetch_go_version(tool: str) -> str:
    """return the `go` directive value from the tool's go.mod on main."""
    resp = requests.get(GO_MOD_URL.format(tool=tool), timeout=30)
    resp.raise_for_status()
    match = re.search(r"^go\s+(\S+)\s*$", resp.text, re.MULTILINE)
    if not match:
        raise ValueError(f"no go directive found in {tool} go.mod")
    return match.group(1)


@click.command()
@click.option(
    "--update",
    is_flag=True,
    help="Update the JSON file even if it already exists",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity (use -v for info, -vv for debug)",
)
def main(update: bool, verbose: int) -> None:
    """Generate minimum Go versions from upstream go.mod files."""
    logger = log.setup(verbose, __file__)
    output = config.paths.go_versions_json

    if output.exists() and not update:
        logger.info(f"Using existing {output}")
        return

    data = {"_comment": config.get_generated_comment(__file__, "json")}
    for tool in TOOLS:
        data[tool] = fetch_go_version(tool)
        logger.info(f"{tool}: go {data[tool]}")

    with open(output, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    logger.info(f"Generated {output}")


if __name__ == "__main__":
    main()
