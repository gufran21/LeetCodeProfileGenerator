"""User profile and solved statistics models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UserProfile:
    """Core user profile information from LeetCode."""

    username: str
    real_name: str | None = None
    ranking: int = 0
    avatar_url: str | None = None
    about: str | None = None

    @property
    def display_name(self) -> str:
        """Return the best available display name."""
        return self.real_name or self.username


@dataclass
class SolvedStats:
    """Problem solving statistics broken down by difficulty."""

    easy_solved: int = 0
    easy_total: int = 0
    medium_solved: int = 0
    medium_total: int = 0
    hard_solved: int = 0
    hard_total: int = 0
    easy_beats: float | None = None
    medium_beats: float | None = None
    hard_beats: float | None = None

    @property
    def total_solved(self) -> int:
        """Total problems solved across all difficulties."""
        return self.easy_solved + self.medium_solved + self.hard_solved

    @property
    def total_total(self) -> int:
        """Total problems available across all difficulties."""
        return self.easy_total + self.medium_total + self.hard_total

    @property
    def acceptance_rate(self) -> float:
        """Overall acceptance rate as a percentage."""
        if self.total_total == 0:
            return 0.0
        return round((self.total_solved / self.total_total) * 100, 1)

    @property
    def easy_percentage(self) -> float:
        """Percentage of easy problems solved."""
        if self.easy_total == 0:
            return 0.0
        return round((self.easy_solved / self.easy_total) * 100, 1)

    @property
    def medium_percentage(self) -> float:
        """Percentage of medium problems solved."""
        if self.medium_total == 0:
            return 0.0
        return round((self.medium_solved / self.medium_total) * 100, 1)

    @property
    def hard_percentage(self) -> float:
        """Percentage of hard problems solved."""
        if self.hard_total == 0:
            return 0.0
        return round((self.hard_solved / self.hard_total) * 100, 1)
