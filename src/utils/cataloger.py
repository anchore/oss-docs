#!/usr/bin/env python3
"""
Utility functions for working with Syft cataloger information.

Provides smart caching for cataloger data retrieved from 'syft cataloger info'
and helper functions to extract ecosystem, pattern, and capability information.
"""

import json
import subprocess

from . import config, log

logger = log.logger(__name__)


def run_syft_cataloger_info(
    syft_image: str = config.docker_images.syft,
    timeout: int = config.timeouts.cataloger_info,
) -> str:
    """
    run 'syft cataloger info' command in Docker and return JSON output.

    Args:
        syft_image: Syft Docker image to use (default: from config)
        timeout: command timeout in seconds (default: from config)

    Returns:
        JSON string containing cataloger information

    Raises:
        RuntimeError: if command fails or times out
    """
    docker_cmd = [
        "docker",
        "run",
        "--rm",
        syft_image,
        "cataloger",
        "info",
        "-o",
        "json",
    ]

    try:
        result = subprocess.run(
            docker_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,  # suppress platform warnings
            text=True,
            timeout=timeout,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Syft cataloger info command failed with code {result.returncode}"
            )

        return result.stdout.strip()

    except subprocess.TimeoutExpired as e:
        raise RuntimeError(
            f"Syft cataloger info command timed out after {timeout} seconds"
        ) from e
    except Exception as e:
        raise RuntimeError(f"Failed to run Syft cataloger info: {e}") from e


def get_cataloger_data(skip_cache: bool = False) -> dict:
    """
    get cataloger data with smart cache management.

    This is the main entry point for retrieving cataloger information.
    It checks for cached data and only calls the Docker command if needed.

    Args:
        skip_cache: if True, bypass cache and fetch fresh data (default: False)

    Returns:
        Dictionary containing parsed cataloger information

    Raises:
        RuntimeError: if data retrieval fails
        json.JSONDecodeError: if cached or fresh data is invalid JSON
    """
    cache_file = config.paths.cataloger_cache_file

    # fast path: return cached data if available and not skipping cache
    if not skip_cache and cache_file.exists():
        try:
            with open(cache_file) as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            # if cache read fails, fall through to fetch fresh data
            pass

    # slow path: fetch fresh data from Docker
    json_output = run_syft_cataloger_info()
    data = json.loads(json_output)

    # persist to cache for future use
    try:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, "w") as f:
            json.dump(data, f, indent=2)
    except OSError as e:
        # cache write failure is not critical, just log and continue
        logger.warning(f"Failed to write cache file: {e}")

    return data


def get_ecosystems(data: dict) -> list[str]:
    """
    extract unique ecosystem list from cataloger data.

    Args:
        data: cataloger data dictionary from get_cataloger_data()

    Returns:
        Sorted list of unique ecosystem names

    Examples:
        >>> data = get_cataloger_data()
        >>> ecosystems = get_ecosystems(data)
        >>> print(ecosystems)
        ['apk', 'dart', 'dotnet', 'go', 'java', ...]
    """
    ecosystems = set()

    catalogers = data.get("catalogers", [])
    for cataloger in catalogers:
        ecosystem = cataloger.get("ecosystem")
        if ecosystem:
            ecosystems.add(ecosystem)

    return sorted(ecosystems)


def get_catalogers_by_ecosystem(data: dict, ecosystem: str) -> list[dict]:
    """
    filter catalogers by ecosystem.

    Args:
        data: cataloger data dictionary from get_cataloger_data()
        ecosystem: ecosystem name to filter by (e.g., "python", "java")

    Returns:
        List of cataloger dictionaries matching the ecosystem

    Examples:
        >>> data = get_cataloger_data()
        >>> python_catalogers = get_catalogers_by_ecosystem(data, "python")
        >>> for cat in python_catalogers:
        ...     print(cat.get("name"))
    """
    catalogers = data.get("catalogers", [])
    return [
        cataloger for cataloger in catalogers if cataloger.get("ecosystem") == ecosystem
    ]


def extract_capabilities(cataloger: dict) -> list[dict]:
    """
    parse capability data from cataloger entry.

    Extracts structured information about what a cataloger can detect.
    Capabilities are defined per pattern, and this function aggregates
    all unique capabilities across all patterns.

    Args:
        cataloger: single cataloger dictionary

    Returns:
        List of capability dictionaries with keys:
        - name: capability name (e.g., "license", "dependency.depth")
        - default: default value for this capability
        - evidence: optional list of evidence sources

    Examples:
        >>> cataloger = {...}
        >>> caps = extract_capabilities(cataloger)
        >>> for cap in caps:
        ...     print(f"{cap['name']}: {cap['default']}")
    """
    capabilities_map = {}

    patterns = cataloger.get("patterns", [])
    for pattern in patterns:
        caps = pattern.get("capabilities", [])
        for cap in caps:
            name = cap.get("name")
            if name and name not in capabilities_map:
                capabilities_map[name] = cap

    return list(capabilities_map.values())


def get_artifact_patterns(cataloger: dict) -> list[str]:
    """
    extract file patterns from cataloger entry.

    Returns the list of file glob patterns that trigger this cataloger.

    Args:
        cataloger: single cataloger dictionary

    Returns:
        List of file glob patterns (e.g., ["**/requirements.txt", "**/setup.py"])

    Examples:
        >>> cataloger = {...}
        >>> patterns = get_artifact_patterns(cataloger)
        >>> print(patterns)
        ['**/requirements.txt', '**/setup.py']
    """
    all_patterns = []

    patterns = cataloger.get("patterns", [])
    for pattern in patterns:
        method = pattern.get("method")
        if method == "glob":
            criteria = pattern.get("criteria", [])
            all_patterns.extend(criteria)

    return all_patterns
