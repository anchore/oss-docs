#!/usr/bin/env python3
"""
Data file loading utilities for documentation generation scripts.

Provides reusable functions for loading configuration and data files
used across multiple scripts.
"""

import json
import sys

import yaml

from . import config, log, syft

logger = log.logger(__name__)


def version_to_number(version: str) -> float:
    """
    convert a version string to a comparable number.

    Examples:
        "5" -> 5.0
        "8.4" -> 8.4
        "10" -> 10.0

    Args:
        version: version string (e.g., "5", "8.4")

    Returns:
        float representation for comparison
    """
    try:
        parts = version.split(".")
        if len(parts) == 1:
            return float(parts[0])
        elif len(parts) == 2:
            return float(parts[0]) + float(parts[1]) / 100.0
        else:
            # for more complex versions, just use major.minor
            return float(parts[0]) + float(parts[1]) / 100.0
    except (ValueError, IndexError):
        logger.warning(f"Could not parse version '{version}', treating as 0")
        return 0.0


def parse_version_constraint(constraint: str) -> tuple[str, float]:
    """
    parse a version constraint expression.

    Examples:
        ">= 5" -> (">=", 5.0)
        "<= 8" -> ("<=", 8.0)
        "> 10.5" -> (">", 10.5)

    Args:
        constraint: constraint string (e.g., ">= 5", "<= 8")

    Returns:
        tuple of (operator, version_number)
    """
    constraint = constraint.strip()

    # try two-character operators first
    for op in [">=", "<=", "=="]:
        if constraint.startswith(op):
            version_str = constraint[2:].strip()
            return (op, version_to_number(version_str))

    # try single-character operators
    for op in [">", "<"]:
        if constraint.startswith(op):
            version_str = constraint[1:].strip()
            return (op, version_to_number(version_str))

    # no operator found, assume equals
    return ("==", version_to_number(constraint))


def matches_constraint(version: str, constraint_tuple: tuple[str, float]) -> bool:
    """
    check if a version satisfies a constraint.

    Args:
        version: version string to check (e.g., "7", "8.4")
        constraint_tuple: tuple of (operator, version_number) from parse_version_constraint()

    Returns:
        True if version satisfies the constraint
    """
    version_num = version_to_number(version)
    operator, constraint_num = constraint_tuple

    if operator == ">=":
        return version_num >= constraint_num
    elif operator == "<=":
        return version_num <= constraint_num
    elif operator == ">":
        return version_num > constraint_num
    elif operator == "<":
        return version_num < constraint_num
    elif operator == "==":
        return abs(version_num - constraint_num) < 0.001
    else:
        logger.warning(f"Unknown operator '{operator}', returning False")
        return False


def load_ecosystem_aliases() -> dict[str, str]:
    """
    load ecosystem aliases from YAML file.

    Returns:
        dict mapping source ecosystem names to target ecosystem names

    Examples:
        >>> aliases = load_ecosystem_aliases()
        >>> # {'javascript': 'npm', 'typescript': 'npm'}
    """
    aliases_file = config.paths.ecosystem_aliases_file

    if not aliases_file.exists():
        logger.warning(f"Ecosystem aliases file not found: {aliases_file}")
        return {}

    try:
        with open(aliases_file) as f:
            data = yaml.safe_load(f)
            return data.get("alias", {})
    except Exception as e:
        logger.warning(f"Failed to load ecosystem aliases: {e}")
        return {}


def load_ecosystem_display_names() -> dict[str, str]:
    """
    load ecosystem display names from YAML file.

    Returns:
        dict mapping ecosystem names to their display names

    Examples:
        >>> display_names = load_ecosystem_display_names()
        >>> display_names.get('python')
        'Python'
        >>> display_names.get('dotnet')
        '.NET'
    """
    aliases_file = config.paths.ecosystem_aliases_file

    if not aliases_file.exists():
        logger.warning(f"Ecosystem aliases file not found: {aliases_file}")
        return {}

    try:
        with open(aliases_file) as f:
            data = yaml.safe_load(f)
            return data.get("display_names", {})
    except Exception as e:
        logger.warning(f"Failed to load ecosystem display names: {e}")
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
    cache_file = config.paths.cataloger_cache_file

    # check if cache exists and we're not forcing update
    if cache_file.exists() and not update:
        logger.info(f"Using existing {cache_file}")
        try:
            with open(cache_file) as f:
                data = json.load(f)
                # filter out the _comment field if present
                return {k: v for k, v in data.items() if k != "_comment"}
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in {cache_file}: {e}")
            logger.info("Regenerating cataloger data...")

    # generate cataloger data from syft
    logger.info("Extracting cataloger information from Syft...")
    try:
        stdout, stderr, returncode = syft.run(
            args=["cataloger", "info", "-o", "json"],
            timeout=config.timeouts.cataloger_info,
            env_vars={
                "SYFT_EXP_CAPABILITIES": "true",
            },
        )

        if returncode != 0:
            logger.error(f"Error running Syft: {stderr or stdout}")
            sys.exit(1)

        data = json.loads(stdout)

        # save to cache
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        comment = config.get_generated_comment(__file__, "json")
        cache_data = {"_comment": comment, **data}

        with open(cache_file, "w") as f:
            json.dump(cache_data, f, indent=2)

        logger.info(f"Generated {cache_file}")
        return data

    except Exception as e:
        logger.error(f"Error generating cataloger data: {e}")
        sys.exit(1)


def load_os_data() -> list[dict]:
    """
    load operating system data from grype-operating-systems.json and synthesize
    entries for OSes with 'like' field in vulnerability-data.yaml.

    OSes with 'like' inherit versions from their parent OS:
    - Only main channel versions are inherited (entries without 'channel' field)
    - Optional 'versions' field can filter inherited versions by range constraints
    - Synthetic entries use parent's provider but can have custom releaseId

    Returns:
        list of OS dictionaries with name, versions, releaseId, provider, etc.

    Examples:
        >>> os_list = load_os_data()
        >>> for os_entry in os_list:
        ...     print(os_entry["name"])
    """
    os_file = config.paths.os_data_file

    if not os_file.exists():
        logger.error(f"OS data file not found: {os_file}")
        sys.exit(1)

    try:
        # load base OS data from grype
        with open(os_file) as f:
            os_data = json.load(f)

        # load vulnerability data to find OSes with 'like' field
        vuln_data = load_vulnerability_data()
        os_definitions = vuln_data.get("os", {})

        # synthesize OS entries for OSes with 'like' field
        synthetic_entries = []
        for os_name, os_def in os_definitions.items():
            if "like" not in os_def:
                continue

            like_os = os_def["like"]
            logger.debug(f"Synthesizing OS entries for '{os_name}' (like '{like_os}')")

            # find parent OS entries (filter to main channel only)
            parent_entries = [
                entry
                for entry in os_data
                if entry.get("name") == like_os and entry.get("channel") is None
            ]

            if not parent_entries:
                logger.warning(
                    f"No main channel entries found for parent OS '{like_os}'"
                )
                continue

            # get version constraints if specified
            version_constraints = os_def.get("versions", [])
            constraint_tuples = [
                parse_version_constraint(c) for c in version_constraints
            ]

            # process each parent entry (typically just one for main channel)
            for parent_entry in parent_entries:
                parent_versions = parent_entry.get("versions", [])

                # filter versions by constraints
                filtered_versions = []
                for version_obj in parent_versions:
                    version_str = version_obj.get("value", "")

                    # if no constraints, include all versions
                    if not constraint_tuples:
                        filtered_versions.append(version_obj)
                        continue

                    # check if version matches all constraints
                    if all(
                        matches_constraint(version_str, ct) for ct in constraint_tuples
                    ):
                        filtered_versions.append(version_obj)

                if not filtered_versions:
                    logger.warning(f"No versions matched constraints for '{os_name}'")
                    continue

                # create synthetic entry
                synthetic_entry = {
                    "name": os_name,
                    "versions": filtered_versions,
                    "provider": parent_entry.get("provider"),
                    "releaseId": os_def.get("releaseId", os_name),
                    # never inherit channel - synthetic entries are always main channel
                }

                synthetic_entries.append(synthetic_entry)
                logger.debug(
                    f"Created synthetic entry for '{os_name}' with {len(filtered_versions)} versions"
                )

        # combine original and synthetic entries
        return os_data + synthetic_entries

    except Exception as e:
        logger.error(f"Error loading OS data: {e}")
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
    vuln_file = config.paths.vulnerability_data_file

    if not vuln_file.exists():
        logger.error(f"Vulnerability data file not found: {vuln_file}")
        sys.exit(1)

    try:
        with open(vuln_file) as f:
            data = yaml.safe_load(f)

        # resolve 'like' references in OS definitions
        os_definitions = data.get("os", {})
        for _os_name, os_def in os_definitions.items():
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
        logger.error(f"Error loading vulnerability data: {e}")
        sys.exit(1)
