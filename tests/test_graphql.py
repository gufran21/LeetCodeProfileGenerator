"""Tests for the GraphQL client — uses mocked HTTP responses."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from leetcode_profile_generator.api.graphql import LeetCodeClient, RateLimitError, UserNotFoundError


class TestLeetCodeClient:
    @pytest.mark.asyncio
    async def test_get_profile_success(self, profile_response):
        """Test successful profile fetch."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": profile_response}

        with patch("leetcode_profile_generator.api.graphql.httpx.AsyncClient") as _mock_client:
            client = LeetCodeClient()
            client._client = MagicMock()
            client._client.post = AsyncMock(return_value=mock_response)

            result = await client.get_profile("TestUser")
            assert result["matchedUser"]["username"] == "TestUser"

    @pytest.mark.asyncio
    async def test_user_not_found(self):
        """Test that UserNotFoundError is raised for non-existent users."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"matchedUser": None, "allQuestionsCount": []}}

        client = LeetCodeClient()
        client._client = MagicMock()
        client._client.post = AsyncMock(return_value=mock_response)

        with pytest.raises(UserNotFoundError):
            await client.get_profile("nonexistent_user_xyz")

    @pytest.mark.asyncio
    async def test_rate_limit(self):
        """Test that RateLimitError is raised on 429 response."""
        mock_response = MagicMock()
        mock_response.status_code = 429

        client = LeetCodeClient()
        client._client = MagicMock()
        client._client.post = AsyncMock(return_value=mock_response)

        with pytest.raises(RateLimitError):
            await client.get_profile("TestUser")

    @pytest.mark.asyncio
    async def test_contest_graceful_failure(self):
        """Test that contest fetch returns empty dict on error."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"errors": [{"message": "Internal error"}]}

        client = LeetCodeClient()
        client._client = MagicMock()
        client._client.post = AsyncMock(return_value=mock_response)

        result = await client.get_contest_info("TestUser")
        assert result == {}

    @pytest.mark.asyncio
    async def test_badges_graceful_failure(self):
        """Test that badges fetch returns empty dict on error."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"errors": [{"message": "Internal error"}]}

        client = LeetCodeClient()
        client._client = MagicMock()
        client._client.post = AsyncMock(return_value=mock_response)

        result = await client.get_badges("TestUser")
        assert result == {}
