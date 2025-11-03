"""
Unit tests for Twitter Client.

WHY: Ensures Twitter client correctly handles Twitter API operations.
HOW: Uses mocked Twitter API to test client behavior without real API calls.

Following TDD methodology (RED-GREEN-REFACTOR):
- Write tests FIRST (these tests will fail initially)
- Implement client to make tests pass
- Refactor while keeping tests green
"""

import sys
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from core.exceptions import IntegrationError


# Mock tweepy module at import level to avoid ImportError
@pytest.fixture(autouse=True)
def mock_tweepy():
    """Mock tweepy module for all tests."""
    mock_tweepy_module = Mock()
    mock_tweepy_module.Client = Mock
    with patch.dict("sys.modules", {"tweepy": mock_tweepy_module}):
        yield mock_tweepy_module


class TestTwitterClient:
    """Test suite for Twitter Client."""

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test that Twitter client initializes correctly."""
        from infrastructure.integrations.twitter import TwitterClient

        client = TwitterClient(
            api_key="test_key",
            api_secret="test_secret",
            access_token="test_token",
            access_token_secret="test_token_secret",
        )

        assert client is not None

    @pytest.mark.asyncio
    async def test_client_initialization_missing_credentials(self):
        """Test that client raises error when credentials missing."""
        from infrastructure.integrations.twitter import TwitterClient

        with pytest.raises(ValueError, match="api_key is required"):
            TwitterClient(
                api_key="",
                api_secret="test_secret",
                access_token="test_token",
                access_token_secret="test_token_secret",
            )

    @pytest.mark.asyncio
    async def test_create_tweet(self):
        """Test creating a tweet."""
        from infrastructure.integrations.twitter import TwitterClient

        # Create client with mocked Twitter API
        client = TwitterClient(
            api_key="test_key",
            api_secret="test_secret",
            access_token="test_token",
            access_token_secret="test_token_secret",
        )

        # Mock the Twitter API client
        mock_twitter_api = Mock()
        # Create mock response object with .data attribute
        mock_response = Mock()
        mock_response.data = {"id": "123456789", "text": "Test tweet"}
        mock_twitter_api.create_tweet = Mock(return_value=mock_response)

        # Set mocked client and mark as authenticated
        client._client = mock_twitter_api
        client._authenticated = True

        tweet = await client.create_tweet(text="Test tweet")

        assert tweet is not None
        assert "id" in tweet
        assert tweet["id"] == "123456789"
        assert tweet["text"] == "Test tweet"

        mock_twitter_api.create_tweet.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_tweet_with_media(self):
        """Test creating a tweet with media."""
        from infrastructure.integrations.twitter import TwitterClient

        client = TwitterClient(
            api_key="test_key",
            api_secret="test_secret",
            access_token="test_token",
            access_token_secret="test_token_secret",
        )

        mock_twitter_api = Mock()
        mock_response = Mock()
        mock_response.data = {"id": "123456789", "text": "Test tweet with image"}
        mock_twitter_api.create_tweet = Mock(return_value=mock_response)

        # Set mocked client and mark as authenticated
        client._client = mock_twitter_api
        client._authenticated = True

        tweet = await client.create_tweet(
            text="Test tweet with image",
            media_urls=["https://example.com/image.jpg"],
        )

        assert tweet is not None
        assert tweet["id"] == "123456789"

    @pytest.mark.asyncio
    async def test_create_thread(self):
        """Test creating a Twitter thread."""
        from infrastructure.integrations.twitter import TwitterClient

        client = TwitterClient(
            api_key="test_key",
            api_secret="test_secret",
            access_token="test_token",
            access_token_secret="test_token_secret",
        )

        mock_twitter_api = Mock()
        # Mock multiple tweet creation calls
        mock_response_1 = Mock()
        mock_response_1.data = {"id": "111", "text": "First tweet"}
        mock_response_2 = Mock()
        mock_response_2.data = {"id": "222", "text": "Second tweet"}
        mock_response_3 = Mock()
        mock_response_3.data = {"id": "333", "text": "Third tweet"}

        mock_twitter_api.create_tweet = Mock(
            side_effect=[mock_response_1, mock_response_2, mock_response_3]
        )

        # Set mocked client and mark as authenticated
        client._client = mock_twitter_api
        client._authenticated = True

        thread = await client.create_thread(
            tweets=["First tweet", "Second tweet", "Third tweet"]
        )

        assert thread is not None
        assert "tweet_ids" in thread
        assert len(thread["tweet_ids"]) == 3
        assert thread["tweet_ids"] == ["111", "222", "333"]

        # Should have called create_tweet 3 times
        assert mock_twitter_api.create_tweet.call_count == 3

    @pytest.mark.asyncio
    async def test_get_profile_stats(self):
        """Test getting Twitter profile statistics."""
        from infrastructure.integrations.twitter import TwitterClient

        client = TwitterClient(
            api_key="test_key",
            api_secret="test_secret",
            access_token="test_token",
            access_token_secret="test_token_secret",
        )

        mock_twitter_api = Mock()
        mock_response = Mock()
        mock_response.data = {
            "id": "123456",
            "username": "testuser",
            "public_metrics": {
                "followers_count": 1000,
                "following_count": 500,
                "tweet_count": 250,
                "listed_count": 10,
            },
        }
        mock_twitter_api.get_me = Mock(return_value=mock_response)

        # Set mocked client and mark as authenticated
        client._client = mock_twitter_api
        client._authenticated = True

        stats = await client.get_profile_stats()

        assert stats is not None
        assert "followers_count" in stats
        assert stats["followers_count"] == 1000
        assert stats["following_count"] == 500
        assert stats["tweet_count"] == 250
        assert stats["platform"] == "twitter"

    @pytest.mark.asyncio
    async def test_search_tweets(self):
        """Test searching for tweets."""
        from infrastructure.integrations.twitter import TwitterClient

        client = TwitterClient(
            api_key="test_key",
            api_secret="test_secret",
            access_token="test_token",
            access_token_secret="test_token_secret",
        )

        mock_twitter_api = Mock()
        # Create mock tweet objects
        mock_tweet_1 = Mock()
        mock_tweet_1.id = "111"
        mock_tweet_1.text = "Tweet about AI"
        mock_tweet_1.created_at = None

        mock_tweet_2 = Mock()
        mock_tweet_2.id = "222"
        mock_tweet_2.text = "Another AI tweet"
        mock_tweet_2.created_at = None

        mock_response = Mock()
        mock_response.data = [mock_tweet_1, mock_tweet_2]
        mock_twitter_api.search_recent_tweets = Mock(return_value=mock_response)

        # Set mocked client and mark as authenticated
        client._client = mock_twitter_api
        client._authenticated = True

        results = await client.search_tweets(query="AI", limit=10)

        assert results is not None
        assert len(results) == 2
        assert results[0]["id"] == "111"
        assert results[1]["id"] == "222"

    @pytest.mark.asyncio
    async def test_create_tweet_length_validation(self):
        """Test that tweets over 280 characters are rejected."""
        from infrastructure.integrations.twitter import TwitterClient

        client = TwitterClient(
            api_key="test_key",
            api_secret="test_secret",
            access_token="test_token",
            access_token_secret="test_token_secret",
        )

        long_text = "a" * 281  # 281 characters (over limit)

        async with client:
            with pytest.raises(ValueError, match="exceeds 280 character limit"):
                await client.create_tweet(text=long_text)

    @pytest.mark.asyncio
    async def test_exception_wrapping(self):
        """Test that external exceptions are wrapped correctly."""
        from infrastructure.integrations.twitter import TwitterClient

        client = TwitterClient(
            api_key="test_key",
            api_secret="test_secret",
            access_token="test_token",
            access_token_secret="test_token_secret",
        )

        mock_twitter_api = Mock()
        # Simulate API error
        mock_twitter_api.create_tweet = Mock(side_effect=Exception("Twitter API error"))

        # Set mocked client and mark as authenticated
        client._client = mock_twitter_api
        client._authenticated = True

        with pytest.raises(IntegrationError) as exc_info:
            await client.create_tweet(text="Test")

        # Verify exception wrapping
        assert "Twitter API error" in str(exc_info.value.__cause__)
        assert exc_info.value.context is not None
        assert exc_info.value.context["platform"] == "twitter"

    @pytest.mark.asyncio
    async def test_context_manager_support(self):
        """Test that client works as async context manager."""
        from infrastructure.integrations.twitter import TwitterClient

        client = TwitterClient(
            api_key="test_key",
            api_secret="test_secret",
            access_token="test_token",
            access_token_secret="test_token_secret",
        )

        # Should not raise exception
        async with client:
            pass
