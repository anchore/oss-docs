"""
Tests for utils.html_table module.

Tests HTML table generation, version sorting/summarization, SVG icons, and tooltips.
"""

import logging

from utils.html_table import (
    OSVersion,
    TableBuilder,
    clean_owned_files,
    format_conditions_for_tooltip,
    format_evidence_for_tooltip,
    format_versions_list,
    get_capability_indicator_svg,
    get_svg_icon,
    sort_versions,
    summarize_versions,
)


class TestSortVersions:
    """test version sorting functionality"""

    def test_sort_numeric_versions_ascending(self):
        """should sort numeric versions in ascending order"""
        versions = [
            OSVersion("11.2"),
            OSVersion("11.1"),
            OSVersion("10.0"),
            OSVersion("12.0"),
        ]
        result = sort_versions(versions)
        assert [v.value for v in result] == ["10.0", "11.1", "11.2", "12.0"]

    def test_sort_single_digit_versions(self):
        """should sort single digit versions"""
        versions = [OSVersion("9"), OSVersion("10"), OSVersion("8")]
        result = sort_versions(versions)
        assert [v.value for v in result] == ["8", "9", "10"]

    def test_sort_special_versions_after_numeric(self):
        """should place special versions after numeric versions"""
        versions = [
            OSVersion("edge"),
            OSVersion("11.2"),
            OSVersion("rolling"),
            OSVersion("11.1"),
        ]
        result = sort_versions(versions)
        assert [v.value for v in result] == ["11.1", "11.2", "edge", "rolling"]

    def test_sort_all_special_versions(self):
        """should preserve order for all special versions"""
        versions = [OSVersion("rolling"), OSVersion("edge"), OSVersion("unstable")]
        result = sort_versions(versions)
        values = [v.value for v in result]
        # all should be present, order doesn't matter since they're not sorted
        assert set(values) == {"rolling", "edge", "unstable"}

    def test_sort_with_multi_part_versions(self):
        """should sort multi-part versions correctly"""
        versions = [
            OSVersion("1.2.3"),
            OSVersion("1.10.5"),
            OSVersion("1.2.10"),
            OSVersion("1.9.0"),
        ]
        result = sort_versions(versions)
        assert [v.value for v in result] == ["1.2.3", "1.2.10", "1.9.0", "1.10.5"]

    def test_sort_preserves_codenames(self):
        """should preserve codenames during sorting"""
        versions = [
            OSVersion("11", "bullseye"),
            OSVersion("10", "buster"),
            OSVersion("12", "bookworm"),
        ]
        result = sort_versions(versions)
        assert [v.value for v in result] == ["10", "11", "12"]
        assert [v.codename for v in result] == ["buster", "bullseye", "bookworm"]

    def test_sort_empty_list(self):
        """should handle empty list"""
        result = sort_versions([])
        assert result == []


class TestSummarizeVersions:
    """test version summarization functionality"""

    def test_summarize_continuous_from_zero(self):
        """should summarize to major version when versions start from .0"""
        versions = [OSVersion("11.0"), OSVersion("11.1"), OSVersion("11.2")]
        result = summarize_versions(versions)
        assert [v.value for v in result] == ["11"]

    def test_summarize_continuous_from_one(self):
        """should summarize to major when versions start from .1"""
        versions = [OSVersion("11.1"), OSVersion("11.2"), OSVersion("11.3")]
        result = summarize_versions(versions)
        assert [v.value for v in result] == ["11"]

    def test_summarize_partial_range(self):
        """should show X.Y+ when versions start mid-range"""
        versions = [OSVersion("11.2"), OSVersion("11.3"), OSVersion("11.4")]
        result = summarize_versions(versions)
        assert [v.value for v in result] == ["11.2+"]

    def test_summarize_with_gaps(self):
        """should still summarize when there are gaps if starts from .0"""
        # note: the actual implementation considers .0 as starting point and summarizes
        versions = [OSVersion("11.0"), OSVersion("11.2"), OSVersion("11.4")]
        result = summarize_versions(versions)
        # has .0, so gets summarized to major version
        assert [v.value for v in result] == ["11"]

    def test_summarize_single_version(self):
        """should keep single version as-is"""
        versions = [OSVersion("11.0")]
        result = summarize_versions(versions)
        assert [v.value for v in result] == ["11.0"]

    def test_summarize_preserves_special_versions(self):
        """should preserve special versions at the end"""
        versions = [
            OSVersion("3.20"),
            OSVersion("3.21"),
            OSVersion("edge"),
            OSVersion("rolling"),
        ]
        result = summarize_versions(versions)
        assert [v.value for v in result] == ["3.20+", "edge", "rolling"]

    def test_summarize_only_special_versions(self):
        """should handle only special versions"""
        versions = [OSVersion("edge"), OSVersion("rolling")]
        result = summarize_versions(versions)
        assert [v.value for v in result] == ["edge", "rolling"]

    def test_summarize_preserves_codename_on_highest(self):
        """should preserve codename from highest version"""
        versions = [
            OSVersion("11.0"),
            OSVersion("11.1"),
            OSVersion("11.2", "bullseye"),
        ]
        result = summarize_versions(versions)
        assert len(result) == 1
        assert result[0].value == "11"
        assert result[0].codename == "bullseye"

    def test_summarize_multiple_major_versions(self):
        """should handle multiple major version groups"""
        versions = [
            OSVersion("10.0"),
            OSVersion("10.1"),
            OSVersion("11.0"),
            OSVersion("11.1"),
        ]
        result = summarize_versions(versions)
        assert [v.value for v in result] == ["10", "11"]

    def test_summarize_empty_list(self):
        """should handle empty list"""
        result = summarize_versions([])
        assert result == []


class TestFormatVersionsList:
    """test format_versions_list() functionality"""

    def test_format_with_codenames(self):
        """should format versions with codenames in parentheses"""
        versions = [
            OSVersion("10", "buster"),
            OSVersion("11", "bullseye"),
            OSVersion("12", "bookworm"),
        ]
        result = format_versions_list(versions)
        assert (
            result
            == "<code>10</code> (buster), <code>11</code> (bullseye), <code>12</code> (bookworm)"
        )

    def test_format_without_codenames(self):
        """should format versions without codenames"""
        versions = [OSVersion("3.20"), OSVersion("3.21"), OSVersion("3.22")]
        result = format_versions_list(versions)
        # should be summarized to 3.20+
        assert result == "<code>3.20+</code>"

    def test_format_with_special_versions(self):
        """should format special versions"""
        versions = [OSVersion("3.21"), OSVersion("edge")]
        result = format_versions_list(versions)
        assert "<code>edge</code>" in result

    def test_format_empty_list(self):
        """should return dash for empty list"""
        result = format_versions_list([])
        assert result == "-"

    def test_format_sorts_and_summarizes(self):
        """should sort and summarize before formatting"""
        versions = [
            OSVersion("11.2"),
            OSVersion("11.0"),
            OSVersion("11.1"),
        ]
        result = format_versions_list(versions)
        # should be sorted and summarized to just "11"
        assert result == "<code>11</code>"


class TestGetSvgIcon:
    """test get_svg_icon() functionality"""

    def test_get_check_icon(self):
        """should return check icon SVG"""
        result = get_svg_icon("check")
        assert '<svg class="capability-icon">' in result
        assert 'href="#icon-check"' in result

    def test_get_gear_icon(self):
        """should return gear icon SVG"""
        result = get_svg_icon("gear")
        assert '<svg class="capability-icon">' in result
        assert 'href="#icon-gear"' in result

    def test_get_dash_icon(self):
        """should return dash icon SVG"""
        result = get_svg_icon("dash")
        assert '<svg class="capability-icon">' in result
        assert 'href="#icon-dash"' in result

    def test_get_unknown_icon_defaults_to_dash(self):
        """should default to dash for unknown icon type"""
        result = get_svg_icon("unknown")
        assert 'href="#icon-dash"' in result


class TestFormatEvidenceForTooltip:
    """test format_evidence_for_tooltip() functionality"""

    def test_format_empty_evidence(self):
        """should return empty string for no evidence"""
        result = format_evidence_for_tooltip([])
        assert result == ""

    def test_format_single_evidence(self):
        """should return single path as-is"""
        result = format_evidence_for_tooltip(["AlpmDBEntry.Files"])
        assert result == "AlpmDBEntry.Files"

    def test_format_multiple_evidence(self):
        """should format multiple paths as bullet list"""
        result = format_evidence_for_tooltip(["Path.A", "Path.B", "Path.C"])
        assert result == "• Path.A&#10;• Path.B&#10;• Path.C"

    def test_format_two_evidence_items(self):
        """should format two items with bullets"""
        result = format_evidence_for_tooltip(["First.Path", "Second.Path"])
        assert result == "• First.Path&#10;• Second.Path"


class TestFormatConditionsForTooltip:
    """test format_conditions_for_tooltip() functionality"""

    def test_format_empty_conditions(self):
        """should return empty string for no conditions"""
        result = format_conditions_for_tooltip([])
        assert result == ""

    def test_format_single_condition(self):
        """should format single condition on one line"""
        conditions = [{"when": {"IncludeArchives": True}}]
        result = format_conditions_for_tooltip(conditions)
        assert result == "Requires: IncludeArchives = true"

    def test_format_single_condition_with_false(self):
        """should format boolean false correctly"""
        conditions = [{"when": {"ExcludeArchives": False}}]
        result = format_conditions_for_tooltip(conditions)
        assert result == "Requires: ExcludeArchives = false"

    def test_format_multiple_conditions(self):
        """should format multiple conditions as bullet list"""
        conditions = [
            {"when": {"Option1": True}},
            {"when": {"Option2": False}},
        ]
        result = format_conditions_for_tooltip(conditions)
        assert result == "Requires:&#10;• Option1 = true&#10;• Option2 = false"

    def test_format_with_custom_prefix(self):
        """should use custom prefix"""
        conditions = [{"when": {"Setting": True}}]
        result = format_conditions_for_tooltip(conditions, prefix="When")
        assert result == "When: Setting = true"

    def test_format_non_boolean_value(self):
        """should format non-boolean values as strings"""
        conditions = [{"when": {"MaxDepth": 5}}]
        result = format_conditions_for_tooltip(conditions)
        assert result == "Requires: MaxDepth = 5"

    def test_format_multiple_keys_in_one_when(self):
        """should handle multiple key-value pairs in one when clause"""
        conditions = [{"when": {"Option1": True, "Option2": False}}]
        result = format_conditions_for_tooltip(conditions)
        # should format as bullet list since there are 2 pairs
        assert "Requires:" in result
        assert "• Option1 = true" in result
        assert "• Option2 = false" in result


class TestGetCapabilityIndicatorSvg:
    """test get_capability_indicator_svg() functionality"""

    def test_not_supported_returns_empty(self):
        """should return empty string for unsupported capability"""

        class CapSupport:
            supported = False
            conditional = False
            evidence = []
            conditions = []

        result = get_capability_indicator_svg(CapSupport())
        assert result == ""

    def test_none_returns_empty(self):
        """should return empty string for None"""
        result = get_capability_indicator_svg(None)
        assert result == ""

    def test_supported_with_check_icon(self):
        """should show check icon for supported capability"""

        class CapSupport:
            supported = True
            conditional = False
            evidence = []
            conditions = []

        result = get_capability_indicator_svg(CapSupport())
        assert '<svg class="capability-icon">' in result
        assert 'href="#icon-check"' in result

    def test_conditional_with_gear_icon(self):
        """should show gear icon for conditional capability"""

        class CapSupport:
            supported = True
            conditional = True
            evidence = []
            conditions = []

        result = get_capability_indicator_svg(CapSupport())
        assert '<svg class="capability-icon">' in result
        assert 'href="#icon-gear"' in result

    def test_with_evidence_tooltip(self):
        """should include evidence in tooltip"""

        class CapSupport:
            supported = True
            conditional = False
            evidence = ["Field.Path"]
            conditions = []

        result = get_capability_indicator_svg(CapSupport())
        assert 'data-tooltip="Field.Path"' in result
        assert '<span class="capability-icon-wrapper"' in result

    def test_with_conditions_tooltip(self):
        """should include conditions in tooltip"""

        class CapSupport:
            supported = True
            conditional = True
            evidence = []
            conditions = [{"when": {"Option": True}}]

        result = get_capability_indicator_svg(CapSupport())
        assert 'data-tooltip="When: Option = true"' in result

    def test_with_evidence_and_conditions_combined(self):
        """should combine evidence and conditions in tooltip"""

        class CapSupport:
            supported = True
            conditional = True
            evidence = ["Field.A"]
            conditions = [{"when": {"Setting": True}}]

        result = get_capability_indicator_svg(CapSupport())
        assert "When: Setting = true" in result
        assert "Evidence: Field.A" in result
        assert "&#10;&#10;" in result  # double line break separator

    def test_with_override_evidence(self):
        """should use override evidence parameter"""

        class CapSupport:
            supported = True
            conditional = False
            evidence = ["Original"]
            conditions = []

        result = get_capability_indicator_svg(CapSupport(), evidence=["Override"])
        assert "Override" in result
        assert "Original" not in result

    def test_with_override_conditions(self):
        """should use override conditions parameter"""

        class CapSupport:
            supported = True
            conditional = True
            evidence = []
            conditions = [{"when": {"Original": True}}]

        result = get_capability_indicator_svg(
            CapSupport(), conditions=[{"when": {"Override": True}}]
        )
        assert "Override" in result
        assert "Original" not in result

    def test_tooltip_escapes_quotes(self):
        """should escape quotes in tooltip"""

        class CapSupport:
            supported = True
            conditional = False
            evidence = ['Field.With"Quote']
            conditions = []

        result = get_capability_indicator_svg(CapSupport())
        assert "&quot;" in result


class TestCleanOwnedFiles:
    """test clean_owned_files() functionality"""

    def test_clean_owned_files_removes_specified(self, tmp_path):
        """should remove only specified owned files"""
        # create test directory structure
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "package.md").write_text("content")
        (output_dir / "config.md").write_text("content")
        (output_dir / "other.md").write_text("content")

        logger = logging.getLogger()
        owned_files = {"package.md", "config.md"}

        clean_owned_files(output_dir, owned_files, logger)

        # check that owned files were removed
        assert not (output_dir / "package.md").exists()
        assert not (output_dir / "config.md").exists()
        # check that other files remain
        assert (output_dir / "other.md").exists()

    def test_clean_owned_files_in_subdirectories(self, tmp_path):
        """should remove owned files from subdirectories"""
        output_dir = tmp_path / "output"
        subdir = output_dir / "sub"
        subdir.mkdir(parents=True)
        (output_dir / "package.md").write_text("content")
        (subdir / "package.md").write_text("content")
        (subdir / "other.md").write_text("content")

        logger = logging.getLogger()
        owned_files = {"package.md"}

        clean_owned_files(output_dir, owned_files, logger)

        # both package.md files should be removed
        assert not (output_dir / "package.md").exists()
        assert not (subdir / "package.md").exists()
        # other files remain
        assert (subdir / "other.md").exists()

    def test_clean_owned_files_nonexistent_directory(self, tmp_path):
        """should handle nonexistent directory gracefully"""
        output_dir = tmp_path / "nonexistent"
        logger = logging.getLogger()
        owned_files = {"package.md"}

        # should not raise exception
        clean_owned_files(output_dir, owned_files, logger)

    def test_clean_owned_files_empty_set(self, tmp_path):
        """should not remove any files with empty owned set"""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "package.md").write_text("content")

        logger = logging.getLogger()
        owned_files = set()

        clean_owned_files(output_dir, owned_files, logger)

        # file should still exist
        assert (output_dir / "package.md").exists()


class TestTableBuilder:
    """test TableBuilder class functionality"""

    def test_init_sets_table_class(self):
        """should initialize with table class"""
        builder = TableBuilder("custom-table")
        assert builder.table_class == "custom-table"

    def test_init_default_table_class(self):
        """should use default table class"""
        builder = TableBuilder()
        assert builder.table_class == "capability-table"

    def test_add_header_row_returns_self(self):
        """should return self for method chaining"""
        builder = TableBuilder()
        result = builder.add_header_row([{"content": "Header"}])
        assert result is builder

    def test_add_body_row_returns_self(self):
        """should return self for method chaining"""
        builder = TableBuilder()
        result = builder.add_body_row([{"content": "Body"}])
        assert result is builder

    def test_build_basic_table(self):
        """should build basic table with header and body"""
        builder = TableBuilder("test-table")
        builder.add_header_row([{"content": "Name"}])
        builder.add_body_row([{"content": "Python"}])

        lines = builder.build()
        html = "\n".join(lines)

        assert '<table class="test-table">' in html
        assert "<thead>" in html
        assert "<th>Name</th>" in html
        assert "<tbody>" in html
        assert "<td>Python</td>" in html
        assert "</table>" in html

    def test_build_with_cell_class(self):
        """should add class attribute to cells"""
        builder = TableBuilder()
        builder.add_header_row([{"content": "Name", "class": "col-name"}])
        builder.add_body_row([{"content": "Python", "class": "col-name"}])

        lines = builder.build()
        html = "\n".join(lines)

        assert '<th class="col-name">Name</th>' in html
        assert '<td class="col-name">Python</td>' in html

    def test_build_with_rowspan(self):
        """should add rowspan attribute"""
        builder = TableBuilder()
        builder.add_header_row([{"content": "Name", "rowspan": 2}])

        lines = builder.build()
        html = "\n".join(lines)

        assert '<th rowspan="2">Name</th>' in html

    def test_build_with_colspan(self):
        """should add colspan attribute"""
        builder = TableBuilder()
        builder.add_header_row([{"content": "Name", "colspan": 3}])

        lines = builder.build()
        html = "\n".join(lines)

        assert '<th colspan="3">Name</th>' in html

    def test_build_with_multiple_attributes(self):
        """should handle multiple attributes on same cell"""
        builder = TableBuilder()
        builder.add_header_row(
            [{"content": "Name", "class": "col-name", "rowspan": 2, "colspan": 3}]
        )

        lines = builder.build()
        html = "\n".join(lines)

        assert '<th class="col-name" rowspan="2" colspan="3">Name</th>' in html

    def test_build_multiple_header_rows(self):
        """should handle multiple header rows"""
        builder = TableBuilder()
        builder.add_header_row([{"content": "Header 1"}])
        builder.add_header_row([{"content": "Header 2"}])

        lines = builder.build()
        html = "\n".join(lines)

        assert html.count("<tr>") >= 2  # at least 2 header rows

    def test_build_multiple_body_rows(self):
        """should handle multiple body rows"""
        builder = TableBuilder()
        builder.add_body_row([{"content": "Row 1"}])
        builder.add_body_row([{"content": "Row 2"}])

        lines = builder.build()
        html = "\n".join(lines)

        assert "<td>Row 1</td>" in html
        assert "<td>Row 2</td>" in html

    def test_build_empty_table(self):
        """should build table with no rows"""
        builder = TableBuilder()
        lines = builder.build()
        html = "\n".join(lines)

        assert '<table class="capability-table">' in html
        assert "</table>" in html
        assert "<thead>" not in html
        assert "<tbody>" not in html

    def test_build_only_headers(self):
        """should build table with only headers"""
        builder = TableBuilder()
        builder.add_header_row([{"content": "Name"}])

        lines = builder.build()
        html = "\n".join(lines)

        assert "<thead>" in html
        assert "<tbody>" not in html

    def test_build_only_body(self):
        """should build table with only body"""
        builder = TableBuilder()
        builder.add_body_row([{"content": "Data"}])

        lines = builder.build()
        html = "\n".join(lines)

        assert "<thead>" not in html
        assert "<tbody>" in html

    def test_method_chaining(self):
        """should support fluent API method chaining"""
        builder = TableBuilder()
        result = (
            builder.add_header_row([{"content": "H1"}])
            .add_header_row([{"content": "H2"}])
            .add_body_row([{"content": "B1"}])
            .add_body_row([{"content": "B2"}])
        )

        assert result is builder
        lines = builder.build()
        assert len(lines) > 0
