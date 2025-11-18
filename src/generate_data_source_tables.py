#!/usr/bin/env python3
"""
Generate vulnerability data source reference tables.

This script generates two HTML tables showing vulnerability data sources:
1. Capabilities table - what capabilities each data source supports
2. Provenance table - where data comes from and which ecosystems use it

NOTE: This script generates HTML tables that use SVG icon symbols (icon-check).
The SVG sprite definitions are in layouts/partials/hooks/body-end.html
and are automatically included on every page by the Docsy theme.
"""

from pathlib import Path

from utils import config, data, log
from utils.constants import HEADER_DEFINITIONS, CSSClasses


def get_ecosystem_display_name(ecosystem: str, display_names: dict[str, str]) -> str:
    """
    get the display name for an ecosystem.

    Args:
        ecosystem: ecosystem key (e.g., "python", "dotnet", "apk")
        display_names: dict mapping ecosystem keys to display names

    Returns:
        display name for the ecosystem, falling back to title case if not found
    """
    return display_names.get(ecosystem, ecosystem.title())


def build_source_to_ecosystems_map(
    vuln_data: dict, display_names: dict[str, str]
) -> dict[str, list[str]]:
    """
    build a mapping from data sources to the ecosystems that use them.

    Args:
        vuln_data: vulnerability data dict from YAML
        display_names: dict mapping ecosystem keys to display names

    Returns:
        dict mapping source keys to sorted lists of ecosystem display names
    """
    source_to_ecosystems: dict[str, set[str]] = {}

    # process language ecosystems from the ecosystems section
    ecosystems_section = vuln_data.get("ecosystems", {})
    for eco_key, eco_def in ecosystems_section.items():
        if eco_key == "default":
            # skip the default entry as it's a fallback
            continue

        sources = eco_def.get("sources", [])
        for source_entry in sources:
            # handle both dict format (with 'name' and 'when') and string format
            if isinstance(source_entry, dict):
                source_key = source_entry.get("name", "")
            else:
                source_key = source_entry

            if source_key:
                if source_key not in source_to_ecosystems:
                    source_to_ecosystems[source_key] = set()
                source_to_ecosystems[source_key].add(eco_key)

    # process OS ecosystems from the os section
    os_section = vuln_data.get("os", {})
    for os_def in os_section.values():
        # get the ecosystem for this OS (e.g., apk, dpkg, rpm)
        ecosystem = os_def.get("ecosystem")
        if not ecosystem:
            continue

        sources = os_def.get("sources", [])
        for source_key in sources:
            if source_key:
                if source_key not in source_to_ecosystems:
                    source_to_ecosystems[source_key] = set()
                source_to_ecosystems[source_key].add(ecosystem)

    # convert sets to sorted lists of display names
    result = {}
    for source_key, ecosystems in source_to_ecosystems.items():
        # convert to display names and sort
        display_eco_names = [
            get_ecosystem_display_name(eco, display_names) for eco in ecosystems
        ]
        result[source_key] = sorted(display_eco_names)

    return result


def format_advisories(source_info: dict) -> str:
    """
    extract and format advisory short names from source.

    Args:
        source_info: source dict with advisories list

    Returns:
        formatted string like 'RHSA, RHBA, RHEA' or empty string
    """
    advisories = source_info.get("advisories", [])
    if not advisories:
        return ""

    # extract 'short' names from advisory dicts
    short_names = [adv.get("short", "") for adv in advisories if adv.get("short")]

    return ", ".join(short_names) if short_names else ""


def generate_capabilities_table(vuln_data: dict, output_file: Path) -> None:
    """
    generate data source capabilities table.

    Shows which capabilities each data source supports (true/false indicators).

    Args:
        vuln_data: vulnerability data dict from YAML
        output_file: output file path
    """
    sources = vuln_data.get("sources", {})

    if not sources:
        logger = log.logger(__name__)
        logger.warning("No sources found in vulnerability data")
        return

    # define capabilities to include
    capabilities_to_include = [
        {
            "key": "disclosure.affected",
            "label": "Affected",
            "description": "Discloses vulnerabilities without requiring fixes",
        },
        {
            "key": "disclosure.date",
            "label": "Disclosure Date",
            "description": "Provides vulnerability disclosure dates",
        },
        {
            "key": "fix.versions",
            "label": "Fix Versions",
            "description": "Provides fix version information",
        },
        {
            "key": "fix.date",
            "label": "Fix Date",
            "description": "Provides fix availability dates",
        },
        {
            "key": "package.upstream_tracking",
            "label": "Upstream Tracking",
            "description": "Tracks source/binary package distinctions",
        },
    ]

    # generate comment
    comment = config.get_generated_comment("src/generate_data_source_tables.py", "html")
    comment += "\n<!-- NOTE: This table uses SVG icons defined in layouts/partials/hooks/body-end.html -->\n"

    # build HTML lines
    html_lines = []

    # table header
    html_lines.append(
        f'<table class="{CSSClasses.CAPABILITY_TABLE} {CSSClasses.CAPABILITY_TABLE_VULNERABILITY}">'
    )
    html_lines.append("  <thead>")
    html_lines.append("    <tr>")
    html_lines.append(
        f'      <th class="{CSSClasses.COL_DATA_SOURCE}" rowspan="2"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["data_source"]}">Data Source</abbr></th>'
    )
    html_lines.append('      <th rowspan="2">Advisories</th>')
    html_lines.append(
        f'      <th colspan="2"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["disclosures"]}">Disclosures</abbr></th>'
    )
    html_lines.append(
        f'      <th colspan="2"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["fixes"]}">Fixes</abbr></th>'
    )
    html_lines.append(
        f'      <th class="{CSSClasses.COL_PACKAGE_UPSTREAM_TRACKING}" rowspan="2"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["source_package"]}">Track by<br>Source<br>Package</abbr></th>'
    )
    html_lines.append("    </tr>")
    html_lines.append("    <tr>")
    html_lines.append(
        f'      <th class="{CSSClasses.COL_DISCLOSURE_AFFECTED}"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["disclosure_affected"]}">Affected</abbr></th>'
    )
    html_lines.append(
        f'      <th class="{CSSClasses.COL_DISCLOSURE_DATE}"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["disclosure_date"]}">Date</abbr></th>'
    )
    html_lines.append(
        f'      <th class="{CSSClasses.COL_FIX_VERSIONS}"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["fix_versions"]}">Versions</abbr></th>'
    )
    html_lines.append(
        f'      <th class="{CSSClasses.COL_FIX_DATE}"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["fix_date"]}">Date</abbr></th>'
    )
    html_lines.append("    </tr>")
    html_lines.append("  </thead>")
    html_lines.append("  <tbody>")

    # add rows for each data source
    for source_key in sorted(sources.keys()):
        source_info = sources[source_key]
        source_name = source_info.get("name", source_key)
        source_url = source_info.get("url", "")
        capabilities = source_info.get("capabilities", [])

        # create a dict for easy lookup of capability support
        cap_support = {}
        for cap in capabilities:
            cap_name = cap.get("name")
            if cap_name and "supported" in cap:
                cap_support[cap_name] = cap.get("supported")

        # format source name as link
        if source_url:
            source_display = f'<a href="{source_url}">{source_name}</a>'
        else:
            source_display = source_name

        # format advisory types
        advisories_display = format_advisories(source_info)

        html_lines.append("    <tr>")
        html_lines.append(
            f'      <td class="{CSSClasses.COL_DATA_SOURCE}">{source_display}</td>'
        )
        html_lines.append(f"      <td>{advisories_display}</td>")

        # add cells for each capability
        for cap in capabilities_to_include:
            cap_key = cap["key"]
            class_name = cap_key.replace(".", "-")

            if cap_key in cap_support:
                if cap_support[cap_key]:
                    icon_html = (
                        '<svg class="capability-icon"><use href="#icon-check"/></svg>'
                    )
                else:
                    icon_html = ""
            else:
                # capability not defined for this source
                icon_html = ""

            html_lines.append(
                f'      <td class="col-{class_name} {CSSClasses.INDICATOR}">{icon_html}</td>'
            )

        html_lines.append("    </tr>")

    # close table
    html_lines.append("  </tbody>")
    html_lines.append("</table>")

    # ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # write file
    with open(output_file, "w") as f:
        f.write(comment)
        for line in html_lines:
            f.write(line + "\n")

    logger = log.logger(__name__)
    logger.info(f"Generated {output_file}")


def generate_provenance_table(
    vuln_data: dict, source_to_ecosystems: dict[str, list[str]], output_file: Path
) -> None:
    """
    generate data source provenance table.

    Shows where data comes from (vunnel provider) and which ecosystems use each source.

    Args:
        vuln_data: vulnerability data dict from YAML
        source_to_ecosystems: mapping from source keys to ecosystem display names
        output_file: output file path
    """
    sources = vuln_data.get("sources", {})

    if not sources:
        logger = log.logger(__name__)
        logger.warning("No sources found in vulnerability data")
        return

    # generate comment
    comment = config.get_generated_comment("src/generate_data_source_tables.py", "html")
    comment += "\n<!-- NOTE: This table uses SVG icons defined in layouts/partials/hooks/body-end.html -->\n"

    # build HTML lines
    html_lines = []

    # table header
    html_lines.append(
        f'<table class="{CSSClasses.CAPABILITY_TABLE} {CSSClasses.CAPABILITY_TABLE_VULNERABILITY}">'
    )
    html_lines.append("  <thead>")
    html_lines.append("    <tr>")
    html_lines.append(
        f'      <th class="{CSSClasses.COL_DATA_SOURCE}"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["data_source"]}">Data Source</abbr></th>'
    )
    html_lines.append(
        f'      <th class="{CSSClasses.COL_PROVIDER}"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["vunnel_provider"]}">Vunnel Provider</abbr></th>'
    )
    html_lines.append(
        f'      <th><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["ecosystem"]}">Ecosystems</abbr></th>'
    )
    html_lines.append("    </tr>")
    html_lines.append("  </thead>")
    html_lines.append("  <tbody>")

    # add rows for each data source
    for source_key in sorted(sources.keys()):
        source_info = sources[source_key]
        source_name = source_info.get("name", source_key)
        source_url = source_info.get("url", "")
        vunnel_provider = source_info.get("vunnel_provider", "")

        # format source name as link
        if source_url:
            source_display = f'<a href="{source_url}">{source_name}</a>'
        else:
            source_display = source_name

        # format ecosystems list
        ecosystems = source_to_ecosystems.get(source_key, [])
        ecosystems_display = ", ".join(ecosystems) if ecosystems else ""

        html_lines.append("    <tr>")
        html_lines.append(
            f'      <td class="{CSSClasses.COL_DATA_SOURCE}">{source_display}</td>'
        )
        html_lines.append(
            f'      <td class="{CSSClasses.COL_PROVIDER}"><code>{vunnel_provider}</code></td>'
        )
        html_lines.append(f"      <td>{ecosystems_display}</td>")
        html_lines.append("    </tr>")

    # close table
    html_lines.append("  </tbody>")
    html_lines.append("</table>")

    # ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # write file
    with open(output_file, "w") as f:
        f.write(comment)
        for line in html_lines:
            f.write(line + "\n")

    logger = log.logger(__name__)
    logger.info(f"Generated {output_file}")


def generate_enrichment_sources_table(vuln_data: dict, output_file: Path) -> None:
    """
    generate enrichment sources table.

    Shows auxiliary data sources that enrich vulnerability data (KEV, EPSS, etc.).

    Args:
        vuln_data: vulnerability data dict from YAML
        output_file: output file path
    """
    enrichment_sources = vuln_data.get("enrichment-sources", {})

    if not enrichment_sources:
        logger = log.logger(__name__)
        logger.warning("No enrichment sources found in vulnerability data")
        return

    # generate comment
    comment = config.get_generated_comment("src/generate_data_source_tables.py", "html")
    comment += "\n<!-- NOTE: This table uses SVG icons defined in layouts/partials/hooks/body-end.html -->\n"

    # build HTML lines
    html_lines = []

    # table header
    html_lines.append(
        f'<table class="{CSSClasses.CAPABILITY_TABLE} {CSSClasses.CAPABILITY_TABLE_VULNERABILITY}">'
    )
    html_lines.append("  <thead>")
    html_lines.append("    <tr>")
    html_lines.append(
        f'      <th class="{CSSClasses.COL_DATA_SOURCE}"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["data_source"]}">Data Source</abbr></th>'
    )
    html_lines.append(
        f'      <th class="{CSSClasses.COL_PROVIDER}"><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["vunnel_provider"]}">Vunnel Provider</abbr></th>'
    )
    html_lines.append(
        f'      <th><abbr class="{CSSClasses.HEADER_HELP}" title="{HEADER_DEFINITIONS["description"]}">Description</abbr></th>'
    )
    html_lines.append("    </tr>")
    html_lines.append("  </thead>")
    html_lines.append("  <tbody>")

    # add rows for each enrichment source
    for source_key in sorted(enrichment_sources.keys()):
        source_info = enrichment_sources[source_key]
        source_name = source_info.get("name", source_key)
        source_url = source_info.get("url", "")
        vunnel_provider = source_info.get("vunnel_provider", "")
        description = source_info.get("description", "")

        # format source name as link
        if source_url:
            source_display = f'<a href="{source_url}">{source_name}</a>'
        else:
            source_display = source_name

        html_lines.append("    <tr>")
        html_lines.append(
            f'      <td class="{CSSClasses.COL_DATA_SOURCE}">{source_display}</td>'
        )
        html_lines.append(
            f'      <td class="{CSSClasses.COL_PROVIDER}"><code>{vunnel_provider}</code></td>'
        )
        html_lines.append(f"      <td>{description}</td>")
        html_lines.append("    </tr>")

    # close table
    html_lines.append("  </tbody>")
    html_lines.append("</table>")

    # ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # write file
    with open(output_file, "w") as f:
        f.write(comment)
        for line in html_lines:
            f.write(line + "\n")

    logger = log.logger(__name__)
    logger.info(f"Generated {output_file}")


def main() -> None:
    """
    generate vulnerability data source reference tables.

    Reads vulnerability data from data/capabilities/vulnerability-data.yaml
    and generates HTML tables showing data source capabilities, provenance, and enrichment sources.
    """
    # load vulnerability data
    vuln_data = data.load_vulnerability_data()

    # load ecosystem display names
    display_names = data.load_ecosystem_display_names()

    # build mapping from sources to ecosystems
    source_to_ecosystems = build_source_to_ecosystems_map(vuln_data, display_names)

    # generate the capabilities table
    generate_capabilities_table(
        vuln_data, config.paths.data_source_capabilities_snippet
    )

    # generate the provenance table
    generate_provenance_table(
        vuln_data, source_to_ecosystems, config.paths.data_source_provenance_snippet
    )

    # generate the enrichment sources table
    generate_enrichment_sources_table(
        vuln_data, config.paths.data_source_enrichment_snippet
    )


if __name__ == "__main__":
    main()
