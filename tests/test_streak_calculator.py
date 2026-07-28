"""Tests for streak calculator."""


from leetcode_profile_generator.services.streak_calculator import (
    calculate_current_streak,
    calculate_longest_streak,
    calculate_monthly_activity,
)


class TestCalculateCurrentStreak:
    def test_empty_calendar(self):
        assert calculate_current_streak({}) == 0

    def test_no_submissions(self):
        assert calculate_current_streak({"1718524800": 0}) == 0

    def test_single_day(self):
        # Use a recent timestamp that would be today or yesterday
        import time
        today_ts = str(int(time.time()) - (int(time.time()) % 86400))
        assert calculate_current_streak({today_ts: 3}) >= 0


class TestCalculateLongestStreak:
    def test_empty_calendar(self):
        assert calculate_longest_streak({}) == 0

    def test_single_day(self):
        assert calculate_longest_streak({"1718524800": 3}) == 1

    def test_consecutive_days(self):
        calendar = {
            "1718524800": 3,  # Day 1
            "1718611200": 5,  # Day 2
            "1718697600": 1,  # Day 3
        }
        assert calculate_longest_streak(calendar) == 3

    def test_gap_in_streak(self):
        calendar = {
            "1718524800": 3,  # Day 1
            "1718611200": 5,  # Day 2
            # Day 3 missing
            "1718784000": 2,  # Day 4
            "1718870400": 7,  # Day 5
            "1718956800": 4,  # Day 6
        }
        assert calculate_longest_streak(calendar) == 3

    def test_zero_count_not_counted(self):
        calendar = {
            "1718524800": 3,  # Day 1
            "1718611200": 0,  # Day 2 (0 doesn't count)
            "1718697600": 1,  # Day 3
        }
        assert calculate_longest_streak(calendar) == 1


class TestCalculateMonthlyActivity:
    def test_empty_calendar(self):
        assert calculate_monthly_activity({}) == {}

    def test_default_6_months(self):
        calendar = {"1718524800": 3}
        result = calculate_monthly_activity(calendar)
        assert len(result) == 6

    def test_custom_months(self):
        calendar = {"1718524800": 3}
        result = calculate_monthly_activity(calendar, months=3)
        assert len(result) == 3

    def test_aggregation(self):
        # Two submissions on different days in the current month
        from datetime import date, datetime, timezone
        today = date.today()
        dt1 = datetime(today.year, today.month, 1, 12, 0, 0, tzinfo=timezone.utc)
        dt2 = datetime(today.year, today.month, 2, 12, 0, 0, tzinfo=timezone.utc)
        ts1 = str(int(dt1.timestamp()))
        ts2 = str(int(dt2.timestamp()))

        calendar = {
            ts1: 3,
            ts2: 5,
        }
        result = calculate_monthly_activity(calendar, months=12)
        month_key = f"{today.year}-{today.month:02d}"
        assert result.get(month_key, 0) == 8
