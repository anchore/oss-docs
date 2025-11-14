#!/usr/bin/env python3
"""
Configuration constants and defaults for documentation generation scripts.

Provides centralized configuration via dataclasses to ensure
consistent paths, images, and settings across all scripts.
"""

from dataclasses import dataclass
from pathlib import Path

# schema processing configuration
min_schema_major_version = 16

# types to exclude from all schema documentation
excluded_schema_types = {"MicrosoftKbPatch"}


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
    capabilities_data_dir: Path = data_dir / "capabilities"
    reference_cache_dir: Path = data_dir  # cache for reference doc generation

    # data files
    format_versions_json: Path = sbom_data_dir / "format-versions.json"
    cataloger_cache_file: Path = capabilities_data_dir / "syft-package-catalogers.json"
    ecosystem_aliases_file: Path = capabilities_data_dir / "ecosystem.yaml"
    os_data_file: Path = capabilities_data_dir / "grype-operating-systems.json"
    vulnerability_data_file: Path = capabilities_data_dir / "vulnerability-data.yaml"

    # content directories (output)
    content_dir: Path = project_root / "content"
    docs_dir: Path = content_dir / "docs"
    user_guides_dir: Path = docs_dir / "guides"
    sbom_guides_dir: Path = user_guides_dir / "sbom"
    snippets_dir: Path = sbom_guides_dir / "snippets"
    reference_dir: Path = docs_dir / "reference"
    syft_reference_dir: Path = reference_dir / "syft"
    json_reference_dir: Path = syft_reference_dir / "json"

    # snippet subdirectories
    templates_snippet_dir: Path = snippets_dir / "templates"
    jq_queries_snippet_dir: Path = snippets_dir / "jq-queries"
    format_snippet_dir: Path = snippets_dir / "format"
    format_examples_snippet_dir: Path = format_snippet_dir / "examples"
    capabilities_snippet_dir: Path = docs_dir / "capabilities" / "snippets"

    # snippet files
    format_versions_snippet: Path = format_snippet_dir / "versions.md"

    # external repositories (for reference doc generation)
    syft_repo_root: Path = project_root.parent / "syft"
    default_schema_dir: Path = syft_repo_root / "schema" / "json"


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
    cataloger_info: int = 60

    # jq operations
    jq_query: int = 30

    # docker operations
    docker_command: int = 10


@dataclass(frozen=True)
class ReferenceDocWeights:
    """weight values for reference documentation ordering in Hugo sidebar.

    lower weights appear first in navigation.
    each tool has a 10-number range to allow future expansion.
    """

    # syft documentation weights (10-19)
    syft_cli: int = 10
    syft_config: int = 11
    syft_json_schema: int = 12

    # grype documentation weights (20-29)
    grype_cli: int = 20
    grype_config: int = 21

    # grant documentation weights (30-39)
    grant_cli: int = 30
    grant_config: int = 31

    def get_weight(self, tool_name: str, doc_type: str) -> int:
        """
        get weight for a specific tool and documentation type.

        Args:
            tool_name: tool name ("syft", "grype", or "grant")
            doc_type: documentation type ("cli", "config", or "json_schema")

        Returns:
            weight value for Hugo front matter

        Raises:
            ValueError: if tool_name or doc_type is invalid
        """
        tool = tool_name.lower()
        dtype = doc_type.lower()

        field_name = f"{tool}_{dtype}"

        if hasattr(self, field_name):
            return getattr(self, field_name)

        raise ValueError(
            f"Unknown tool/doc_type combination: {tool_name}/{doc_type}. "
            f"Valid tools: syft, grype, grant. Valid doc types: cli, config, json_schema"
        )


def get_generated_comment(script_path: str, format_type: str = "html") -> str:
    """
    generate an auto-generated comment for the specified format type.

    args:
        script_path: relative path to the script that generates the file
        format_type: one of "html", "yaml", or "json"

    returns:
        formatted comment string with trailing newlines
    """
    message = f"AUTO-GENERATED by {script_path} -- DO NOT MANUALLY EDIT"

    if format_type == "html":
        return f"<!-- {message} -->\n\n"
    elif format_type == "yaml":
        return f"# {message}\n\n"
    elif format_type == "json":
        # JSON doesn't support comments, return a field name/value pair
        return message
    else:
        raise ValueError(f"Unsupported format type: {format_type}")


# singleton instances for easy import
paths = Paths()
docker_images = DockerImages()
timeouts = Timeouts()
reference_weights = ReferenceDocWeights()
