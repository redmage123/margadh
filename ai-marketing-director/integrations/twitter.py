"""Twitter/X API integration for social media posting"""
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
import time

from .base import BaseIntegration, retry_on_failure, AuthenticationError, APIError, RateLimitError


class TwitterIntegration(BaseIntegration):
    """
    Twitter API v2 integration

    Capabilities:
    - Post tweets
    - Create tweet threads
    - Get tweet analytics
    - Search mentions

    API Documentation: https://developer.twitter.com/en/docs/twitter-api
    """

    def __init__(self, bearer_token: str):
        """
        Initialize Twitter integration

        Args:
            bearer_token: Twitter API v2 Bearer Token
        """
        super().__init__(access_token=bearer_token)
        self.base_url = "https://api.twitter.com/2"

    def authenticate(self) -> bool:
        """Verify authentication"""
        try:
            response = requests.get(
                f"{self.base_url}/users/me",
                headers=self._get_headers()
            )

            if response.status_code == 401:
                raise AuthenticationError("Invalid or expired bearer token")

            response.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Authentication failed: {e}")

    def test_connection(self) -> Dict[str, Any]:
        """Test API connection"""
        try:
            response = requests.get(
                f"{self.base_url}/users/me",
                headers=self._get_headers(),
                params={"user.fields": "username,name,public_metrics"}
            )
            response.raise_for_status()
            user_data = response.json().get("data", {})

            return {
                "status": "connected",
                "platform": "Twitter",
                "user_id": user_data.get("id"),
                "username": user_data.get("username"),
                "name": user_data.get("name"),
                "followers": user_data.get("public_metrics", {}).get("followers_count", 0),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "status": "failed",
                "platform": "Twitter",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    @retry_on_failure(max_retries=3)
    def create_tweet(
        self,
        text: str,
        reply_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Post a tweet

        Args:
            text: Tweet text (max 280 characters)
            reply_to: Optional tweet ID to reply to

        Returns:
            Dict with tweet ID and metadata
        """
        start_time = time.time()
        self._check_rate_limit()

        # Prepare tweet data
        tweet_data = {"text": text}
        if reply_to:
            tweet_data["reply"] = {"in_reply_to_tweet_id": reply_to}

        try:
            response = requests.post(
                f"{self.base_url}/tweets",
                headers=self._get_headers(),
                json=tweet_data
            )

            self._update_rate_limit(response.headers)

            if response.status_code == 429:
                retry_after = int(response.headers.get('x-rate-limit-reset', time.time() + 60)) - int(time.time())
                raise RateLimitError("Twitter rate limit exceeded", retry_after=retry_after)

            response.raise_for_status()

            tweet_response = response.json().get("data", {})
            response_time = time.time() - start_time

            self._log_api_call("POST", "/tweets", True, response_time)

            tweet_id = tweet_response.get("id")
            return {
                "id": tweet_id,
                "platform": "twitter",
                "text": text,
                "created_at": datetime.now().isoformat(),
                "url": f"https://twitter.com/i/web/status/{tweet_id}"
            }

        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            self._log_api_call("POST", "/tweets", False, response_time)
            raise APIError(f"Failed to create tweet: {e}")

    @retry_on_failure(max_retries=2)
    def create_thread(self, tweets: List[str]) -> List[Dict[str, Any]]:
        """
        Create a thread of tweets

        Args:
            tweets: List of tweet texts (each max 280 chars)

        Returns:
            List of tweet response dicts
        """
        thread_results = []
        previous_tweet_id = None

        for i, tweet_text in enumerate(tweets):
            try:
                tweet = self.create_tweet(
                    text=tweet_text,
                    reply_to=previous_tweet_id
                )
                thread_results.append(tweet)
                previous_tweet_id = tweet["id"]

                # Wait between tweets to avoid rate limits
                if i < len(tweets) - 1:
                    time.sleep(2)

            except Exception as e:
                thread_results.append({
                    "error": str(e),
                    "text": tweet_text,
                    "position": i
                })
                break

        return thread_results

    @retry_on_failure(max_retries=2)
    def get_tweet_metrics(self, tweet_id: str) -> Dict[str, Any]:
        """
        Get metrics for a tweet

        Args:
            tweet_id: Twitter tweet ID

        Returns:
            Dict with engagement metrics
        """
        start_time = time.time()

        try:
            response = requests.get(
                f"{self.base_url}/tweets/{tweet_id}",
                headers=self._get_headers(),
                params={
                    "tweet.fields": "public_metrics,created_at",
                    "expansions": "author_id"
                }
            )

            self._update_rate_limit(response.headers)
            response.raise_for_status()

            tweet_data = response.json().get("data", {})
            metrics = tweet_data.get("public_metrics", {})
            response_time = time.time() - start_time

            self._log_api_call("GET", f"/tweets/{tweet_id}", True, response_time)

            return {
                "tweet_id": tweet_id,
                "likes": metrics.get("like_count", 0),
                "retweets": metrics.get("retweet_count", 0),
                "replies": metrics.get("reply_count", 0),
                "quotes": metrics.get("quote_count", 0),
                "impressions": metrics.get("impression_count", 0),
                "engagement_rate": self._calculate_engagement_rate(metrics),
                "created_at": tweet_data.get("created_at"),
                "fetched_at": datetime.now().isoformat()
            }

        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            self._log_api_call("GET", f"/tweets/{tweet_id}", False, response_time)
            raise APIError(f"Failed to fetch tweet metrics: {e}")

    def search_mentions(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for mentions or tweets matching a query

        Args:
            query: Search query (e.g., "@AIElevate" or "#AI")
            max_results: Max tweets to return (default 10, max 100)

        Returns:
            List of tweet dicts
        """
        try:
            response = requests.get(
                f"{self.base_url}/tweets/search/recent",
                headers=self._get_headers(),
                params={
                    "query": query,
                    "max_results": min(max_results, 100),
                    "tweet.fields": "created_at,public_metrics,author_id"
                }
            )

            self._update_rate_limit(response.headers)
            response.raise_for_status()

            tweets = response.json().get("data", [])

            return [
                {
                    "id": tweet.get("id"),
                    "text": tweet.get("text"),
                    "author_id": tweet.get("author_id"),
                    "created_at": tweet.get("created_at"),
                    "metrics": tweet.get("public_metrics", {})
                }
                for tweet in tweets
            ]

        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to search mentions: {e}")

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def _calculate_engagement_rate(self, metrics: Dict[str, int]) -> float:
        """Calculate engagement rate"""
        impressions = metrics.get("impression_count", 0)
        if impressions == 0:
            return 0.0

        engagements = (
            metrics.get("like_count", 0) +
            metrics.get("retweet_count", 0) +
            metrics.get("reply_count", 0) +
            metrics.get("quote_count", 0)
        )

        return round((engagements / impressions) * 100, 2)


# Example usage
if __name__ == "__main__":
    import os

    twitter = TwitterIntegration(bearer_token=os.getenv("TWITTER_BEARER_TOKEN"))

    # Test connection
    status = twitter.test_connection()
    print(f"Connection status: {status}")

    # Post a tweet
    tweet = twitter.create_tweet(
        text="Excited to share our new AI training insights! 🚀 #AI #MachineLearning"
    )
    print(f"Created tweet: {tweet}")

    # Create a thread
    thread = twitter.create_thread([
        "1/ Why 80% of AI implementations fail (and how to be in the 20%) 🧵",
        "2/ Generic prompts lead to generic results. The key is structured frameworks like A-C-E and ReAct.",
        "3/ Learn more about prompt engineering best practices at ai-elevate.ai"
    ])
    print(f"Created thread: {thread}")
