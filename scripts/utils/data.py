#!/usr/bin/env python3
"""
Data file loading utilities for documentation generation scripts.

Provides reusable functions for loading configuration and data files
used across multiple scripts.
"""

import json
import sys

import yaml

from .config import get_generated_comment, paths, timeouts
from .syft import run_syft


def load_ecosystem_aliases() -> dict[str, str]:
    """
    load ecosystem aliases from YAML file.

    Returns:
        dict mapping source ecosystem names to target ecosystem names

    Examples:
        >>> aliases = load_ecosystem_aliases()
        >>> # {'javascript': 'npm', 'typescript': 'npm'}
    """
    aliases_file = paths.ecosystem_aliases_file

    if not aliases_file.exists():
        print(
            f"Warning: Ecosystem aliases file not found: {aliases_file}", file=sys.stderr
        )
        return {}

    try:
        with open(aliases_file) as f:
            data = yaml.safe_load(f)
            return data.get("alias", {})
    except Exception as e:
        print(f"Warning: Failed to load ecosystem aliases: {e}", file=sys.stderr)
        return {}


def load_cataloger_data(update: bool = False) -> dict:
    """
    load cataloger data from cache or generate it from syft.

    Args:
        update: if true, regenerate data even if cache exists

    Returns:
        dict with cataloger information

    Examples:
        >>> data = load_cataloger_data()
        >>> catalogers = data.get("catalogers", [])
    """
    cache_file = paths.cataloger_cache_file

    # check if cache exists and we're not forcing update
    if cache_file.exists() and not update:
        print(f"Using existing {cache_file}")
        try:
            with open(cache_file) as f:
                data = json.load(f)
                # filter out the _comment field if present
                return {k: v for k, v in data.items() if k != "_comment"}
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON in {cache_file}: {e}", file=sys.stderr)
            print("Regenerating cataloger data...", file=sys.stderr)

    # generate cataloger data from syft
    print("Extracting cataloger information from Syft...")
    try:
        stdout, stderr, returncode = run_syft(
            args=["cataloger", "info", "-o", "json"],
            timeout=timeouts.cataloger_info,
        )

        if returncode != 0:
            print(f"Error running Syft: {stderr or stdout}", file=sys.stderr)
            sys.exit(1)

        data = json.loads(stdout)

        # save to cache
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        comment = get_generated_comment("scripts/generate_capability_tables.py", "json")
        cache_data = {"_comment": comment, **data}

        with open(cache_file, "w") as f:
            json.dump(cache_data, f, indent=2)

        print(f"Generated {cache_file}")
        return data

    except Exception as e:
        print(f"Error generating cataloger data: {e}", file=sys.stderr)
        sys.exit(1)


def load_os_data() -> list[dict]:
    """
    load operating system data from grype-operating-systems.json.

    Returns:
        list of OS dictionaries with name, versions, releaseId, provider, etc.

    Examples:
        >>> os_list = load_os_data()
        >>> for os_entry in os_list:
        ...     print(os_entry["name"])
    """
    os_file = paths.os_data_file

    if not os_file.exists():
        print(f"Error: OS data file not found: {os_file}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(os_file) as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading OS data: {e}", file=sys.stderr)
        sys.exit(1)


def load_vulnerability_data() -> dict:
    """
    load vulnerability data from vulnerability-data.yaml and resolve 'like' references.

    when an OS has a 'like' field, it inherits the 'ecosystem' and 'sources' from the
    referenced OS. this resolution happens at load time so all downstream code works
    with complete OS definitions.

    Returns:
        dict with 'sources', 'ecosystems', and 'os' keys (with 'like' references resolved)

    Examples:
        >>> vuln_data = load_vulnerability_data()
        >>> sources = vuln_data.get("sources", {})
        >>> ecosystems = vuln_data.get("ecosystems", {})
    """
    vuln_file = paths.vulnerability_data_file

    if not vuln_file.exists():
        print(
            f"Error: Vulnerability data file not found: {vuln_file}", file=sys.stderr
        )
        sys.exit(1)

    try:
        with open(vuln_file) as f:
            data = yaml.safe_load(f)

        # resolve 'like' references in OS definitions
        os_definitions = data.get("os", {})
        for os_name, os_def in os_definitions.items():
            if "like" in os_def:
                like_os = os_def["like"]
                like_def = os_definitions.get(like_os, {})

                # inherit ecosystem and sources from referenced OS
                if "ecosystem" not in os_def and "ecosystem" in like_def:
                    os_def["ecosystem"] = like_def["ecosystem"]
                if "sources" not in os_def and "sources" in like_def:
                    os_def["sources"] = like_def["sources"]

        return data
    except Exception as e:
        print(f"Error loading vulnerability data: {e}", file=sys.stderr)
        sys.exit(1)
