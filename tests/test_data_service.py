"""Tests for the data service — JSON to model mapping."""

from pathlib import Path

import pytest

from leetcode_profile_generator.services.data_service import LeetCodeDataService

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestParseProfile:
    def test_parses_profile(self, profile_response):
        service = LeetCodeDataService(use_cache=False, fetch_avatar=False)
        profile = service._parse_profile(profile_response, "TestUser")
        assert profile.username == "TestUser"
        assert profile.real_name == "Test User"
        assert profile.ranking == 42156

    def test_parses_solved_stats(self, profile_response):
        service = LeetCodeDataService(use_cache=False, fetch_avatar=False)
        solved = service._parse_solved(profile_response)
        assert solved.easy_solved == 142
        assert solved.medium_solved == 203
        assert solved.hard_solved == 58
        assert solved.easy_total == 830
        assert solved.easy_beats == 85.2


class TestParseContest:
    def test_parses_contest_ranking(self, contest_response):
        service = LeetCodeDataService(use_cache=False, fetch_avatar=False)
        ranking, records = service._parse_contest(contest_response)

        assert ranking is not None
        assert ranking.attended_count == 47
        assert ranking.rating == pytest.approx(1847.234)
        assert ranking.badge_name == "Knight"

    def test_parses_contest_history(self, contest_response):
        service = LeetCodeDataService(use_cache=False, fetch_avatar=False)
        ranking, records = service._parse_contest(contest_response)

        # Should filter out non-attended contests
        assert len(records) == 9  # 10 total - 1 not attended
        assert all(r.title for r in records)

    def test_computes_delta_ratings(self, contest_response):
        service = LeetCodeDataService(use_cache=False, fetch_avatar=False)
        _, records = service._parse_contest(contest_response)

        # First record has delta 0, subsequent have computed deltas
        for i in range(1, len(records)):
            expected_delta = records[i].rating - records[i - 1].rating
            assert records[i].delta_rating == pytest.approx(expected_delta)

    def test_empty_contest_data(self):
        service = LeetCodeDataService(use_cache=False, fetch_avatar=False)
        ranking, records = service._parse_contest({})
        assert ranking is None
        assert records == []


class TestParseActivity:
    def test_parses_calendar(self, calendar_response):
        service = LeetCodeDataService(use_cache=False, fetch_avatar=False)
        activity = service._parse_activity(calendar_response)

        assert activity.total_active_days == 312
        assert len(activity.submission_calendar) > 0
        assert activity.active_years == [2023, 2024, 2025]

    def test_computes_longest_streak(self, calendar_response):
        service = LeetCodeDataService(use_cache=False, fetch_avatar=False)
        activity = service._parse_activity(calendar_response)
        assert activity.longest_streak > 0

    def test_computes_monthly_activity(self, calendar_response):
        service = LeetCodeDataService(use_cache=False, fetch_avatar=False)
        activity = service._parse_activity(calendar_response)
        assert len(activity.monthly_activity) == 6


class TestParseBadges:
    def test_parses_badges(self, badges_response):
        service = LeetCodeDataService(use_cache=False, fetch_avatar=False)
        badges, upcoming = service._parse_badges(badges_response)

        assert len(badges) == 4
        assert badges[0].name == "100 Solved"
        assert badges[2].name == "Knight"

    def test_parses_upcoming(self, badges_response):
        service = LeetCodeDataService(use_cache=False, fetch_avatar=False)
        badges, upcoming = service._parse_badges(badges_response)

        assert len(upcoming) == 1
        assert upcoming[0].name == "1000 Solved"
        assert upcoming[0].progress == pytest.approx(0.403)

    def test_empty_badges(self):
        service = LeetCodeDataService(use_cache=False, fetch_avatar=False)
        badges, upcoming = service._parse_badges({})
        assert badges == []
        assert upcoming == []
