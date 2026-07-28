"""Tests for the FileCache utility."""

import time

import pytest

from leetcode_profile_generator.utils.cache import FileCache


class TestFileCache:
    @pytest.fixture
    def cache(self, tmp_path):
        return FileCache(cache_dir=str(tmp_path / ".cache"), ttl=3600)

    def test_set_and_get(self, cache):
        cache.set("test_key", {"value": 42})
        result = cache.get("test_key")
        assert result == {"value": 42}

    def test_get_nonexistent(self, cache):
        assert cache.get("nonexistent") is None

    def test_is_valid(self, cache):
        cache.set("test_key", {"value": 1})
        assert cache.is_valid("test_key") is True

    def test_ttl_expiry(self, tmp_path):
        cache = FileCache(cache_dir=str(tmp_path / ".cache"), ttl=0)
        cache.set("test_key", {"value": 1})
        # With TTL=0, cache should expire immediately
        time.sleep(0.1)
        assert cache.get("test_key") is None

    def test_clear(self, cache):
        cache.set("key1", {"a": 1})
        cache.set("key2", {"b": 2})
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_clear_user(self, cache):
        cache.set("testuser_profile", {"profile": True})
        cache.set("testuser_contest", {"contest": True})
        cache.set("otheruser_profile", {"other": True})

        cache.clear_user("testuser")

        assert cache.get("testuser_profile") is None
        assert cache.get("testuser_contest") is None
        assert cache.get("otheruser_profile") == {"other": True}

    def test_corrupted_cache(self, cache, tmp_path):
        # Write invalid JSON to a cache file
        cache_dir = tmp_path / ".cache"
        cache_file = cache_dir / "corrupted.json"
        cache_file.write_text("not valid json {{{")

        assert cache.get("corrupted") is None
        # File should be cleaned up
        assert not cache_file.exists()

    def test_sanitizes_key(self, cache):
        # Keys with special characters should be sanitized
        cache.set("user@name/special", {"value": 1})
        result = cache.get("user@name/special")
        assert result == {"value": 1}

    def test_creates_directory(self, tmp_path):
        cache_dir = tmp_path / "nested" / "deep" / ".cache"
        cache = FileCache(cache_dir=str(cache_dir))
        cache.set("test", {"value": 1})
        assert cache_dir.exists()
