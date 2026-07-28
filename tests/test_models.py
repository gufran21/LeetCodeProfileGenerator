"""Tests for data models."""

from leetcode_profile_generator.models.activity import Badge, UpcomingBadge
from leetcode_profile_generator.models.contest import ContestRanking, ContestRecord
from leetcode_profile_generator.models.profile import SolvedStats, UserProfile


class TestUserProfile:
    def test_display_name_with_real_name(self):
        profile = UserProfile(username="user1", real_name="John Doe")
        assert profile.display_name == "John Doe"

    def test_display_name_without_real_name(self):
        profile = UserProfile(username="user1")
        assert profile.display_name == "user1"


class TestSolvedStats:
    def test_total_solved(self, sample_solved):
        assert sample_solved.total_solved == 403

    def test_total_total(self, sample_solved):
        assert sample_solved.total_total == 3328

    def test_acceptance_rate(self, sample_solved):
        assert sample_solved.acceptance_rate == 12.1  # 403/3328

    def test_easy_percentage(self, sample_solved):
        assert sample_solved.easy_percentage == 17.1

    def test_medium_percentage(self, sample_solved):
        assert sample_solved.medium_percentage == 11.7

    def test_hard_percentage(self, sample_solved):
        assert sample_solved.hard_percentage == 7.7

    def test_zero_total(self):
        stats = SolvedStats()
        assert stats.acceptance_rate == 0.0
        assert stats.easy_percentage == 0.0


class TestContestRanking:
    def test_has_competed(self, sample_contest_ranking):
        assert sample_contest_ranking.has_competed is True

    def test_has_not_competed(self):
        ranking = ContestRanking()
        assert ranking.has_competed is False


class TestContestRecord:
    def test_positive_delta(self):
        record = ContestRecord(
            title="Test", rating=1800, ranking=100, timestamp=1000, delta_rating=23
        )
        assert record.is_positive is True
        assert record.formatted_delta == "+23"

    def test_negative_delta(self):
        record = ContestRecord(
            title="Test", rating=1800, ranking=100, timestamp=1000, delta_rating=-18
        )
        assert record.is_positive is False
        assert record.formatted_delta == "-18"

    def test_zero_delta(self):
        record = ContestRecord(title="Test", rating=1800, ranking=100, timestamp=1000)
        assert record.formatted_delta == "0"


class TestActivityData:
    def test_total_submissions(self, sample_activity):
        assert sample_activity.total_submissions > 0


class TestBadge:
    def test_short_label(self):
        badge = Badge(id="1", name="test", display_name="Test Badge")
        assert badge.short_label == "Test Badge"

    def test_short_label_fallback(self):
        badge = Badge(id="1", name="test", display_name="")
        assert badge.short_label == "test"


class TestUpcomingBadge:
    def test_progress_percentage(self):
        badge = UpcomingBadge(name="test", progress=0.403)
        assert badge.progress_percentage == 40.3


class TestLeetCodeData:
    def test_has_contests(self, sample_data):
        assert sample_data.has_contests is True

    def test_no_contests(self, sample_data_no_contests):
        assert sample_data_no_contests.has_contests is False

    def test_has_badges(self, sample_data):
        assert sample_data.has_badges is True

    def test_has_activity(self, sample_data):
        assert sample_data.has_activity is True
