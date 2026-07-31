"""Shared pytest fixtures for all test modules."""

# ruff: noqa: E402
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure src directory is in python path
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest

from leetcode_profile_generator.models.activity import ActivityData, Badge, UpcomingBadge
from leetcode_profile_generator.models.combined import LeetCodeData
from leetcode_profile_generator.models.contest import ContestRanking, ContestRecord
from leetcode_profile_generator.models.profile import SolvedStats, UserProfile
from leetcode_profile_generator.render.themes import Theme, get_theme

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _load_fixture(name: str) -> dict:
    """Load a JSON fixture file."""
    with open(FIXTURES_DIR / name, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def profile_response() -> dict:
    """Raw profile API response fixture."""
    return _load_fixture("profile_response.json")


@pytest.fixture
def contest_response() -> dict:
    """Raw contest API response fixture."""
    return _load_fixture("contest_response.json")


@pytest.fixture
def calendar_response() -> dict:
    """Raw calendar API response fixture."""
    return _load_fixture("calendar_response.json")


@pytest.fixture
def badges_response() -> dict:
    """Raw badges API response fixture."""
    return _load_fixture("badges_response.json")


@pytest.fixture
def sample_profile() -> UserProfile:
    """Sample UserProfile for testing."""
    return UserProfile(
        username="TestUser",
        real_name="Test User",
        ranking=42156,
        avatar_url="https://example.com/avatar.jpg",
        about="Competitive programmer",
    )


@pytest.fixture
def sample_solved() -> SolvedStats:
    """Sample SolvedStats for testing."""
    return SolvedStats(
        easy_solved=142,
        easy_total=830,
        medium_solved=203,
        medium_total=1742,
        hard_solved=58,
        hard_total=756,
        easy_beats=85.2,
        medium_beats=72.1,
        hard_beats=65.8,
    )


@pytest.fixture
def sample_contest_ranking() -> ContestRanking:
    """Sample ContestRanking for testing."""
    return ContestRanking(
        attended_count=47,
        rating=1847.234,
        max_rating=1847.234,
        global_ranking=42156,
        total_participants=512000,
        top_percentage=8.23,
        badge_name="Knight",
    )


@pytest.fixture
def sample_contest_history() -> list[ContestRecord]:
    """Sample contest history for testing."""
    records = [
        ContestRecord(
            title="Weekly Contest 395", rating=1694.0, ranking=10455,
            timestamp=1718524800, trend="UP", delta_rating=51,
        ),
        ContestRecord(
            title="Weekly Contest 396", rating=1754.0, ranking=7890,
            timestamp=1719734400, trend="UP", delta_rating=38,
        ),
        ContestRecord(
            title="Weekly Contest 397", rating=1749.0, ranking=8102,
            timestamp=1720339200, trend="DOWN", delta_rating=-5,
        ),
        ContestRecord(
            title="Weekly Contest 398", rating=1816.0, ranking=4998,
            timestamp=1720944000, trend="UP", delta_rating=67,
        ),
        ContestRecord(
            title="Weekly Contest 401", rating=1847.0, ranking=4521,
            timestamp=1723968000, trend="UP", delta_rating=23,
        ),
    ]
    return records


@pytest.fixture
def sample_activity() -> ActivityData:
    """Sample ActivityData for testing."""
    return ActivityData(
        longest_streak=87,
        total_active_days=312,
        submission_calendar={
            "1718524800": 3, "1718611200": 5, "1718697600": 1,
            "1718784000": 2, "1718870400": 7, "1718956800": 4,
        },
        active_years=[2023, 2024, 2025],
        monthly_activity={
            "2025-02": 45, "2025-03": 38, "2025-04": 52,
            "2025-05": 33, "2025-06": 48, "2025-07": 61,
        },
    )


@pytest.fixture
def sample_badges() -> list[Badge]:
    """Sample badge list for testing."""
    return [
        Badge(
            id="1", name="100 Solved", display_name="100 Days Badge",
            category="solving", creation_date="2023-06-15",
        ),
        Badge(
            id="2", name="500 Solved", display_name="500 Days Badge",
            category="solving", creation_date="2024-02-20",
        ),
        Badge(
            id="3", name="Knight", display_name="Knight Badge",
            category="contest", creation_date="2024-05-10",
        ),
        Badge(
            id="4", name="Dec 2023", display_name="Dec LeetCoding Challenge",
            category="daily", creation_date="2023-12-31",
        ),
    ]


@pytest.fixture
def sample_upcoming_badges() -> list[UpcomingBadge]:
    """Sample upcoming badges for testing."""
    return [UpcomingBadge(name="1000 Solved", progress=40.3)]


@pytest.fixture
def sample_data(
    sample_profile,
    sample_solved,
    sample_contest_ranking,
    sample_contest_history,
    sample_activity,
    sample_badges,
    sample_upcoming_badges,
) -> LeetCodeData:
    """Complete LeetCodeData sample for card generation tests."""
    return LeetCodeData(
        profile=sample_profile,
        solved=sample_solved,
        contest=sample_contest_ranking,
        contest_history=sample_contest_history,
        activity=sample_activity,
        badges=sample_badges,
        upcoming_badges=sample_upcoming_badges,
        fetched_at=datetime(2025, 7, 15, 12, 0, 0, tzinfo=timezone.utc),
    )


@pytest.fixture
def sample_data_no_contests(sample_profile, sample_solved, sample_activity) -> LeetCodeData:
    """LeetCodeData sample with no contest history."""
    return LeetCodeData(
        profile=sample_profile,
        solved=sample_solved,
        contest=None,
        contest_history=[],
        activity=sample_activity,
        fetched_at=datetime(2025, 7, 15, 12, 0, 0, tzinfo=timezone.utc),
    )


@pytest.fixture
def dark_theme() -> Theme:
    """GitHub dark theme for testing."""
    return get_theme("github_dark")


@pytest.fixture
def light_theme() -> Theme:
    """GitHub light theme for testing."""
    return get_theme("github_light")
