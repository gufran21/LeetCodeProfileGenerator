"""Combined data model that bundles all LeetCode data for a user."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from .activity import ActivityData, Badge, UpcomingBadge
from .contest import ContestRanking, ContestRecord
from .profile import SolvedStats, UserProfile


@dataclass
class LeetCodeData:
    """Complete data bundle for a user — passed to card generators.

    This is the single object that flows through the entire pipeline:
    API → DataService → LeetCodeData → CardGenerators → SVG output.
    """

    profile: UserProfile
    solved: SolvedStats
    contest: ContestRanking | None = None
    contest_history: list[ContestRecord] = field(default_factory=list)
    activity: ActivityData = field(default_factory=ActivityData)
    badges: list[Badge] = field(default_factory=list)
    upcoming_badges: list[UpcomingBadge] = field(default_factory=list)
    fetched_at: datetime = field(default_factory=datetime.now)
    avatar_b64: str | None = None

    @property
    def has_contests(self) -> bool:
        """Whether the user has any contest history."""
        return self.contest is not None and self.contest.has_competed

    @property
    def has_badges(self) -> bool:
        """Whether the user has any earned badges."""
        return len(self.badges) > 0

    @property
    def has_activity(self) -> bool:
        """Whether the user has any submission activity."""
        return self.activity.total_active_days > 0
