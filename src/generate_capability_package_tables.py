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
import sys
from collections import defaultdict
from dataclasses import dataclass
from logging import Logger
from pathlib import Path
from typing import Any

import click

from utils import config, data, html_table, log
from utils.constants import HEADER_DEFINITIONS, CSSClasses

# catalogers that should be aggregated into a single row with class-pattern pills
SPECIAL_AGGREGATED_CATALOGERS = {"binary-classifier-cataloger"}


@dataclass
class CapabilitySupport:
    """represents support level for a capability."""

    supported: bool  # true if capability is supported (default=true or non-empty)
    conditional: bool  # true if support depends on configuration
    default_value: Any  # the actual default value from the cataloger
    evidence: list[str]  # evidence field paths in syft package metadata
    conditions: list[dict]  # raw condition data for tooltip generation


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
    # whether this cataloger is deprecated
    deprecated: bool = False
    # pattern-level conditions (config requirements for this pattern)
    conditions: list[dict] | None = None


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
    logger = log.setup(verbose, __file__)

    # Clean only owned files to avoid deleting artifacts from other scripts
    output_dir = config.paths.capabilities_snippet_dir
    owned_files = {
        "package.md",
        "syft-app-config.md",
        "binary-package-details.md",
    }
    html_table.clean_owned_files(output_dir, owned_files, logger)

    # load ecosystem aliases
    logger.debug("Loading ecosystem aliases...")
    ecosystem_aliases = data.load_ecosystem_aliases()
    if ecosystem_aliases:
        logger.debug(f"Loaded {len(ecosystem_aliases)} ecosystem aliases")

    # load ecosystem display names
    logger.debug("Loading ecosystem display names...")
    ecosystem_display_names = data.load_ecosystem_display_names()
    if ecosystem_display_names:
        logger.debug(f"Loaded {len(ecosystem_display_names)} ecosystem display names")

    # load or generate cataloger data
    cataloger_data = data.load_cataloger_data(update=update)

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
        config.paths.capabilities_snippet_dir / "overview",
        ecosystem_display_names,
        logger,
    )

    # generate individual ecosystem tables
    ecosystems = {r.ecosystem for r in rows}
    for ecosystem in sorted(ecosystems):
        generate_ecosystem_table(
            ecosystem, rows, config.paths.capabilities_snippet_dir / "ecosystem", logger
        )

    # generate binary package details table (for binary ecosystem)
    if "binary" in ecosystems:
        logger.info("Generating binary package details table...")
        generate_binary_package_details_table(
            cataloger_data,
            config.paths.capabilities_snippet_dir / "ecosystem",
            logger,
        )

    # collect and generate app config snippets
    logger.info("Generating app config snippets...")
    app_configs = collect_app_configs_by_ecosystem(cataloger_data, ecosystem_aliases)
    for ecosystem, config_fields in app_configs.items():
        generate_app_config_snippet(
            ecosystem,
            config_fields,
            config.paths.capabilities_snippet_dir / "ecosystem",
            logger,
        )

    logger.info("Generation complete!")


def determine_capability_support(capability: dict) -> CapabilitySupport:
    """
    determine the support level for a capability based on its default value and conditions.

    Args:
        capability: dict with 'name', 'default', and optionally 'conditions' fields

    Returns:
        CapabilitySupport object
    """
    default_value = capability.get("default")
    conditions = capability.get("conditions", [])
    has_conditions = bool(conditions)
    evidence = capability.get("evidence", [])

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
        evidence=evidence,
        conditions=conditions,
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
        deprecated = cataloger.get("deprecated", False)

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
                    deprecated=deprecated,
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
                    deprecated=deprecated,
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

                # extract pattern-level conditions
                pattern_conditions = pattern.get("conditions")

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
                        deprecated=deprecated,
                        conditions=pattern_conditions,
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


def format_class_pattern_pills(class_pattern_pairs: list[tuple[str, list[str]]]) -> str:
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
    deprecated: bool = False,
    conditions: list[dict] | None = None,
) -> str:
    """
    format cataloger name with evidence patterns for display in a combined table cell.

    Shows cataloger name prominently (in div, not code), then evidence patterns below in a div with code tags.
    For special catalogers, displays class-pattern pills instead of regular evidence.
    If pattern has conditions, shows a gear icon inline after the cataloger name.

    Args:
        cataloger_name: name of the cataloger
        globs: list of glob patterns
        paths: list of path patterns
        mimetypes: list of mimetype patterns
        class_pattern_pairs: optional list of (class_name, [patterns]) for special catalogers
        deprecated: whether this cataloger is deprecated
        conditions: optional pattern-level conditions (config requirements)

    Returns:
        formatted HTML string for combined cataloger+evidence cell
    """
    # use exact cataloger name (keep -cataloger suffix)
    # build combined cell content - cataloger name in div, not code
    # add deprecated pill inline if cataloger is deprecated
    deprecated_pill = (
        ' <span class="deprecated-pill">deprecated</span>' if deprecated else ""
    )

    # add conditional gear icon inline if pattern has conditions
    condition_icon = ""
    if conditions:
        formatted_condition = html_table.format_conditions_for_tooltip(
            conditions, prefix="Requires"
        )
        if formatted_condition:
            escaped_condition = formatted_condition.replace('"', "&quot;")
            condition_icon = f' <span class="cataloger-condition-wrapper" data-tooltip="{escaped_condition}"><svg class="capability-icon inline-icon"><use href="#icon-gear"/></svg></span>'

    html = f'<div class="cataloger-name">{cataloger_name}{deprecated_pill}{condition_icon}</div>'

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

    # if it contains both direct and indirect, show "Transitive"
    if "direct" in value and "indirect" in value:
        return "Transitive"
    elif "direct" in value:
        return "Direct"
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
        return value.title() if value else ""
    elif isinstance(value, list):
        return ", ".join(str(v).title() for v in value) if value else ""
    else:
        return str(value).title() if value else ""


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
        return ", ".join(str(v).title() for v in value)
    elif isinstance(value, str) and value:
        return value.title()
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
    ecosystem: str, config_fields: list[dict], output_dir: Path, logger: Logger
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
    comment = config.get_generated_comment("src/generate_capability_tables.py", "html")
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
    html_lines.append(
        f'      <th class="{CSSClasses.COL_CONFIG_KEY}"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["configuration_key"]}">Configuration Key</abbr></th>'
    )
    html_lines.append(
        f'      <th class="{CSSClasses.COL_DESCRIPTION}"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["description"]}">Description</abbr></th>'
    )
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
            f'      <td class="{CSSClasses.COL_CONFIG_KEY}"><code>{app_key}</code></td>'
        )
        html_lines.append(
            f'      <td class="{CSSClasses.COL_DESCRIPTION}">{cleaned_description}</td>'
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
            evidence=[],  # aggregated dependency support has no specific evidence
            conditions=[],  # aggregated dependency support has no specific conditions
        )

    return None


def generate_overview_table(
    rows: list[CatalogerRow],
    output_dir: Path,
    display_names: dict[str, str],
    logger: Logger,
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
    comment = config.get_generated_comment("src/generate_capability_tables.py", "html")
    comment += "\n<!-- NOTE: This table uses SVG icons defined in layouts/partials/hooks/body-end.html -->\n"
    comment += "<!-- markdownlint-disable MD013 -->\n"

    # build HTML lines
    html_lines = []

    # table header - single row with simple columns (5 columns total)
    html_lines.append(
        f'<table class="{CSSClasses.CAPABILITY_TABLE} {CSSClasses.CAPABILITY_TABLE_OVERVIEW}">'
    )
    html_lines.append("  <thead>")
    html_lines.append("    <tr>")
    html_lines.append(
        f'      <th class="{CSSClasses.COL_ECOSYSTEM}"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["ecosystem"]}">Ecosystem</abbr></th>'
    )
    html_lines.append(
        f'      <th class="{CSSClasses.COL_CATALOGER}"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["cataloger"]}">Cataloger + Evidence</abbr></th>'
    )
    html_lines.append(
        f'      <th class="{CSSClasses.COL_LICENSE}"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["licenses"]}">Licenses</abbr></th>'
    )
    html_lines.append(
        f'      <th class="{CSSClasses.COL_DEPENDENCY}"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["dependencies"]}">Dependencies</abbr></th>'
    )
    html_lines.append(
        f'      <th class="{CSSClasses.COL_FILES}"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["files"]}">Files</abbr></th>'
    )
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
                f'      <td class="{CSSClasses.COL_ECOSYSTEM}"{rowspan_attr}>{ecosystem_display}</td>'
            )

        # cataloger column with evidence (no rowspan - each row shows its own)
        cataloger_content = format_cataloger_with_evidence(
            row.cataloger_name,
            row.globs,
            row.paths,
            row.mimetypes,
            row.class_pattern_pairs,
            row.deprecated,
            row.conditions,
        )
        html_lines.append(
            f'      <td class="{CSSClasses.COL_CATALOGER}">{cataloger_content}</td>'
        )

        # license column (SVG indicator)
        license_cap = row.capabilities.get("license")
        html_lines.append(
            f'      <td class="{CSSClasses.COL_LICENSE} {CSSClasses.INDICATOR}">{html_table.get_capability_indicator_svg(license_cap)}</td>'
        )

        # dependency column (aggregated SVG indicator)
        dependency_cap = has_any_dependency_support(row.capabilities)
        html_lines.append(
            f'      <td class="{CSSClasses.COL_DEPENDENCY} {CSSClasses.INDICATOR}">{html_table.get_capability_indicator_svg(dependency_cap)}</td>'
        )

        # files column (SVG indicator)
        files_cap = row.capabilities.get("package_manager.files.listing")
        html_lines.append(
            f'      <td class="{CSSClasses.COL_FILES} {CSSClasses.INDICATOR}">{html_table.get_capability_indicator_svg(files_cap)}</td>'
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
    ecosystem: str, rows: list[CatalogerRow], output_dir: Path, logger: Logger
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
    comment = config.get_generated_comment("src/generate_capability_tables.py", "html")
    comment += "\n<!-- NOTE: This table uses SVG icons defined in layouts/partials/hooks/body-end.html -->\n"
    comment += "<!-- markdownlint-disable MD013 -->\n"

    # build HTML lines
    html_lines = []

    # table header with two-row grouped structure
    html_lines.append(
        f'<table class="{CSSClasses.CAPABILITY_TABLE} {CSSClasses.CAPABILITY_TABLE_ECOSYSTEM}">'
    )
    html_lines.append("  <thead>")
    html_lines.append("    <tr>")
    html_lines.append(
        f'      <th class="{CSSClasses.COL_CATALOGER}" rowspan="2"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["cataloger"]}">Cataloger + Evidence</abbr></th>'
    )
    html_lines.append(
        f'      <th class="{CSSClasses.COL_LICENSE}" rowspan="2"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["license"]}">License</abbr></th>'
    )
    html_lines.append(
        f'      <th colspan="3"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["dependencies"]}">Dependencies</abbr></th>'
    )
    html_lines.append(
        f'      <th colspan="3"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["package_manager_claims"]}">Package Manager Claims</abbr></th>'
    )
    html_lines.append("    </tr>")
    html_lines.append("    <tr>")
    html_lines.append(
        f'      <th class="{CSSClasses.COL_DEPTH}"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["depth"]}">Depth</abbr></th>'
    )
    html_lines.append(
        f'      <th class="{CSSClasses.COL_EDGES}"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["edges"]}">Edges</abbr></th>'
    )
    html_lines.append(
        f'      <th class="{CSSClasses.COL_KINDS}"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["kinds"]}">Kinds</abbr></th>'
    )
    html_lines.append(
        f'      <th class="{CSSClasses.COL_FILES}"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["files"]}">Files</abbr></th>'
    )
    html_lines.append(
        f'      <th class="{CSSClasses.COL_DIGESTS}"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["digests"]}">Digests</abbr></th>'
    )
    html_lines.append(
        f'      <th class="{CSSClasses.COL_INTEGRITY_HASH}"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["integrity_hash"]}">Integrity Hash</abbr></th>'
    )
    html_lines.append("    </tr>")
    html_lines.append("  </thead>")
    html_lines.append("  <tbody>")

    # table body (each row shows its own cataloger+evidence and capabilities)
    for row in sorted_rows:
        html_lines.append("    <tr>")

        # cataloger column with evidence (no rowspan - each row shows its own)
        # special handling for binary-classifier-cataloger in ecosystem-specific tables
        if row.cataloger_name == "binary-classifier-cataloger":
            deprecated_pill = (
                ' <span class="deprecated-pill">deprecated</span>'
                if row.deprecated
                else ""
            )
            cataloger_content = f'<div class="cataloger-name">binary-classifier-cataloger{deprecated_pill}</div><div class="evidence-patterns"><em>(see table below)</em></div>'
        else:
            cataloger_content = format_cataloger_with_evidence(
                row.cataloger_name,
                row.globs,
                row.paths,
                row.mimetypes,
                row.class_pattern_pairs,
                row.deprecated,
                row.conditions,
            )
        html_lines.append(
            f'      <td class="{CSSClasses.COL_CATALOGER}">{cataloger_content}</td>'
        )

        # license column (SVG indicator)
        license_cap = row.capabilities.get("license")
        html_lines.append(
            f'      <td class="{CSSClasses.COL_LICENSE} {CSSClasses.INDICATOR}">{html_table.get_capability_indicator_svg(license_cap)}</td>'
        )

        # dependency columns (individual values)
        depth_cap = row.capabilities.get("dependency.depth")
        html_lines.append(
            f'      <td class="{CSSClasses.COL_DEPTH} {CSSClasses.VALUE}">{format_depth_value(depth_cap)}</td>'
        )

        edges_cap = row.capabilities.get("dependency.edges")
        html_lines.append(
            f'      <td class="{CSSClasses.COL_EDGES} {CSSClasses.VALUE}">{format_edges_value(edges_cap)}</td>'
        )

        kinds_cap = row.capabilities.get("dependency.kinds")
        html_lines.append(
            f'      <td class="{CSSClasses.COL_KINDS} {CSSClasses.VALUE}">{format_kinds_value(kinds_cap)}</td>'
        )

        # package manager columns (SVG indicators)
        files_cap = row.capabilities.get("package_manager.files.listing")
        html_lines.append(
            f'      <td class="{CSSClasses.COL_FILES} {CSSClasses.INDICATOR}">{html_table.get_capability_indicator_svg(files_cap)}</td>'
        )

        digests_cap = row.capabilities.get("package_manager.files.digests")
        html_lines.append(
            f'      <td class="{CSSClasses.COL_DIGESTS} {CSSClasses.INDICATOR}">{html_table.get_capability_indicator_svg(digests_cap)}</td>'
        )

        integrity_cap = row.capabilities.get("package_manager.package_integrity_hash")
        html_lines.append(
            f'      <td class="{CSSClasses.COL_INTEGRITY_HASH} {CSSClasses.INDICATOR}">{html_table.get_capability_indicator_svg(integrity_cap)}</td>'
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


def generate_binary_package_details_table(
    cataloger_data: dict, output_dir: Path, logger: Logger
) -> None:
    """
    generate binary package details table showing class-to-package mappings.

    creates a table showing detailed information about each pattern in the
    binary-classifier-cataloger, including class, criteria, PURL, and CPEs.

    Args:
        cataloger_data: dict from syft cataloger info
        output_dir: output directory for snippets (ecosystem/binary/)
        logger: logger instance
    """
    # find binary-classifier-cataloger
    catalogers = cataloger_data.get("catalogers", [])
    binary_cataloger = None
    for cataloger in catalogers:
        if cataloger.get("name") == "binary-classifier-cataloger":
            binary_cataloger = cataloger
            break

    if not binary_cataloger:
        logger.warning("binary-classifier-cataloger not found in cataloger data")
        return

    patterns = binary_cataloger.get("patterns", [])
    if not patterns:
        logger.warning("No patterns found in binary-classifier-cataloger")
        return

    # create output directory
    binary_dir = output_dir / "binary"
    binary_dir.mkdir(parents=True, exist_ok=True)

    output_file = binary_dir / "binary-package-details.md"

    # generate comment
    comment = config.get_generated_comment("src/generate_capability_tables.py", "html")
    comment += "\n<!-- NOTE: This table uses SVG icons defined in layouts/partials/hooks/body-end.html -->\n"
    comment += "<!-- markdownlint-disable MD013 -->\n"

    # build HTML lines
    html_lines = []

    # table header text
    html_lines.append('<div class="config-table-header">Binary Package Details</div>')

    # table header
    html_lines.append(
        f'<table class="{CSSClasses.CAPABILITY_TABLE} {CSSClasses.BINARY_DETAILS_TABLE}">'
    )
    html_lines.append("  <thead>")
    html_lines.append("    <tr>")
    html_lines.append(
        '      <th class="{CSSClasses.COL_CLASS}"><abbr class="{CSSClasses.HEADER_HELP}" title="The classification identifier for this binary pattern">Class</abbr></th>'
    )
    html_lines.append(
        '      <th class="{CSSClasses.COL_CRITERIA}"><abbr class="{CSSClasses.HEADER_HELP}" title="The glob patterns used to identify this binary">Criteria</abbr></th>'
    )
    html_lines.append(
        '      <th class="{CSSClasses.COL_PURL}"><abbr class="{CSSClasses.HEADER_HELP}" title="The Package URL identifier for packages matching this pattern">PURL</abbr></th>'
    )
    html_lines.append(
        '      <th class="{CSSClasses.COL_CPES}"><abbr class="{CSSClasses.HEADER_HELP}" title="Common Platform Enumeration identifiers associated with this package">CPEs</abbr></th>'
    )
    html_lines.append("    </tr>")
    html_lines.append("  </thead>")
    html_lines.append("  <tbody>")

    # sort patterns by class name for consistent output
    def get_class_name(pattern):
        packages = pattern.get("packages", [])
        if packages:
            return packages[0].get("class", "")
        return ""

    sorted_patterns = sorted(patterns, key=get_class_name)

    # table body - one row per pattern
    for pattern in sorted_patterns:
        packages = pattern.get("packages", [])
        if not packages:
            continue

        pkg = packages[0]  # each pattern has exactly one package
        class_name = pkg.get("class", "")
        purl = pkg.get("purl", "")
        cpes = pkg.get("cpes", [])

        # format criteria (glob patterns)
        criteria = pattern.get("criteria", [])
        if criteria:
            criteria_html = ", ".join(
                f"<code>{clean_glob_pattern(c)}</code>" for c in criteria
            )
        else:
            criteria_html = "-"

        # format CPEs
        if not cpes:
            cpes_html = "-"
        elif len(cpes) == 1:
            cpes_html = f"<code>{cpes[0]}</code>"
        else:
            # multiple CPEs - show as separate lines
            cpes_html = "<br>".join(f"<code>{cpe}</code>" for cpe in cpes)

        html_lines.append("    <tr>")
        html_lines.append(f'      <td class="{CSSClasses.COL_CLASS}">{class_name}</td>')
        html_lines.append(
            f'      <td class="{CSSClasses.COL_CRITERIA}">{criteria_html}</td>'
        )
        html_lines.append(
            f'      <td class="{CSSClasses.COL_PURL}"><code>{purl}</code></td>'
        )
        html_lines.append(f'      <td class="{CSSClasses.COL_CPES}">{cpes_html}</td>')
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


if __name__ == "__main__":
    main()
