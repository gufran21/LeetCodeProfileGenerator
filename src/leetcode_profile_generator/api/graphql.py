"""Async GraphQL client for LeetCode's undocumented API.

Uses httpx for async HTTP with retry logic, error handling, and rate limit detection.
All public data is fetched without authentication.
"""

from __future__ import annotations

import asyncio
import logging
import random
from typing import Any

import httpx

from .queries import (
    QUERY_BADGES,
    QUERY_CALENDAR,
    QUERY_CONTEST_INFO,
    QUERY_RECENT_SUBMISSIONS,
    QUERY_USER_PROFILE,
)

logger = logging.getLogger(__name__)

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"

# Default headers to mimic a browser request
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com",
    "Origin": "https://leetcode.com",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
}


class APIError(Exception):
    """Base exception for LeetCode API errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class UserNotFoundError(APIError):
    """Raised when the requested LeetCode username does not exist."""

    def __init__(self, username: str) -> None:
        super().__init__(f"LeetCode user '{username}' not found")
        self.username = username


class RateLimitError(APIError):
    """Raised when LeetCode rate-limits the request."""

    def __init__(self) -> None:
        super().__init__("Rate limited by LeetCode. Please wait and try again.", 429)


class LeetCodeClient:
    """Async client for fetching public LeetCode data via GraphQL.

    Usage:
        async with LeetCodeClient() as client:
            profile = await client.get_profile("username")
    """

    def __init__(
        self,
        timeout: float = 15.0,
        max_retries: int = 3,
    ) -> None:
        """Initialize the LeetCode client.

        Args:
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts for transient failures.
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> LeetCodeClient:
        """Enter the async context manager."""
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            headers=DEFAULT_HEADERS,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit the async context manager."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client, creating one if needed."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers=DEFAULT_HEADERS,
                follow_redirects=True,
            )
        return self._client

    async def _execute(
        self,
        query: str,
        variables: dict[str, Any],
        operation_name: str | None = None,
    ) -> dict[str, Any]:
        """Execute a GraphQL query with retry logic.

        Args:
            query: The GraphQL query string.
            variables: Query variables.
            operation_name: Optional GraphQL operation name.

        Returns:
            The 'data' field from the GraphQL response.

        Raises:
            UserNotFoundError: If the user doesn't exist.
            RateLimitError: If rate-limited by LeetCode.
            APIError: For other API errors.
        """
        payload: dict[str, Any] = {
            "query": query,
            "variables": variables,
        }
        if operation_name:
            payload["operationName"] = operation_name

        last_error: Exception | None = None

        for attempt in range(self.max_retries):
            try:
                response = await self.client.post(
                    LEETCODE_GRAPHQL_URL,
                    json=payload,
                )

                if response.status_code == 429:
                    raise RateLimitError()

                if response.status_code == 403:
                    raise RateLimitError()

                if response.status_code != 200:
                    raise APIError(
                        f"HTTP {response.status_code}: {response.text[:200]}",
                        response.status_code,
                    )

                data = response.json()

                # Check for GraphQL errors
                if "errors" in data:
                    errors = data["errors"]
                    error_msg = (
                        errors[0].get("message", "Unknown GraphQL error")
                        if errors else "Unknown"
                    )
                    logger.warning("GraphQL error: %s", error_msg)

                    # Check if it's a "user not found" error
                    if "not exist" in error_msg.lower() or "not found" in error_msg.lower():
                        username = variables.get("username", "unknown")
                        raise UserNotFoundError(username)

                    raise APIError(f"GraphQL error: {error_msg}")

                res = data.get("data")
                return res if isinstance(res, dict) else {}

            except (RateLimitError, UserNotFoundError):
                # Don't retry these
                raise

            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    # Exponential backoff with jitter
                    wait = (2**attempt) + random.uniform(0, 1)
                    logger.warning(
                        "Request failed (attempt %d/%d), retrying in %.1fs: %s",
                        attempt + 1,
                        self.max_retries,
                        wait,
                        str(e),
                    )
                    await asyncio.sleep(wait)

            except APIError:
                raise

            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait = (2**attempt) + random.uniform(0, 1)
                    logger.warning(
                        "Unexpected error (attempt %d/%d), retrying in %.1fs: %s",
                        attempt + 1,
                        self.max_retries,
                        wait,
                        str(e),
                    )
                    await asyncio.sleep(wait)

        raise APIError(f"Failed after {self.max_retries} attempts: {last_error}")

    async def get_profile(self, username: str) -> dict[str, Any]:
        """Fetch user profile info and solved statistics.

        Args:
            username: LeetCode username.

        Returns:
            Raw API response data containing matchedUser and allQuestionsCount.

        Raises:
            UserNotFoundError: If the username doesn't exist.
        """
        data = await self._execute(
            QUERY_USER_PROFILE,
            {"username": username},
            "getUserProfile",
        )

        # Validate that the user exists
        if not data.get("matchedUser"):
            raise UserNotFoundError(username)

        return data

    async def get_contest_info(self, username: str) -> dict[str, Any]:
        """Fetch contest ranking and history.

        Args:
            username: LeetCode username.

        Returns:
            Raw API response with userContestRanking and userContestRankingHistory.
            Returns empty dicts if the user has never competed.
        """
        try:
            data = await self._execute(
                QUERY_CONTEST_INFO,
                {"username": username},
                "getUserContestInfo",
            )
            return data
        except APIError as e:
            # Some users have no contest data — gracefully return empty
            logger.warning("Contest data unavailable for %s: %s", username, e)
            return {}

    async def get_calendar(self, username: str, year: int | None = None) -> dict[str, Any]:
        """Fetch submission calendar and streak data.

        Args:
            username: LeetCode username.
            year: Optional year filter. None fetches all-time data.

        Returns:
            Raw API response with userCalendar data.
        """
        variables: dict[str, Any] = {"username": username}
        if year is not None:
            variables["year"] = year

        data = await self._execute(
            QUERY_CALENDAR,
            variables,
            "userProfileCalendar",
        )
        return data

    async def get_badges(self, username: str) -> dict[str, Any]:
        """Fetch earned badges and upcoming badge progress.

        Args:
            username: LeetCode username.

        Returns:
            Raw API response with badges and upcomingBadges.
        """
        try:
            data = await self._execute(
                QUERY_BADGES,
                {"username": username},
                "userBadges",
            )
            return data
        except APIError as e:
            logger.warning("Badge data unavailable for %s: %s", username, e)
            return {}

    async def get_recent_submissions(
        self, username: str, limit: int = 20
    ) -> dict[str, Any]:
        """Fetch recent accepted submissions.

        Args:
            username: LeetCode username.
            limit: Maximum number of submissions to fetch.

        Returns:
            Raw API response with recentAcSubmissionList.
        """
        data = await self._execute(
            QUERY_RECENT_SUBMISSIONS,
            {"username": username, "limit": limit},
            "recentAcSubmissions",
        )
        return data

    async def fetch_all(self, username: str) -> dict[str, Any]:
        """Fetch all data for a user in parallel.

        Makes concurrent API calls for profile, contests, calendar, and badges
        using asyncio.gather for maximum speed.

        Args:
            username: LeetCode username.

        Returns:
            A dict with keys: 'profile', 'contest', 'calendar', 'badges'.
            Each value is the raw API response from the corresponding method.

        Raises:
            UserNotFoundError: If the username doesn't exist (checked via profile).
        """
        # Run all fetches concurrently
        profile_task = self.get_profile(username)
        contest_task = self.get_contest_info(username)
        calendar_task = self.get_calendar(username)
        badges_task = self.get_badges(username)

        results = await asyncio.gather(
            profile_task,
            contest_task,
            calendar_task,
            badges_task,
            return_exceptions=True,
        )

        profile_data, contest_data, calendar_data, badges_data = results

        # Profile is required — re-raise if it failed
        if isinstance(profile_data, Exception):
            raise profile_data

        # Others can gracefully degrade
        if isinstance(contest_data, Exception):
            logger.warning("Contest fetch failed: %s", contest_data)
            contest_data = {}

        if isinstance(calendar_data, Exception):
            logger.warning("Calendar fetch failed: %s", calendar_data)
            calendar_data = {}

        if isinstance(badges_data, Exception):
            logger.warning("Badges fetch failed: %s", badges_data)
            badges_data = {}

        return {
            "profile": profile_data,
            "contest": contest_data,
            "calendar": calendar_data,
            "badges": badges_data,
        }

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
