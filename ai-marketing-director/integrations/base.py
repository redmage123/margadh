"""Base integration class for all third-party platform integrations"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)


class IntegrationError(Exception):
    """Base exception for integration errors"""
    pass


class AuthenticationError(IntegrationError):
    """Authentication failed"""
    pass


class RateLimitError(IntegrationError):
    """Rate limit exceeded"""
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after or 60


class APIError(IntegrationError):
    """Generic API error"""
    pass


def retry_on_failure(max_retries: int = 3, backoff: int = 2):
    """Decorator to retry failed API calls with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except RateLimitError as e:
                    if attempt == max_retries - 1:
                        raise
                    wait_time = e.retry_after if e.retry_after else (backoff ** attempt)
                    logger.warning(f"Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                    time.sleep(wait_time)
                except APIError as e:
                    if attempt == max_retries - 1:
                        raise
                    wait_time = backoff ** attempt
                    logger.warning(f"API error: {e}. Retrying in {wait_time}s ({attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
            return None
        return wrapper
    return decorator


class BaseIntegration(ABC):
    """
    Base class for all third-party integrations

    Provides common functionality:
    - Authentication handling
    - Rate limiting
    - Error handling
    - Logging
    """

    def __init__(self, api_key: Optional[str] = None, access_token: Optional[str] = None):
        self.api_key = api_key
        self.access_token = access_token
        self.base_url = ""
        self.rate_limit_remaining = None
        self.rate_limit_reset = None

    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the platform

        Returns:
            True if authentication successful, False otherwise
        """
        pass

    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the API connection

        Returns:
            Dict with status and details
        """
        pass

    def _check_rate_limit(self) -> None:
        """Check if rate limit is exceeded"""
        if self.rate_limit_remaining is not None and self.rate_limit_remaining == 0:
            if self.rate_limit_reset:
                wait_time = self.rate_limit_reset - int(time.time())
                if wait_time > 0:
                    raise RateLimitError(
                        f"Rate limit exceeded. Resets in {wait_time}s",
                        retry_after=wait_time
                    )

    def _update_rate_limit(self, response_headers: Dict[str, str]) -> None:
        """Update rate limit info from response headers"""
        # Common header names across platforms
        remaining_headers = ['x-rate-limit-remaining', 'x-ratelimit-remaining']
        reset_headers = ['x-rate-limit-reset', 'x-ratelimit-reset']

        for header in remaining_headers:
            if header in response_headers:
                self.rate_limit_remaining = int(response_headers[header])
                break

        for header in reset_headers:
            if header in response_headers:
                self.rate_limit_reset = int(response_headers[header])
                break

    def _log_api_call(self, method: str, endpoint: str, success: bool, response_time: float) -> None:
        """Log API call details"""
        logger.info(
            f"{self.__class__.__name__} API call: {method} {endpoint} - "
            f"{'SUCCESS' if success else 'FAILED'} ({response_time:.2f}s)"
        )

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get API usage statistics

        Returns:
            Dict with usage information
        """
        return {
            "rate_limit_remaining": self.rate_limit_remaining,
            "rate_limit_reset": datetime.fromtimestamp(self.rate_limit_reset) if self.rate_limit_reset else None,
            "platform": self.__class__.__name__,
        }
