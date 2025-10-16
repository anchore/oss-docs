from scripts.trash.generate_python_capabilities import (
    extract_hash_type,
    format_capability_value,
    generate_cataloger_details_table,
    generate_configuration_section,
    generate_dependency_graph_table,
    generate_vulnerability_matching_section,
)


def test_format_capability_value():
    """test capability value formatting."""
    tests = [
        {
            "name": "boolean true",
            "input": True,
            "expected": "✓",
        },
        {
            "name": "boolean false",
            "input": False,
            "expected": "-",
        },
        {
            "name": "empty list",
            "input": [],
            "expected": "-",
        },
        {
            "name": "list with values",
            "input": ["direct", "indirect"],
            "expected": "direct, indirect",
        },
        {
            "name": "empty string",
            "input": "",
            "expected": "-",
        },
        {
            "name": "non-empty string",
            "input": "complete",
            "expected": "complete",
        },
    ]

    for tt in tests:
        result = format_capability_value(tt["input"])
        assert (
            result == tt["expected"]
        ), f"{tt['name']}: expected {tt['expected']}, got {result}"


def test_extract_hash_type():
    """test hash type extraction from evidence fields."""
    tests = [
        {
            "name": "sha256 in field",
            "input": ["PythonPackage.Files[].Sha256"],
            "expected": "sha256",
        },
        {
            "name": "generic digest field",
            "input": ["PythonPackage.Files[].Digest"],
            "expected": "hash",
        },
        {
            "name": "no hash info",
            "input": ["PythonPackage.Files"],
            "expected": "",
        },
        {
            "name": "empty evidence",
            "input": [],
            "expected": "",
        },
        {
            "name": "none evidence",
            "input": None,
            "expected": "",
        },
    ]

    for tt in tests:
        result = extract_hash_type(tt["input"])
        assert (
            result == tt["expected"]
        ), f"{tt['name']}: expected {tt['expected']}, got {result}"


def test_generate_cataloger_details_table():
    """test cataloger details table generation."""
    catalogers = [
        {
            "name": "test-cataloger",
            "patterns": [
                {
                    "criteria": ["**/test.txt"],
                    "capabilities": [
                        {"name": "license", "default": True},
                        {
                            "name": "package_manager.files.listing",
                            "default": True,
                        },
                        {
                            "name": "package_manager.files.digests",
                            "default": True,
                            "evidence": ["Test.Digest"],
                        },
                        {
                            "name": "package_manager.package_integrity_hash",
                            "default": False,
                        },
                    ],
                }
            ],
        }
    ]

    result = generate_cataloger_details_table(catalogers)

    # check table structure
    lines = result.strip().split("\n")
    assert len(lines) == 3  # header + separator + 1 data row

    # check header
    assert "| Cataloger | Artifact | License |" in lines[0]
    assert "|-----------|----------|---------|" in lines[1]

    # check data row
    assert "test-cataloger" in lines[2]
    assert "`**/test.txt`" in lines[2]
    assert "✓" in lines[2]


def test_generate_dependency_graph_table():
    """test dependency graph table generation."""
    catalogers = [
        {
            "name": "test-cataloger",
            "patterns": [
                {
                    "criteria": ["**/test.lock"],
                    "capabilities": [
                        {
                            "name": "dependency.depth",
                            "default": ["direct", "indirect"],
                        },
                        {"name": "dependency.edges", "default": "complete"},
                        {"name": "dependency.kinds", "default": ["runtime"]},
                    ],
                }
            ],
        }
    ]

    result = generate_dependency_graph_table(catalogers)

    # check table structure
    lines = result.strip().split("\n")
    assert len(lines) == 3  # header + separator + 1 data row

    # check header
    assert "| Artifact | Dependency depth | Dependency edges |" in lines[0]

    # check data row contains expected values
    assert "`**/test.lock`" in lines[2]
    assert "direct, indirect" in lines[2]
    assert "complete" in lines[2]
    assert "runtime" in lines[2]


def test_generate_vulnerability_matching_section():
    """test vulnerability matching section generation."""
    vuln_data = {
        "ecosystems": {
            "test": {
                "sources": [
                    {
                        "name": "Test Source",
                        "url": "https://example.com",
                        "vunnel_provider": "test",
                    }
                ],
                "matching_rules": ["Uses test rules"],
                "version_matching": "Test version matching description.",
                "assumptions": ["Test assumption"],
            }
        }
    }

    result = generate_vulnerability_matching_section(vuln_data, "test")

    # check section structure
    assert "### Data sources" in result
    assert "| Source | URL | Vunnel Provider |" in result
    assert "Test Source" in result
    assert "[Link](https://example.com)" in result
    assert "`test`" in result

    # check matching rules
    assert "### Matching rules" in result
    assert "- Uses test rules" in result

    # check version matching
    assert "Test version matching description." in result

    # check assumptions
    assert "### Assumptions" in result
    assert "- Test assumption" in result


def test_generate_vulnerability_matching_section_no_data():
    """test vulnerability matching section with no ecosystem data."""
    vuln_data = {"ecosystems": {}}

    result = generate_vulnerability_matching_section(vuln_data, "nonexistent")

    assert "No vulnerability data available" in result


def test_generate_configuration_section():
    """test configuration section generation."""
    catalogers = [
        {
            "name": "test-cataloger",
            "config": {
                "type": "test.Config",
                "fields": [
                    {
                        "key": "TestOption",
                        "description": "This is a test configuration option.",
                        "app_key": "test.option",
                    }
                ],
            },
        }
    ]

    result = generate_configuration_section(catalogers)

    # check section structure
    assert "### Configuration options" in result
    assert "**`test.option`**" in result
    assert "This is a test configuration option." in result


def test_generate_configuration_section_no_config():
    """test configuration section with no config fields."""
    catalogers = [{"name": "test-cataloger"}]

    result = generate_configuration_section(catalogers)

    assert "No configuration options available" in result
