"""
Tests for utils.markdown module.

Tests markdown code fence generation, front matter generation, and format detection.
"""

from utils.markdown import create_code_fence, detect_format, generate_front_matter


class TestCreateCodeFence:
    """test create_code_fence() functionality"""

    def test_with_language(self):
        """should create code fence with language specifier"""
        result = create_code_fence("print('hello')", "python")
        assert result == "```python\nprint('hello')\n```\n"

    def test_without_language(self):
        """should create code fence without language specifier"""
        result = create_code_fence("plain text")
        assert result == "```\nplain text\n```\n"

    def test_with_empty_language(self):
        """should treat empty string as no language"""
        result = create_code_fence("content", "")
        assert result == "```\ncontent\n```\n"

    def test_multiline_content(self):
        """should handle multiline content"""
        content = "line 1\nline 2\nline 3"
        result = create_code_fence(content, "bash")
        assert result == "```bash\nline 1\nline 2\nline 3\n```\n"

    def test_empty_content(self):
        """should handle empty content"""
        result = create_code_fence("", "json")
        assert result == "```json\n\n```\n"

    def test_various_languages(self):
        """should handle various language identifiers"""
        for lang in ["python", "javascript", "go", "rust", "yaml", "json"]:
            result = create_code_fence("code", lang)
            assert result.startswith(f"```{lang}\n")
            assert result.endswith("\n```\n")


class TestGenerateFrontMatter:
    """test generate_front_matter() functionality"""

    def test_title_only(self):
        """should generate front matter with only title"""
        result = generate_front_matter(title="Test Page")
        assert "+++" in result
        assert 'title = "Test Page"' in result
        assert result.startswith("+++\n")
        assert result.endswith("+++\n\n")

    def test_with_link_title(self):
        """should include linkTitle field"""
        result = generate_front_matter(title="Test", link_title="Short Test")
        assert 'title = "Test"' in result
        assert 'linkTitle = "Short Test"' in result

    def test_with_weight(self):
        """should include weight field"""
        result = generate_front_matter(title="Test", weight=10)
        assert "weight = 10" in result

    def test_with_tags(self):
        """should format tags as list"""
        result = generate_front_matter(title="Test", tags=["syft", "cli"])
        assert "tags = ['syft', 'cli']" in result

    def test_with_single_tag(self):
        """should handle single tag"""
        result = generate_front_matter(title="Test", tags=["syft"])
        assert "tags = ['syft']" in result

    def test_with_empty_tags(self):
        """should handle empty tags list"""
        result = generate_front_matter(title="Test", tags=[])
        assert "tags = []" in result

    def test_with_categories(self):
        """should format categories as list"""
        result = generate_front_matter(title="Test", categories=["reference", "docs"])
        assert "categories = ['reference', 'docs']" in result

    def test_with_url(self):
        """should include url field"""
        result = generate_front_matter(title="Test", url="docs/reference/cli")
        assert 'url = "docs/reference/cli"' in result

    def test_with_description(self):
        """should include description field"""
        result = generate_front_matter(title="Test", description="This is a test page")
        assert 'description = "This is a test page"' in result

    def test_with_aliases(self):
        """should format aliases as list"""
        result = generate_front_matter(title="Test", aliases=["/old-path", "/other"])
        assert 'aliases = ["/old-path", "/other"]' in result

    def test_with_menu_group(self):
        """should include menu_group field"""
        result = generate_front_matter(title="Test", menu_group="main")
        assert 'menu_group = "main"' in result

    def test_with_string_param(self):
        """should include string parameters"""
        result = generate_front_matter(title="Test", params={"custom": "value"})
        assert 'custom = "value"' in result

    def test_with_boolean_param(self):
        """should include boolean parameters as lowercase"""
        result = generate_front_matter(
            title="Test", params={"draft": True, "published": False}
        )
        assert "draft = true" in result
        assert "published = false" in result

    def test_with_int_param(self):
        """should include integer parameters"""
        result = generate_front_matter(title="Test", params={"count": 42})
        assert "count = 42" in result

    def test_with_float_param(self):
        """should include float parameters"""
        result = generate_front_matter(title="Test", params={"rating": 4.5})
        assert "rating = 4.5" in result

    def test_with_multiple_params(self):
        """should include multiple custom parameters"""
        result = generate_front_matter(
            title="Test",
            params={"key1": "value1", "key2": 123, "key3": True},
        )
        assert 'key1 = "value1"' in result
        assert "key2 = 123" in result
        assert "key3 = true" in result

    def test_complete_front_matter(self):
        """should generate complete front matter with all fields"""
        result = generate_front_matter(
            title="Syft CLI Reference",
            link_title="CLI",
            weight=10,
            tags=["syft", "cli"],
            categories=["reference"],
            url="docs/reference/syft/cli",
            description="Syft command line interface reference",
            aliases=["/old-cli-ref"],
            menu_group="reference",
            params={"draft": False, "version": "1.0"},
        )

        # check all fields are present
        assert 'title = "Syft CLI Reference"' in result
        assert 'linkTitle = "CLI"' in result
        assert "weight = 10" in result
        assert "tags = ['syft', 'cli']" in result
        assert "categories = ['reference']" in result
        assert 'url = "docs/reference/syft/cli"' in result
        assert 'description = "Syft command line interface reference"' in result
        assert 'aliases = ["/old-cli-ref"]' in result
        assert 'menu_group = "reference"' in result
        assert "draft = false" in result
        assert 'version = "1.0"' in result

        # check structure
        assert result.startswith("+++\n")
        assert result.endswith("+++\n\n")

    def test_field_order(self):
        """should have title as first field"""
        result = generate_front_matter(
            title="Test", weight=10, description="Description"
        )
        lines = result.split("\n")
        # first non-delimiter line should be title
        assert lines[1] == 'title = "Test"'


class TestDetectFormat:
    """test detect_format() functionality"""

    def test_detect_json_object(self):
        """should detect JSON objects"""
        assert detect_format('{"foo": "bar"}') == "json"
        assert detect_format('{"key": "value", "nested": {}}') == "json"

    def test_detect_json_array(self):
        """should detect JSON arrays"""
        assert detect_format("[1, 2, 3]") == "json"
        assert detect_format('[{"id": 1}, {"id": 2}]') == "json"

    def test_detect_csv(self):
        """should detect CSV format"""
        csv_content = "name,value\nfoo,bar\nbaz,qux"
        assert detect_format(csv_content) == "csv"

    def test_detect_csv_with_headers(self):
        """should detect CSV with header row"""
        csv_content = "id,name,status\n1,test,active\n2,demo,inactive"
        assert detect_format(csv_content) == "csv"

    def test_detect_yaml_with_list(self):
        """should detect YAML with list items"""
        yaml_content = "items:\n  - first\n  - second\n  - third"
        assert detect_format(yaml_content) == "yaml"

    def test_detect_yaml_with_colon(self):
        """should detect YAML with key-value pairs"""
        yaml_content = "name: test\nvalue: 123\nlist:\n  - item"
        assert detect_format(yaml_content) == "yaml"

    def test_detect_xml_with_declaration(self):
        """should detect XML with declaration"""
        xml_content = '<?xml version="1.0"?><root><item>test</item></root>'
        assert detect_format(xml_content) == "xml"

    def test_detect_xml_without_declaration(self):
        """should detect XML without declaration"""
        xml_content = "<root><item>test</item></root>"
        assert detect_format(xml_content) == "xml"

    def test_detect_plain_text(self):
        """should detect plain text"""
        assert detect_format("plain text output") == "text"
        assert detect_format("No special formatting here") == "text"

    def test_empty_content(self):
        """should return text for empty content"""
        assert detect_format("") == "text"

    def test_no_results(self):
        """should return text for '(no results)' marker"""
        assert detect_format("(no results)") == "text"

    def test_single_line_text(self):
        """should detect single line text"""
        assert detect_format("Just a single line") == "text"

    def test_csv_requires_multiple_lines(self):
        """should not detect CSV for single line"""
        assert detect_format("foo,bar") != "csv"

    def test_yaml_requires_dash(self):
        """should not detect YAML without list markers"""
        # just having colons isn't enough
        content = "key: value\nother: thing"
        # this will be text since there's no dash for yaml list
        assert detect_format(content) == "text"

    def test_json_with_whitespace(self):
        """should not detect JSON with leading whitespace"""
        # implementation doesn't strip whitespace before checking
        assert detect_format('  {"foo": "bar"}') == "text"
        assert detect_format("  [1, 2, 3]") == "text"

    def test_xml_with_whitespace(self):
        """should detect XML with leading whitespace"""
        assert detect_format("  <?xml version='1.0'?>") == "xml"
        assert detect_format("  <root>content</root>") == "xml"
