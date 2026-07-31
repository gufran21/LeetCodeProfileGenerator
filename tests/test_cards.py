"""Tests for card generators — validates SVG output structure and content."""

import xml.etree.ElementTree as ET

import pytest

from leetcode_profile_generator.cards import (
    generate_badges_card,
    generate_contest_history_card,
    generate_dashboard_card,
    generate_difficulty_card,
    generate_heatmap_card,
    generate_rating_card,
    generate_stats_card,
    generate_streak_card,
)
from leetcode_profile_generator.render.themes import get_theme


def _validate_svg(svg_string: str) -> ET.Element:
    """Parse SVG string and return root element. Raises on invalid XML."""
    return ET.fromstring(svg_string)


def _svg_size_kb(svg_string: str) -> float:
    """Return SVG size in kilobytes."""
    return len(svg_string.encode("utf-8")) / 1024


class TestStatsCard:
    def test_generates_valid_svg(self, sample_data, dark_theme):
        svg = generate_stats_card(sample_data, dark_theme)
        root = _validate_svg(svg)
        assert root.tag == "{http://www.w3.org/2000/svg}svg"

    def test_contains_username(self, sample_data, dark_theme):
        svg = generate_stats_card(sample_data, dark_theme)
        assert "TestUser" in svg

    def test_contains_solved_counts(self, sample_data, dark_theme):
        svg = generate_stats_card(sample_data, dark_theme)
        assert "403" in svg  # total solved (142 + 203 + 58)

    def test_under_size_limit(self, sample_data, dark_theme):
        svg = generate_stats_card(sample_data, dark_theme)
        assert _svg_size_kb(svg) < 250

    def test_light_theme(self, sample_data, light_theme):
        svg = generate_stats_card(sample_data, light_theme)
        root = _validate_svg(svg)
        assert root.tag == "{http://www.w3.org/2000/svg}svg"

    def test_no_contests(self, sample_data_no_contests, dark_theme):
        svg = generate_stats_card(sample_data_no_contests, dark_theme)
        root = _validate_svg(svg)
        assert root.tag == "{http://www.w3.org/2000/svg}svg"
        assert "TestUser" in svg


class TestRatingCard:
    def test_generates_valid_svg(self, sample_data, dark_theme):
        svg = generate_rating_card(sample_data, dark_theme)
        root = _validate_svg(svg)
        assert root.tag == "{http://www.w3.org/2000/svg}svg"

    def test_contains_rating(self, sample_data, dark_theme):
        svg = generate_rating_card(sample_data, dark_theme)
        assert "1847" in svg

    def test_placeholder_no_contests(self, sample_data_no_contests, dark_theme):
        svg = generate_rating_card(sample_data_no_contests, dark_theme)
        assert "No contest data" in svg

    def test_under_size_limit(self, sample_data, dark_theme):
        svg = generate_rating_card(sample_data, dark_theme)
        assert _svg_size_kb(svg) < 250


class TestDifficultyCard:
    def test_generates_valid_svg(self, sample_data, dark_theme):
        svg = generate_difficulty_card(sample_data, dark_theme)
        root = _validate_svg(svg)
        assert root.tag == "{http://www.w3.org/2000/svg}svg"

    def test_contains_labels(self, sample_data, dark_theme):
        svg = generate_difficulty_card(sample_data, dark_theme)
        assert "Easy" in svg
        assert "Medium" in svg
        assert "Hard" in svg


class TestHeatmapCard:
    def test_generates_valid_svg(self, sample_data, dark_theme):
        svg = generate_heatmap_card(sample_data, dark_theme)
        root = _validate_svg(svg)
        assert root.tag == "{http://www.w3.org/2000/svg}svg"

    def test_contains_submission_count(self, sample_data, dark_theme):
        svg = generate_heatmap_card(sample_data, dark_theme)
        assert "submissions" in svg

    def test_under_size_limit(self, sample_data, dark_theme):
        svg = generate_heatmap_card(sample_data, dark_theme)
        assert _svg_size_kb(svg) < 250


class TestContestHistoryCard:
    def test_generates_valid_svg(self, sample_data, dark_theme):
        svg = generate_contest_history_card(sample_data, dark_theme)
        root = _validate_svg(svg)
        assert root.tag == "{http://www.w3.org/2000/svg}svg"

    def test_contains_contest_names(self, sample_data, dark_theme):
        svg = generate_contest_history_card(sample_data, dark_theme)
        assert "Weekly Contest" in svg

    def test_placeholder_no_contests(self, sample_data_no_contests, dark_theme):
        svg = generate_contest_history_card(sample_data_no_contests, dark_theme)
        assert "No contest history" in svg


class TestBadgesCard:
    def test_generates_valid_svg(self, sample_data, dark_theme):
        svg = generate_badges_card(sample_data, dark_theme)
        root = _validate_svg(svg)
        assert root.tag == "{http://www.w3.org/2000/svg}svg"

    def test_contains_badge_count(self, sample_data, dark_theme):
        svg = generate_badges_card(sample_data, dark_theme)
        assert "4 earned" in svg

    def test_placeholder_no_badges(self, sample_data_no_contests, dark_theme):
        svg = generate_badges_card(sample_data_no_contests, dark_theme)
        assert "No badges" in svg


class TestStreakCard:
    def test_generates_valid_svg(self, sample_data, dark_theme):
        svg = generate_streak_card(sample_data, dark_theme)
        root = _validate_svg(svg)
        assert root.tag == "{http://www.w3.org/2000/svg}svg"

    def test_contains_streak_values(self, sample_data, dark_theme):
        svg = generate_streak_card(sample_data, dark_theme)
        assert "87" in svg   # longest streak

    def test_contains_monthly_activity(self, sample_data, dark_theme):
        svg = generate_streak_card(sample_data, dark_theme)
        assert "Monthly Activity" in svg


class TestDashboardCard:
    def test_generates_valid_svg(self, sample_data, dark_theme):
        svg = generate_dashboard_card(sample_data, dark_theme)
        root = _validate_svg(svg)
        assert root.tag == "{http://www.w3.org/2000/svg}svg"

    def test_contains_username(self, sample_data, dark_theme):
        svg = generate_dashboard_card(sample_data, dark_theme)
        assert "TestUser" in svg

    def test_under_size_limit(self, sample_data, dark_theme):
        svg = generate_dashboard_card(sample_data, dark_theme)
        assert _svg_size_kb(svg) < 250


class TestAllCardsAllThemes:
    """Ensure every card generates valid SVG with every theme."""

    @pytest.mark.parametrize("theme_name", [
        "github_dark", "github_light", "dracula", "nord",
        "catppuccin_mocha", "catppuccin_latte", "tokyo_night",
        "gruvbox_dark", "one_dark",
    ])
    def test_all_cards_all_themes(self, sample_data, theme_name):
        theme = get_theme(theme_name)
        generators = [
            generate_stats_card,
            generate_rating_card,
            generate_difficulty_card,
            generate_heatmap_card,
            generate_contest_history_card,
            generate_badges_card,
            generate_streak_card,
            generate_dashboard_card,
        ]
        for gen in generators:
            svg = gen(sample_data, theme)
            root = _validate_svg(svg)
            assert root.tag == "{http://www.w3.org/2000/svg}svg"
            assert _svg_size_kb(svg) < 250
