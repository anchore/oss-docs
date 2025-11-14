"""
Shared fixtures for test suite.
"""

import pytest

from utils.html_table import OSVersion


@pytest.fixture
def sample_numeric_versions():
    """numeric OS versions for testing version sorting and summarization"""
    return [
        OSVersion("11.1"),
        OSVersion("11.2"),
        OSVersion("11.3"),
        OSVersion("10.0"),
        OSVersion("12.0"),
    ]


@pytest.fixture
def sample_versions_with_codenames():
    """OS versions with codenames for testing version display"""
    return [
        OSVersion("10", "buster"),
        OSVersion("11", "bullseye"),
        OSVersion("12", "bookworm"),
    ]


@pytest.fixture
def sample_versions_with_special():
    """OS versions including special versions like 'edge' and 'rolling'"""
    return [
        OSVersion("3.20"),
        OSVersion("3.21"),
        OSVersion("edge"),
        OSVersion("rolling"),
    ]


@pytest.fixture
def sample_version_command_outputs():
    """sample command outputs containing version strings"""
    return {
        "standard": "Version: 1.2.3\nBuild: abc123\nDate: 2024-01-01",
        "with_v_prefix": "syft v1.0.0\nOther info",
        "with_prerelease": "version: 2.0.0-beta.1\nstatus: stable",
        "multiple_versions": "Version: 1.2.3\nAPI Version: 2.0.0\nBuild: xyz",
    }


@pytest.fixture
def sample_cataloger_data():
    """sample cataloger data structure for testing cataloger utilities"""
    return {
        "catalogers": [
            {
                "name": "python-package-cataloger",
                "ecosystem": "python",
                "patterns": [
                    {
                        "method": "glob",
                        "criteria": ["**/requirements.txt", "**/setup.py"],
                        "capabilities": [
                            {"name": "license", "default": "true"},
                            {"name": "version", "default": "true"},
                        ],
                    }
                ],
            },
            {
                "name": "npm-package-cataloger",
                "ecosystem": "javascript",
                "patterns": [
                    {
                        "method": "glob",
                        "criteria": ["**/package.json"],
                        "capabilities": [
                            {"name": "license", "default": "true"},
                        ],
                    }
                ],
            },
        ]
    }
