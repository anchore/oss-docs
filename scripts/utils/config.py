#!/usr/bin/env python3
"""
Configuration constants and defaults for documentation generation scripts.

Provides centralized configuration via dataclasses to ensure
consistent paths, images, and settings across all scripts.
"""

from dataclasses import dataclass
from pathlib import Path


def _get_project_root() -> Path:
    """get the project root directory (parent of scripts/)."""
    return Path(__file__).parent.parent.parent


@dataclass(frozen=True)
class Paths:
    """file system paths used across scripts."""

    # project root directory
    project_root: Path = _get_project_root()

    # data directories (input)
    data_dir: Path = project_root / "data"
    sbom_data_dir: Path = data_dir / "sbom"
    template_examples_dir: Path = sbom_data_dir / "template-examples"
    jq_query_examples_dir: Path = sbom_data_dir / "jq-query-examples"

    # data files
    format_versions_json: Path = sbom_data_dir / "format-versions.json"

    # content directories (output)
    content_dir: Path = project_root / "content"
    docs_dir: Path = content_dir / "docs"
    user_guides_dir: Path = docs_dir / "user-guides"
    sbom_guides_dir: Path = user_guides_dir / "sbom"
    snippets_dir: Path = sbom_guides_dir / "snippets"

    # snippet subdirectories
    templates_snippet_dir: Path = snippets_dir / "templates"
    jq_queries_snippet_dir: Path = snippets_dir / "jq-queries"
    format_snippet_dir: Path = snippets_dir / "format"
    format_examples_snippet_dir: Path = format_snippet_dir / "examples"

    # snippet files
    format_versions_snippet: Path = format_snippet_dir / "versions.md"


@dataclass(frozen=True)
class DockerImages:
    """docker image references used across scripts."""

    # syft image for running scans
    syft: str = "anchore/syft:latest"

    # test images for generating examples
    alpine_test: str = "alpine:3.9.2"
    busybox_test: str = "busybox:latest"


@dataclass(frozen=True)
class Timeouts:
    """timeout values in seconds for various operations."""

    # syft operations
    syft_scan_default: int = 60
    syft_scan_with_config: int = 120
    syft_format_version_check: int = 60

    # jq operations
    jq_query: int = 30

    # docker operations
    docker_command: int = 10


# singleton instances for easy import
paths = Paths()
docker_images = DockerImages()
timeouts = Timeouts()
