#!/usr/bin/env python3
"""
Utility functions for working with Syft cataloger information.

Helper functions to extract ecosystem, pattern, and capability information from
cataloger data. To fetch the cataloger data itself (running Syft, honoring
<TOOL>_LOCAL_PATH overrides, and caching), use data.load_cataloger_data().
"""


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
