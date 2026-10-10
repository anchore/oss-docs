"""OS tables must distinguish data sources that share a Vunnel provider."""

from html.parser import HTMLParser

import pytest

import generate_capability_vulnerability_tables as ecosystem_tables
import generate_supported_os_table as overview_tables
from utils.html_table import OSVersion


class TableRows(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.row = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.row = []
        elif tag == "a" and self.row is not None:
            self.row.append(dict(attrs)["href"])

    def handle_data(self, data):
        if self.row is not None and data.strip():
            self.row.append(data.strip())

    def handle_endtag(self, tag):
        if tag == "tr":
            self.rows.append(self.row)
            self.row = None


@pytest.mark.parametrize("module", [ecosystem_tables, overview_tables])
@pytest.mark.parametrize(
    "declared_sources",
    [["azure"], ["nvd", "azure"], [], ["missing"], ["nvd"]],
)
def test_os_table_source_selection(module, declared_sources, tmp_path):
    vuln_data = {
        "sources": {
            "azure": {
                "name": "Azure Linux OVAL",
                "url": "https://example.com/azurelinux-3.0-oval.xml",
                "vunnel_provider": "mariner",
            },
            "mariner": {
                "name": "CBL-Mariner OVAL",
                "url": "https://example.com/cbl-mariner-2.0-oval.xml",
                "vunnel_provider": "mariner",
            },
            "nvd": {"name": "NVD", "vunnel_provider": "nvd"},
        },
        "os": {
            "azurelinux": {"ecosystem": "rpm", "sources": declared_sources},
            "mariner": {"ecosystem": "rpm", "sources": ["mariner"]},
        },
    }
    os_list = [
        module.OS("azurelinux", [OSVersion("3.0")], "azurelinux", "mariner"),
        module.OS("mariner", [OSVersion("2.0")], "mariner", "mariner"),
    ]
    if module is ecosystem_tables:
        module.generate_os_ecosystem_table("rpm", os_list, vuln_data, tmp_path)
        output_file = tmp_path / "rpm" / "os.md"
    else:
        output_file = tmp_path / "os.md"
        module.generate_overview_os_table(os_list, vuln_data, output_file)

    table = TableRows()
    table.feed(output_file.read_text())
    azure_row = next(row for row in table.rows if row[0] == "Azurelinux")
    mariner_row = next(row for row in table.rows if row[0] == "Mariner")
    expected_source = "azure" if "azure" in declared_sources else "mariner"
    for row, source in [(azure_row, expected_source), (mariner_row, "mariner")]:
        assert "mariner" in row  # The provider must not change with the source.
        assert vuln_data["sources"][source]["url"] in row
        assert vuln_data["sources"][source]["name"] in row
