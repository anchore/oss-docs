#!/usr/bin/env python3
"""
Version handling utilities for extracting and parsing version strings.

Provides utilities for:
- Extracting version information from command output
- Parsing semantic version strings
- Comparing and sorting versions
"""

import re
from dataclasses import dataclass
from pathlib import Path


def extract_from_output(
    output: str,
    patterns: list[str] | None = None,
    tool_name: str | None = None,
) -> str:
    """
    extract version string from command output.

    Tries multiple patterns to find version information:
    1. "Version: X.Y.Z" format (case-insensitive)
    2. "ToolName: X.Y.Z" format (if tool_name provided)
    3. Lines containing "version" and a colon
    4. Custom regex patterns

    Args:
        output: command output text
        patterns: optional custom regex patterns to try first
        tool_name: tool name to look for (e.g., "Syft", "Grype")

    Returns:
        version string or "unknown" if not found

    Examples:
        >>> version.extract_from_output("Version: 1.2.3\\nBuild: xyz")
        '1.2.3'

        >>> version.extract_from_output("Syft: v1.0.0\\nOther: info", tool_name="Syft")
        'v1.0.0'

        >>> version.extract_from_output("application version: 2.0.0")
        '2.0.0'
    """
    if not output:
        return "unknown"

    lines = output.strip().split("\n")

    # Try custom patterns first if provided
    if patterns:
        for pattern in patterns:
            for line in lines:
                match = re.search(pattern, line)
                if match:
                    # Return first capture group if present, otherwise full match
                    return match.group(1) if match.groups() else match.group(0)

    # Try standard "Version:" pattern (case-insensitive)
    for line in lines:
        if line.lower().startswith("version:"):
            version = line.split(":", 1)[1].strip()
            if version:
                return version

    # Try tool-specific pattern if tool_name provided
    if tool_name:
        tool_display = tool_name.title()
        for line in lines:
            # Try both original case and title case
            for name_variant in [tool_name, tool_display]:
                if line.startswith(f"{name_variant}:"):
                    version = line.split(":", 1)[1].strip()
                    if version:
                        return version

    # Try any line containing "version" and a colon
    for line in lines:
        if "version" in line.lower() and ":" in line:
            parts = line.split(":", 1)
            if len(parts) == 2:
                version = parts[1].strip()
                if version:
                    return version

    # If nothing found, return unknown
    return "unknown"


def get_app_version(
    image: str, tool_name: str, cache_path: Path, update: bool = False
) -> str | None:
    """
    get application version from container image.

    Retrieves version information from a container image, using caching
    to avoid redundant calls. Parses the version output using extract_from_output().

    Args:
        image: container image name (e.g., "anchore/syft:latest")
        tool_name: tool name for version extraction (e.g., "syft", "grype")
        cache_path: path to cache file for storing version output
        update: if True, bypass cache and fetch fresh version info

    Returns:
        version string (e.g., "v1.2.3") or None if version cannot be retrieved

    Examples:
        >>> cache_path = Path("/tmp/cache/syft/version/output.txt")
        >>> get_app_version("anchore/syft:latest", "syft", cache_path)
        'v1.2.3'
    """
    from . import cache, syft

    # check cache first
    cached = cache.get_output(cache_path, update)

    if cached is not None:
        # parse cached output using utility function
        return extract_from_output(cached, tool_name=tool_name)

    # run command
    stdout, stderr, returncode = syft.run(
        syft_image=image,
        args=["version"],
    )

    if returncode == 0:
        # save to cache
        cache.save(cache_path, stdout)

        # parse output using utility function
        return extract_from_output(stdout, tool_name=tool_name)

    return None


@dataclass
class Version:
    """Parsed semantic version."""

    major: int
    minor: int
    patch: int
    prerelease: str | None = None

    @classmethod
    def parse(cls, version_str: str) -> "Version":
        """
        parse version string into components.

        Handles:
        - Standard semver: "1.2.3"
        - With 'v' prefix: "v1.2.3"
        - With prerelease: "1.2.3-beta.1"

        Args:
            version_str: version string to parse

        Returns:
            Version object

        Raises:
            ValueError: if version string is invalid

        Examples:
            >>> Version.parse("1.2.3")
            Version(major=1, minor=2, patch=3, prerelease=None)

            >>> Version.parse("v2.0.0-beta.1")
            Version(major=2, minor=0, patch=0, prerelease='beta.1')
        """
        # Remove leading 'v' if present
        clean_version = version_str.strip()
        if clean_version.startswith("v"):
            clean_version = clean_version[1:]

        # Split on '-' to separate prerelease
        parts = clean_version.split("-", 1)
        version_parts = parts[0]
        prerelease = parts[1] if len(parts) > 1 else None

        # Parse major.minor.patch
        version_components = version_parts.split(".")
        if len(version_components) < 3:
            raise ValueError(
                f"Invalid version string: {version_str} (expected format: X.Y.Z)"
            )

        try:
            major = int(version_components[0])
            minor = int(version_components[1])
            patch = int(version_components[2])
        except ValueError as e:
            raise ValueError(f"Invalid version string: {version_str}") from e

        return cls(major=major, minor=minor, patch=patch, prerelease=prerelease)

    def __lt__(self, other: "Version") -> bool:
        """
        compare versions for sorting.

        Versions are compared by major, minor, patch in order.
        Prerelease versions are considered less than release versions.
        """
        if not isinstance(other, Version):
            return NotImplemented

        # Compare major.minor.patch
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch

        # If versions are equal, check prerelease
        # No prerelease (release) is greater than prerelease
        if self.prerelease is None and other.prerelease is None:
            return False
        if self.prerelease is None:
            return False  # Release > prerelease
        if other.prerelease is None:
            return True  # Prerelease < release

        # Both have prerelease, compare lexically
        return self.prerelease < other.prerelease

    def __eq__(self, other: object) -> bool:
        """Check if versions are equal."""
        if not isinstance(other, Version):
            return NotImplemented
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.prerelease == other.prerelease
        )

    def __str__(self) -> str:
        """
        format as version string.

        Returns:
            version string in format "X.Y.Z" or "X.Y.Z-prerelease"

        Examples:
            >>> str(Version(1, 2, 3))
            '1.2.3'

            >>> str(Version(2, 0, 0, 'beta.1'))
            '2.0.0-beta.1'
        """
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        return version


def parse(version_str: str) -> Version:
    """
    parse semantic version string into components.

    convenience wrapper around Version.parse().

    Args:
        version_str: version string to parse

    Returns:
        Version object

    Raises:
        ValueError: if version string is invalid

    Examples:
        >>> version.parse("1.2.3")
        Version(major=1, minor=2, patch=3, prerelease=None)

        >>> version.parse("v2.0.0-beta.1")
        Version(major=2, minor=0, patch=0, prerelease='beta.1')
    """
    return Version.parse(version_str)


def compare(v1: str, v2: str) -> int:
    """
    compare two version strings.

    Args:
        v1: first version string
        v2: second version string

    Returns:
        -1 if v1 < v2, 0 if equal, 1 if v1 > v2

    Raises:
        ValueError: if either version string is invalid

    Examples:
        >>> version.compare("1.2.3", "1.2.4")
        -1

        >>> version.compare("2.0.0", "1.9.9")
        1

        >>> version.compare("1.0.0", "1.0.0")
        0
    """
    version1 = parse(v1)
    version2 = parse(v2)

    if version1 < version2:
        return -1
    elif version1 == version2:
        return 0
    else:
        return 1


def sort_strings(versions: list[str], reverse: bool = False) -> list[str]:
    """
    sort version strings numerically.

    Args:
        versions: list of version strings
        reverse: sort descending if True (default: False for ascending)

    Returns:
        sorted list of version strings

    Raises:
        ValueError: if any version string is invalid

    Examples:
        >>> version.sort_strings(["1.2.3", "1.0.0", "2.0.0"])
        ['1.0.0', '1.2.3', '2.0.0']

        >>> version.sort_strings(["1.2.3", "1.0.0", "2.0.0"], reverse=True)
        ['2.0.0', '1.2.3', '1.0.0']
    """
    # Parse all versions
    parsed_versions = [(v, parse(v)) for v in versions]

    # Sort by parsed version
    sorted_versions = sorted(parsed_versions, key=lambda x: x[1], reverse=reverse)

    # Return original strings
    return [v[0] for v in sorted_versions]
