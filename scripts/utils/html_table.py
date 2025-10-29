"""
HTML table generation utilities for capability and vulnerability tables.

This module provides shared functions for generating HTML tables with consistent
formatting, SVG icons, tooltips, and version handling across capability and
vulnerability documentation.
"""

from dataclasses import dataclass
from pathlib import Path

from utils.constants import CSSClasses, SVGIcons


@dataclass
class OSVersion:
    """represents an operating system version."""

    value: str
    codename: str | None = None


def sort_versions(versions: list[OSVersion]) -> list[OSVersion]:
    """
    sort OS versions numerically with special handling for non-numeric versions.

    special versions like "rolling", "unstable", "edge" are sorted after numeric versions.
    numeric versions are sorted by converting version parts to integers when possible.

    Args:
        versions: list of OSVersion objects to sort

    Returns:
        sorted list of OSVersion objects (numeric first, then special versions)

    Examples:
        >>> versions = [OSVersion("edge"), OSVersion("11.2"), OSVersion("11.1")]
        >>> sorted_versions = sort_versions(versions)
        >>> [v.value for v in sorted_versions]
        ['11.1', '11.2', 'edge']
    """
    special_versions = []
    numeric_versions = []

    for version in versions:
        # check if version is special (non-numeric or single word)
        if version.value.lower() in ["rolling", "unstable", "edge"]:
            special_versions.append(version)
        else:
            numeric_versions.append(version)

    # sort numeric versions
    def version_key(v: OSVersion) -> tuple:
        """generate sort key for version."""
        try:
            # split on '.' and convert to numbers
            parts = v.value.split(".")
            # convert each part to int if possible, otherwise keep as string
            numeric_parts = []
            for part in parts:
                try:
                    numeric_parts.append(int(part))
                except ValueError:
                    # if we hit a non-numeric part, keep it as high value string
                    numeric_parts.append((999999, part))
            return tuple(numeric_parts)
        except Exception:
            # fallback to string comparison
            return (999999, v.value)

    numeric_versions.sort(key=version_key)

    # combine numeric first, then special versions
    return numeric_versions + special_versions


def summarize_versions(versions: list[OSVersion]) -> list[OSVersion]:
    """
    summarize continuous version ranges into condensed format.

    this function groups versions by major version and determines if they can be
    summarized based on whether they form a continuous sequence.

    Args:
        versions: sorted list of OSVersion objects

    Returns:
        condensed list of OSVersion objects

    Examples:
        >>> versions = [OSVersion("11.1"), OSVersion("11.2"), OSVersion("11.3")]
        >>> result = summarize_versions(versions)
        >>> [v.value for v in result]
        ['11']

        >>> versions = [OSVersion("11.2"), OSVersion("11.3"), OSVersion("11.4")]
        >>> result = summarize_versions(versions)
        >>> [v.value for v in result]
        ['11.2+']

        >>> versions = [OSVersion("3.20"), OSVersion("3.21"), OSVersion("edge")]
        >>> result = summarize_versions(versions)
        >>> [v.value for v in result]
        ['3.20+', 'edge']
    """
    if not versions:
        return []

    # separate special versions
    special_versions = []
    numeric_versions = []

    for v in versions:
        if v.value.lower() in ["rolling", "unstable", "edge"]:
            special_versions.append(v)
        else:
            numeric_versions.append(v)

    if not numeric_versions:
        return special_versions

    # group by major version
    from collections import defaultdict

    major_groups = defaultdict(list)

    for v in numeric_versions:
        try:
            parts = v.value.split(".")
            major = parts[0]
            major_groups[major].append(v)
        except Exception:
            # can't parse, keep as-is
            major_groups[v.value].append(v)

    result = []

    # process each major version group
    for major in sorted(
        major_groups.keys(), key=lambda x: int(x) if x.isdigit() else 999999
    ):
        group = major_groups[major]

        if len(group) == 1:
            # single version, keep as-is
            result.append(group[0])
            continue

        # check if we have version.0
        has_zero = any(v.value == major or v.value == f"{major}.0" for v in group)

        # extract minor versions
        minors = []
        for v in group:
            parts = v.value.split(".")
            if len(parts) == 1:
                # just major version (e.g., "11")
                minors.append((0, v))
            elif len(parts) == 2:
                try:
                    minor = int(parts[1])
                    minors.append((minor, v))
                except ValueError:
                    # non-numeric minor, keep as-is
                    result.append(v)
                    continue
            else:
                # more complex version, keep as-is
                result.append(v)
                continue

        # sort by minor version
        minors.sort(key=lambda x: x[0])

        if not minors:
            # no valid minors, add all as-is
            result.extend(group)
            continue

        # check for continuous sequence
        min_minor = minors[0][0]
        max_minor = minors[-1][0]

        # check if sequence is continuous
        expected_minors = set(range(min_minor, max_minor + 1))
        actual_minors = {m[0] for m in minors}
        is_continuous = expected_minors == actual_minors

        # decide how to summarize
        if has_zero or (min_minor == 1 and is_continuous):
            # has .0 or starts from .1 continuously - show just major
            # keep codename from highest minor version if present
            highest_version = minors[-1][1]
            if highest_version.codename:
                result.append(OSVersion(value=major, codename=highest_version.codename))
            else:
                result.append(OSVersion(value=major))
        elif min_minor > 1 and is_continuous:
            # starts from .2+ without .0 or .1 - show "major.minor+"
            result.append(OSVersion(value=f"{major}.{min_minor}+"))
        else:
            # not continuous or has gaps, keep all versions
            for _, v in minors:
                result.append(v)

    return result + special_versions


def format_versions_list(versions: list[OSVersion]) -> str:
    """
    format OS versions for display, with codenames in parentheses.

    versions are sorted numerically and continuous ranges are summarized.
    each version is wrapped in <code> tags, and codenames are shown in parentheses.

    Args:
        versions: list of OSVersion objects

    Returns:
        formatted HTML string for display

    Examples:
        >>> versions = [
        ...     OSVersion("10", "buster"),
        ...     OSVersion("11", "bullseye"),
        ...     OSVersion("12", "bookworm")
        ... ]
        >>> format_versions_list(versions)
        '<code>10</code> (buster), <code>11</code> (bullseye), <code>12</code> (bookworm)'

        >>> versions = [OSVersion("3.2"), OSVersion("3.3"), OSVersion("edge")]
        >>> format_versions_list(versions)
        '<code>3.2+</code>, <code>edge</code>'
    """
    if not versions:
        return "-"

    # sort and summarize versions
    sorted_versions = sort_versions(versions)
    summarized_versions = summarize_versions(sorted_versions)

    formatted = []
    for version in summarized_versions:
        if version.codename:
            formatted.append(f"<code>{version.value}</code> ({version.codename})")
        else:
            formatted.append(f"<code>{version.value}</code>")

    return ", ".join(formatted)


def get_svg_icon(icon_type: str) -> str:
    """
    get SVG icon HTML for a capability indicator.

    the SVG sprite definitions are in layouts/partials/hooks/body-end.html
    and are automatically included on every page by the Docsy theme.

    Args:
        icon_type: 'check', 'gear', or 'dash'

    Returns:
        HTML string with SVG icon reference

    Examples:
        >>> get_svg_icon('check')
        '<svg class="capability-icon"><use href="#icon-check"/></svg>'

        >>> get_svg_icon('gear')
        '<svg class="capability-icon"><use href="#icon-gear"/></svg>'
    """
    # map string to enum
    icon_map = {
        "check": SVGIcons.CHECK,
        "gear": SVGIcons.GEAR,
        "dash": SVGIcons.DASH,
    }
    icon = icon_map.get(icon_type, SVGIcons.DASH)
    return f'<svg class="{CSSClasses.CAPABILITY_ICON}"><use href="#{icon}"/></svg>'


def format_evidence_for_tooltip(evidence: list[str]) -> str:
    """
    format evidence field paths for tooltip display.

    single evidence items are shown as-is, multiple items are formatted as
    a bullet list with line breaks using &#10; HTML entity.

    Args:
        evidence: list of evidence field paths (e.g., ['AlpmDBEntry.Files'])

    Returns:
        formatted string for tooltip:
        - empty string if no evidence
        - single path if one item
        - bullet list with line breaks if multiple items

    Examples:
        >>> format_evidence_for_tooltip([])
        ''

        >>> format_evidence_for_tooltip(['AlpmDBEntry.Files'])
        'AlpmDBEntry.Files'

        >>> format_evidence_for_tooltip(['Path.A', 'Path.B'])
        '&#10;• Path.A&#10;• Path.B'
    """
    if not evidence:
        return ""

    if len(evidence) == 1:
        return evidence[0]

    # format as bullet list with line breaks for multiple items
    return "&#10;".join(f"• {path}" for path in evidence)


def format_conditions_for_tooltip(
    conditions: list[dict], prefix: str = "Requires"
) -> str:
    """
    format condition requirements for tooltip display.

    extracts configuration key-value pairs from condition objects and formats
    them with a prefix. single conditions are shown on one line, multiple
    conditions are formatted as a bullet list.

    Args:
        conditions: list of condition dicts with 'when' and optionally 'value' fields
                   e.g., [{"when": {"IncludeUnindexedArchives": true}}]
                   or [{"when": {"SearchLocalModCacheLicenses": true}, "value": true}]
        prefix: prefix text for the condition (default: "Requires")

    Returns:
        formatted string for tooltip:
        - empty string if no conditions
        - single line for one condition: "Requires: ConfigKey = value"
        - multi-line for multiple conditions with bullet list

    Examples:
        >>> conditions = [{"when": {"IncludeArchives": True}}]
        >>> format_conditions_for_tooltip(conditions)
        'Requires: IncludeArchives = true'

        >>> conditions = [
        ...     {"when": {"Option1": True}},
        ...     {"when": {"Option2": False}}
        ... ]
        >>> format_conditions_for_tooltip(conditions, "When")
        'When:&#10;• Option1 = true&#10;• Option2 = false'
    """
    if not conditions:
        return ""

    # extract all config key-value pairs from conditions
    config_pairs = []
    for condition in conditions:
        when = condition.get("when", {})
        for config_key, config_value in when.items():
            # format value as lowercase string for boolean values
            if isinstance(config_value, bool):
                value_str = str(config_value).lower()
            else:
                value_str = str(config_value)
            config_pairs.append((config_key, value_str))

    if not config_pairs:
        return ""

    # format based on number of config pairs
    if len(config_pairs) == 1:
        config_key, config_value = config_pairs[0]
        return f"{prefix}: {config_key} = {config_value}"

    # multiple pairs - use bullet list with line breaks
    lines = [f"{prefix}:"]
    for config_key, config_value in config_pairs:
        lines.append(f"• {config_key} = {config_value}")
    return "&#10;".join(lines)


def get_capability_indicator_svg(
    cap_support,
    evidence: list[str] | None = None,
    conditions: list[dict] | None = None,
) -> str:
    """
    get the SVG icon for a capability support level with optional tooltip.

    determines the appropriate icon (check or gear) based on whether the capability
    is supported and/or conditional. combines condition and evidence information
    into a tooltip if present.

    Args:
        cap_support: CapabilitySupport object or None (must have supported, conditional,
                    evidence, and conditions attributes if not None)
        evidence: optional evidence list to override cap_support.evidence
        conditions: optional conditions list to override cap_support.conditions

    Returns:
        HTML string with SVG icon (with data-tooltip attribute if tooltip exists),
        or empty string if not supported

    Examples:
        >>> # With supported capability
        >>> class CapSupport:
        ...     supported = True
        ...     conditional = False
        ...     evidence = ['Field.Path']
        ...     conditions = []
        >>> get_capability_indicator_svg(CapSupport())
        '<span class="capability-icon-wrapper" data-tooltip="Field.Path"><svg class="capability-icon"><use href="#icon-check"/></svg></span>'

        >>> # With conditional capability
        >>> class CapSupport:
        ...     supported = True
        ...     conditional = True
        ...     evidence = []
        ...     conditions = [{"when": {"Option": True}}]
        >>> get_capability_indicator_svg(CapSupport())
        '<span class="capability-icon-wrapper" data-tooltip="When: Option = true"><svg class="capability-icon"><use href="#icon-gear"/></svg></span>'
    """
    if cap_support is None:
        return ""

    # use provided evidence/conditions or fall back to cap_support attributes
    if evidence is None:
        evidence = getattr(cap_support, "evidence", [])
    if conditions is None:
        conditions = getattr(cap_support, "conditions", [])

    # determine icon type
    if cap_support.conditional:
        icon_type = "gear"
    elif cap_support.supported:
        icon_type = "check"
    else:
        return ""

    # format tooltip content - combine conditions and evidence if both exist
    tooltip_parts = []

    # add condition info if present
    if conditions:
        formatted_condition = format_conditions_for_tooltip(conditions, prefix="When")
        if formatted_condition:
            tooltip_parts.append(formatted_condition)

    # add evidence info if present
    if evidence:
        formatted_evidence = format_evidence_for_tooltip(evidence)
        if formatted_evidence:
            # add "Evidence:" prefix if we also have conditions
            if tooltip_parts:
                tooltip_parts.append(f"Evidence: {formatted_evidence}")
            else:
                tooltip_parts.append(formatted_evidence)

    # create data attribute for combined tooltip
    tooltip_attr = ""
    if tooltip_parts:
        # join with double line break for visual separation
        combined_tooltip = "&#10;&#10;".join(tooltip_parts)
        # escape quotes for HTML attribute
        escaped_tooltip = combined_tooltip.replace('"', "&quot;")
        tooltip_attr = f' data-tooltip="{escaped_tooltip}"'

    # wrap SVG in span when tooltip exists (SVG elements don't support ::after pseudo-elements)
    icon_enum = SVGIcons.CHECK if icon_type == "check" else SVGIcons.GEAR
    if tooltip_attr:
        return f'<span class="{CSSClasses.CAPABILITY_ICON_WRAPPER}"{tooltip_attr}><svg class="{CSSClasses.CAPABILITY_ICON}"><use href="#{icon_enum}"/></svg></span>'
    else:
        return f'<svg class="{CSSClasses.CAPABILITY_ICON}"><use href="#{icon_enum}"/></svg>'


def clean_owned_files(output_dir: Path, owned_files: set[str], logger) -> None:
    """
    clean only specified files from output directory.

    removes stale files without deleting artifacts from other scripts.
    this is useful when multiple scripts generate files to the same directory
    and each script should only clean up its own files.

    Args:
        output_dir: root output directory
        owned_files: set of filenames this script owns (e.g., {"package.md", "config.md"})
        logger: logger instance for debug output

    Examples:
        >>> from pathlib import Path
        >>> import logging
        >>> logger = logging.getLogger()
        >>> output_dir = Path("/tmp/output")
        >>> owned_files = {"package.md", "config.md"}
        >>> clean_owned_files(output_dir, owned_files, logger)
        # Removes only package.md and config.md from output_dir and subdirectories
    """
    if not output_dir.exists():
        return

    # walk through the directory tree and remove only owned files
    removed_count = 0
    for file_path in output_dir.rglob("*"):
        if file_path.is_file() and file_path.name in owned_files:
            logger.debug(f"Removing stale file: {file_path}")
            file_path.unlink()
            removed_count += 1

    if removed_count > 0:
        logger.debug(f"Cleaned up {removed_count} stale file(s)")


class TableBuilder:
    """
    programmatic HTML table builder for capability and vulnerability tables.

    provides a fluent API for building complex HTML tables with multi-row headers,
    cell attributes (class, rowspan, colspan), and automatic HTML generation.

    Examples:
        >>> builder = TableBuilder("capability-table")
        >>> builder.add_header_row([
        ...     {"class": "col-ecosystem", "content": "Ecosystem", "rowspan": 2},
        ...     {"class": "col-license", "content": "License", "rowspan": 2}
        ... ])
        >>> builder.add_body_row([
        ...     {"class": "col-ecosystem", "content": "Python"},
        ...     {"class": "col-license", "content": "✅"}
        ... ])
        >>> html_lines = builder.build()
    """

    def __init__(self, table_class: str = "capability-table") -> None:
        """
        initialize table builder with CSS class.

        Args:
            table_class: CSS class name for the table element
        """
        self.table_class = table_class
        self.header_rows: list[list[dict[str, str | int]]] = []
        self.body_rows: list[list[dict[str, str | int]]] = []

    def add_header_row(self, cells: list[dict[str, str | int]]) -> "TableBuilder":
        """
        add a header row to the table.

        Args:
            cells: list of cell definitions, each dict can contain:
                - content: cell HTML content (required)
                - class: CSS class name (optional)
                - rowspan: number of rows to span (optional)
                - colspan: number of columns to span (optional)
                - tooltip: tooltip text for abbr element (optional)

        Returns:
            self for method chaining

        Examples:
            >>> builder.add_header_row([
            ...     {"content": "Name", "class": "col-name"},
            ...     {"content": "Value", "class": "col-value", "rowspan": 2}
            ... ])
        """
        self.header_rows.append(cells)
        return self

    def add_body_row(self, cells: list[dict[str, str | int]]) -> "TableBuilder":
        """
        add a body row to the table.

        Args:
            cells: list of cell definitions (same format as add_header_row)

        Returns:
            self for method chaining

        Examples:
            >>> builder.add_body_row([
            ...     {"content": "Python", "class": "col-name"},
            ...     {"content": "3.11", "class": "col-value"}
            ... ])
        """
        self.body_rows.append(cells)
        return self

    def build(self) -> list[str]:
        """
        build the complete HTML table.

        Returns:
            list of HTML lines for the table

        Examples:
            >>> lines = builder.build()
            >>> print("\\n".join(lines))
            <table class="capability-table">
              <thead>
                <tr>
                  <th class="col-name">Name</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td class="col-name">Python</td>
                </tr>
              </tbody>
            </table>
        """
        lines = []

        # table opening
        lines.append(f'<table class="{self.table_class}">')

        # thead
        if self.header_rows:
            lines.append("  <thead>")
            for row in self.header_rows:
                lines.append("    <tr>")
                for cell in row:
                    lines.append(self._format_header_cell(cell))
                lines.append("    </tr>")
            lines.append("  </thead>")

        # tbody
        if self.body_rows:
            lines.append("  <tbody>")
            for row in self.body_rows:
                lines.append("    <tr>")
                for cell in row:
                    lines.append(self._format_body_cell(cell))
                lines.append("    </tr>")
            lines.append("  </tbody>")

        # table closing
        lines.append("</table>")

        return lines

    def _format_header_cell(self, cell: dict[str, str | int]) -> str:
        """
        format a single header cell with attributes.

        Args:
            cell: cell definition dict

        Returns:
            formatted <th> HTML line
        """
        attrs = []

        # add class
        if "class" in cell:
            attrs.append(f'class="{cell["class"]}"')

        # add rowspan
        if "rowspan" in cell and int(cell["rowspan"]) > 1:
            attrs.append(f'rowspan="{cell["rowspan"]}"')

        # add colspan
        if "colspan" in cell and int(cell["colspan"]) > 1:
            attrs.append(f'colspan="{cell["colspan"]}"')

        # format content with optional tooltip
        content = cell.get("content", "")
        tooltip = cell.get("tooltip")

        if tooltip:
            # wrap content in <abbr> with tooltip
            content = f'<abbr class="header-help" title="{tooltip}">{content}</abbr>'

        # build tag
        attr_str = " " + " ".join(attrs) if attrs else ""
        return f"      <th{attr_str}>{content}</th>"

    def _format_body_cell(self, cell: dict[str, str | int]) -> str:
        """
        format a single body cell with attributes.

        Args:
            cell: cell definition dict

        Returns:
            formatted <td> HTML line
        """
        attrs = []

        # add class
        if "class" in cell:
            attrs.append(f'class="{cell["class"]}"')

        # add rowspan
        if "rowspan" in cell and int(cell["rowspan"]) > 1:
            attrs.append(f'rowspan="{cell["rowspan"]}"')

        # add colspan
        if "colspan" in cell and int(cell["colspan"]) > 1:
            attrs.append(f'colspan="{cell["colspan"]}"')

        content = cell.get("content", "")

        # build tag
        attr_str = " " + " ".join(attrs) if attrs else ""
        return f"      <td{attr_str}>{content}</td>"
