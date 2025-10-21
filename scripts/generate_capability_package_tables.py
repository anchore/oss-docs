#!/usr/bin/env python3
"""
Generate package capability tables from Syft cataloger information.

This script generates complete HTML tables showing which package analysis
capabilities (license detection, dependency tracking, file listings, etc.)
are supported across different ecosystems and catalogers.

Outputs:
1. Overview table: content/docs/capabilities/snippets/overview/package.md
   - Single-row header with 5 columns: Ecosystem, Cataloger, License, Dependency, Files
   - Cataloger column combines cataloger name with evidence patterns
   - Dependency aggregates depth/edges/kinds into single indicator
   - All capabilities shown as ✅/-/⚙️ indicators

2. Individual ecosystem tables: content/docs/capabilities/snippets/{ecosystem}/package.md
   - Two-row grouped header with 8 columns:
     Row 1: Cataloger, License, Dependency (colspan=3), Package Manager (colspan=3)
     Row 2: (under Dependency) Depth, Edges, Kinds; (under Package Manager) Files, Digests, Integrity Hash
   - Cataloger column combines cataloger name with evidence patterns
   - Depth/Edges/Kinds show actual values, others show ✅/-/⚙️ indicators

NOTE: This script generates HTML tables that use SVG icon symbols (icon-check,
icon-gear, icon-dash). The SVG sprite definitions are in the file
layouts/partials/hooks/body-end.html and are automatically included on every
page by the Docsy theme.
"""

import re
import shutil
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import click
from utils.config import get_generated_comment, paths
from utils.data import (
    load_cataloger_data,
    load_ecosystem_aliases,
    load_ecosystem_display_names,
)
from utils.logging import setup_logging


# Header definitions for tooltips
HEADER_DEFINITIONS = {
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
    "integrity_hash": "Whether Syft can capture a single package-level integrity hash used by package managers to verify the package archive itself",
    "configuration_key": "The configuration field name used in Syft application configuration",
    "description": "Explanation of what the configuration option does",
}


# catalogers that should be aggregated into a single row with class-pattern pills
SPECIAL_AGGREGATED_CATALOGERS = {"binary-classifier-cataloger"}


@dataclass
class CapabilitySupport:
    """represents support level for a capability."""

    supported: bool  # true if capability is supported (default=true or non-empty)
    conditional: bool  # true if support depends on configuration
    default_value: Any  # the actual default value from the cataloger


@dataclass
class CatalogerRow:
    """represents a single row in the capability table."""

    ecosystem: str
    cataloger_name: str
    # evidence aggregated across all patterns for this cataloger
    globs: list[str]  # glob patterns
    paths: list[str]  # path patterns
    mimetypes: list[str]  # mimetype patterns
    # capabilities for this specific pattern/row
    capabilities: dict[str, CapabilitySupport]
    # for special aggregated catalogers: class-to-pattern mappings
    # each tuple is (class_name, [pattern1, pattern2, ...])
    class_pattern_pairs: list[tuple[str, list[str]]] | None = None



def determine_capability_support(capability: dict) -> CapabilitySupport:
    """
    determine the support level for a capability based on its default value and conditions.

    Args:
        capability: dict with 'name', 'default', and optionally 'conditions' fields

    Returns:
        CapabilitySupport object
    """
    default_value = capability.get("default")
    has_conditions = "conditions" in capability

    # determine if capability is supported based on default value
    if isinstance(default_value, bool):
        supported = default_value
    elif isinstance(default_value, (list, str)):
        supported = bool(default_value)  # non-empty list/string means supported
    else:
        supported = False

    return CapabilitySupport(
        supported=supported,
        conditional=has_conditions,
        default_value=default_value,
    )


def parse_catalogers(
    cataloger_data: dict, ecosystem_aliases: dict[str, str]
) -> list[CatalogerRow]:
    """
    parse cataloger data into table rows.

    Args:
        cataloger_data: dict from syft cataloger info
        ecosystem_aliases: dict mapping source to target ecosystem names

    Returns:
        list of CatalogerRow objects
    """
    rows = []
    catalogers = cataloger_data.get("catalogers", [])

    for cataloger in catalogers:
        raw_ecosystem = cataloger.get("ecosystem", "unknown")
        # apply ecosystem aliasing
        ecosystem = ecosystem_aliases.get(raw_ecosystem, raw_ecosystem)
        cataloger_name = cataloger.get("name", "unknown")

        patterns = cataloger.get("patterns", [])
        # cataloger-level capabilities (fallback if pattern doesn't define them)
        cataloger_level_caps = cataloger.get("capabilities", [])

        if not patterns:
            # no patterns, use cataloger-level capabilities with empty evidence
            capabilities = _parse_capabilities(cataloger_level_caps)
            rows.append(
                CatalogerRow(
                    ecosystem=ecosystem,
                    cataloger_name=cataloger_name,
                    globs=[],
                    paths=[],
                    mimetypes=[],
                    capabilities=capabilities,
                )
            )
        elif cataloger_name in SPECIAL_AGGREGATED_CATALOGERS:
            # special catalogers: aggregate all patterns into a single row with class-pattern pills
            class_patterns = defaultdict(set)  # class -> set of patterns

            # collect all class-pattern mappings
            for pattern in patterns:
                method = pattern.get("method", "")
                criteria = pattern.get("criteria", [])

                # extract patterns (assume glob for binary-classifier-cataloger)
                pattern_strings = criteria if method == "glob" else []

                # extract class from packages
                packages = pattern.get("packages", [])
                if packages and pattern_strings:
                    class_name = packages[0].get("class", "unknown")
                    # add all patterns for this class (deduplicated via set)
                    for p in pattern_strings:
                        class_patterns[class_name].add(p)

            # convert to sorted list of tuples for consistent ordering
            class_pattern_pairs = [
                (class_name, sorted(patterns))
                for class_name, patterns in sorted(class_patterns.items())
            ]

            # use cataloger-level capabilities for aggregated row
            capabilities = _parse_capabilities(cataloger_level_caps)

            rows.append(
                CatalogerRow(
                    ecosystem=ecosystem,
                    cataloger_name=cataloger_name,
                    globs=[],  # empty - will use class_pattern_pairs instead
                    paths=[],
                    mimetypes=[],
                    capabilities=capabilities,
                    class_pattern_pairs=class_pattern_pairs,
                )
            )
        else:
            # process each pattern - extract pattern-specific evidence
            for pattern in patterns:
                # extract evidence from THIS pattern only
                method = pattern.get("method", "")
                criteria = pattern.get("criteria", [])

                globs = []
                paths = []
                mimetypes = []

                if method == "glob":
                    globs = criteria
                elif method == "path":
                    paths = criteria
                elif method == "mimetype":
                    mimetypes = criteria

                # prefer pattern-level capabilities, fall back to cataloger-level
                pattern_caps = pattern.get("capabilities", cataloger_level_caps)
                capabilities = _parse_capabilities(pattern_caps)

                rows.append(
                    CatalogerRow(
                        ecosystem=ecosystem,
                        cataloger_name=cataloger_name,
                        globs=globs,
                        paths=paths,
                        mimetypes=mimetypes,
                        capabilities=capabilities,
                    )
                )

    return rows


def _parse_capabilities(capabilities_list: list[dict]) -> dict[str, CapabilitySupport]:
    """
    parse a list of capabilities into a dict keyed by capability name.

    Args:
        capabilities_list: list of capability dicts

    Returns:
        dict mapping capability name to CapabilitySupport
    """
    result = {}

    for cap in capabilities_list:
        cap_name = cap.get("name")
        if cap_name:
            result[cap_name] = determine_capability_support(cap)

    return result


def _calculate_rowspans_for_overview(rows: list[CatalogerRow]) -> dict[str, list[int]]:
    """
    calculate rowspan values for overview table (ecosystem merging only).

    cataloger cells are not merged - each row shows its own cataloger+evidence.

    Args:
        rows: sorted list of CatalogerRow objects

    Returns:
        dict with 'ecosystem' and 'cataloger' keys, each containing list of rowspan values
    """
    n = len(rows)
    rowspans = {
        "ecosystem": [0] * n,
        "cataloger": [0] * n,  # all zeros - no cataloger merging
    }

    if not rows:
        return rowspans

    # calculate ecosystem rowspans
    i = 0
    while i < n:
        current_ecosystem = rows[i].ecosystem
        count = 1
        j = i + 1
        while j < n and rows[j].ecosystem == current_ecosystem:
            count += 1
            j += 1

        rowspans["ecosystem"][i] = count
        i = j

    # cataloger rowspans are all 0 (no merging)
    # each row shows its own cataloger name + pattern-specific evidence

    return rowspans


def _calculate_rowspans_for_ecosystem(rows: list[CatalogerRow]) -> list[int]:
    """
    calculate rowspan values for ecosystem table (no merging).

    cataloger cells are not merged - each row shows its own cataloger+evidence.

    Args:
        rows: sorted list of CatalogerRow objects (all same ecosystem)

    Returns:
        list of rowspan values for cataloger column (all zeros)
    """
    n = len(rows)
    rowspans = [0] * n  # all zeros - no cataloger merging

    # each row shows its own cataloger name + pattern-specific evidence
    return rowspans


def get_capability_indicator(cap_support: CapabilitySupport | None) -> str:
    """
    get the HTML indicator for a capability support level.

    Args:
        cap_support: CapabilitySupport object or None

    Returns:
        HTML string for the indicator
    """
    if cap_support is None:
        return "-"
    elif cap_support.conditional:
        # show conditional indicator even if default is false (user can enable it)
        return "⚙️"  # gear emoji for conditional support
    elif cap_support.supported:
        return "✅"  # checkmark for default support
    else:
        return "-"


def format_evidence(globs: list[str], paths: list[str], mimetypes: list[str]) -> str:
    """
    format evidence patterns for display in a table cell.

    Shows globs and paths (cleaned), and if mimetypes exist, shows them with "(mimetype)" suffix.

    Args:
        globs: list of glob patterns
        paths: list of path patterns
        mimetypes: list of mimetype patterns

    Returns:
        formatted HTML string for evidence cell
    """
    # collect all patterns to display
    patterns = []

    # add cleaned globs and paths (strip **/ prefix)
    patterns.extend(clean_glob_pattern(g) for g in globs)
    patterns.extend(clean_glob_pattern(p) for p in paths)

    # if no patterns at all, return dash
    if not patterns and not mimetypes:
        return "-"

    # format the cell content
    if patterns:
        # show patterns as comma-separated list wrapped in <code>
        content = ", ".join(f"<code>{p}</code>" for p in patterns)
    else:
        content = ""

    # append actual mimetype values if mimetypes exist
    if mimetypes:
        if content:
            content += ", "
        # show actual mimetype values with (mimetype) suffix
        content += ", ".join(f"<code>{m}</code>" for m in mimetypes) + " (mimetype)"

    return content


def format_class_pattern_pills(
    class_pattern_pairs: list[tuple[str, list[str]]]
) -> str:
    """
    format class-to-pattern mappings as two-toned pills.

    Each pill shows the class name on the left (darker) and comma-separated
    patterns on the right (lighter), with patterns in code tags.

    Args:
        class_pattern_pairs: list of (class_name, [pattern1, pattern2, ...]) tuples

    Returns:
        formatted HTML string with class-pattern pills
    """
    if not class_pattern_pairs:
        return "-"

    pills = []
    for class_name, patterns in class_pattern_pairs:
        # clean patterns (remove **/ prefix)
        cleaned_patterns = [clean_glob_pattern(p) for p in patterns]

        # format patterns as comma-separated code tags
        patterns_html = ", ".join(f"<code>{p}</code>" for p in cleaned_patterns)

        # create pill with two-toned structure
        pill_html = (
            f'<span class="class-pattern-pill">'
            f'<span class="pill-class">{class_name}</span>'
            f'<span class="pill-pattern">{patterns_html}</span>'
            f"</span>"
        )
        pills.append(pill_html)

    # wrap all pills in container div
    return f'<div class="class-pattern-pills">{" ".join(pills)}</div>'


def format_cataloger_with_evidence(
    cataloger_name: str,
    globs: list[str],
    paths: list[str],
    mimetypes: list[str],
    class_pattern_pairs: list[tuple[str, list[str]]] | None = None,
) -> str:
    """
    format cataloger name with evidence patterns for display in a combined table cell.

    Shows cataloger name prominently (in div, not code), then evidence patterns below in a div with code tags.
    For special catalogers, displays class-pattern pills instead of regular evidence.

    Args:
        cataloger_name: name of the cataloger
        globs: list of glob patterns
        paths: list of path patterns
        mimetypes: list of mimetype patterns
        class_pattern_pairs: optional list of (class_name, [patterns]) for special catalogers

    Returns:
        formatted HTML string for combined cataloger+evidence cell
    """
    # use exact cataloger name (keep -cataloger suffix)
    # build combined cell content - cataloger name in div, not code
    html = f'<div class="cataloger-name">{cataloger_name}</div>'

    # check if this is a special cataloger with class-pattern pills
    if class_pattern_pairs is not None:
        # use class-pattern pills for special catalogers
        pills_content = format_class_pattern_pills(class_pattern_pairs)
        if pills_content and pills_content != "-":
            html += f'<div class="evidence-patterns">{pills_content}</div>'
    else:
        # use regular evidence patterns
        evidence_content = format_evidence(globs, paths, mimetypes)
        if evidence_content and evidence_content != "-":
            html += f'<div class="evidence-patterns">{evidence_content}</div>'

    return html


def format_depth_value(cap_support: CapabilitySupport | None) -> str:
    """
    format dependency depth value for ecosystem-specific tables.

    Converts ["direct", "indirect"] to "transitive", ["direct"] to "direct".

    Args:
        cap_support: CapabilitySupport object or None

    Returns:
        formatted string: "direct", "transitive", or "-"
    """
    if cap_support is None or not cap_support.supported:
        return ""

    # get the default value (should be a list)
    value = cap_support.default_value
    if not isinstance(value, list) or not value:
        return ""

    # if it contains both direct and indirect, show "transitive"
    if "direct" in value and "indirect" in value:
        return "transitive"
    elif "direct" in value:
        return "direct"
    elif "indirect" in value:
        return "transitive"
    else:
        return ""


def format_edges_value(cap_support: CapabilitySupport | None) -> str:
    """
    format dependency edges value for ecosystem-specific tables.

    Shows the raw value from JSON.

    Args:
        cap_support: CapabilitySupport object or None

    Returns:
        formatted string or "-"
    """
    if cap_support is None or not cap_support.supported:
        return ""

    value = cap_support.default_value
    if isinstance(value, bool):
        return "✅" if value else ""
    elif isinstance(value, str):
        return value if value else ""
    elif isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else ""
    else:
        return str(value) if value else ""


def format_kinds_value(cap_support: CapabilitySupport | None) -> str:
    """
    format dependency kinds value for ecosystem-specific tables.

    Shows comma-separated list of kinds.

    Args:
        cap_support: CapabilitySupport object or None

    Returns:
        formatted string or "-"
    """
    if cap_support is None or not cap_support.supported:
        return ""

    value = cap_support.default_value
    if isinstance(value, list) and value:
        return ", ".join(str(v) for v in value)
    elif isinstance(value, str) and value:
        return value
    else:
        return ""


def collect_app_configs_by_ecosystem(
    cataloger_data: dict, ecosystem_aliases: dict[str, str]
) -> dict[str, list[dict]]:
    """
    collect all app-level configuration options grouped by ecosystem.

    Args:
        cataloger_data: dict from syft cataloger info
        ecosystem_aliases: dict mapping source to target ecosystem names

    Returns:
        dict mapping ecosystem name to list of unique config field dicts
    """
    ecosystem_configs = defaultdict(lambda: {})  # ecosystem -> {app_key -> field_dict}
    catalogers = cataloger_data.get("catalogers", [])

    for cataloger in catalogers:
        raw_ecosystem = cataloger.get("ecosystem", "unknown")
        # apply ecosystem aliasing
        ecosystem = ecosystem_aliases.get(raw_ecosystem, raw_ecosystem)

        # check if this cataloger has config
        config = cataloger.get("config")
        if not config:
            continue

        # extract config fields
        fields = config.get("fields", [])
        for field in fields:
            app_key = field.get("app_key")
            if not app_key:
                continue

            # deduplicate by app_key (catalogers may share config)
            if app_key not in ecosystem_configs[ecosystem]:
                ecosystem_configs[ecosystem][app_key] = {
                    "app_key": app_key,
                    "key": field.get("key", ""),
                    "description": field.get("description", ""),
                }

    # convert to sorted lists
    result = {}
    for ecosystem, configs_dict in ecosystem_configs.items():
        # sort by app_key for consistent output
        result[ecosystem] = sorted(configs_dict.values(), key=lambda x: x["app_key"])

    return result


def strip_field_name_from_description(description: str, field_key: str) -> str:
    """
    strip redundant field name prefix from godoc-style description.

    godoc strings typically start with the field name, e.g.:
    "GuessUnpinnedRequirements attempts to infer..."

    this function removes that prefix and capitalizes the remaining text.

    Args:
        description: the description string
        field_key: the field name (e.g., "GuessUnpinnedRequirements")

    Returns:
        cleaned description with field name prefix removed
    """
    if not description or not field_key:
        return description

    # check if description starts with field name followed by space
    prefix = field_key + " "
    if description.startswith(prefix):
        # remove the prefix
        cleaned = description[len(prefix) :]
        # capitalize first letter
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]
        return cleaned

    return description


def generate_app_config_snippet(
    ecosystem: str, config_fields: list[dict], output_dir: Path, logger
) -> None:
    """
    generate app configuration snippet for an ecosystem.

    Args:
        ecosystem: ecosystem name
        config_fields: list of config field dicts with app_key and description
        output_dir: output directory for snippets
        logger: logger instance
    """
    if not config_fields:
        return

    ecosystem_dir = output_dir / ecosystem
    ecosystem_dir.mkdir(parents=True, exist_ok=True)

    output_file = ecosystem_dir / "syft-app-config.md"

    # generate comment
    comment = get_generated_comment("scripts/generate_capability_tables.py", "html")
    comment += "\n<!-- NOTE: This table uses SVG icons defined in layouts/partials/hooks/body-end.html -->\n"
    comment += "<!-- markdownlint-disable MD013 -->\n"

    # build HTML lines
    html_lines = []

    # table header text
    html_lines.append('<div class="config-table-header">Syft Configuration</div>')

    # table header
    html_lines.append('<table class="config-table syft-config-table">')
    html_lines.append("  <thead>")
    html_lines.append("    <tr>")
    html_lines.append(f'      <th class="col-config-key">Configuration Key <abbr class="header-help" title="{HEADER_DEFINITIONS["configuration_key"]}"><svg class="capability-icon header-help-icon"><use href="#icon-help"/></svg></abbr></th>')
    html_lines.append(f'      <th class="col-description">Description <abbr class="header-help" title="{HEADER_DEFINITIONS["description"]}"><svg class="capability-icon header-help-icon"><use href="#icon-help"/></svg></abbr></th>')
    html_lines.append("    </tr>")
    html_lines.append("  </thead>")
    html_lines.append("  <tbody>")

    # table body
    for field in config_fields:
        app_key = field.get("app_key", "")
        key = field.get("key", "")
        description = field.get("description", "")

        # strip redundant field name prefix from godoc-style descriptions
        cleaned_description = strip_field_name_from_description(description, key)

        html_lines.append("    <tr>")
        html_lines.append(
            f'      <td class="col-config-key"><code>{app_key}</code></td>'
        )
        html_lines.append(
            f'      <td class="col-description">{cleaned_description}</td>'
        )
        html_lines.append("    </tr>")

    # close table
    html_lines.append("  </tbody>")
    html_lines.append("</table>")

    # write file
    with open(output_file, "w") as f:
        f.write(comment)
        for line in html_lines:
            f.write(line + "\n")

    logger.debug(f"Generated {output_file}")


def clean_cataloger_name(name: str) -> str:
    """
    clean cataloger name by removing -cataloger suffix.

    Args:
        name: cataloger name

    Returns:
        cleaned name without -cataloger suffix
    """
    return name.removesuffix("-cataloger")


def get_ecosystem_display_name(ecosystem: str, display_names: dict[str, str]) -> str:
    """
    get the display name for an ecosystem.

    Args:
        ecosystem: ecosystem key (e.g., "python", "dotnet", "github-actions")
        display_names: dict mapping ecosystem keys to display names

    Returns:
        display name for the ecosystem, falling back to title case if not found

    Examples:
        >>> get_ecosystem_display_name("python", {"python": "Python"})
        'Python'
        >>> get_ecosystem_display_name("dotnet", {"dotnet": ".NET"})
        '.NET'
        >>> get_ecosystem_display_name("unknown", {})
        'Unknown'
    """
    # look up display name, fall back to title case
    return display_names.get(ecosystem, ecosystem.title())


def get_ecosystem_sort_key(ecosystem: str, display_names: dict[str, str]) -> str:
    """
    get the sort key for an ecosystem, stripping leading non-alphabetic characters from display name.

    this ensures ecosystems like ".NET" sort under "N" rather than at the beginning or in the "d" section.

    Args:
        ecosystem: ecosystem key (e.g., "dotnet", "python")
        display_names: dict mapping ecosystem keys to display names

    Returns:
        lowercase sort key with leading non-alphabetic characters removed

    Examples:
        >>> get_ecosystem_sort_key("dotnet", {"dotnet": ".NET"})
        'net'
        >>> get_ecosystem_sort_key("python", {"python": "Python"})
        'python'
        >>> get_ecosystem_sort_key("c++", {"c++": "C++"})
        'c++'
    """
    display_name = get_ecosystem_display_name(ecosystem, display_names)
    # strip leading non-alphabetic characters and convert to lowercase for case-insensitive sorting
    cleaned = re.sub(r"^[^a-zA-Z]+", "", display_name)
    return cleaned.lower()


def clean_glob_pattern(pattern: str) -> str:
    """
    clean glob pattern by removing **/ prefix.

    Args:
        pattern: glob pattern

    Returns:
        cleaned pattern without **/ prefix
    """
    return pattern.removeprefix("**/")


def get_svg_icon(icon_type: str) -> str:
    """
    get SVG icon HTML for a capability indicator.

    Args:
        icon_type: 'check', 'gear', or 'dash'

    Returns:
        HTML string with SVG icon
    """
    if icon_type not in ["check", "gear", "dash"]:
        icon_type = "dash"
    return f'<svg class="capability-icon"><use href="#icon-{icon_type}"/></svg>'


def get_capability_indicator_svg(cap_support: CapabilitySupport | None) -> str:
    """
    get the SVG icon for a capability support level.

    Args:
        cap_support: CapabilitySupport object or None

    Returns:
        HTML string with SVG icon, or empty string if not supported
    """
    if cap_support is None:
        return ""
    elif cap_support.conditional:
        return get_svg_icon("gear")
    elif cap_support.supported:
        return get_svg_icon("check")
    else:
        return ""


def has_any_dependency_support(
    capabilities: dict[str, CapabilitySupport],
) -> CapabilitySupport | None:
    """
    check if any dependency capability is supported (for aggregated indicator).

    Args:
        capabilities: dict of capability name to CapabilitySupport

    Returns:
        CapabilitySupport representing aggregated dependency support, or None
    """
    # check depth, edges, kinds
    dependency_keys = ["dependency.depth", "dependency.edges", "dependency.kinds"]

    has_support = False
    has_conditional = False

    for key in dependency_keys:
        cap = capabilities.get(key)
        if cap and cap.supported:
            has_support = True
        if cap and cap.conditional:
            has_conditional = True

    if has_support or has_conditional:
        return CapabilitySupport(
            supported=has_support,
            conditional=has_conditional,
            default_value=None,
        )

    return None


def generate_overview_table(
    rows: list[CatalogerRow], output_dir: Path, display_names: dict[str, str], logger
) -> None:
    """
    generate overview table with simple single-row header.

    Columns: Ecosystem, Cataloger, License, Dependency, Files (5 columns)
    - Cataloger column combines cataloger name with evidence patterns
    - Dependency aggregates depth/edges/kinds into single indicator
    - Files shows package_manager.files.listing indicator

    Args:
        rows: list of all CatalogerRow objects
        output_dir: output directory for snippets
        display_names: dict mapping ecosystem keys to display names
        logger: logger instance
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "package.md"

    # sort rows by ecosystem and cataloger (using display name for ecosystem sorting)
    sorted_rows = sorted(
        rows,
        key=lambda r: (
            get_ecosystem_sort_key(r.ecosystem, display_names),
            r.cataloger_name,
        ),
    )

    # calculate rowspans for ecosystem and cataloger columns
    rowspans = _calculate_rowspans_for_overview(sorted_rows)

    # generate comment
    comment = get_generated_comment("scripts/generate_capability_tables.py", "html")
    comment += "\n<!-- NOTE: This table uses SVG icons defined in layouts/partials/hooks/body-end.html -->\n"
    comment += "<!-- markdownlint-disable MD013 -->\n"

    # build HTML lines
    html_lines = []

    # table header - single row with simple columns (5 columns total)
    html_lines.append('<table class="capability-table capability-table-overview">')
    html_lines.append("  <thead>")
    html_lines.append("    <tr>")
    html_lines.append(f'      <th class="col-ecosystem">Ecosystem <abbr class="header-help" title="{HEADER_DEFINITIONS["ecosystem"]}"><svg class="capability-icon header-help-icon"><use href="#icon-help"/></svg></abbr></th>')
    html_lines.append(f'      <th class="col-cataloger">Cataloger + Evidence <abbr class="header-help" title="{HEADER_DEFINITIONS["cataloger"]}"><svg class="capability-icon header-help-icon"><use href="#icon-help"/></svg></abbr></th>')
    html_lines.append(f'      <th class="col-license">Licenses <abbr class="header-help" title="{HEADER_DEFINITIONS["licenses"]}"><svg class="capability-icon header-help-icon"><use href="#icon-help"/></svg></abbr></th>')
    html_lines.append(f'      <th class="col-dependency">Dependencies <abbr class="header-help" title="{HEADER_DEFINITIONS["dependencies"]}"><svg class="capability-icon header-help-icon"><use href="#icon-help"/></svg></abbr></th>')
    html_lines.append(f'      <th class="col-files">Files <abbr class="header-help" title="{HEADER_DEFINITIONS["files"]}"><svg class="capability-icon header-help-icon"><use href="#icon-help"/></svg></abbr></th>')
    html_lines.append("    </tr>")
    html_lines.append("  </thead>")
    html_lines.append("  <tbody>")

    # table body
    for i, row in enumerate(sorted_rows):
        html_lines.append("    <tr>")

        # ecosystem column (with rowspan) - use display name
        if rowspans["ecosystem"][i] > 0:
            rowspan_attr = (
                f' rowspan="{rowspans["ecosystem"][i]}"'
                if rowspans["ecosystem"][i] > 1
                else ""
            )
            ecosystem_display = get_ecosystem_display_name(row.ecosystem, display_names)
            html_lines.append(
                f'      <td class="col-ecosystem"{rowspan_attr}>{ecosystem_display}</td>'
            )

        # cataloger column with evidence (no rowspan - each row shows its own)
        cataloger_content = format_cataloger_with_evidence(
            row.cataloger_name,
            row.globs,
            row.paths,
            row.mimetypes,
            row.class_pattern_pairs,
        )
        html_lines.append(f'      <td class="col-cataloger">{cataloger_content}</td>')

        # license column (SVG indicator)
        license_cap = row.capabilities.get("license")
        html_lines.append(
            f'      <td class="col-license indicator">{get_capability_indicator_svg(license_cap)}</td>'
        )

        # dependency column (aggregated SVG indicator)
        dependency_cap = has_any_dependency_support(row.capabilities)
        html_lines.append(
            f'      <td class="col-dependency indicator">{get_capability_indicator_svg(dependency_cap)}</td>'
        )

        # files column (SVG indicator)
        files_cap = row.capabilities.get("package_manager.files.listing")
        html_lines.append(
            f'      <td class="col-files indicator">{get_capability_indicator_svg(files_cap)}</td>'
        )

        html_lines.append("    </tr>")

    # close table
    html_lines.append("  </tbody>")
    html_lines.append("</table>")

    # write file
    with open(output_file, "w") as f:
        f.write(comment)
        for line in html_lines:
            f.write(line + "\n")

    logger.debug(f"Generated {output_file}")


def generate_ecosystem_table(
    ecosystem: str, rows: list[CatalogerRow], output_dir: Path, logger
) -> None:
    """
    generate complete ecosystem-specific table with grouped capability columns.

    Two-row header structure:
    Row 1: Cataloger, License, Dependency (colspan=3), Package Manager (colspan=3)
    Row 2: (under Dependency) Depth, Edges, Kinds; (under Package Manager) Files, Digests, Integrity Hash

    Cataloger column combines cataloger name with evidence patterns.

    Args:
        ecosystem: ecosystem name
        rows: list of all CatalogerRow objects
        output_dir: output directory for snippets
        logger: logger instance
    """
    ecosystem_dir = output_dir / ecosystem
    ecosystem_dir.mkdir(parents=True, exist_ok=True)

    output_file = ecosystem_dir / "package.md"

    # filter rows for this ecosystem
    ecosystem_rows = [r for r in rows if r.ecosystem == ecosystem]

    if not ecosystem_rows:
        return

    # sort rows by cataloger (grouping needed for evidence rowspans)
    sorted_rows = sorted(ecosystem_rows, key=lambda r: r.cataloger_name)

    # generate comment
    comment = get_generated_comment("scripts/generate_capability_tables.py", "html")
    comment += "\n<!-- NOTE: This table uses SVG icons defined in layouts/partials/hooks/body-end.html -->\n"
    comment += "<!-- markdownlint-disable MD013 -->\n"

    # build HTML lines
    html_lines = []

    # table header with two-row grouped structure
    html_lines.append('<table class="capability-table capability-table-ecosystem">')
    html_lines.append("  <thead>")
    html_lines.append("    <tr>")
    html_lines.append(f'      <th class="col-cataloger" rowspan="2">Cataloger + Evidence <abbr class="header-help" title="{HEADER_DEFINITIONS["cataloger"]}"><svg class="capability-icon header-help-icon"><use href="#icon-help"/></svg></abbr></th>')
    html_lines.append(f'      <th class="col-license" rowspan="2">License <abbr class="header-help" title="{HEADER_DEFINITIONS["license"]}"><svg class="capability-icon header-help-icon"><use href="#icon-help"/></svg></abbr></th>')
    html_lines.append(f'      <th colspan="3">Dependencies <abbr class="header-help" title="{HEADER_DEFINITIONS["dependencies"]}"><svg class="capability-icon header-help-icon"><use href="#icon-help"/></svg></abbr></th>')
    html_lines.append(f'      <th colspan="3">Package Manager Claims <abbr class="header-help" title="{HEADER_DEFINITIONS["package_manager_claims"]}"><svg class="capability-icon header-help-icon"><use href="#icon-help"/></svg></abbr></th>')
    html_lines.append("    </tr>")
    html_lines.append("    <tr>")
    html_lines.append(f'      <th class="col-depth">Depth <abbr class="header-help" title="{HEADER_DEFINITIONS["depth"]}"><svg class="capability-icon header-help-icon"><use href="#icon-help"/></svg></abbr></th>')
    html_lines.append(f'      <th class="col-edges">Edges <abbr class="header-help" title="{HEADER_DEFINITIONS["edges"]}"><svg class="capability-icon header-help-icon"><use href="#icon-help"/></svg></abbr></th>')
    html_lines.append(f'      <th class="col-kinds">Kinds <abbr class="header-help" title="{HEADER_DEFINITIONS["kinds"]}"><svg class="capability-icon header-help-icon"><use href="#icon-help"/></svg></abbr></th>')
    html_lines.append(f'      <th class="col-files">Files <abbr class="header-help" title="{HEADER_DEFINITIONS["files"]}"><svg class="capability-icon header-help-icon"><use href="#icon-help"/></svg></abbr></th>')
    html_lines.append(f'      <th class="col-digests">Digests <abbr class="header-help" title="{HEADER_DEFINITIONS["digests"]}"><svg class="capability-icon header-help-icon"><use href="#icon-help"/></svg></abbr></th>')
    html_lines.append(f'      <th class="col-integrity-hash">Integrity Hash <abbr class="header-help" title="{HEADER_DEFINITIONS["integrity_hash"]}"><svg class="capability-icon header-help-icon"><use href="#icon-help"/></svg></abbr></th>')
    html_lines.append("    </tr>")
    html_lines.append("  </thead>")
    html_lines.append("  <tbody>")

    # table body (each row shows its own cataloger+evidence and capabilities)
    for row in sorted_rows:
        html_lines.append("    <tr>")

        # cataloger column with evidence (no rowspan - each row shows its own)
        cataloger_content = format_cataloger_with_evidence(
            row.cataloger_name,
            row.globs,
            row.paths,
            row.mimetypes,
            row.class_pattern_pairs,
        )
        html_lines.append(f'      <td class="col-cataloger">{cataloger_content}</td>')

        # license column (SVG indicator)
        license_cap = row.capabilities.get("license")
        html_lines.append(
            f'      <td class="col-license indicator">{get_capability_indicator_svg(license_cap)}</td>'
        )

        # dependency columns (individual values)
        depth_cap = row.capabilities.get("dependency.depth")
        html_lines.append(
            f'      <td class="col-depth value">{format_depth_value(depth_cap)}</td>'
        )

        edges_cap = row.capabilities.get("dependency.edges")
        html_lines.append(
            f'      <td class="col-edges value">{format_edges_value(edges_cap)}</td>'
        )

        kinds_cap = row.capabilities.get("dependency.kinds")
        html_lines.append(
            f'      <td class="col-kinds value">{format_kinds_value(kinds_cap)}</td>'
        )

        # package manager columns (SVG indicators)
        files_cap = row.capabilities.get("package_manager.files.listing")
        html_lines.append(
            f'      <td class="col-files indicator">{get_capability_indicator_svg(files_cap)}</td>'
        )

        digests_cap = row.capabilities.get("package_manager.files.digests")
        html_lines.append(
            f'      <td class="col-digests indicator">{get_capability_indicator_svg(digests_cap)}</td>'
        )

        integrity_cap = row.capabilities.get("package_manager.package_integrity_hash")
        html_lines.append(
            f'      <td class="col-integrity-hash indicator">{get_capability_indicator_svg(integrity_cap)}</td>'
        )

        html_lines.append("    </tr>")

    # close table
    html_lines.append("  </tbody>")
    html_lines.append("</table>")

    # write file
    with open(output_file, "w") as f:
        f.write(comment)
        for line in html_lines:
            f.write(line + "\n")

    logger.debug(f"Generated {output_file}")


@click.command()
@click.option(
    "--update",
    is_flag=True,
    help="Update the cataloger data cache even if it already exists",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity (use -v for info, -vv for debug)",
)
def main(update: bool, verbose: int) -> None:
    """Generate package capability table snippets from Syft cataloger information."""
    logger = setup_logging(verbose, __file__)

    # Clean output directory to ensure no stale content
    # Note: This script runs first and shares output dir with generate_capability_vulnerability_tables.py
    output_dir = paths.capabilities_snippet_dir
    if output_dir.exists():
        logger.debug(f"Cleaning output directory: {output_dir}")
        shutil.rmtree(output_dir)

    # load ecosystem aliases
    logger.debug("Loading ecosystem aliases...")
    ecosystem_aliases = load_ecosystem_aliases()
    if ecosystem_aliases:
        logger.debug(f"Loaded {len(ecosystem_aliases)} ecosystem aliases")

    # load ecosystem display names
    logger.debug("Loading ecosystem display names...")
    ecosystem_display_names = load_ecosystem_display_names()
    if ecosystem_display_names:
        logger.debug(f"Loaded {len(ecosystem_display_names)} ecosystem display names")

    # load or generate cataloger data
    cataloger_data = load_cataloger_data(update=update)

    # parse catalogers into rows
    logger.info("Parsing cataloger capabilities...")
    rows = parse_catalogers(cataloger_data, ecosystem_aliases)

    if not rows:
        logger.error("No catalogers found")
        sys.exit(1)

    logger.info(
        f"Found {len(rows)} cataloger patterns across {len({r.ecosystem for r in rows})} ecosystems"
    )

    # generate tables
    logger.info("Generating tables...")

    # generate overview table
    generate_overview_table(
        rows,
        paths.capabilities_snippet_dir / "overview",
        ecosystem_display_names,
        logger,
    )

    # generate individual ecosystem tables
    ecosystems = {r.ecosystem for r in rows}
    for ecosystem in sorted(ecosystems):
        generate_ecosystem_table(
            ecosystem, rows, paths.capabilities_snippet_dir / "ecosystem", logger
        )

    # collect and generate app config snippets
    logger.info("Generating app config snippets...")
    app_configs = collect_app_configs_by_ecosystem(cataloger_data, ecosystem_aliases)
    for ecosystem, config_fields in app_configs.items():
        generate_app_config_snippet(
            ecosystem,
            config_fields,
            paths.capabilities_snippet_dir / "ecosystem",
            logger,
        )

    logger.info("Generation complete!")


if __name__ == "__main__":
    main()
