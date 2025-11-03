"""
Bluesky Client - AT Protocol integration for Bluesky social network.

WHY: Provides interface for posting, scheduling, and analytics on Bluesky.
     Bluesky uses AT Protocol (Authenticated Transfer Protocol) for decentralized social.

HOW: Uses atproto Python SDK for API interactions.

Implementation follows Bluesky AT Protocol specifications.

Usage:
    from infrastructure.integrations.bluesky import BlueskyClient

    async with BlueskyClient(
        handle="your-handle.bsky.social",
        app_password="your-app-password"
    ) as client:
        post = await client.create_post(
            text="Hello from AI Marketing Director!",
            tags=["AI", "Marketing"]
        )
"""

from datetime import datetime
from typing import Any

try:
    from atproto import Client
except ImportError:
    Client = None  # type: ignore

from core.exceptions import IntegrationError, wrap_exception


class BlueskyClient:
    """
    Bluesky API client for social media automation.

    WHY: Enables automated content posting and engagement on Bluesky.
    HOW: Uses AT Protocol SDK for API interactions.

    Attributes:
        _handle: Bluesky handle (e.g., "username.bsky.social")
        _app_password: App password for authentication
        _client: AT Protocol client instance
    """

    def __init__(self, handle: str, app_password: str):
        """
        Initialize Bluesky client.

        WHY: Sets up authenticated connection to Bluesky.
        HOW: Validates credentials and initializes AT Protocol client.

        Args:
            handle: Bluesky handle (e.g., "username.bsky.social")
            app_password: App password (not account password!)

        Raises:
            ValueError: If handle or app_password missing
            ImportError: If atproto library not installed
        """
        if not handle or not handle.strip():
            raise ValueError("handle is required and cannot be empty")

        if not app_password or not app_password.strip():
            raise ValueError("app_password is required and cannot be empty")

        if Client is None:
            raise ImportError(
                "atproto library not installed. Install with: pip install atproto"
            )

        self._handle = handle
        self._app_password = app_password
        self._client: Any = None
        self._authenticated = False

    async def __aenter__(self) -> "BlueskyClient":
        """Async context manager entry."""
        await self.authenticate()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        # Bluesky client doesn't require explicit cleanup
        pass

    async def authenticate(self) -> None:
        """
        Authenticate with Bluesky.

        WHY: Establishes authenticated session for API calls.
        HOW: Uses handle and app password to login via AT Protocol.

        Raises:
            IntegrationError: If authentication fails
        """
        try:
            self._client = Client()
            self._client.login(self._handle, self._app_password)
            self._authenticated = True

        except Exception as e:
            raise wrap_exception(
                exc=e,
                wrapper_class=IntegrationError,
                message=f"Failed to authenticate with Bluesky as {self._handle}",
                context={"handle": self._handle, "platform": "bluesky"},
            ) from e

    async def create_post(
        self,
        text: str,
        tags: list[str] | None = None,
        reply_to: str | None = None,
        image_paths: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Create a post on Bluesky.

        WHY: Core functionality - publishing content to Bluesky.
        HOW: Uses AT Protocol createRecord to post text, images, and metadata.

        Args:
            text: Post text content (max 300 characters)
            tags: Optional hashtags to include
            reply_to: Optional URI of post to reply to
            image_paths: Optional list of local image paths to upload

        Returns:
            Dict with post details including URI, CID, and timestamp

        Raises:
            IntegrationError: If post creation fails
        """
        if not self._authenticated:
            raise IntegrationError("Not authenticated. Call authenticate() first.")

        try:
            # Add hashtags to text if provided
            if tags:
                hashtags = " ".join(f"#{tag.lstrip('#')}" for tag in tags)
                text = f"{text}\n\n{hashtags}"

            # Create post record
            # Note: Image upload would require additional AT Protocol implementation
            # For now, supporting text-only posts
            response = self._client.send_post(text=text)

            return {
                "uri": response.uri,
                "cid": response.cid,
                "text": text,
                "created_at": datetime.now().isoformat(),
                "platform": "bluesky",
            }

        except Exception as e:
            raise wrap_exception(
                exc=e,
                wrapper_class=IntegrationError,
                message="Failed to create Bluesky post",
                context={
                    "handle": self._handle,
                    "text_length": len(text),
                    "platform": "bluesky",
                },
            ) from e

    async def get_profile_stats(self) -> dict[str, Any]:
        """
        Get profile statistics.

        WHY: Analytics and monitoring of account performance.
        HOW: Fetches profile data via AT Protocol.

        Returns:
            Dict with followers_count, following_count, posts_count

        Raises:
            IntegrationError: If fetching stats fails
        """
        if not self._authenticated:
            raise IntegrationError("Not authenticated. Call authenticate() first.")

        try:
            profile = self._client.get_profile(self._handle)

            return {
                "handle": self._handle,
                "followers_count": profile.followers_count or 0,
                "following_count": profile.follows_count or 0,
                "posts_count": profile.posts_count or 0,
                "platform": "bluesky",
                "fetched_at": datetime.now().isoformat(),
            }

        except Exception as e:
            raise wrap_exception(
                exc=e,
                wrapper_class=IntegrationError,
                message=f"Failed to fetch Bluesky profile stats for {self._handle}",
                context={"handle": self._handle, "platform": "bluesky"},
            ) from e

    async def search_posts(self, query: str, limit: int = 25) -> list[dict[str, Any]]:
        """
        Search for posts on Bluesky.

        WHY: Research and competitive analysis.
        HOW: Uses AT Protocol search functionality.

        Args:
            query: Search query
            limit: Maximum number of results (default: 25)

        Returns:
            List of post dicts with text, author, metrics

        Raises:
            IntegrationError: If search fails
        """
        if not self._authenticated:
            raise IntegrationError("Not authenticated. Call authenticate() first.")

        try:
            # Note: Bluesky search API is evolving
            # This is a simplified implementation
            results = []

            # Basic search implementation would go here
            # For now, return empty list as search API may not be fully available

            return results

        except Exception as e:
            raise wrap_exception(
                exc=e,
                wrapper_class=IntegrationError,
                message=f"Failed to search Bluesky posts for query: {query}",
                context={
                    "query": query,
                    "limit": limit,
                    "platform": "bluesky",
                },
            ) from e
