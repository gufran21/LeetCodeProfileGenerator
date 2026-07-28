"""Activity, badge, and streak models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ActivityData:
    """Submission activity data including streaks and calendar."""

    current_streak: int = 0
    longest_streak: int = 0
    total_active_days: int = 0
    submission_calendar: dict[str, int] = field(default_factory=dict)
    active_years: list[int] = field(default_factory=list)
    monthly_activity: dict[str, int] = field(default_factory=dict)

    @property
    def total_submissions(self) -> int:
        """Total submissions across all days."""
        return sum(self.submission_calendar.values())


@dataclass
class Badge:
    """An earned LeetCode badge."""

    id: str
    name: str
    display_name: str
    icon_url: str = ""
    category: str = ""
    creation_date: str = ""
    hover_text: str = ""

    @property
    def short_label(self) -> str:
        """A short label for display in compact layouts."""
        return self.display_name or self.name


@dataclass
class UpcomingBadge:
    """A badge the user is progressing toward."""

    name: str
    icon_url: str = ""
    progress: float = 0.0  # 0.0 - 1.0

    @property
    def progress_percentage(self) -> float:
        """Progress as a percentage (0-100)."""
        return round(self.progress * 100, 1)
