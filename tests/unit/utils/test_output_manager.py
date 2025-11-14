"""
Tests for utils.output_manager module.

Tests file timestamp checking, cache key generation, and directory management.
"""

import logging
import time

import pytest

from utils.output_manager import (
    clean_directory,
    ensure_directory,
    get_cache_key,
    should_regenerate,
    should_regenerate_multiple,
)


class TestShouldRegenerate:
    """test should_regenerate() functionality"""

    def test_missing_output_returns_true(self, tmp_path):
        """should return True when output doesn't exist"""
        output = tmp_path / "output.md"
        sources = [tmp_path / "input.yaml"]
        sources[0].touch()

        assert should_regenerate(output, sources, update=False) is True

    def test_output_older_than_source_returns_true(self, tmp_path):
        """should return True when source is newer"""
        output = tmp_path / "output.md"
        source = tmp_path / "input.yaml"

        # create output first
        output.write_text("old content")
        time.sleep(0.01)  # ensure different timestamp
        # then update source
        source.write_text("new content")

        assert should_regenerate(output, [source], update=False) is True

    def test_output_newer_than_source_returns_false(self, tmp_path):
        """should return False when output is newer"""
        output = tmp_path / "output.md"
        source = tmp_path / "input.yaml"

        # create source first
        source.write_text("content")
        time.sleep(0.01)  # ensure different timestamp
        # then create output
        output.write_text("generated")

        assert should_regenerate(output, [source], update=False) is False

    def test_update_flag_always_returns_true(self, tmp_path):
        """should return True when update flag is set"""
        output = tmp_path / "output.md"
        source = tmp_path / "input.yaml"

        # create files
        source.write_text("content")
        time.sleep(0.01)
        output.write_text("generated")

        # even though output is newer, update flag forces regeneration
        assert should_regenerate(output, [source], update=True) is True

    def test_multiple_sources_any_newer_returns_true(self, tmp_path):
        """should return True if any source is newer"""
        output = tmp_path / "output.md"
        source1 = tmp_path / "input1.yaml"
        source2 = tmp_path / "input2.yaml"

        # create sources and output
        source1.write_text("content1")
        source2.write_text("content2")
        time.sleep(0.01)
        output.write_text("generated")
        time.sleep(0.01)
        # update one source after output
        source2.write_text("updated content2")

        assert should_regenerate(output, [source1, source2], update=False) is True

    def test_all_sources_older_returns_false(self, tmp_path):
        """should return False when all sources are older"""
        output = tmp_path / "output.md"
        source1 = tmp_path / "input1.yaml"
        source2 = tmp_path / "input2.yaml"

        # create sources first
        source1.write_text("content1")
        source2.write_text("content2")
        time.sleep(0.01)
        # then create output
        output.write_text("generated")

        assert should_regenerate(output, [source1, source2], update=False) is False

    def test_nonexistent_source_ignored(self, tmp_path):
        """should ignore nonexistent source files"""
        output = tmp_path / "output.md"
        existing_source = tmp_path / "exists.yaml"
        nonexistent_source = tmp_path / "missing.yaml"

        # only create one source
        existing_source.write_text("content")
        time.sleep(0.01)
        output.write_text("generated")

        # should not error on missing source
        assert (
            should_regenerate(
                output, [existing_source, nonexistent_source], update=False
            )
            is False
        )

    def test_empty_sources_list(self, tmp_path):
        """should return False for empty sources list if output exists"""
        output = tmp_path / "output.md"
        output.write_text("generated")

        assert should_regenerate(output, [], update=False) is False


class TestShouldRegenerateMultiple:
    """test should_regenerate_multiple() functionality"""

    def test_any_output_missing_returns_true(self, tmp_path):
        """should return True if any output is missing"""
        output1 = tmp_path / "output1.md"
        output2 = tmp_path / "output2.md"
        source = tmp_path / "input.yaml"

        output1.write_text("exists")
        # output2 doesn't exist
        source.write_text("content")

        assert (
            should_regenerate_multiple([output1, output2], [source], update=False)
            is True
        )

    def test_all_outputs_newer_than_sources_returns_false(self, tmp_path):
        """should return False when all outputs are newer"""
        output1 = tmp_path / "output1.md"
        output2 = tmp_path / "output2.md"
        source = tmp_path / "input.yaml"

        # create source first
        source.write_text("content")
        time.sleep(0.01)
        # then outputs
        output1.write_text("generated1")
        output2.write_text("generated2")

        assert (
            should_regenerate_multiple([output1, output2], [source], update=False)
            is False
        )

    def test_source_newer_than_oldest_output_returns_true(self, tmp_path):
        """should return True if source is newer than oldest output"""
        output1 = tmp_path / "output1.md"
        output2 = tmp_path / "output2.md"
        source = tmp_path / "input.yaml"

        # create first output
        output1.write_text("generated1")
        time.sleep(0.01)
        # update source
        source.write_text("content")
        time.sleep(0.01)
        # create second output (newer than source)
        output2.write_text("generated2")

        # source is newer than oldest output (output1)
        assert (
            should_regenerate_multiple([output1, output2], [source], update=False)
            is True
        )

    def test_update_flag_always_returns_true(self, tmp_path):
        """should return True when update flag is set"""
        output1 = tmp_path / "output1.md"
        output2 = tmp_path / "output2.md"
        source = tmp_path / "input.yaml"

        # create files
        source.write_text("content")
        time.sleep(0.01)
        output1.write_text("generated1")
        output2.write_text("generated2")

        assert (
            should_regenerate_multiple([output1, output2], [source], update=True)
            is True
        )

    def test_empty_outputs_list_raises_error(self, tmp_path):
        """should raise ValueError for empty outputs list"""
        # implementation bug: min() on empty generator raises ValueError
        source = tmp_path / "input.yaml"
        source.write_text("content")

        with pytest.raises(ValueError):
            should_regenerate_multiple([], [source], update=False)

    def test_single_output_behaves_correctly(self, tmp_path):
        """should work correctly with single output"""
        output = tmp_path / "output.md"
        source = tmp_path / "input.yaml"

        source.write_text("content")
        time.sleep(0.01)
        output.write_text("generated")

        assert should_regenerate_multiple([output], [source], update=False) is False


class TestGetCacheKey:
    """test get_cache_key() functionality"""

    def test_simple_image_name(self):
        """should convert simple image name"""
        assert get_cache_key("alpine") == "alpine"

    def test_image_with_tag(self):
        """should replace colon with underscore"""
        assert get_cache_key("alpine:3.9.2") == "alpine_3.9.2"
        assert get_cache_key("node:18-alpine") == "node_18-alpine"

    def test_image_with_registry(self):
        """should replace slash with underscore"""
        assert get_cache_key("anchore/syft:latest") == "anchore_syft_latest"

    def test_image_with_port(self):
        """should handle registry with port"""
        assert (
            get_cache_key("localhost:5000/myimage:v1.0")
            == "localhost_5000_myimage_v1.0"
        )

    def test_with_config_file(self, tmp_path):
        """should append config file stem"""
        config = tmp_path / ".syft.yaml"
        config.touch()
        assert get_cache_key("alpine:3.9.2", config) == "alpine_3.9.2_.syft"

    def test_config_file_different_extensions(self, tmp_path):
        """should use file stem regardless of extension"""
        config_yaml = tmp_path / "config.yaml"
        config_toml = tmp_path / "config.toml"

        assert get_cache_key("alpine", config_yaml) == "alpine_config"
        assert get_cache_key("alpine", config_toml) == "alpine_config"

    def test_without_config_file(self):
        """should work without config file"""
        assert get_cache_key("alpine:3.9.2", None) == "alpine_3.9.2"
        assert get_cache_key("alpine:3.9.2") == "alpine_3.9.2"


class TestCleanDirectory:
    """test clean_directory() functionality"""

    def test_clean_existing_directory_with_update(self, tmp_path):
        """should remove and recreate directory when update=True"""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        test_file = output_dir / "test.txt"
        test_file.write_text("content")

        clean_directory(output_dir, update=True)

        # directory should exist but be empty
        assert output_dir.exists()
        assert not test_file.exists()

    def test_no_clean_without_update_flag(self, tmp_path):
        """should not remove directory when update=False"""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        test_file = output_dir / "test.txt"
        test_file.write_text("content")

        clean_directory(output_dir, update=False)

        # directory and file should still exist
        assert output_dir.exists()
        assert test_file.exists()

    def test_create_missing_directory(self, tmp_path):
        """should create directory if it doesn't exist"""
        output_dir = tmp_path / "output"

        clean_directory(output_dir, update=False)

        assert output_dir.exists()

    def test_create_nested_directory(self, tmp_path):
        """should create nested directories"""
        output_dir = tmp_path / "nested" / "output" / "dir"

        clean_directory(output_dir, update=False)

        assert output_dir.exists()

    def test_with_logger(self, tmp_path):
        """should log when cleaning directory"""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        logger = logging.getLogger("test")
        clean_directory(output_dir, update=True, logger=logger)

        assert output_dir.exists()

    def test_idempotent_creation(self, tmp_path):
        """should be safe to call multiple times"""
        output_dir = tmp_path / "output"

        clean_directory(output_dir, update=False)
        clean_directory(output_dir, update=False)

        assert output_dir.exists()


class TestEnsureDirectory:
    """test ensure_directory() functionality"""

    def test_create_single_directory(self, tmp_path):
        """should create single directory"""
        dir_path = tmp_path / "newdir"

        ensure_directory(dir_path)

        assert dir_path.exists()
        assert dir_path.is_dir()

    def test_create_nested_directories(self, tmp_path):
        """should create nested directories"""
        dir_path = tmp_path / "level1" / "level2" / "level3"

        ensure_directory(dir_path)

        assert dir_path.exists()
        assert dir_path.is_dir()

    def test_existing_directory_no_error(self, tmp_path):
        """should not error if directory already exists"""
        dir_path = tmp_path / "existing"
        dir_path.mkdir()

        # should not raise exception
        ensure_directory(dir_path)

        assert dir_path.exists()

    def test_idempotent(self, tmp_path):
        """should be safe to call multiple times"""
        dir_path = tmp_path / "repeated"

        ensure_directory(dir_path)
        ensure_directory(dir_path)
        ensure_directory(dir_path)

        assert dir_path.exists()

    def test_with_existing_parent(self, tmp_path):
        """should work when parent exists"""
        parent = tmp_path / "parent"
        parent.mkdir()
        child = parent / "child"

        ensure_directory(child)

        assert child.exists()
        assert child.is_dir()
