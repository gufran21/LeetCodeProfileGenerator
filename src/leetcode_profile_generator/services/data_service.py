"""Main data service that orchestrates API calls and transforms raw data into models.

This is the primary facade that the CLI and card generators interact with.
It handles: API calls → JSON parsing → model mapping → caching → avatar fetch.
"""

from __future__ import annotations

import base64
import json
import logging
from datetime import datetime, timezone
from typing import Any

import httpx

from ..api.graphql import LeetCodeClient
from ..models.activity import ActivityData, Badge, UpcomingBadge
from ..models.combined import LeetCodeData
from ..models.contest import ContestRanking, ContestRecord
from ..models.profile import SolvedStats, UserProfile
from ..utils.cache import FileCache
from .streak_calculator import (
    calculate_longest_streak,
    calculate_monthly_activity,
)

logger = logging.getLogger(__name__)


class LeetCodeDataService:
    """Orchestrates data fetching, parsing, and caching for a LeetCode user.

    Usage:
        service = LeetCodeDataService()
        data = await service.fetch_user_data("username")
    """

    def __init__(
        self,
        cache_dir: str = ".cache",
        cache_ttl: int = 86400,
        use_cache: bool = True,
        fetch_avatar: bool = True,
        timeout: float = 15.0,
    ) -> None:
        """Initialize the data service.

        Args:
            cache_dir: Directory for cached API responses.
            cache_ttl: Cache time-to-live in seconds.
            use_cache: Whether to use the filesystem cache.
            fetch_avatar: Whether to fetch and encode the user's avatar.
            timeout: API request timeout in seconds.
        """
        self.cache = FileCache(cache_dir=cache_dir, ttl=cache_ttl) if use_cache else None
        self.fetch_avatar = fetch_avatar
        self.timeout = timeout

    async def fetch_user_data(self, username: str) -> LeetCodeData:
        """Fetch all data for a LeetCode user and return a complete LeetCodeData bundle.

        Args:
            username: The LeetCode username.

        Returns:
            A LeetCodeData object with all available data.

        Raises:
            UserNotFoundError: If the username doesn't exist on LeetCode.
            APIError: For other API failures.
        """
        # Try cache first
        if self.cache:
            cached = self.cache.get(f"{username}_all")
            if cached:
                logger.info("Using cached data for %s", username)
                return self._parse_cached(cached, username)

        # Fetch fresh data
        async with LeetCodeClient(timeout=self.timeout) as client:
            raw_data = await client.fetch_all(username)

        # Parse into models
        data = self._parse_raw_data(raw_data, username)

        # Fetch avatar if enabled
        if self.fetch_avatar and data.profile.avatar_url:
            data.avatar_b64 = await self._fetch_avatar(data.profile.avatar_url)

        # Cache the raw data
        if self.cache:
            self.cache.set(f"{username}_all", raw_data)

        return data

    def _parse_raw_data(self, raw: dict[str, Any], username: str) -> LeetCodeData:
        """Parse raw API responses into a LeetCodeData model.

        Args:
            raw: Dict with 'profile', 'contest', 'calendar', 'badges' keys.
            username: The LeetCode username.

        Returns:
            A fully populated LeetCodeData object.
        """
        profile = self._parse_profile(raw.get("profile", {}), username)
        solved = self._parse_solved(raw.get("profile", {}))
        contest, contest_history = self._parse_contest(raw.get("contest", {}))
        activity = self._parse_activity(raw.get("calendar", {}))
        badges, upcoming = self._parse_badges(raw.get("badges", {}))

        return LeetCodeData(
            profile=profile,
            solved=solved,
            contest=contest,
            contest_history=contest_history,
            activity=activity,
            badges=badges,
            upcoming_badges=upcoming,
            fetched_at=datetime.now(tz=timezone.utc),
        )

    def _parse_cached(self, cached: dict[str, Any], username: str) -> LeetCodeData:
        """Parse cached raw data into models.

        Args:
            cached: The cached raw data dict.
            username: The LeetCode username.

        Returns:
            A LeetCodeData object reconstructed from cache.
        """
        return self._parse_raw_data(cached, username)

    def _parse_profile(self, data: dict[str, Any], username: str) -> UserProfile:
        """Parse profile data from the API response.

        Args:
            data: Raw profile API response.
            username: The LeetCode username.

        Returns:
            A UserProfile object.
        """
        matched = data.get("matchedUser", {})
        profile_data = matched.get("profile", {})

        return UserProfile(
            username=matched.get("username", username),
            real_name=profile_data.get("realName") or None,
            ranking=profile_data.get("ranking", 0),
            avatar_url=profile_data.get("userAvatar") or None,
            about=profile_data.get("aboutMe") or None,
        )

    def _parse_solved(self, data: dict[str, Any]) -> SolvedStats:
        """Parse solved statistics from the API response.

        Args:
            data: Raw profile API response (contains matchedUser and allQuestionsCount).

        Returns:
            A SolvedStats object.
        """
        matched = data.get("matchedUser", {})
        all_questions = data.get("allQuestionsCount", [])
        ac_stats = matched.get("submitStatsGlobal", {}).get("acSubmissionNum", [])
        beats_stats = matched.get("problemsSolvedBeatsStats", [])

        # Build lookup dicts
        total_by_diff: dict[str, int] = {}
        for item in all_questions:
            total_by_diff[item.get("difficulty", "")] = item.get("count", 0)

        solved_by_diff: dict[str, int] = {}
        for item in ac_stats:
            solved_by_diff[item.get("difficulty", "")] = item.get("count", 0)

        beats_by_diff: dict[str, float | None] = {}
        for item in beats_stats:
            pct = item.get("percentage")
            beats_by_diff[item.get("difficulty", "")] = pct if pct is not None else None

        return SolvedStats(
            easy_solved=solved_by_diff.get("Easy", 0),
            easy_total=total_by_diff.get("Easy", 0),
            medium_solved=solved_by_diff.get("Medium", 0),
            medium_total=total_by_diff.get("Medium", 0),
            hard_solved=solved_by_diff.get("Hard", 0),
            hard_total=total_by_diff.get("Hard", 0),
            easy_beats=beats_by_diff.get("Easy"),
            medium_beats=beats_by_diff.get("Medium"),
            hard_beats=beats_by_diff.get("Hard"),
        )

    def _parse_contest(
        self, data: dict[str, Any]
    ) -> tuple[ContestRanking | None, list[ContestRecord]]:
        """Parse contest ranking and history from the API response.

        Args:
            data: Raw contest API response.

        Returns:
            Tuple of (ContestRanking or None, list of ContestRecords).
        """
        ranking_data = data.get("userContestRanking")
        history_data = data.get("userContestRankingHistory", [])

        if not ranking_data:
            return None, []

        # Parse contest history (only attended contests)
        records: list[ContestRecord] = []
        for item in history_data:
            if not item.get("attended", True):
                continue
            contest = item.get("contest", {})
            records.append(
                ContestRecord(
                    title=contest.get("title", "Unknown Contest"),
                    rating=item.get("rating", 0),
                    ranking=item.get("ranking", 0),
                    timestamp=int(contest.get("startTime", 0)),
                    trend=item.get("trendDirection", "NONE"),
                )
            )

        # Sort by timestamp
        records.sort(key=lambda r: r.timestamp)

        # Compute delta ratings
        for i in range(len(records)):
            if i > 0:
                records[i].delta_rating = records[i].rating - records[i - 1].rating

        # Compute max rating from history
        max_rating = max((r.rating for r in records), default=0.0)

        badge_data = ranking_data.get("badge")
        badge_name = badge_data.get("name") if badge_data else None

        ranking = ContestRanking(
            attended_count=ranking_data.get("attendedContestsCount", 0),
            rating=ranking_data.get("rating", 0),
            max_rating=max_rating,
            global_ranking=ranking_data.get("globalRanking", 0),
            total_participants=ranking_data.get("totalParticipants", 0),
            top_percentage=ranking_data.get("topPercentage", 0),
            badge_name=badge_name,
        )

        return ranking, records

    def _parse_activity(self, data: dict[str, Any]) -> ActivityData:
        """Parse activity/calendar data from the API response.

        Args:
            data: Raw calendar API response.

        Returns:
            An ActivityData object with computed streaks and monthly activity.
        """
        matched = data.get("matchedUser", {})
        cal_data = matched.get("userCalendar", {})

        # Parse the submission calendar JSON string
        calendar_str = cal_data.get("submissionCalendar", "{}")
        try:
            if isinstance(calendar_str, str):
                calendar = json.loads(calendar_str)
            else:
                calendar = calendar_str or {}
        except json.JSONDecodeError:
            calendar = {}

        computed_longest = calculate_longest_streak(calendar)
        monthly = calculate_monthly_activity(calendar)

        return ActivityData(
            longest_streak=max(cal_data.get("streak", 0), computed_longest),
            total_active_days=cal_data.get("totalActiveDays", 0),
            submission_calendar=calendar,
            active_years=cal_data.get("activeYears", []),
            monthly_activity=monthly,
        )

    def _parse_badges(
        self, data: dict[str, Any]
    ) -> tuple[list[Badge], list[UpcomingBadge]]:
        """Parse badges from the API response.

        Args:
            data: Raw badges API response.

        Returns:
            Tuple of (earned badges list, upcoming badges list).
        """
        matched = data.get("matchedUser", {})
        badge_list = matched.get("badges", [])
        upcoming_list = matched.get("upcomingBadges", [])

        badges: list[Badge] = []
        for item in badge_list:
            badges.append(
                Badge(
                    id=str(item.get("id", "")),
                    name=item.get("name", ""),
                    display_name=item.get("displayName", "") or item.get("name", ""),
                    icon_url=item.get("icon", ""),
                    category=item.get("category", ""),
                    creation_date=item.get("creationDate", ""),
                    hover_text=item.get("hoverText", ""),
                )
            )

        upcoming: list[UpcomingBadge] = []
        for item in upcoming_list:
            upcoming.append(
                UpcomingBadge(
                    name=item.get("name", ""),
                    icon_url=item.get("icon", ""),
                    progress=item.get("progress", 0),
                )
            )

        return badges, upcoming

    async def _fetch_avatar(self, url: str) -> str | None:
        """Fetch a user's avatar image and encode it as base64.

        Args:
            url: The avatar image URL.

        Returns:
            Base64-encoded image data string, or None if fetch fails.
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    content_type = response.headers.get("content-type", "image/png")
                    b64 = base64.b64encode(response.content).decode("utf-8")
                    return f"data:{content_type};base64,{b64}"
        except Exception as e:
            logger.warning("Failed to fetch avatar: %s", e)

        return None
