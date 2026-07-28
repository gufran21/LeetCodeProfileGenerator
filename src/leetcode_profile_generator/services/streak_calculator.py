"""Streak and activity calculation from submission calendar data.

The LeetCode submission calendar is a JSON string mapping Unix timestamp
strings to submission counts. These functions compute streaks, monthly
activity, and other derived metrics from that raw data.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone


def _parse_calendar(calendar: dict[str, int]) -> dict[date, int]:
    """Convert timestamp-keyed calendar to date-keyed calendar.

    Args:
        calendar: Dict mapping Unix timestamp strings to submission counts.

    Returns:
        Dict mapping date objects to submission counts.
    """
    result: dict[date, int] = {}
    for ts_str, count in calendar.items():
        try:
            ts = int(ts_str)
            d = datetime.fromtimestamp(ts, tz=timezone.utc).date()
            result[d] = result.get(d, 0) + count
        except (ValueError, OSError):
            continue
    return result


def calculate_current_streak(calendar: dict[str, int]) -> int:
    """Calculate the current consecutive day streak ending today.

    A streak is broken if the user didn't submit anything on a day.
    Today counts as part of the streak (if there's a submission today)
    or the streak ended yesterday.

    Args:
        calendar: Dict mapping Unix timestamp strings to submission counts.

    Returns:
        Current streak length in days.
    """
    if not calendar:
        return 0

    date_calendar = _parse_calendar(calendar)
    if not date_calendar:
        return 0

    today = date.today()
    streak = 0

    # Check if there's a submission today; if not, start from yesterday
    current = today
    if current not in date_calendar or date_calendar[current] == 0:
        current = today - timedelta(days=1)

    # Count backwards
    while current in date_calendar and date_calendar[current] > 0:
        streak += 1
        current -= timedelta(days=1)

    return streak


def calculate_longest_streak(calendar: dict[str, int]) -> int:
    """Calculate the longest consecutive day streak in the submission history.

    Args:
        calendar: Dict mapping Unix timestamp strings to submission counts.

    Returns:
        Longest streak length in days.
    """
    if not calendar:
        return 0

    date_calendar = _parse_calendar(calendar)
    if not date_calendar:
        return 0

    # Sort all dates with submissions
    active_dates = sorted(d for d, count in date_calendar.items() if count > 0)
    if not active_dates:
        return 0

    longest = 1
    current_streak = 1

    for i in range(1, len(active_dates)):
        if active_dates[i] - active_dates[i - 1] == timedelta(days=1):
            current_streak += 1
            longest = max(longest, current_streak)
        else:
            current_streak = 1

    return longest


def calculate_monthly_activity(
    calendar: dict[str, int],
    months: int = 6,
) -> dict[str, int]:
    """Aggregate submission counts by month for the last N months.

    Args:
        calendar: Dict mapping Unix timestamp strings to submission counts.
        months: Number of months to include (default: 6).

    Returns:
        Ordered dict mapping 'YYYY-MM' strings to total submission counts,
        most recent month last.
    """
    if not calendar:
        return {}

    date_calendar = _parse_calendar(calendar)

    # Determine the month range
    today = date.today()
    result: dict[str, int] = {}

    for i in range(months - 1, -1, -1):
        # Calculate the target month
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1

        key = f"{year}-{month:02d}"
        result[key] = 0

    # Aggregate submissions by month
    for d, count in date_calendar.items():
        key = f"{d.year}-{d.month:02d}"
        if key in result:
            result[key] += count

    return result
