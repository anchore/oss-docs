"""
Tests for utils.cataloger module.

Tests cataloger data extraction functions for ecosystems, capabilities, and patterns.
"""

from utils.cataloger import (
    extract_capabilities,
    get_artifact_patterns,
    get_catalogers_by_ecosystem,
    get_ecosystems,
)


class TestGetEcosystems:
    """test get_ecosystems() functionality"""

    def test_extracts_unique_ecosystems(self, sample_cataloger_data):
        """should extract unique ecosystems from cataloger data"""
        result = get_ecosystems(sample_cataloger_data)

        assert "python" in result
        assert "javascript" in result
        assert len(result) == 2

    def test_returns_sorted_list(self):
        """should return alphabetically sorted ecosystem list"""
        data = {
            "catalogers": [
                {"name": "cat1", "ecosystem": "rust"},
                {"name": "cat2", "ecosystem": "go"},
                {"name": "cat3", "ecosystem": "python"},
            ]
        }

        result = get_ecosystems(data)

        assert result == ["go", "python", "rust"]

    def test_handles_duplicate_ecosystems(self):
        """should deduplicate ecosystems"""
        data = {
            "catalogers": [
                {"name": "cat1", "ecosystem": "python"},
                {"name": "cat2", "ecosystem": "python"},
                {"name": "cat3", "ecosystem": "go"},
            ]
        }

        result = get_ecosystems(data)

        assert result == ["go", "python"]
        assert len(result) == 2

    def test_ignores_catalogers_without_ecosystem(self):
        """should skip catalogers missing ecosystem field"""
        data = {
            "catalogers": [
                {"name": "cat1", "ecosystem": "python"},
                {"name": "cat2"},  # no ecosystem
                {"name": "cat3", "ecosystem": "go"},
            ]
        }

        result = get_ecosystems(data)

        assert result == ["go", "python"]

    def test_handles_empty_catalogers_list(self):
        """should return empty list for no catalogers"""
        data = {"catalogers": []}

        result = get_ecosystems(data)

        assert result == []

    def test_handles_missing_catalogers_key(self):
        """should return empty list when catalogers key missing"""
        data = {}

        result = get_ecosystems(data)

        assert result == []

    def test_handles_none_ecosystem_value(self):
        """should skip catalogers with None ecosystem"""
        data = {
            "catalogers": [
                {"name": "cat1", "ecosystem": "python"},
                {"name": "cat2", "ecosystem": None},
            ]
        }

        result = get_ecosystems(data)

        assert result == ["python"]


class TestGetCatalogersByEcosystem:
    """test get_catalogers_by_ecosystem() functionality"""

    def test_filters_by_ecosystem(self, sample_cataloger_data):
        """should return only catalogers matching ecosystem"""
        result = get_catalogers_by_ecosystem(sample_cataloger_data, "python")

        assert len(result) == 1
        assert result[0]["name"] == "python-package-cataloger"
        assert result[0]["ecosystem"] == "python"

    def test_returns_empty_for_no_matches(self, sample_cataloger_data):
        """should return empty list when no catalogers match"""
        result = get_catalogers_by_ecosystem(sample_cataloger_data, "nonexistent")

        assert result == []

    def test_returns_multiple_matches(self):
        """should return all catalogers for ecosystem"""
        data = {
            "catalogers": [
                {"name": "python-cat-1", "ecosystem": "python"},
                {"name": "go-cat", "ecosystem": "go"},
                {"name": "python-cat-2", "ecosystem": "python"},
            ]
        }

        result = get_catalogers_by_ecosystem(data, "python")

        assert len(result) == 2
        assert all(c["ecosystem"] == "python" for c in result)

    def test_case_sensitive_matching(self):
        """should match ecosystem case-sensitively"""
        data = {
            "catalogers": [
                {"name": "cat1", "ecosystem": "Python"},
                {"name": "cat2", "ecosystem": "python"},
            ]
        }

        result = get_catalogers_by_ecosystem(data, "python")

        assert len(result) == 1
        assert result[0]["name"] == "cat2"

    def test_handles_empty_catalogers_list(self):
        """should return empty list for no catalogers"""
        data = {"catalogers": []}

        result = get_catalogers_by_ecosystem(data, "python")

        assert result == []

    def test_handles_missing_catalogers_key(self):
        """should return empty list when catalogers key missing"""
        data = {}

        result = get_catalogers_by_ecosystem(data, "python")

        assert result == []

    def test_preserves_cataloger_structure(self):
        """should return complete cataloger dictionaries"""
        data = {
            "catalogers": [
                {
                    "name": "python-cat",
                    "ecosystem": "python",
                    "patterns": [{"method": "glob"}],
                }
            ]
        }

        result = get_catalogers_by_ecosystem(data, "python")

        assert "patterns" in result[0]
        assert result[0]["name"] == "python-cat"


class TestExtractCapabilities:
    """test extract_capabilities() functionality"""

    def test_extracts_capabilities_from_patterns(self):
        """should extract capabilities from all patterns"""
        cataloger = {
            "name": "test-cataloger",
            "patterns": [
                {
                    "method": "glob",
                    "capabilities": [
                        {"name": "license", "default": "true"},
                        {"name": "version", "default": "true"},
                    ],
                },
                {
                    "method": "glob",
                    "capabilities": [
                        {"name": "author", "default": "false"},
                    ],
                },
            ],
        }

        result = extract_capabilities(cataloger)

        assert len(result) == 3
        capability_names = {cap["name"] for cap in result}
        assert capability_names == {"license", "version", "author"}

    def test_deduplicates_capabilities(self):
        """should deduplicate capabilities across patterns"""
        cataloger = {
            "name": "test-cataloger",
            "patterns": [
                {
                    "capabilities": [
                        {"name": "license", "default": "true"},
                    ],
                },
                {
                    "capabilities": [
                        {"name": "license", "default": "true"},  # duplicate
                        {"name": "version", "default": "true"},
                    ],
                },
            ],
        }

        result = extract_capabilities(cataloger)

        assert len(result) == 2
        capability_names = {cap["name"] for cap in result}
        assert capability_names == {"license", "version"}

    def test_preserves_capability_structure(self):
        """should preserve all capability fields"""
        cataloger = {
            "patterns": [
                {
                    "capabilities": [
                        {
                            "name": "license",
                            "default": "true",
                            "evidence": ["field.A", "field.B"],
                        },
                    ],
                },
            ],
        }

        result = extract_capabilities(cataloger)

        assert len(result) == 1
        cap = result[0]
        assert cap["name"] == "license"
        assert cap["default"] == "true"
        assert cap["evidence"] == ["field.A", "field.B"]

    def test_handles_empty_patterns(self):
        """should return empty list for no patterns"""
        cataloger = {"name": "test-cataloger", "patterns": []}

        result = extract_capabilities(cataloger)

        assert result == []

    def test_handles_missing_patterns_key(self):
        """should return empty list when patterns key missing"""
        cataloger = {"name": "test-cataloger"}

        result = extract_capabilities(cataloger)

        assert result == []

    def test_handles_patterns_without_capabilities(self):
        """should handle patterns without capabilities field"""
        cataloger = {
            "patterns": [
                {"method": "glob", "criteria": ["**/*.txt"]},
            ],
        }

        result = extract_capabilities(cataloger)

        assert result == []

    def test_handles_empty_capabilities_list(self):
        """should handle empty capabilities lists"""
        cataloger = {
            "patterns": [
                {"capabilities": []},
                {"capabilities": []},
            ],
        }

        result = extract_capabilities(cataloger)

        assert result == []

    def test_skips_capabilities_without_name(self):
        """should skip capability entries missing name field"""
        cataloger = {
            "patterns": [
                {
                    "capabilities": [
                        {"name": "license", "default": "true"},
                        {"default": "true"},  # no name
                        {"name": "version", "default": "true"},
                    ],
                },
            ],
        }

        result = extract_capabilities(cataloger)

        assert len(result) == 2
        capability_names = {cap["name"] for cap in result}
        assert capability_names == {"license", "version"}

    def test_preserves_first_occurrence_of_duplicate(self):
        """should keep first occurrence when deduplicating"""
        cataloger = {
            "patterns": [
                {
                    "capabilities": [
                        {"name": "license", "default": "true", "extra": "first"},
                    ],
                },
                {
                    "capabilities": [
                        {"name": "license", "default": "false", "extra": "second"},
                    ],
                },
            ],
        }

        result = extract_capabilities(cataloger)

        assert len(result) == 1
        assert result[0]["extra"] == "first"


class TestGetArtifactPatterns:
    """test get_artifact_patterns() functionality"""

    def test_extracts_glob_patterns(self):
        """should extract patterns from glob method"""
        cataloger = {
            "patterns": [
                {
                    "method": "glob",
                    "criteria": ["**/requirements.txt", "**/setup.py"],
                },
            ],
        }

        result = get_artifact_patterns(cataloger)

        assert result == ["**/requirements.txt", "**/setup.py"]

    def test_aggregates_patterns_from_multiple_entries(self):
        """should collect patterns from all glob entries"""
        cataloger = {
            "patterns": [
                {
                    "method": "glob",
                    "criteria": ["**/package.json"],
                },
                {
                    "method": "glob",
                    "criteria": ["**/yarn.lock", "**/package-lock.json"],
                },
            ],
        }

        result = get_artifact_patterns(cataloger)

        assert len(result) == 3
        assert "**/package.json" in result
        assert "**/yarn.lock" in result
        assert "**/package-lock.json" in result

    def test_ignores_non_glob_methods(self):
        """should only include patterns from glob method"""
        cataloger = {
            "patterns": [
                {
                    "method": "glob",
                    "criteria": ["**/requirements.txt"],
                },
                {
                    "method": "regex",
                    "criteria": [".*\\.py$"],
                },
                {
                    "method": "mimetype",
                    "criteria": ["application/json"],
                },
            ],
        }

        result = get_artifact_patterns(cataloger)

        assert result == ["**/requirements.txt"]

    def test_handles_empty_patterns(self):
        """should return empty list for no patterns"""
        cataloger = {"patterns": []}

        result = get_artifact_patterns(cataloger)

        assert result == []

    def test_handles_missing_patterns_key(self):
        """should return empty list when patterns key missing"""
        cataloger = {"name": "test-cataloger"}

        result = get_artifact_patterns(cataloger)

        assert result == []

    def test_handles_patterns_without_criteria(self):
        """should handle patterns missing criteria field"""
        cataloger = {
            "patterns": [
                {"method": "glob"},  # no criteria
            ],
        }

        result = get_artifact_patterns(cataloger)

        assert result == []

    def test_handles_empty_criteria_list(self):
        """should handle empty criteria lists"""
        cataloger = {
            "patterns": [
                {"method": "glob", "criteria": []},
            ],
        }

        result = get_artifact_patterns(cataloger)

        assert result == []

    def test_preserves_pattern_order(self):
        """should maintain order of patterns"""
        cataloger = {
            "patterns": [
                {"method": "glob", "criteria": ["first.txt", "second.txt"]},
                {"method": "glob", "criteria": ["third.txt"]},
            ],
        }

        result = get_artifact_patterns(cataloger)

        assert result == ["first.txt", "second.txt", "third.txt"]

    def test_allows_duplicate_patterns(self):
        """should not deduplicate patterns"""
        cataloger = {
            "patterns": [
                {"method": "glob", "criteria": ["**/file.txt"]},
                {"method": "glob", "criteria": ["**/file.txt"]},
            ],
        }

        result = get_artifact_patterns(cataloger)

        assert len(result) == 2
        assert result == ["**/file.txt", "**/file.txt"]
