"""LinkedIn API integration for social media posting and analytics"""
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
import time

from .base import BaseIntegration, retry_on_failure, AuthenticationError, APIError, RateLimitError


class LinkedInIntegration(BaseIntegration):
    """
    LinkedIn Marketing API integration

    Capabilities:
    - Create and publish posts
    - Schedule posts
    - Get post analytics (likes, comments, shares, impressions)
    - Fetch company page statistics

    API Documentation: https://docs.microsoft.com/en-us/linkedin/marketing/
    """

    def __init__(self, access_token: str, organization_id: Optional[str] = None):
        """
        Initialize LinkedIn integration

        Args:
            access_token: OAuth 2.0 access token
            organization_id: LinkedIn organization/company page ID (optional)
        """
        super().__init__(access_token=access_token)
        self.base_url = "https://api.linkedin.com/v2"
        self.organization_id = organization_id

    def authenticate(self) -> bool:
        """
        Verify authentication by making a test API call

        Returns:
            True if authenticated successfully
        """
        try:
            response = requests.get(
                f"{self.base_url}/me",
                headers=self._get_headers()
            )

            if response.status_code == 401:
                raise AuthenticationError("Invalid or expired access token")

            response.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Authentication failed: {e}")

    def test_connection(self) -> Dict[str, Any]:
        """
        Test API connection and return user/organization info

        Returns:
            Dict with connection status and profile information
        """
        try:
            # Get user profile
            response = requests.get(
                f"{self.base_url}/me",
                headers=self._get_headers()
            )
            response.raise_for_status()
            profile = response.json()

            return {
                "status": "connected",
                "platform": "LinkedIn",
                "user_id": profile.get("id"),
                "organization_id": self.organization_id,
                "rate_limit": self.get_usage_stats(),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "status": "failed",
                "platform": "LinkedIn",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    @retry_on_failure(max_retries=3)
    def create_post(
        self,
        text: str,
        visibility: str = "PUBLIC",
        media_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create and publish a LinkedIn post

        Args:
            text: Post content (max 3000 characters)
            visibility: "PUBLIC" or "CONNECTIONS"
            media_urls: Optional list of image URLs

        Returns:
            Dict with post ID and metadata

        Raises:
            APIError: If post creation fails
        """
        start_time = time.time()

        # Check rate limits before making request
        self._check_rate_limit()

        # Prepare post data
        post_data = {
            "author": f"urn:li:person:{self.organization_id}" if self.organization_id else "urn:li:person:me",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"  # or "IMAGE" if media provided
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/ugcPosts",
                headers=self._get_headers(),
                json=post_data
            )

            # Update rate limit info
            self._update_rate_limit(response.headers)

            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                raise RateLimitError("LinkedIn rate limit exceeded", retry_after=retry_after)

            response.raise_for_status()

            post_response = response.json()
            response_time = time.time() - start_time

            self._log_api_call("POST", "/ugcPosts", True, response_time)

            return {
                "id": post_response.get("id"),
                "platform": "linkedin",
                "text": text,
                "visibility": visibility,
                "created_at": datetime.now().isoformat(),
                "url": f"https://www.linkedin.com/feed/update/{post_response.get('id')}"
            }

        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            self._log_api_call("POST", "/ugcPosts", False, response_time)
            raise APIError(f"Failed to create LinkedIn post: {e}")

    @retry_on_failure(max_retries=2)
    def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        """
        Get engagement analytics for a post

        Args:
            post_id: LinkedIn post URN or ID

        Returns:
            Dict with engagement metrics (likes, comments, shares, impressions)
        """
        start_time = time.time()

        try:
            # LinkedIn Analytics API endpoint
            response = requests.get(
                f"{self.base_url}/organizationalEntityShareStatistics",
                headers=self._get_headers(),
                params={
                    "q": "organizationalEntity",
                    "organizationalEntity": f"urn:li:organization:{self.organization_id}",
                    "ugcPosts": post_id
                }
            )

            self._update_rate_limit(response.headers)
            response.raise_for_status()

            stats = response.json()
            response_time = time.time() - start_time

            self._log_api_call("GET", "/organizationalEntityShareStatistics", True, response_time)

            # Extract metrics
            elements = stats.get("elements", [])
            if elements:
                metrics = elements[0].get("totalShareStatistics", {})
                return {
                    "post_id": post_id,
                    "likes": metrics.get("likeCount", 0),
                    "comments": metrics.get("commentCount", 0),
                    "shares": metrics.get("shareCount", 0),
                    "clicks": metrics.get("clickCount", 0),
                    "impressions": metrics.get("impressionCount", 0),
                    "engagement_rate": self._calculate_engagement_rate(metrics),
                    "fetched_at": datetime.now().isoformat()
                }

            return {
                "post_id": post_id,
                "error": "No analytics data available",
                "fetched_at": datetime.now().isoformat()
            }

        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            self._log_api_call("GET", "/organizationalEntityShareStatistics", False, response_time)
            raise APIError(f"Failed to fetch LinkedIn analytics: {e}")

    def schedule_post(
        self,
        text: str,
        publish_time: datetime,
        visibility: str = "PUBLIC"
    ) -> Dict[str, Any]:
        """
        Schedule a post for future publication

        Note: LinkedIn doesn't have native scheduling via API.
        This stores the post for later publication by the system scheduler.

        Args:
            text: Post content
            publish_time: When to publish
            visibility: Post visibility

        Returns:
            Dict with scheduled post information
        """
        # This would integrate with your internal scheduling system
        # For now, return a placeholder
        return {
            "id": f"scheduled_{int(time.time())}",
            "platform": "linkedin",
            "text": text,
            "visibility": visibility,
            "scheduled_for": publish_time.isoformat(),
            "status": "scheduled",
            "created_at": datetime.now().isoformat()
        }

    def get_company_statistics(self) -> Dict[str, Any]:
        """
        Get organization/company page statistics

        Returns:
            Dict with follower count, recent activity, etc.
        """
        if not self.organization_id:
            raise ValueError("Organization ID required for company statistics")

        try:
            response = requests.get(
                f"{self.base_url}/organizations/{self.organization_id}",
                headers=self._get_headers()
            )

            self._update_rate_limit(response.headers)
            response.raise_for_status()

            org_data = response.json()

            return {
                "name": org_data.get("localizedName"),
                "followers": org_data.get("followersCount", 0),
                "organization_id": self.organization_id,
                "fetched_at": datetime.now().isoformat()
            }

        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to fetch company statistics: {e}")

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }

    def _calculate_engagement_rate(self, metrics: Dict[str, int]) -> float:
        """Calculate engagement rate from metrics"""
        impressions = metrics.get("impressionCount", 0)
        if impressions == 0:
            return 0.0

        engagements = (
            metrics.get("likeCount", 0) +
            metrics.get("commentCount", 0) +
            metrics.get("shareCount", 0)
        )

        return round((engagements / impressions) * 100, 2)


# Example usage
if __name__ == "__main__":
    import os

    # Initialize with access token
    linkedin = LinkedInIntegration(
        access_token=os.getenv("LINKEDIN_ACCESS_TOKEN"),
        organization_id=os.getenv("LINKEDIN_ORG_ID")
    )

    # Test connection
    status = linkedin.test_connection()
    print(f"Connection status: {status}")

    # Create a post
    post = linkedin.create_post(
        text="Excited to announce our new AI training program! 🚀 #AI #Training",
        visibility="PUBLIC"
    )
    print(f"Created post: {post}")

    # Get analytics (after some time)
    analytics = linkedin.get_post_analytics(post["id"])
    print(f"Post analytics: {analytics}")
