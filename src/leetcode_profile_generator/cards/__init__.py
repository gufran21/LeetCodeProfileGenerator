"""SVG card generators for LeetCode profile data.

Each card module exposes a `generate(data, theme) -> str` function
that returns a complete SVG string.
"""

from .badges import generate_badges_card
from .contest_history import generate_contest_history_card
from .dashboard import generate_dashboard_card
from .difficulty import generate_difficulty_card
from .heatmap import generate_heatmap_card
from .rating import generate_rating_card
from .stats import generate_stats_card
from .streak import generate_streak_card

__all__ = [
    "generate_stats_card",
    "generate_rating_card",
    "generate_difficulty_card",
    "generate_heatmap_card",
    "generate_contest_history_card",
    "generate_badges_card",
    "generate_streak_card",
    "generate_dashboard_card",
]
