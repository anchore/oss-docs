"""
Tests for utils.cache module.

Tests cache reading and writing operations.
"""

from utils.cache import get_output, save


class TestGetOutput:
    """test get_output() functionality"""

    def test_returns_content_when_cache_exists(self, tmp_path):
        """should return cached content when file exists"""
        cache_file = tmp_path / "cache.txt"
        cache_file.write_text("cached content")

        result = get_output(cache_file, update=False)

        assert result == "cached content"

    def test_returns_none_when_cache_missing(self, tmp_path):
        """should return None when cache doesn't exist"""
        cache_file = tmp_path / "nonexistent.txt"

        result = get_output(cache_file, update=False)

        assert result is None

    def test_deletes_and_returns_none_when_update_true(self, tmp_path):
        """should delete cache and return None when update=True"""
        cache_file = tmp_path / "cache.txt"
        cache_file.write_text("old content")

        result = get_output(cache_file, update=True)

        assert result is None
        assert not cache_file.exists()

    def test_returns_none_when_update_true_and_no_cache(self, tmp_path):
        """should return None when update=True and cache doesn't exist"""
        cache_file = tmp_path / "nonexistent.txt"

        result = get_output(cache_file, update=True)

        assert result is None

    def test_returns_multiline_content(self, tmp_path):
        """should return multiline cached content"""
        cache_file = tmp_path / "cache.txt"
        content = "line 1\nline 2\nline 3"
        cache_file.write_text(content)

        result = get_output(cache_file, update=False)

        assert result == content

    def test_returns_empty_string_for_empty_file(self, tmp_path):
        """should return empty string for empty cache file"""
        cache_file = tmp_path / "empty.txt"
        cache_file.write_text("")

        result = get_output(cache_file, update=False)

        assert result == ""

    def test_preserves_unicode_content(self, tmp_path):
        """should preserve unicode characters"""
        cache_file = tmp_path / "unicode.txt"
        content = "Hello 世界 🚀"
        cache_file.write_text(content)

        result = get_output(cache_file, update=False)

        assert result == content


class TestSave:
    """test save() functionality"""

    def test_saves_content_to_file(self, tmp_path):
        """should save content to cache file"""
        cache_file = tmp_path / "cache.txt"

        save(cache_file, "test content")

        assert cache_file.exists()
        assert cache_file.read_text() == "test content"

    def test_creates_parent_directories(self, tmp_path):
        """should create parent directories if they don't exist"""
        cache_file = tmp_path / "nested" / "deep" / "cache.txt"

        save(cache_file, "content")

        assert cache_file.exists()
        assert cache_file.read_text() == "content"

    def test_overwrites_existing_file(self, tmp_path):
        """should overwrite existing cache file"""
        cache_file = tmp_path / "cache.txt"
        cache_file.write_text("old content")

        save(cache_file, "new content")

        assert cache_file.read_text() == "new content"

    def test_saves_multiline_content(self, tmp_path):
        """should save multiline content"""
        cache_file = tmp_path / "cache.txt"
        content = "line 1\nline 2\nline 3"

        save(cache_file, content)

        assert cache_file.read_text() == content

    def test_saves_empty_string(self, tmp_path):
        """should save empty string"""
        cache_file = tmp_path / "empty.txt"

        save(cache_file, "")

        assert cache_file.exists()
        assert cache_file.read_text() == ""

    def test_saves_unicode_content(self, tmp_path):
        """should save unicode characters"""
        cache_file = tmp_path / "unicode.txt"
        content = "Hello 世界 🚀"

        save(cache_file, content)

        assert cache_file.read_text() == content

    def test_creates_parent_when_parent_exists(self, tmp_path):
        """should work when parent directory already exists"""
        parent = tmp_path / "existing"
        parent.mkdir()
        cache_file = parent / "cache.txt"

        save(cache_file, "content")

        assert cache_file.exists()


class TestCacheIntegration:
    """test integration of cache functions"""

    def test_save_and_get_workflow(self, tmp_path):
        """should save and retrieve cache successfully"""
        cache_file = tmp_path / "cache" / "output.txt"
        content = "cached output"

        # save content
        save(cache_file, content)

        # retrieve content
        result = get_output(cache_file, update=False)

        assert result == content

    def test_update_workflow(self, tmp_path):
        """should invalidate cache with update flag"""
        cache_file = tmp_path / "cache.txt"

        # save initial content
        save(cache_file, "old content")

        # get with update=True (invalidates cache)
        result = get_output(cache_file, update=True)
        assert result is None
        assert not cache_file.exists()

        # save new content
        save(cache_file, "new content")

        # get new content
        result = get_output(cache_file, update=False)
        assert result == "new content"

    def test_multiple_saves(self, tmp_path):
        """should handle multiple saves to same file"""
        cache_file = tmp_path / "cache.txt"

        save(cache_file, "content 1")
        assert get_output(cache_file, update=False) == "content 1"

        save(cache_file, "content 2")
        assert get_output(cache_file, update=False) == "content 2"

        save(cache_file, "content 3")
        assert get_output(cache_file, update=False) == "content 3"
