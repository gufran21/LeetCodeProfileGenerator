"""Tests for the theme engine."""

import json

import pytest

from leetcode_profile_generator.render.themes import (
    Theme,
    get_theme,
    list_themes,
    load_custom_theme,
)


class TestGetTheme:
    def test_all_builtin_themes_load(self):
        """Every built-in theme should load without errors."""
        for name in list_themes():
            theme = get_theme(name)
            assert isinstance(theme, Theme)
            assert theme.name == name

    def test_case_insensitive(self):
        theme = get_theme("GitHub_Dark")
        assert theme.name == "github_dark"

    def test_unknown_theme_raises(self):
        with pytest.raises(ValueError, match="Unknown theme"):
            get_theme("nonexistent_theme")

    def test_theme_has_valid_colors(self):
        """All color fields should be valid hex strings."""
        theme = get_theme("github_dark")
        color_fields = [
            "bg_color", "title_color", "text_color", "text_secondary",
            "border_color", "easy_color", "medium_color", "hard_color",
            "accent_color", "chart_line_color",
        ]
        for field in color_fields:
            value = getattr(theme, field)
            assert value.startswith("#"), f"{field} = {value} is not a hex color"


class TestListThemes:
    def test_returns_sorted_list(self):
        themes = list_themes()
        assert themes == sorted(themes)

    def test_has_expected_count(self):
        themes = list_themes()
        assert len(themes) == 9

    def test_contains_key_themes(self):
        themes = list_themes()
        assert "github_dark" in themes
        assert "dracula" in themes
        assert "nord" in themes


class TestLoadCustomTheme:
    def test_load_from_json(self, tmp_path):
        theme_data = {
            "name": "test_theme",
            "bg_color": "#111111",
            "title_color": "#ffffff",
            "text_color": "#cccccc",
        }
        path = tmp_path / "test_theme.json"
        path.write_text(json.dumps(theme_data))

        theme = load_custom_theme(str(path))
        assert theme.name == "test_theme"
        assert theme.bg_color == "#111111"

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_custom_theme("/nonexistent/path.json")

    def test_missing_name_raises(self, tmp_path):
        path = tmp_path / "bad_theme.json"
        path.write_text('{"bg_color": "#111"}')

        with pytest.raises(ValueError, match="name"):
            load_custom_theme(str(path))

    def test_gradient_list_to_tuple(self, tmp_path):
        theme_data = {
            "name": "grad_test",
            "bg_color": "#111111",
            "bg_gradient": ["#111111", "#222222"],
        }
        path = tmp_path / "grad_theme.json"
        path.write_text(json.dumps(theme_data))

        theme = load_custom_theme(str(path))
        assert theme.bg_gradient == ("#111111", "#222222")
