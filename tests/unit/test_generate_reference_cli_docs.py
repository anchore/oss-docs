from pathlib import Path

import pytest
from generate_reference_cli_docs import split_help_output

# fixtures directory containing test inputs
FIXTURES_DIR = Path(__file__).parent / "fixtures" / "split_help_output"


@pytest.mark.parametrize(
    "test_case,is_main_help",
    [
        ("basic-help-with-description-and-usage", False),
        ("main-help-includes-global-flags", True),
        ("multi-paragraph-description", False),
        ("description-already-ends-with-period", False),
        ("description-with-trailing-empty-lines", False),
        ("no-usage-line-found", False),
        ("empty-description", False),
        ("single-character-description", False),
        ("description-with-only-whitespace-lines", False),
        ("non-main-help-truncates-before-global-flags", False),
        ("description-with-lowercase-first-letter-gets-capitalized", False),
        ("description-with-multiple-empty-lines-between-paragraphs", False),
    ],
)
def test_split_help_output(test_case: str, is_main_help: bool, snapshot) -> None:
    # read input
    help_input = (FIXTURES_DIR / f"{test_case}.txt").read_text()

    # run function
    description, details = split_help_output(help_input, is_main_help)

    # assert against snapshots
    snapshot.assert_match(description, "description.txt")
    snapshot.assert_match(details, "details.txt")
