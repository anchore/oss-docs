"""
output file management utilities for documentation generation scripts.

This module provides utilities for managing output file generation with intelligent
caching and timestamp-based up-to-date checking to avoid unnecessary regeneration.
"""

import shutil
from pathlib import Path


def should_regenerate(
    output_file: Path,
    source_files: list[Path],
    update: bool = False,
) -> bool:
    """
    check if output file needs regeneration based on source file timestamps.

    compares modification times of output file against all source files to determine
    if regeneration is needed. If any source file is newer than the output, or if
    the output doesn't exist, regeneration is needed.

    Args:
        output_file: path to output file to check
        source_files: list of source files that contribute to the output
        update: if True, always return True to force regeneration

    Returns:
        True if output needs regeneration, False if output is up-to-date

    Examples:
        >>> output = Path("output.md")
        >>> sources = [Path("input.yaml"), Path("sbom.json")]
        >>> if should_regenerate(output, sources, update=False):
        ...     # regenerate output
        ...     pass
    """
    # always regenerate if --update flag is set
    if update:
        return True

    # regenerate if output doesn't exist
    if not output_file.exists():
        return True

    # get output modification time
    output_mtime = output_file.stat().st_mtime

    # check if any source file is newer than output
    for source_file in source_files:
        if source_file.exists():
            source_mtime = source_file.stat().st_mtime
            if source_mtime > output_mtime:
                # source is newer, need to regenerate
                return True

    # output is up-to-date
    return False


def should_regenerate_multiple(
    output_files: list[Path],
    source_files: list[Path],
    update: bool = False,
) -> bool:
    """
    check if any output files need regeneration based on source file timestamps.

    similar to should_regenerate(), but checks multiple output files. If any output
    is missing or stale, regeneration is needed.

    Args:
        output_files: list of output files to check
        source_files: list of source files that contribute to outputs
        update: if True, always return True to force regeneration

    Returns:
        True if any output needs regeneration, False if all outputs are up-to-date

    Examples:
        >>> outputs = [Path("query.md"), Path("example.md"), Path("output.md")]
        >>> sources = [Path("query.yaml"), Path("sbom.json")]
        >>> if should_regenerate_multiple(outputs, sources, update=False):
        ...     # regenerate all outputs
        ...     pass
    """
    # always regenerate if --update flag is set
    if update:
        return True

    # check if all outputs exist
    if not all(output.exists() for output in output_files):
        return True

    # get oldest output modification time
    output_mtime = min(output.stat().st_mtime for output in output_files)

    # check if any source file is newer than oldest output
    for source_file in source_files:
        if source_file.exists():
            source_mtime = source_file.stat().st_mtime
            if source_mtime > output_mtime:
                # source is newer, need to regenerate
                return True

    # all outputs are up-to-date
    return False


def get_cache_key(image: str, config_file: Path | None = None) -> str:
    """
    generate a cache key for SBOM caching based on image and optional config.

    converts image name and config file into a filesystem-safe cache key by
    replacing special characters.

    Args:
        image: container image name (e.g., "alpine:3.9.2", "node:18-alpine")
        config_file: optional config file path that affects SBOM generation

    Returns:
        cache key string safe for use in filenames

    Examples:
        >>> get_cache_key("alpine:3.9.2")
        'alpine_3.9.2'

        >>> get_cache_key("node:18-alpine", Path(".syft.yaml"))
        'node_18-alpine_.syft'

        >>> get_cache_key("anchore/syft:latest")
        'anchore_syft_latest'
    """
    # replace special characters with underscores
    cache_key = image.replace(":", "_").replace("/", "_")

    # append config file stem if provided
    if config_file:
        cache_key += f"_{config_file.stem}"

    return cache_key


def clean_directory(
    output_dir: Path,
    update: bool = False,
    logger=None,
) -> None:
    """
    clean output directory when update flag is set.

    removes and recreates the output directory to ensure a clean slate for
    regeneration. Only cleans if update flag is True and directory exists.

    Args:
        output_dir: directory to clean
        update: if True, perform the cleanup
        logger: optional logger for debug output

    Examples:
        >>> from pathlib import Path
        >>> output_dir = Path("/tmp/output")
        >>> output_manager.clean_directory(output_dir, update=True)
        # Removes /tmp/output and recreates it
    """
    if update and output_dir.exists():
        if logger:
            logger.debug(f"Cleaning output directory (--update flag): {output_dir}")
        shutil.rmtree(output_dir)

    # ensure directory exists
    output_dir.mkdir(parents=True, exist_ok=True)


def ensure_directory(path: Path) -> None:
    """
    ensure directory exists, creating it and parents if needed.

    Args:
        path: directory path to create

    Examples:
        >>> ensure_directory(Path("/tmp/nested/dir"))
        # Creates /tmp/nested/dir and any missing parent directories
    """
    path.mkdir(parents=True, exist_ok=True)
