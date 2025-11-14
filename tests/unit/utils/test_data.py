"""
Tests for utils.data module.

Tests version constraint parsing, version matching, and data file loading.
"""

from unittest import mock

import yaml

from utils.data import (
    load_ecosystem_aliases,
    load_ecosystem_display_names,
    matches_constraint,
    parse_version_constraint,
    version_to_number,
)


class TestVersionToNumber:
    """test version_to_number() functionality"""

    def test_single_digit_version(self):
        """should convert single digit to float"""
        assert version_to_number("5") == 5.0
        assert version_to_number("10") == 10.0

    def test_two_part_version(self):
        """should convert two-part version to decimal"""
        assert version_to_number("8.4") == 8.04
        assert version_to_number("10.12") == 10.12

    def test_major_minor_zero(self):
        """should handle zero minor version"""
        assert version_to_number("5.0") == 5.0

    def test_high_minor_version(self):
        """should handle high minor versions"""
        assert version_to_number("1.99") == 1.99

    def test_three_part_version(self):
        """should use only major and minor for three-part versions"""
        assert version_to_number("1.2.3") == 1.02
        assert version_to_number("10.5.99") == 10.05

    def test_invalid_version_returns_zero(self):
        """should return 0.0 for invalid versions"""
        assert version_to_number("invalid") == 0.0
        assert version_to_number("x.y") == 0.0
        assert version_to_number("") == 0.0

    def test_zero_version(self):
        """should handle zero versions"""
        assert version_to_number("0") == 0.0
        assert version_to_number("0.0") == 0.0


class TestParseVersionConstraint:
    """test parse_version_constraint() functionality"""

    def test_greater_than_or_equal(self):
        """should parse >= constraint"""
        op, version = parse_version_constraint(">= 5")
        assert op == ">="
        assert version == 5.0

    def test_less_than_or_equal(self):
        """should parse <= constraint"""
        op, version = parse_version_constraint("<= 8")
        assert op == "<="
        assert version == 8.0

    def test_equal_explicit(self):
        """should parse == constraint"""
        op, version = parse_version_constraint("== 10")
        assert op == "=="
        assert version == 10.0

    def test_greater_than(self):
        """should parse > constraint"""
        op, version = parse_version_constraint("> 7")
        assert op == ">"
        assert version == 7.0

    def test_less_than(self):
        """should parse < constraint"""
        op, version = parse_version_constraint("< 12")
        assert op == "<"
        assert version == 12.0

    def test_no_operator_defaults_to_equal(self):
        """should default to == when no operator"""
        op, version = parse_version_constraint("5")
        assert op == "=="
        assert version == 5.0

    def test_with_decimal_version(self):
        """should handle decimal versions"""
        op, version = parse_version_constraint(">= 8.4")
        assert op == ">="
        assert version == 8.04

    def test_with_whitespace(self):
        """should handle extra whitespace"""
        op, version = parse_version_constraint("  >=   10  ")
        assert op == ">="
        assert version == 10.0

    def test_version_only_with_whitespace(self):
        """should handle version only with whitespace"""
        op, version = parse_version_constraint("  5  ")
        assert op == "=="
        assert version == 5.0


class TestMatchesConstraint:
    """test matches_constraint() functionality"""

    def test_greater_than_or_equal_match(self):
        """should match >= constraint"""
        constraint = (">=", 5.0)
        assert matches_constraint("7", constraint) is True
        assert matches_constraint("5", constraint) is True
        assert matches_constraint("4", constraint) is False

    def test_greater_than_or_equal_decimal(self):
        """should match >= constraint with decimals"""
        constraint = (">=", 8.04)  # 8.4
        assert matches_constraint("8.4", constraint) is True
        assert matches_constraint("8.5", constraint) is True
        assert matches_constraint("8.3", constraint) is False

    def test_less_than_or_equal_match(self):
        """should match <= constraint"""
        constraint = ("<=", 10.0)
        assert matches_constraint("9", constraint) is True
        assert matches_constraint("10", constraint) is True
        assert matches_constraint("11", constraint) is False

    def test_greater_than_match(self):
        """should match > constraint"""
        constraint = (">", 5.0)
        assert matches_constraint("6", constraint) is True
        assert matches_constraint("5", constraint) is False
        assert matches_constraint("4", constraint) is False

    def test_less_than_match(self):
        """should match < constraint"""
        constraint = ("<", 10.0)
        assert matches_constraint("9", constraint) is True
        assert matches_constraint("10", constraint) is False
        assert matches_constraint("11", constraint) is False

    def test_equal_match(self):
        """should match == constraint"""
        constraint = ("==", 5.0)
        assert matches_constraint("5", constraint) is True
        assert matches_constraint("5.0", constraint) is True
        assert matches_constraint("6", constraint) is False

    def test_equal_with_decimal(self):
        """should match == constraint with decimals"""
        constraint = ("==", 8.04)  # 8.4
        assert matches_constraint("8.4", constraint) is True
        assert matches_constraint("8.5", constraint) is False

    def test_unknown_operator_returns_false(self):
        """should return False for unknown operators"""
        constraint = ("!!", 5.0)
        assert matches_constraint("5", constraint) is False

    def test_edge_case_floating_point(self):
        """should handle floating point precision"""
        constraint = ("==", 8.04)
        # should be within tolerance
        assert matches_constraint("8.4", constraint) is True


class TestLoadEcosystemAliases:
    """test load_ecosystem_aliases() functionality"""

    def test_load_aliases_from_file(self, tmp_path, monkeypatch):
        """should load aliases from YAML file"""
        # create temporary aliases file
        aliases_file = tmp_path / "ecosystem-aliases.yaml"
        content = {
            "alias": {
                "javascript": "npm",
                "typescript": "npm",
                "golang": "go",
            },
            "display_names": {"python": "Python"},
        }
        with open(aliases_file, "w") as f:
            yaml.dump(content, f)

        # mock config.paths.ecosystem_aliases_file
        with mock.patch("utils.data.config.paths") as mock_paths:
            mock_paths.ecosystem_aliases_file = aliases_file
            aliases = load_ecosystem_aliases()

        assert aliases == {
            "javascript": "npm",
            "typescript": "npm",
            "golang": "go",
        }

    def test_missing_aliases_returns_empty(self, tmp_path, monkeypatch):
        """should return empty dict if file missing"""
        nonexistent = tmp_path / "nonexistent.yaml"

        with mock.patch("utils.data.config.paths") as mock_paths:
            mock_paths.ecosystem_aliases_file = nonexistent
            aliases = load_ecosystem_aliases()

        assert aliases == {}

    def test_missing_alias_key_returns_empty(self, tmp_path):
        """should return empty dict if 'alias' key missing"""
        aliases_file = tmp_path / "ecosystem-aliases.yaml"
        content = {"display_names": {"python": "Python"}}
        with open(aliases_file, "w") as f:
            yaml.dump(content, f)

        with mock.patch("utils.data.config.paths") as mock_paths:
            mock_paths.ecosystem_aliases_file = aliases_file
            aliases = load_ecosystem_aliases()

        assert aliases == {}

    def test_invalid_yaml_returns_empty(self, tmp_path):
        """should return empty dict for invalid YAML"""
        aliases_file = tmp_path / "ecosystem-aliases.yaml"
        with open(aliases_file, "w") as f:
            f.write("invalid: yaml: content: [")

        with mock.patch("utils.data.config.paths") as mock_paths:
            mock_paths.ecosystem_aliases_file = aliases_file
            aliases = load_ecosystem_aliases()

        assert aliases == {}


class TestLoadEcosystemDisplayNames:
    """test load_ecosystem_display_names() functionality"""

    def test_load_display_names_from_file(self, tmp_path):
        """should load display names from YAML file"""
        aliases_file = tmp_path / "ecosystem-aliases.yaml"
        content = {
            "alias": {"javascript": "npm"},
            "display_names": {
                "python": "Python",
                "dotnet": ".NET",
                "go": "Go",
            },
        }
        with open(aliases_file, "w") as f:
            yaml.dump(content, f)

        with mock.patch("utils.data.config.paths") as mock_paths:
            mock_paths.ecosystem_aliases_file = aliases_file
            display_names = load_ecosystem_display_names()

        assert display_names == {
            "python": "Python",
            "dotnet": ".NET",
            "go": "Go",
        }

    def test_missing_file_returns_empty(self, tmp_path):
        """should return empty dict if file missing"""
        nonexistent = tmp_path / "nonexistent.yaml"

        with mock.patch("utils.data.config.paths") as mock_paths:
            mock_paths.ecosystem_aliases_file = nonexistent
            display_names = load_ecosystem_display_names()

        assert display_names == {}

    def test_missing_display_names_key_returns_empty(self, tmp_path):
        """should return empty dict if 'display_names' key missing"""
        aliases_file = tmp_path / "ecosystem-aliases.yaml"
        content = {"alias": {"javascript": "npm"}}
        with open(aliases_file, "w") as f:
            yaml.dump(content, f)

        with mock.patch("utils.data.config.paths") as mock_paths:
            mock_paths.ecosystem_aliases_file = aliases_file
            display_names = load_ecosystem_display_names()

        assert display_names == {}

    def test_empty_display_names_returns_empty(self, tmp_path):
        """should return empty dict if display_names is empty"""
        aliases_file = tmp_path / "ecosystem-aliases.yaml"
        content = {
            "alias": {"javascript": "npm"},
            "display_names": {},
        }
        with open(aliases_file, "w") as f:
            yaml.dump(content, f)

        with mock.patch("utils.data.config.paths") as mock_paths:
            mock_paths.ecosystem_aliases_file = aliases_file
            display_names = load_ecosystem_display_names()

        assert display_names == {}


class TestVersionConstraintIntegration:
    """test integration of version constraint functions"""

    def test_parse_and_match_workflow(self):
        """should parse constraint and use it to match versions"""
        # parse constraint
        constraint = parse_version_constraint(">= 8.4")

        # test various versions
        assert matches_constraint("8.4", constraint) is True
        assert matches_constraint("8.5", constraint) is True
        assert matches_constraint("9.0", constraint) is True
        assert matches_constraint("8.3", constraint) is False
        assert matches_constraint("7.9", constraint) is False

    def test_multiple_constraints(self):
        """should handle multiple constraints for filtering"""
        constraints = [
            parse_version_constraint(">= 8"),
            parse_version_constraint("<= 11"),
        ]

        versions = ["7", "8", "9", "10", "11", "12"]

        # filter versions matching all constraints
        matching = [
            v for v in versions if all(matches_constraint(v, c) for c in constraints)
        ]

        assert matching == ["8", "9", "10", "11"]

    def test_single_version_constraint(self):
        """should match exact version"""
        constraint = parse_version_constraint("10")

        assert matches_constraint("10", constraint) is True
        assert matches_constraint("10.0", constraint) is True
        assert matches_constraint("9", constraint) is False
        assert matches_constraint("11", constraint) is False
