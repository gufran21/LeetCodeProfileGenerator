"""Filesystem cache with TTL for LeetCode API responses.

Caches API responses as JSON files to avoid repeated requests within
the TTL window. Supports atomic writes and corrupted cache recovery.
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any


class FileCache:
    """A simple filesystem-based JSON cache with time-to-live (TTL).

    Cache files are stored as `{key}.json` in the cache directory.
    Each file contains a JSON object with 'timestamp' and 'data' fields.

    Attributes:
        cache_dir: Path to the cache directory.
        ttl: Time-to-live in seconds (default: 86400 = 24 hours).
    """

    def __init__(self, cache_dir: str = ".cache", ttl: int = 86400) -> None:
        """Initialize the file cache.

        Args:
            cache_dir: Path to the cache directory. Created if it doesn't exist.
            ttl: Cache time-to-live in seconds.
        """
        self.cache_dir = Path(cache_dir)
        self.ttl = ttl
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key_path(self, key: str) -> Path:
        """Get the file path for a cache key.

        Args:
            key: Cache key (will be sanitized for filesystem use).

        Returns:
            Path to the cache file.
        """
        # Sanitize the key for use as a filename
        safe_key = "".join(c if c.isalnum() or c in "-_" else "_" for c in key)
        return self.cache_dir / f"{safe_key}.json"

    def get(self, key: str) -> dict[str, Any] | None:
        """Retrieve cached data if it exists and hasn't expired.

        Args:
            key: Cache key.

        Returns:
            The cached data dict, or None if not found/expired/corrupted.
        """
        path = self._key_path(key)
        if not path.exists():
            return None

        try:
            with open(path, encoding="utf-8") as f:
                cached = json.load(f)

            timestamp = cached.get("timestamp", 0)
            if time.time() - timestamp > self.ttl:
                # Cache expired — remove it
                path.unlink(missing_ok=True)
                return None

            data_val = cached.get("data")
            if isinstance(data_val, dict):
                return data_val
            return None

        except (json.JSONDecodeError, KeyError, OSError):
            # Corrupted cache — remove it
            path.unlink(missing_ok=True)
            return None

    def set(self, key: str, data: dict[str, Any]) -> None:
        """Store data in the cache with the current timestamp.

        Uses atomic write (write to temp file, then rename) to prevent
        corruption from interrupted writes.

        Args:
            key: Cache key.
            data: Data to cache (must be JSON-serializable).
        """
        path = self._key_path(key)
        cache_entry = {
            "timestamp": time.time(),
            "data": data,
        }

        # Atomic write: write to temp file, then rename
        try:
            fd, tmp_path = tempfile.mkstemp(
                dir=str(self.cache_dir),
                suffix=".tmp",
            )
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(cache_entry, f, ensure_ascii=False)
                # On Windows, we need to remove the target first
                path.unlink(missing_ok=True)
                os.rename(tmp_path, str(path))
            except Exception:
                # Clean up temp file on error
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise
        except OSError:
            # If atomic write fails, fall back to direct write
            with open(path, "w", encoding="utf-8") as f:
                json.dump(cache_entry, f, ensure_ascii=False)

    def is_valid(self, key: str) -> bool:
        """Check if a cache entry exists and hasn't expired.

        Args:
            key: Cache key.

        Returns:
            True if the cache entry is valid.
        """
        return self.get(key) is not None

    def clear(self) -> None:
        """Remove all cache files."""
        if self.cache_dir.exists():
            for path in self.cache_dir.glob("*.json"):
                path.unlink(missing_ok=True)

    def clear_user(self, username: str) -> None:
        """Remove all cache files for a specific user.

        Args:
            username: The LeetCode username whose cache to clear.
        """
        if self.cache_dir.exists():
            for path in self.cache_dir.glob(f"{username}_*.json"):
                path.unlink(missing_ok=True)
