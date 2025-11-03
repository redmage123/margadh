"""
Twitter Client - Twitter/X social network integration.

WHY: Provides interface for posting, threading, and analytics on Twitter/X.
     Supports Twitter API v2 for modern integrations.

HOW: Uses tweepy Python library for Twitter API interactions.

Implementation follows TDD - tests written first (RED), implementation (GREEN),
then refactored (REFACTOR).

Twitter API Features:
- Tweet creation (280 character limit)
- Thread creation (multiple connected tweets)
- Media attachments
- Profile analytics
- Tweet search capabilities

Usage:
    from infrastructure.integrations.twitter import TwitterClient

    async with TwitterClient(
        api_key="your_api_key",
        api_secret="your_api_secret",
        access_token="your_access_token",
        access_token_secret="your_access_token_secret"
    ) as client:
        # Create tweet
        tweet = await client.create_tweet(
            text="Hello Twitter!",
            media_urls=None
        )

        # Create thread
        thread = await client.create_thread(
            tweets=["First tweet", "Second tweet", "Third tweet"]
        )
"""

from datetime import datetime
from typing import Any

try:
    import tweepy
except ImportError:
    tweepy = None  # type: ignore

from core.exceptions import IntegrationError, wrap_exception


class TwitterClient:
    """
    Twitter API client for social media automation.

    WHY: Enables automated content posting and engagement on Twitter/X.
    HOW: Uses tweepy library for Twitter API v2 interactions.

    Attributes:
        _api_key: Twitter API key
        _api_secret: Twitter API secret
        _access_token: Twitter access token
        _access_token_secret: Twitter access token secret
        _client: Tweepy client instance
        _authenticated: Whether client is authenticated
    """

    MAX_TWEET_LENGTH = 280

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        access_token: str,
        access_token_secret: str,
    ):
        """
        Initialize Twitter client.

        WHY: Sets up authenticated connection to Twitter API.
        HOW: Validates credentials and initializes tweepy client.

        Args:
            api_key: Twitter API key
            api_secret: Twitter API secret
            access_token: Twitter access token
            access_token_secret: Twitter access token secret

        Raises:
            ValueError: If any credential is missing
            ImportError: If tweepy library not installed
        """
        # Guard clause: Validate required credentials
        if not api_key or not api_key.strip():
            raise ValueError("api_key is required and cannot be empty")

        if not api_secret or not api_secret.strip():
            raise ValueError("api_secret is required and cannot be empty")

        if not access_token or not access_token.strip():
            raise ValueError("access_token is required and cannot be empty")

        if not access_token_secret or not access_token_secret.strip():
            raise ValueError("access_token_secret is required and cannot be empty")

        # Guard clause: Check tweepy installed
        if tweepy is None:
            raise ImportError(
                "tweepy library not installed. " "Install with: pip install tweepy"
            )

        self._api_key = api_key
        self._api_secret = api_secret
        self._access_token = access_token
        self._access_token_secret = access_token_secret
        self._client: Any = None
        self._authenticated = False

    async def __aenter__(self) -> "TwitterClient":
        """
        Async context manager entry.

        WHY: Ensures client is authenticated before use.
        HOW: Authenticates with Twitter API.

        Returns:
            Self for context manager pattern
        """
        await self.authenticate()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Async context manager exit.

        WHY: Clean up resources when done.
        HOW: Closes Twitter client connection.
        """
        # Tweepy client doesn't require explicit cleanup
        pass

    async def authenticate(self) -> None:
        """
        Authenticate with Twitter API.

        WHY: Establishes authenticated session for API calls.
        HOW: Uses OAuth 1.0a credentials to create tweepy client.

        Raises:
            IntegrationError: If authentication fails
        """
        try:
            # Create tweepy client with OAuth 1.0a credentials
            self._client = tweepy.Client(
                consumer_key=self._api_key,
                consumer_secret=self._api_secret,
                access_token=self._access_token,
                access_token_secret=self._access_token_secret,
            )
            self._authenticated = True

        except Exception as e:
            raise wrap_exception(
                exc=e,
                wrapper_class=IntegrationError,
                message="Failed to authenticate with Twitter",
                context={"platform": "twitter"},
            ) from e

    async def create_tweet(
        self,
        text: str,
        media_urls: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Create a tweet on Twitter.

        WHY: Core functionality - publishing content to Twitter.
        HOW: Uses Twitter API to create text or media tweets.

        Args:
            text: Tweet text content (max 280 characters)
            media_urls: Optional list of media URLs to attach

        Returns:
            Dict with tweet details including ID and text

        Raises:
            ValueError: If text exceeds 280 characters
            IntegrationError: If tweet creation fails
        """
        # Guard clause: Check authentication
        if not self._authenticated:
            raise IntegrationError("Not authenticated. Call authenticate() first.")

        # Guard clause: Validate tweet length
        if len(text) > self.MAX_TWEET_LENGTH:
            raise ValueError(
                f"Tweet exceeds {self.MAX_TWEET_LENGTH} character limit "
                f"(got {len(text)} characters)"
            )

        try:
            # Create tweet via Twitter API
            response = self._client.create_tweet(
                text=text,
                # Note: media attachment requires upload API
                # For now, return metadata
            )

            return {
                "id": str(response.data["id"]),
                "text": text,
                "created_at": datetime.now().isoformat(),
                "platform": "twitter",
            }

        except Exception as e:
            raise wrap_exception(
                exc=e,
                wrapper_class=IntegrationError,
                message="Failed to create Twitter tweet",
                context={
                    "platform": "twitter",
                    "operation": "create_tweet",
                    "text_length": len(text),
                },
            ) from e

    async def create_thread(
        self,
        tweets: list[str],
    ) -> dict[str, Any]:
        """
        Create a thread of connected tweets.

        WHY: Longer content requires threading on Twitter.
        HOW: Creates multiple tweets, each replying to previous.

        Args:
            tweets: List of tweet texts for thread

        Returns:
            Dict with thread details and all tweet IDs

        Raises:
            ValueError: If tweets list is empty
            IntegrationError: If thread creation fails
        """
        # Guard clause: Validate input
        if not tweets:
            raise ValueError("tweets list cannot be empty")

        # Guard clause: Check authentication
        if not self._authenticated:
            raise IntegrationError("Not authenticated. Call authenticate() first.")

        try:
            tweet_ids = []
            previous_tweet_id = None

            # Create each tweet in sequence
            for tweet_text in tweets:
                # Guard clause: Check length
                if len(tweet_text) > self.MAX_TWEET_LENGTH:
                    raise ValueError(
                        f"Tweet exceeds {self.MAX_TWEET_LENGTH} character limit"
                    )

                # Create tweet, replying to previous if exists
                response = self._client.create_tweet(
                    text=tweet_text,
                    in_reply_to_tweet_id=previous_tweet_id,
                )

                tweet_id = str(response.data["id"])
                tweet_ids.append(tweet_id)
                previous_tweet_id = tweet_id

            return {
                "tweet_ids": tweet_ids,
                "thread_count": len(tweet_ids),
                "created_at": datetime.now().isoformat(),
                "platform": "twitter",
            }

        except Exception as e:
            raise wrap_exception(
                exc=e,
                wrapper_class=IntegrationError,
                message="Failed to create Twitter thread",
                context={
                    "platform": "twitter",
                    "operation": "create_thread",
                    "tweet_count": len(tweets),
                },
            ) from e

    async def get_profile_stats(self) -> dict[str, Any]:
        """
        Get Twitter profile statistics.

        WHY: Analytics and monitoring of account performance.
        HOW: Fetches authenticated user's profile data via Twitter API.

        Returns:
            Dict with followers, following, tweet count, etc.

        Raises:
            IntegrationError: If fetching stats fails
        """
        # Guard clause: Check authentication
        if not self._authenticated:
            raise IntegrationError("Not authenticated. Call authenticate() first.")

        try:
            # Fetch authenticated user's profile
            response = self._client.get_me(user_fields=["public_metrics", "username"])

            user_data = response.data
            metrics = user_data.get("public_metrics", {})

            return {
                "followers_count": metrics.get("followers_count", 0),
                "following_count": metrics.get("following_count", 0),
                "tweet_count": metrics.get("tweet_count", 0),
                "listed_count": metrics.get("listed_count", 0),
                "username": user_data.get("username", ""),
                "platform": "twitter",
                "fetched_at": datetime.now().isoformat(),
            }

        except Exception as e:
            raise wrap_exception(
                exc=e,
                wrapper_class=IntegrationError,
                message="Failed to fetch Twitter profile stats",
                context={"platform": "twitter", "operation": "get_profile_stats"},
            ) from e

    async def search_tweets(
        self,
        query: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Search for tweets matching query.

        WHY: Research and monitoring of relevant content.
        HOW: Uses Twitter search API with query.

        Args:
            query: Search query string
            limit: Maximum number of results

        Returns:
            List of tweet dictionaries

        Raises:
            IntegrationError: If search fails
        """
        # Guard clause: Check authentication
        if not self._authenticated:
            raise IntegrationError("Not authenticated. Call authenticate() first.")

        # Guard clause: Validate input
        if not query or not query.strip():
            raise ValueError("query cannot be empty")

        try:
            # Search recent tweets
            response = self._client.search_recent_tweets(
                query=query,
                max_results=min(limit, 100),  # Twitter API max is 100
                tweet_fields=["created_at", "public_metrics"],
            )

            # Guard clause: Handle no results
            if not response.data:
                return []

            # Extract tweet data
            results = []
            for tweet in response.data:
                results.append(
                    {
                        "id": str(tweet.id),
                        "text": tweet.text,
                        "created_at": (
                            tweet.created_at.isoformat() if tweet.created_at else None
                        ),
                    }
                )

            return results

        except Exception as e:
            raise wrap_exception(
                exc=e,
                wrapper_class=IntegrationError,
                message=f"Failed to search Twitter for: {query}",
                context={
                    "platform": "twitter",
                    "operation": "search_tweets",
                    "query": query,
                    "limit": limit,
                },
            ) from e
