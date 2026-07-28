"""Contest ranking and history models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ContestRanking:
    """Aggregate contest ranking information for a user."""

    attended_count: int = 0
    rating: float = 0.0
    max_rating: float = 0.0
    global_ranking: int = 0
    total_participants: int = 0
    top_percentage: float = 0.0
    badge_name: str | None = None

    @property
    def has_competed(self) -> bool:
        """Whether the user has participated in any contest."""
        return self.attended_count > 0


@dataclass
class ContestRecord:
    """A single contest participation record."""

    title: str
    rating: float
    ranking: int
    timestamp: int
    trend: str = "NONE"  # "UP" | "DOWN" | "NONE"
    delta_rating: float = 0.0

    @property
    def is_positive(self) -> bool:
        """Whether the rating change was positive."""
        return self.delta_rating > 0

    @property
    def formatted_delta(self) -> str:
        """Formatted delta string like '+23' or '-18'."""
        if self.delta_rating > 0:
            return f"+{self.delta_rating:.0f}"
        elif self.delta_rating < 0:
            return f"{self.delta_rating:.0f}"
        return "0"
