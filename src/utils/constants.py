"""
constants for HTML generation, output formats, and configuration.

This module centralizes magic strings used across documentation generation scripts
to improve maintainability, reduce typos, and provide IDE autocomplete support.
"""

from enum import Enum


class CSSClasses(str, Enum):
    """CSS class names used in HTML table generation."""

    # table classes
    CAPABILITY_TABLE = "capability-table"
    CAPABILITY_TABLE_OVERVIEW = "capability-table-overview"
    CAPABILITY_TABLE_ECOSYSTEM = "capability-table-ecosystem"
    CAPABILITY_TABLE_OS = "capability-table-os"
    CAPABILITY_TABLE_OS_OVERVIEW = "capability-table-os-overview"
    CAPABILITY_TABLE_VULNERABILITY = "capability-table-vulnerability-capabilities"
    CONFIG_TABLE = "config-table"
    SYFT_CONFIG_TABLE = "syft-config-table"
    GRYPE_CONFIG_TABLE = "grype-config-table"
    BINARY_DETAILS_TABLE = "binary-details-table"

    # column classes - ecosystem/cataloger
    COL_ECOSYSTEM = "col-ecosystem"
    COL_CATALOGER = "col-cataloger"

    # column classes - capabilities
    COL_LICENSE = "col-license"
    COL_DEPENDENCY = "col-dependency"
    COL_FILES = "col-files"
    COL_DEPTH = "col-depth"
    COL_EDGES = "col-edges"
    COL_KINDS = "col-kinds"
    COL_DIGESTS = "col-digests"
    COL_INTEGRITY_HASH = "col-integrity-hash"

    # column classes - OS/vulnerability
    COL_OS_NAME = "col-os-name"
    COL_VERSIONS = "col-versions"
    COL_PROVIDER = "col-provider"
    COL_DATA_SOURCE = "col-data-source"
    COL_DISCLOSURE_AFFECTED = "col-disclosure-affected"
    COL_DISCLOSURE_DATE = "col-disclosure-date"
    COL_FIX_VERSIONS = "col-fix-versions"
    COL_FIX_DATE = "col-fix-date"
    COL_PACKAGE_UPSTREAM_TRACKING = "col-package-upstream_tracking"

    # column classes - config
    COL_CONFIG_KEY = "col-config-key"
    COL_DESCRIPTION = "col-description"

    # column classes - binary details
    COL_CLASS = "col-class"
    COL_CRITERIA = "col-criteria"
    COL_PURL = "col-purl"
    COL_CPES = "col-cpes"

    # column classes - JSON schema
    COL_FIELD_NAME = "col-field-name"
    COL_TYPE = "col-type"

    # table classes - JSON schema
    SCHEMA_TABLE = "schema-table"

    # indicator classes
    INDICATOR = "indicator"
    VALUE = "value"

    # icon and UI classes
    CAPABILITY_ICON = "capability-icon"
    CAPABILITY_ICON_WRAPPER = "capability-icon-wrapper"
    INLINE_ICON = "inline-icon"
    HEADER_HELP = "header-help"
    REQUIRED_ICON = "required-icon"

    # content classes
    CATALOGER_NAME = "cataloger-name"
    EVIDENCE_PATTERNS = "evidence-patterns"
    CONFIG_TABLE_HEADER = "config-table-header"
    DEPRECATED_PILL = "deprecated-pill"
    CATALOGER_CONDITION_WRAPPER = "cataloger-condition-wrapper"
    CLASS_PATTERN_PILL = "class-pattern-pill"
    CLASS_PATTERN_PILLS = "class-pattern-pills"
    PILL_CLASS = "pill-class"
    PILL_PATTERN = "pill-pattern"

    def __str__(self) -> str:
        return self.value


class SVGIcons(str, Enum):
    """SVG icon identifiers for capability indicators."""

    CHECK = "icon-check"
    GEAR = "icon-gear"
    DASH = "icon-dash"

    def __str__(self) -> str:
        return self.value


class OutputFormats(str, Enum):
    """Syft output format identifiers."""

    # SBOM formats
    SYFT_JSON = "syft-json"
    JSON = "json"
    CYCLONEDX_JSON = "cyclonedx-json"
    CYCLONEDX_XML = "cyclonedx-xml"
    SPDX_JSON = "spdx-json"
    SPDX_TAG_VALUE = "spdx-tag-value"
    GITHUB_JSON = "github-json"

    # display formats
    TABLE = "table"
    TEXT = "text"
    PURLS = "purls"

    # code fence languages
    YAML = "yaml"
    CSV = "csv"
    XML = "xml"
    BASH = "bash"
    PYTHON = "python"
    GO_TEXT_TEMPLATE = "go-text-template"
    MARKDOWN = "markdown"

    def __str__(self) -> str:
        return self.value


# Header definitions for table tooltips
# these are shared across capability and vulnerability tables
HEADER_DEFINITIONS: dict[str, str] = {
    # ecosystem/package headers
    "ecosystem": "The package manager or programming language ecosystem",
    "cataloger": "The Syft cataloger name and file patterns it analyzes to discover packages",
    "license": "Whether Syft can detect and catalog license information from package metadata",
    "licenses": "Whether Syft can detect and catalog license information from package metadata",
    "dependencies": "Whether dependency information can be captured (depth, edges, kinds)",
    "depth": "How far into the dependency graph packages are discovered (direct = only explicit dependencies, transitive = all depths)",
    "edges": "Whether relationships between packages can be captured (flat = star topology from root, complete = full dependency graph)",
    "kinds": "Types of dependencies captured (runtime = required at runtime, dev = development dependencies)",
    "package_manager_claims": "Metadata and integrity information explicitly tracked by the package manager about packages and their files",
    "files": "Whether Syft can catalog the list of files that are part of a package installation",
    "digests": "Whether Syft can capture file checksums (digests/hashes) claimed by the package manager for individual files within a package",
    "integrity_hash": "Whether Syft can capture a single package-level hash used by package managers to verify the package itself",
    "configuration_key": "The configuration field name used in Syft/Grype application configuration",
    "description": "Explanation of what the configuration option controls",
    # OS/vulnerability headers
    "operating_system": "The operating system distribution name",
    "supported_versions": "Which OS versions have vulnerability data available",
    "vunnel_provider": "The vunnel provider that supplies vulnerability data for this OS",
    "provider": "The vunnel provider that supplies vulnerability data",
    "data_source": "The upstream vulnerability database or security feed",
    "disclosures": "Information about when and how vulnerabilities are disclosed",
    "fixes": "Information about vulnerability fixes and their availability",
    "disclosure_affected": "Whether vulnerabilities are reported even when no fix exists yet",
    "disclosure_date": "When the vulnerability was first publicly disclosed (separate from fix availability date)",
    "fix_versions": "Which package versions contain fixes for the vulnerability",
    "fix_date": "When the fix was made available",
    "source_package": "Whether the data source tracks upstream/source packages in addition to binary packages (important for RPM/DEB ecosystems)",
}
