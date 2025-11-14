"""
Shared fixtures for test suite.
"""

import pytest


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
