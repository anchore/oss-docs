#!/usr/bin/env python3
"""
Generate supported operating systems table for Grype.

This script generates an HTML table showing all supported operating systems
with their versions, vunnel providers, and data sources.

NOTE: This script generates HTML tables that use SVG icon symbols.
The SVG sprite definitions are in layouts/partials/hooks/body-end.html
and are automatically included on every page by the Docsy theme.
"""

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from utils import config, data, html_table, log
from utils.constants import HEADER_DEFINITIONS, CSSClasses


@dataclass
class OS:
    """represents an operating system with its versions."""

    name: str
    versions: list[html_table.OSVersion]
    release_id: str
    provider: str
    channel: str | None = None


def _convert_os_data_to_objects(os_data: list[dict]) -> list[OS]:
    """
    convert OS data from JSON format to OS objects.

    Args:
        os_data: list of OS dictionaries from data.load_os_data()

    Returns:
        list of OS objects
    """
    os_list = []
    for os_entry in os_data:
        versions = []
        for version_entry in os_entry.get("versions", []):
            versions.append(
                html_table.OSVersion(
                    value=version_entry.get("value", ""),
                    codename=version_entry.get("codename"),
                )
            )

        os_list.append(
            OS(
                name=os_entry.get("name", ""),
                versions=versions,
                release_id=os_entry.get("releaseId", ""),
                provider=os_entry.get("provider", ""),
                channel=os_entry.get("channel"),
            )
        )

    return os_list


def generate_overview_os_table(
    os_list: list[OS],
    vuln_data: dict,
    output_file: Path,
) -> None:
    """
    generate overview table of all supported operating systems.

    Args:
        os_list: list of OS objects
        vuln_data: vulnerability data dict
        output_file: output file path
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # get sources from vulnerability data
    sources = vuln_data.get("sources", {})

    # get OS definitions from vulnerability data
    os_definitions = vuln_data.get("os", {})

    # group OSes by name to handle duplicates (e.g., RedHat with EUS channel)
    os_by_name = defaultdict(list)
    for os_entry in os_list:
        os_by_name[os_entry.name].append(os_entry)

    # use grype OS data as source of truth for which OSes to display
    all_os_names = set(os_by_name.keys())

    # generate comment
    comment = config.get_generated_comment("src/generate_supported_os_table.py", "html")
    comment += "\n<!-- NOTE: This table uses SVG icons defined in layouts/partials/hooks/body-end.html -->\n"

    # build HTML lines
    html_lines = []

    # table header with CSS classes matching capability tables
    html_lines.append(
        f'<table class="{CSSClasses.CAPABILITY_TABLE} {CSSClasses.CAPABILITY_TABLE_OS_OVERVIEW}">'
    )
    html_lines.append("  <thead>")
    html_lines.append("    <tr>")
    html_lines.append(
        f'      <th class="{CSSClasses.COL_OS_NAME}"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["operating_system"]}">Operating System</abbr></th>'
    )
    html_lines.append(
        f'      <th class="{CSSClasses.COL_VERSIONS}"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["supported_versions"]}">Supported Versions</abbr></th>'
    )
    html_lines.append(
        f'      <th class="{CSSClasses.COL_PROVIDER}"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["vunnel_provider"]}">Vunnel Provider</abbr></th>'
    )
    html_lines.append(
        f'      <th class="{CSSClasses.COL_DATA_SOURCE}"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["data_source"]}">Data Source</abbr></th>'
    )
    html_lines.append("    </tr>")
    html_lines.append("  </thead>")
    html_lines.append("  <tbody>")

    # add OS rows, sorted alphabetically by name
    for os_name in sorted(all_os_names):
        os_entries = os_by_name.get(os_name, [])

        # get display name from vulnerability data OS definitions
        os_def = os_definitions.get(os_name, {})
        display_info = os_def.get("display", {})
        display_name = display_info.get("long", os_name.title())

        os_name_cell = display_name

        if os_entries:
            # OS has vulnerability data
            # get data source info (should be same for all entries of same OS)
            source_key = os_entries[0].provider
            source_info = sources.get(source_key, {})
            source_name = source_info.get("name", source_key)
            source_url = source_info.get("url", "")

            # handle multiple entries (e.g., RedHat with EUS)
            if len(os_entries) == 1:
                # single entry, format versions normally
                versions_str = html_table.format_versions_list(os_entries[0].versions)
            else:
                # multiple entries, combine with <br> separator
                version_parts = []
                for entry in os_entries:
                    versions = html_table.format_versions_list(entry.versions)
                    if entry.channel:
                        # annotate with channel name (e.g., "EUS: ")
                        version_parts.append(f"{entry.channel.upper()}: {versions}")
                    else:
                        version_parts.append(versions)
                versions_str = "<br>".join(version_parts)

            provider_cell = f"<code>{os_entries[0].provider}</code>"

            # format data source as link
            if source_url:
                data_source_cell = f'<a href="{source_url}">{source_name}</a>'
            else:
                data_source_cell = source_name
        else:
            # OS has no vulnerability data yet
            versions_str = "unsupported"
            provider_cell = "-"
            data_source_cell = "-"

        html_lines.append("    <tr>")
        html_lines.append(
            f'      <td class="{CSSClasses.COL_OS_NAME}">{os_name_cell}</td>'
        )
        html_lines.append(
            f'      <td class="{CSSClasses.COL_VERSIONS}">{versions_str}</td>'
        )
        html_lines.append(
            f'      <td class="{CSSClasses.COL_PROVIDER}">{provider_cell}</td>'
        )
        html_lines.append(
            f'      <td class="{CSSClasses.COL_DATA_SOURCE}">{data_source_cell}</td>'
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

    logger = log.logger(__name__)
    logger.info(f"Generated {output_file}")


def main() -> None:
    """
    generate supported operating systems table.

    Reads OS data and vulnerability data to generate a table showing
    all supported operating systems with their versions and data sources.
    """
    # load OS data
    os_data = data.load_os_data()
    os_list = _convert_os_data_to_objects(os_data)

    # load vulnerability data
    vuln_data = data.load_vulnerability_data()

    # generate the table
    generate_overview_os_table(os_list, vuln_data, config.paths.supported_os_snippet)


if __name__ == "__main__":
    main()
