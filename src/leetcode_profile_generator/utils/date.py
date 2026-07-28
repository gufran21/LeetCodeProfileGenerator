"""Date and time utilities for formatting and calendar calculations."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone


def format_relative(timestamp: int | float | datetime) -> str:
    """Format a timestamp as a human-readable relative time string.

    Args:
        timestamp: Unix timestamp (int/float) or datetime object.

    Returns:
        A string like '2 hours ago', '3 days ago', 'just now'.
    """
    if isinstance(timestamp, (int, float)):
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    else:
        dt = timestamp

    now = datetime.now(tz=timezone.utc)
    diff = now - dt

    seconds = int(diff.total_seconds())
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m ago" if minutes > 1 else "1m ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours}h ago" if hours > 1 else "1h ago"
    elif seconds < 604800:
        days = seconds // 86400
        return f"{days}d ago" if days > 1 else "1d ago"
    elif seconds < 2592000:
        weeks = seconds // 604800
        return f"{weeks}w ago" if weeks > 1 else "1w ago"
    elif seconds < 31536000:
        months = seconds // 2592000
        return f"{months}mo ago" if months > 1 else "1mo ago"
    else:
        years = seconds // 31536000
        return f"{years}y ago" if years > 1 else "1y ago"


def format_date(timestamp: int | float, fmt: str = "%b %d, %Y") -> str:
    """Format a Unix timestamp as a date string.

    Args:
        timestamp: Unix timestamp.
        fmt: strftime format string.

    Returns:
        Formatted date string.
    """
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return dt.strftime(fmt)


def format_short_date(timestamp: int | float) -> str:
    """Format a Unix timestamp as a short date like 'Jan 15'.

    Args:
        timestamp: Unix timestamp.

    Returns:
        Short date string.
    """
    return format_date(timestamp, "%b %d")


def format_month_year(timestamp: int | float) -> str:
    """Format a Unix timestamp as 'Jan 2025'.

    Args:
        timestamp: Unix timestamp.

    Returns:
        Month-year string.
    """
    return format_date(timestamp, "%b %Y")


def timestamp_to_date(ts: int | float | str) -> date:
    """Convert a Unix timestamp to a date object.

    Args:
        ts: Unix timestamp (can be string from LeetCode API).

    Returns:
        A date object.
    """
    if isinstance(ts, str):
        ts = int(ts)
    return datetime.fromtimestamp(ts, tz=timezone.utc).date()


def get_week_grid(year: int | None = None) -> list[list[date | None]]:
    """Generate a 53×7 grid of dates for heatmap rendering.

    Creates a GitHub-style contribution grid where:
    - Columns represent weeks (53 columns for a full year)
    - Rows represent days of the week (0=Mon, 6=Sun)
    - The grid covers the last 53 weeks from today (or end of given year)

    Args:
        year: Optional year. If None, uses the last 53 weeks from today.

    Returns:
        A list of 53 lists, each containing 7 date objects or None.
        grid[week_index][day_of_week] = date or None.
    """
    if year is not None:
        end_date = date(year, 12, 31)
    else:
        end_date = date.today()

    # Find the start: go back ~53 weeks and find the previous Sunday
    start_date = end_date - timedelta(weeks=53)
    # Adjust to the nearest Sunday (weekday 6 in Python's Monday=0 system)
    days_since_sunday = (start_date.weekday() + 1) % 7
    start_date = start_date - timedelta(days=days_since_sunday)

    grid: list[list[date | None]] = []
    current = start_date

    while current <= end_date:
        week: list[date | None] = []
        for day in range(7):  # Sun=0 through Sat=6
            d = current + timedelta(days=day)
            if d <= end_date:
                week.append(d)
            else:
                week.append(None)
        grid.append(week)
        current += timedelta(weeks=1)

    # Ensure exactly 53 weeks
    while len(grid) < 53:
        grid.append([None] * 7)

    return grid[:53]


def get_month_labels(grid: list[list[date | None]]) -> list[tuple[int, str]]:
    """Get month labels and their column positions for a heatmap grid.

    Args:
        grid: The 53×7 week grid from get_week_grid().

    Returns:
        A list of (column_index, month_abbreviation) tuples.
    """
    labels: list[tuple[int, str]] = []
    last_month = -1

    for col_idx, week in enumerate(grid):
        # Find the first non-None date in this week
        for d in week:
            if d is not None:
                if d.month != last_month:
                    labels.append((col_idx, d.strftime("%b")))
                    last_month = d.month
                break

    return labels
