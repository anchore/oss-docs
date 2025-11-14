"""
Tests for utils.version module.

Tests version extraction, parsing, comparison, and sorting functionality.
"""

import pytest

from utils.version import (
    Version,
    compare,
    extract_from_output,
    parse,
    sort_strings,
)


class TestExtractFromOutput:
    """test version extraction from command output"""

    def test_standard_version_line(self):
        """should extract version from 'Version:' line"""
        output = "Version: 1.2.3\nBuild: abc123"
        assert extract_from_output(output) == "1.2.3"

    def test_case_insensitive_version_line(self):
        """should extract version from 'version:' (lowercase)"""
        output = "version: 2.0.0\nother: info"
        assert extract_from_output(output) == "2.0.0"

    def test_tool_name_extraction(self):
        """should extract version from tool-specific line"""
        output = "Syft: v1.0.0\nOther: info"
        assert extract_from_output(output, tool_name="syft") == "v1.0.0"

    def test_tool_name_title_case(self):
        """should handle tool name in title case"""
        output = "Grype: v2.1.0\nBuild: xyz"
        assert extract_from_output(output, tool_name="grype") == "v2.1.0"

    def test_generic_version_with_colon(self):
        """should extract from any line with 'version' and colon"""
        output = "application version: 3.4.5\nstatus: ok"
        assert extract_from_output(output) == "3.4.5"

    def test_custom_pattern(self):
        """should use custom regex pattern"""
        output = "Release v1.2.3 is ready"
        patterns = [r"Release (v[\d.]+)"]
        assert extract_from_output(output, patterns=patterns) == "v1.2.3"

    def test_custom_pattern_full_match(self):
        """should return full match if no capture group"""
        output = "Version: 1.2.3"
        patterns = [r"[\d.]+"]
        assert extract_from_output(output, patterns=patterns) == "1.2.3"

    def test_empty_output(self):
        """should return 'unknown' for empty output"""
        assert extract_from_output("") == "unknown"

    def test_no_version_found(self):
        """should return 'unknown' if no version found"""
        output = "No version information here\nJust some text"
        assert extract_from_output(output) == "unknown"

    def test_multiline_output_first_match(self):
        """should return first version match"""
        output = "Version: 1.2.3\nAPI Version: 2.0.0"
        assert extract_from_output(output) == "1.2.3"


class TestVersionParse:
    """test Version.parse() functionality"""

    def test_parse_standard_semver(self):
        """should parse standard semver"""
        v = Version.parse("1.2.3")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3
        assert v.prerelease is None

    def test_parse_with_v_prefix(self):
        """should handle 'v' prefix"""
        v = Version.parse("v2.0.0")
        assert v.major == 2
        assert v.minor == 0
        assert v.patch == 0
        assert v.prerelease is None

    def test_parse_with_prerelease(self):
        """should parse prerelease version"""
        v = Version.parse("1.0.0-beta.1")
        assert v.major == 1
        assert v.minor == 0
        assert v.patch == 0
        assert v.prerelease == "beta.1"

    def test_parse_with_v_prefix_and_prerelease(self):
        """should handle both v prefix and prerelease"""
        v = Version.parse("v2.1.0-rc.3")
        assert v.major == 2
        assert v.minor == 1
        assert v.patch == 0
        assert v.prerelease == "rc.3"

    def test_parse_with_whitespace(self):
        """should handle leading/trailing whitespace"""
        v = Version.parse("  1.2.3  ")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3

    def test_parse_zero_version(self):
        """should handle zero versions"""
        v = Version.parse("0.0.0")
        assert v.major == 0
        assert v.minor == 0
        assert v.patch == 0

    def test_parse_large_numbers(self):
        """should handle large version numbers"""
        v = Version.parse("123.456.789")
        assert v.major == 123
        assert v.minor == 456
        assert v.patch == 789

    def test_parse_invalid_format_missing_patch(self):
        """should raise ValueError for missing patch version"""
        with pytest.raises(ValueError, match="Invalid version string"):
            Version.parse("1.2")

    def test_parse_invalid_format_not_numeric(self):
        """should raise ValueError for non-numeric parts"""
        with pytest.raises(ValueError, match="Invalid version string"):
            Version.parse("1.x.3")

    def test_parse_invalid_format_empty(self):
        """should raise ValueError for empty string"""
        with pytest.raises(ValueError, match="Invalid version string"):
            Version.parse("")


class TestVersionComparison:
    """test Version comparison operators"""

    def test_less_than_by_major(self):
        """should compare by major version"""
        v1 = Version.parse("1.0.0")
        v2 = Version.parse("2.0.0")
        assert v1 < v2
        assert not v2 < v1

    def test_less_than_by_minor(self):
        """should compare by minor version when major equal"""
        v1 = Version.parse("1.2.0")
        v2 = Version.parse("1.3.0")
        assert v1 < v2
        assert not v2 < v1

    def test_less_than_by_patch(self):
        """should compare by patch version when major and minor equal"""
        v1 = Version.parse("1.2.3")
        v2 = Version.parse("1.2.4")
        assert v1 < v2
        assert not v2 < v1

    def test_prerelease_less_than_release(self):
        """should consider prerelease less than release"""
        v1 = Version.parse("1.0.0-beta")
        v2 = Version.parse("1.0.0")
        assert v1 < v2
        assert not v2 < v1

    def test_prerelease_comparison(self):
        """should compare prereleases lexically"""
        v1 = Version.parse("1.0.0-alpha")
        v2 = Version.parse("1.0.0-beta")
        assert v1 < v2
        assert not v2 < v1

    def test_equal_versions(self):
        """should not be less than if equal"""
        v1 = Version.parse("1.2.3")
        v2 = Version.parse("1.2.3")
        assert not v1 < v2
        assert not v2 < v1

    def test_equality(self):
        """should check equality correctly"""
        v1 = Version.parse("1.2.3")
        v2 = Version.parse("1.2.3")
        assert v1 == v2

    def test_equality_with_prerelease(self):
        """should check equality including prerelease"""
        v1 = Version.parse("1.0.0-beta.1")
        v2 = Version.parse("1.0.0-beta.1")
        assert v1 == v2

    def test_inequality_different_major(self):
        """should not be equal if major different"""
        v1 = Version.parse("1.2.3")
        v2 = Version.parse("2.2.3")
        assert v1 != v2

    def test_inequality_different_prerelease(self):
        """should not be equal if prerelease different"""
        v1 = Version.parse("1.0.0-beta")
        v2 = Version.parse("1.0.0-alpha")
        assert v1 != v2

    def test_inequality_release_vs_prerelease(self):
        """should not be equal if one is release and other prerelease"""
        v1 = Version.parse("1.0.0")
        v2 = Version.parse("1.0.0-beta")
        assert v1 != v2


class TestVersionString:
    """test Version.__str__() formatting"""

    def test_format_standard_version(self):
        """should format standard version"""
        v = Version(1, 2, 3)
        assert str(v) == "1.2.3"

    def test_format_with_prerelease(self):
        """should format version with prerelease"""
        v = Version(2, 0, 0, "beta.1")
        assert str(v) == "2.0.0-beta.1"

    def test_format_zero_version(self):
        """should format zero version"""
        v = Version(0, 0, 0)
        assert str(v) == "0.0.0"

    def test_format_large_numbers(self):
        """should format large version numbers"""
        v = Version(100, 200, 300)
        assert str(v) == "100.200.300"


class TestParseConvenience:
    """test parse() convenience function"""

    def test_parse_wrapper(self):
        """should delegate to Version.parse()"""
        v = parse("1.2.3")
        assert isinstance(v, Version)
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3

    def test_parse_wrapper_with_prerelease(self):
        """should handle prerelease versions"""
        v = parse("v2.0.0-beta")
        assert v.major == 2
        assert v.prerelease == "beta"


class TestCompare:
    """test compare() function"""

    def test_compare_less_than(self):
        """should return -1 when first version is less"""
        assert compare("1.2.3", "1.2.4") == -1
        assert compare("1.0.0", "2.0.0") == -1

    def test_compare_greater_than(self):
        """should return 1 when first version is greater"""
        assert compare("1.2.4", "1.2.3") == 1
        assert compare("2.0.0", "1.9.9") == 1

    def test_compare_equal(self):
        """should return 0 when versions are equal"""
        assert compare("1.2.3", "1.2.3") == 0
        assert compare("v2.0.0", "2.0.0") == 0

    def test_compare_prerelease(self):
        """should compare prerelease versions"""
        assert compare("1.0.0-beta", "1.0.0") == -1
        assert compare("1.0.0", "1.0.0-beta") == 1


class TestSortStrings:
    """test sort_strings() function"""

    def test_sort_ascending(self):
        """should sort versions in ascending order"""
        versions = ["1.2.3", "1.0.0", "2.0.0", "1.2.1"]
        result = sort_strings(versions)
        assert result == ["1.0.0", "1.2.1", "1.2.3", "2.0.0"]

    def test_sort_descending(self):
        """should sort versions in descending order"""
        versions = ["1.2.3", "1.0.0", "2.0.0", "1.2.1"]
        result = sort_strings(versions, reverse=True)
        assert result == ["2.0.0", "1.2.3", "1.2.1", "1.0.0"]

    def test_sort_with_v_prefix(self):
        """should handle v prefix in sorting"""
        versions = ["v1.2.0", "v1.0.0", "v2.0.0"]
        result = sort_strings(versions)
        assert result == ["v1.0.0", "v1.2.0", "v2.0.0"]

    def test_sort_with_prerelease(self):
        """should sort prerelease before release"""
        versions = ["1.0.0", "1.0.0-beta", "1.0.0-alpha", "0.9.0"]
        result = sort_strings(versions)
        assert result == ["0.9.0", "1.0.0-alpha", "1.0.0-beta", "1.0.0"]

    def test_sort_empty_list(self):
        """should handle empty list"""
        result = sort_strings([])
        assert result == []

    def test_sort_single_version(self):
        """should handle single version"""
        result = sort_strings(["1.2.3"])
        assert result == ["1.2.3"]

    def test_sort_preserves_original_format(self):
        """should preserve original string format"""
        versions = ["  v1.2.3  ", "v1.0.0"]
        result = sort_strings(versions)
        # Original strings should be preserved
        assert result[0] == "v1.0.0"
        assert result[1] == "  v1.2.3  "
