"""
Tests for schema helper functions in generate_reference_syft_json_schema.

Tests pure string transformation functions for schema parsing and formatting.
"""

import sys
from pathlib import Path

# import functions from the script
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from generate_reference_syft_json_schema import (
    clean_type_description,
    extract_type_prefix,
    is_single_word_type,
    parse_schema_filename,
    shorten_type_string,
)


class TestParseSchemaFilename:
    """test parse_schema_filename() functionality"""

    def test_valid_schema_filename(self):
        """should parse valid schema filename"""
        result = parse_schema_filename("schema-16.10.0.json")

        assert result == (16, 10, 0)

    def test_major_only_version(self):
        """should parse major version only"""
        result = parse_schema_filename("schema-1.0.0.json")

        assert result == (1, 0, 0)

    def test_large_version_numbers(self):
        """should handle large version numbers"""
        result = parse_schema_filename("schema-99.999.9999.json")

        assert result == (99, 999, 9999)

    def test_zero_version(self):
        """should handle zero versions"""
        result = parse_schema_filename("schema-0.0.0.json")

        assert result == (0, 0, 0)

    def test_mixed_version_numbers(self):
        """should parse mixed version numbers"""
        result = parse_schema_filename("schema-17.0.40.json")

        assert result == (17, 0, 40)

    def test_latest_schema_returns_none(self):
        """should return None for latest schema"""
        result = parse_schema_filename("schema-latest.json")

        assert result is None

    def test_missing_extension_returns_none(self):
        """should return None for missing extension"""
        result = parse_schema_filename("schema-16.10.0")

        assert result is None

    def test_wrong_extension_returns_none(self):
        """should return None for wrong extension"""
        result = parse_schema_filename("schema-16.10.0.txt")

        assert result is None

    def test_missing_version_returns_none(self):
        """should return None for missing version"""
        result = parse_schema_filename("schema-.json")

        assert result is None

    def test_partial_version_returns_none(self):
        """should return None for partial version"""
        result = parse_schema_filename("schema-16.10.json")

        assert result is None

    def test_non_numeric_version_returns_none(self):
        """should return None for non-numeric version"""
        result = parse_schema_filename("schema-v16.10.0.json")

        assert result is None

    def test_readme_returns_none(self):
        """should return None for README"""
        result = parse_schema_filename("README.md")

        assert result is None

    def test_empty_string_returns_none(self):
        """should return None for empty string"""
        result = parse_schema_filename("")

        assert result is None

    def test_wrong_prefix_returns_none(self):
        """should return None for wrong prefix"""
        result = parse_schema_filename("foo-16.10.0.json")

        assert result is None

    def test_extra_dots_returns_none(self):
        """should return None for extra dots"""
        result = parse_schema_filename("schema-16.10.0.1.json")

        assert result is None


class TestExtractTypePrefix:
    """test extract_type_prefix() functionality"""

    def test_extract_two_word_prefix(self):
        """should extract prefix from two-word type"""
        result = extract_type_prefix("AlpmDbEntry")

        assert result == "Alpm"

    def test_extract_from_multi_word_type(self):
        """should extract first word from multi-word type"""
        result = extract_type_prefix("ApkFileRecord")

        assert result == "Apk"

    def test_extract_from_java_type(self):
        """should extract Java from JavaArchive"""
        result = extract_type_prefix("JavaArchive")

        assert result == "Java"

    def test_extract_from_dotnet_type(self):
        """should extract Dotnet from DotnetDepsEntry"""
        result = extract_type_prefix("DotnetDepsEntry")

        assert result == "Dotnet"

    def test_single_word_returns_whole_name(self):
        """should return whole name for single-word type"""
        result = extract_type_prefix("Digest")

        assert result == "Digest"

    def test_file_returns_whole_name(self):
        """should return whole name for File"""
        result = extract_type_prefix("File")

        assert result == "File"

    def test_location_returns_whole_name(self):
        """should return whole name for Location"""
        result = extract_type_prefix("Location")

        assert result == "Location"

    def test_lowercase_first_char(self):
        """should handle lowercase first character"""
        result = extract_type_prefix("javaArchive")

        assert result == "java"

    def test_all_lowercase_returns_whole_string(self):
        """should return whole string for all lowercase"""
        result = extract_type_prefix("lowercase")

        assert result == "lowercase"

    def test_all_uppercase_returns_first_char(self):
        """should return first char for all uppercase"""
        result = extract_type_prefix("ALPM")

        assert result == "A"

    def test_single_character_returns_itself(self):
        """should return single character for single char input"""
        result = extract_type_prefix("A")

        assert result == "A"

    def test_empty_string_returns_empty(self):
        """should return empty string for empty input"""
        result = extract_type_prefix("")

        assert result == ""

    def test_long_multi_word_type(self):
        """should extract first word from long type name"""
        result = extract_type_prefix("PhpComposerInstalledEntry")

        assert result == "Php"

    def test_uppercase_after_digits(self):
        """should handle uppercase after digits"""
        result = extract_type_prefix("Type123Name")

        assert result == "Type123"


class TestIsSingleWordType:
    """test is_single_word_type() functionality"""

    def test_digest_is_single_word(self):
        """should return True for Digest"""
        result = is_single_word_type("Digest")

        assert result is True

    def test_file_is_single_word(self):
        """should return True for File"""
        result = is_single_word_type("File")

        assert result is True

    def test_location_is_single_word(self):
        """should return True for Location"""
        result = is_single_word_type("Location")

        assert result is True

    def test_key_values_is_not_single_word(self):
        """should return False for KeyValues"""
        result = is_single_word_type("KeyValues")

        assert result is False

    def test_alpm_file_record_is_not_single_word(self):
        """should return False for AlpmFileRecord"""
        result = is_single_word_type("AlpmFileRecord")

        assert result is False

    def test_apk_db_entry_is_not_single_word(self):
        """should return False for ApkDbEntry"""
        result = is_single_word_type("ApkDbEntry")

        assert result is False

    def test_lowercase_is_single_word(self):
        """should return False for all lowercase (0 uppercase letters)"""
        result = is_single_word_type("lowercase")

        assert result is False

    def test_all_uppercase_is_not_single_word(self):
        """should return False for all uppercase (multiple letters)"""
        result = is_single_word_type("ALPM")

        assert result is False

    def test_single_uppercase_letter(self):
        """should return True for single uppercase letter"""
        result = is_single_word_type("A")

        assert result is True

    def test_camel_case_two_words(self):
        """should return False for two camelCase words"""
        result = is_single_word_type("JavaArchive")

        assert result is False

    def test_three_uppercase_letters(self):
        """should return False for three uppercase letters"""
        result = is_single_word_type("AlpmDbEntry")

        assert result is False

    def test_empty_string(self):
        """should return False for empty string (no uppercase)"""
        result = is_single_word_type("")

        assert result is False

    def test_no_uppercase(self):
        """should return False when no uppercase letters"""
        result = is_single_word_type("package")

        assert result is False


class TestCleanTypeDescription:
    """test clean_type_description() functionality"""

    def test_removes_type_name_prefix(self):
        """should remove type name prefix from description"""
        result = clean_type_description(
            "PhpComposerAuthors", "PhpComposerAuthors represents author info"
        )

        assert result == "Represents author info"

    def test_preserves_description_without_prefix(self):
        """should preserve description without type name prefix"""
        result = clean_type_description("Package", "represents a package")

        assert result == "represents a package"

    def test_handles_empty_description(self):
        """should handle empty description"""
        result = clean_type_description("Package", "")

        assert result == ""

    def test_handles_none_description(self):
        """should handle None description"""
        result = clean_type_description("Package", None)

        assert result is None

    def test_case_insensitive_matching(self):
        """should match type name case-insensitively"""
        result = clean_type_description(
            "Package", "package represents a software package"
        )

        assert result == "Represents a software package"

    def test_capitalizes_remainder(self):
        """should capitalize first letter of remainder"""
        result = clean_type_description(
            "AlpmDbEntry", "AlpmDbEntry contains database entry info"
        )

        assert result == "Contains database entry info"

    def test_handles_description_with_only_type_name(self):
        """should return empty string when description is only type name"""
        result = clean_type_description("Package", "Package")

        assert result == ""

    def test_preserves_description_when_no_match(self):
        """should preserve description when type name not at start"""
        result = clean_type_description("Package", "This is a Package representation")

        assert result == "This is a Package representation"

    def test_handles_multiword_description(self):
        """should handle multi-word descriptions"""
        result = clean_type_description(
            "Location", "Location represents the physical location of a file"
        )

        assert result == "Represents the physical location of a file"

    def test_handles_description_with_whitespace(self):
        """should handle description with extra whitespace"""
        result = clean_type_description("File", "File  contains file metadata")

        assert result == "Contains file metadata"

    def test_preserves_punctuation(self):
        """should preserve punctuation when not matching"""
        result = clean_type_description("Package", "Package: represents a package.")

        # first word is "Package:" (with colon), doesn't match "Package"
        assert result == "Package: represents a package."

    def test_single_char_remainder(self):
        """should capitalize single char remainder"""
        result = clean_type_description("Pkg", "Pkg a")

        assert result == "A"

    def test_empty_remainder_after_removal(self):
        """should handle empty remainder after type name removal"""
        result = clean_type_description("Package", "Package ")

        # after removing "Package", remainder is " " which becomes ""
        assert result == ""


class TestShortenTypeString:
    """test shorten_type_string() functionality"""

    def test_shortens_string(self):
        """should shorten string to str"""
        result = shorten_type_string("string")

        assert result == "str"

    def test_shortens_integer(self):
        """should shorten integer to int"""
        result = shorten_type_string("integer")

        assert result == "int"

    def test_shortens_boolean(self):
        """should shorten boolean to bool"""
        result = shorten_type_string("boolean")

        assert result == "bool"

    def test_shortens_object(self):
        """should shorten object to obj"""
        result = shorten_type_string("object")

        assert result == "obj"

    def test_preserves_custom_type(self):
        """should preserve custom type names"""
        result = shorten_type_string("Package")

        assert result == "Package"

    def test_shortens_in_array(self):
        """should shorten primitives in array types"""
        result = shorten_type_string("Array&lt;integer&gt;")

        assert result == "Array&lt;int&gt;"

    def test_shortens_in_union(self):
        """should shorten primitives in union types"""
        result = shorten_type_string("string | boolean")

        assert result == "str | bool"

    def test_preserves_custom_types_in_union(self):
        """should preserve custom types in unions"""
        result = shorten_type_string("string | Package")

        assert result == "str | Package"

    def test_shortens_multiple_primitives(self):
        """should shorten multiple primitives"""
        result = shorten_type_string("string | integer | boolean")

        assert result == "str | int | bool"

    def test_preserves_html_entities(self):
        """should preserve HTML entities"""
        result = shorten_type_string("Array&lt;string&gt;")

        assert result == "Array&lt;str&gt;"

    def test_does_not_replace_partial_match(self):
        """should not replace partial matches"""
        result = shorten_type_string("StringType")

        # "string" is not replaced because it's part of "StringType"
        assert result == "StringType"

    def test_does_not_replace_in_type_name(self):
        """should not replace primitive words inside type names"""
        result = shorten_type_string("BooleanConfig")

        # "boolean" is part of type name, not standalone
        assert result == "BooleanConfig"

    def test_shortens_at_word_boundaries(self):
        """should only shorten at word boundaries"""
        result = shorten_type_string("integer")

        assert result == "int"

        # but not in "integers" (plural)
        result = shorten_type_string("integers")

        assert result == "integers"

    def test_complex_type_with_links(self):
        """should handle complex types with HTML links"""
        result = shorten_type_string(
            'Array&lt;<a href="#package">string</a> | integer&gt;'
        )

        assert result == 'Array&lt;<a href="#package">str</a> | int&gt;'

    def test_empty_string(self):
        """should handle empty string"""
        result = shorten_type_string("")

        assert result == ""

    def test_preserves_whitespace(self):
        """should preserve whitespace around types"""
        result = shorten_type_string("  string  ")

        assert result == "  str  "
