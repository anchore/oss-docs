#!/usr/bin/env python3
"""
Generic cache management utilities for documentation generation scripts.

Provides reusable functions for reading and writing cached content
to avoid redundant command executions.
"""

from pathlib import Path


def get_cached_output(cache_path: Path, update: bool) -> str | None:
    """
    get cached output if available and not updating.

    Args:
        cache_path: path to cache file
        update: if true, ignore cache and return None

    Returns:
        cached output string or None if not available/updating

    Examples:
        >>> cache_path = Path("cache/syft/cli/main/output.txt")
        >>> cached = get_cached_output(cache_path, update=False)
        >>> if cached:
        ...     print("Using cached output")
        ... else:
        ...     print("Need to regenerate")
    """
    # if updating, delete existing cache
    if update and cache_path.exists():
        cache_path.unlink()
        return None

    # check if cache exists
    if cache_path.exists():
        return cache_path.read_text()

    return None


def save_to_cache(cache_path: Path, content: str) -> None:
    """
    save content to cache file.

    creates parent directories if they don't exist.

    Args:
        cache_path: path to cache file
        content: content to save

    Examples:
        >>> cache_path = Path("cache/syft/version/output.txt")
        >>> save_to_cache(cache_path, "Syft version 1.0.0")
    """
    # create directory if it doesn't exist
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(content)
