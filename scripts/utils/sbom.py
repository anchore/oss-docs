#!/usr/bin/env python3
"""
SBOM caching utilities for documentation generation scripts.

Provides smart caching for SBOM generation to avoid redundant scans
of the same images during documentation generation.
"""

from pathlib import Path

from .config import timeouts
from .logging import get_logger
from .syft import run_syft_scan, run_syft_with_config

logger = get_logger(__name__)


def get_or_generate_sbom(
    image: str,
    cache_dir: Path,
    syft_image: str,
    update: bool = False,
    config_file: Path | None = None,
    return_content: bool = False,
) -> Path | str:
    """
    get SBOM from cache or generate it using Syft.

    creates a cache key from the image name (and optionally config file name).
    if cache exists and update is False, returns cached SBOM. otherwise,
    generates a new SBOM and caches it.

    Args:
        image: container image to scan (e.g., "alpine:3.9.2")
        cache_dir: directory to store cached SBOMs
        syft_image: Syft Docker image to use for scanning
        update: if true, regenerate SBOM even if cache exists
        config_file: optional Syft config file to use during scan
        return_content: if true, return SBOM content as string; else return Path

    Returns:
        Path to cached SBOM file or SBOM content as string (based on return_content)

    Examples:
        >>> # basic usage - returns Path
        >>> sbom_path = get_or_generate_sbom(
        ...     image="alpine:3.9.2",
        ...     cache_dir=Path("cache"),
        ...     syft_image="anchore/syft:latest"
        ... )
        >>>
        >>> # with config file - returns content
        >>> sbom_json = get_or_generate_sbom(
        ...     image="node:18",
        ...     cache_dir=Path("cache"),
        ...     syft_image="anchore/syft:latest",
        ...     config_file=Path(".syft.yaml"),
        ...     return_content=True
        ... )
    """
    # create cache key from image name (and config if provided)
    cache_key = image.replace(":", "_").replace("/", "_")
    if config_file:
        cache_key += f"_{config_file.stem}"
    cache_file = cache_dir / f"{cache_key}.json"

    # if updating, delete existing cache
    if update and cache_file.exists():
        cache_file.unlink()
        logger.debug(f"Deleted cached SBOM: {cache_file}")

    # check cache
    if cache_file.exists():
        logger.debug(f"Using cached SBOM: {cache_file}")
        if return_content:
            return cache_file.read_text()
        return cache_file

    # generate SBOM
    logger.debug(f"Generating SBOM for: {image}")

    if config_file:
        sbom_json = run_syft_with_config(
            target_image=image,
            config_file=config_file,
            syft_image=syft_image,
            output_format="syft-json",
            timeout=timeouts.syft_scan_with_config,
        )
    else:
        sbom_json = run_syft_scan(
            target_image=image,
            syft_image=syft_image,
            output_format="syft-json",
            timeout=timeouts.syft_scan_default,
        )

    # save to cache
    cache_file.write_text(sbom_json)
    logger.debug(f"Cached SBOM to: {cache_file}")

    if return_content:
        return sbom_json
    return cache_file
