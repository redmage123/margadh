"""OAuth 2.0 authentication flow handler for social media platforms"""
import secrets
import webbrowser
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlencode, parse_qs, urlparse
import requests
from dataclasses import dataclass
import json
import os


@dataclass
class OAuthConfig:
    """OAuth configuration for a platform"""
    platform: str
    client_id: str
    client_secret: str
    redirect_uri: str
    authorization_url: str
    token_url: str
    scopes: list


class OAuthManager:
    """
    Manages OAuth 2.0 authentication flows for multiple platforms

    Supports:
    - LinkedIn
    - Twitter/X
    - Custom OAuth 2.0 providers
    """

    def __init__(self):
        self.configs = self._load_configs()
        self.state_store = {}  # In production, use Redis or database

    def _load_configs(self) -> Dict[str, OAuthConfig]:
        """Load OAuth configurations from environment"""
        configs = {}

        # LinkedIn configuration
        if os.getenv("LINKEDIN_CLIENT_ID"):
            configs["linkedin"] = OAuthConfig(
                platform="linkedin",
                client_id=os.getenv("LINKEDIN_CLIENT_ID"),
                client_secret=os.getenv("LINKEDIN_CLIENT_SECRET"),
                redirect_uri=os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8888/oauth/linkedin/callback"),
                authorization_url="https://www.linkedin.com/oauth/v2/authorization",
                token_url="https://www.linkedin.com/oauth/v2/accessToken",
                scopes=["openid", "profile", "w_member_social", "r_basicprofile", "r_organization_social"]
            )

        # Twitter configuration
        if os.getenv("TWITTER_CLIENT_ID"):
            configs["twitter"] = OAuthConfig(
                platform="twitter",
                client_id=os.getenv("TWITTER_CLIENT_ID"),
                client_secret=os.getenv("TWITTER_CLIENT_SECRET"),
                redirect_uri=os.getenv("TWITTER_REDIRECT_URI", "http://localhost:8888/oauth/twitter/callback"),
                authorization_url="https://twitter.com/i/oauth2/authorize",
                token_url="https://api.twitter.com/2/oauth2/token",
                scopes=["tweet.read", "tweet.write", "users.read", "offline.access"]
            )

        return configs

    def generate_authorization_url(self, platform: str) -> Tuple[str, str]:
        """
        Generate OAuth authorization URL for user to visit

        Args:
            platform: Platform name (linkedin, twitter)

        Returns:
            Tuple of (authorization_url, state) where state is used for CSRF protection
        """
        if platform not in self.configs:
            raise ValueError(f"Platform '{platform}' not configured. Check your .env file.")

        config = self.configs[platform]

        # Generate CSRF protection state
        state = secrets.token_urlsafe(32)
        self.state_store[state] = {
            "platform": platform,
            "created_at": datetime.now()
        }

        # Build authorization URL
        params = {
            "response_type": "code",
            "client_id": config.client_id,
            "redirect_uri": config.redirect_uri,
            "scope": " ".join(config.scopes),
            "state": state
        }

        # Twitter-specific parameters
        if platform == "twitter":
            # Generate code verifier and challenge for PKCE
            code_verifier = secrets.token_urlsafe(64)
            self.state_store[state]["code_verifier"] = code_verifier

            # Twitter uses PKCE (Proof Key for Code Exchange)
            import hashlib
            import base64
            code_challenge = base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode()).digest()
            ).decode().rstrip("=")

            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"

        authorization_url = f"{config.authorization_url}?{urlencode(params)}"

        return authorization_url, state

    def exchange_code_for_token(
        self,
        platform: str,
        code: str,
        state: str
    ) -> Dict[str, any]:
        """
        Exchange authorization code for access token

        Args:
            platform: Platform name
            code: Authorization code from callback
            state: State parameter for CSRF validation

        Returns:
            Dict with access_token, refresh_token, expires_in
        """
        # Validate state
        if state not in self.state_store:
            raise ValueError("Invalid state parameter. Possible CSRF attack.")

        stored_state = self.state_store[state]
        if stored_state["platform"] != platform:
            raise ValueError("State platform mismatch")

        # Check state age (should be used within 10 minutes)
        if datetime.now() - stored_state["created_at"] > timedelta(minutes=10):
            raise ValueError("State expired. Please start OAuth flow again.")

        config = self.configs[platform]

        # Prepare token request
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": config.redirect_uri,
            "client_id": config.client_id,
            "client_secret": config.client_secret
        }

        # Twitter PKCE
        if platform == "twitter":
            token_data["code_verifier"] = stored_state["code_verifier"]

        # Exchange code for token
        try:
            response = requests.post(
                config.token_url,
                data=token_data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json"
                }
            )

            response.raise_for_status()
            token_response = response.json()

            # Clean up state
            del self.state_store[state]

            return {
                "platform": platform,
                "access_token": token_response.get("access_token"),
                "refresh_token": token_response.get("refresh_token"),
                "expires_in": token_response.get("expires_in"),
                "token_type": token_response.get("token_type", "Bearer"),
                "scope": token_response.get("scope"),
                "created_at": datetime.now().isoformat()
            }

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to exchange code for token: {e}")

    def refresh_access_token(
        self,
        platform: str,
        refresh_token: str
    ) -> Dict[str, any]:
        """
        Refresh an expired access token

        Args:
            platform: Platform name
            refresh_token: Refresh token

        Returns:
            Dict with new access_token and expiry
        """
        if platform not in self.configs:
            raise ValueError(f"Platform '{platform}' not configured")

        config = self.configs[platform]

        token_data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": config.client_id,
            "client_secret": config.client_secret
        }

        try:
            response = requests.post(
                config.token_url,
                data=token_data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json"
                }
            )

            response.raise_for_status()
            token_response = response.json()

            return {
                "platform": platform,
                "access_token": token_response.get("access_token"),
                "refresh_token": token_response.get("refresh_token", refresh_token),  # Some platforms don't return new refresh token
                "expires_in": token_response.get("expires_in"),
                "token_type": token_response.get("token_type", "Bearer"),
                "refreshed_at": datetime.now().isoformat()
            }

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to refresh token: {e}")

    def save_token(self, token_data: Dict, user_id: Optional[str] = None) -> None:
        """
        Save token to secure storage (encrypted)

        In production, this should:
        1. Encrypt the token
        2. Store in database
        3. Associate with user_id

        Args:
            token_data: Token information from OAuth flow
            user_id: Optional user ID to associate token with
        """
        # For now, save to local file (NOT SECURE - for development only)
        # In production, use encrypted database storage

        tokens_file = ".oauth_tokens.json"
        tokens = {}

        if os.path.exists(tokens_file):
            with open(tokens_file, "r") as f:
                tokens = json.load(f)

        platform = token_data["platform"]
        tokens[platform] = {
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token"),
            "expires_in": token_data.get("expires_in"),
            "created_at": token_data.get("created_at", datetime.now().isoformat()),
            "user_id": user_id
        }

        with open(tokens_file, "w") as f:
            json.dump(tokens, f, indent=2)

        print(f"✅ Token saved for {platform}")
        print(f"⚠️  WARNING: Tokens are stored unencrypted in {tokens_file}")
        print("   In production, use encrypted database storage!")

    def load_token(self, platform: str) -> Optional[Dict]:
        """
        Load token from storage

        Args:
            platform: Platform name

        Returns:
            Token data or None if not found
        """
        tokens_file = ".oauth_tokens.json"

        if not os.path.exists(tokens_file):
            return None

        with open(tokens_file, "r") as f:
            tokens = json.load(f)

        return tokens.get(platform)

    def is_token_expired(self, token_data: Dict) -> bool:
        """Check if access token is expired"""
        if not token_data.get("expires_in"):
            return False  # No expiry means it doesn't expire

        created_at = datetime.fromisoformat(token_data.get("created_at"))
        expires_in = token_data.get("expires_in")
        expires_at = created_at + timedelta(seconds=expires_in)

        # Consider expired if less than 5 minutes remaining
        return datetime.now() >= expires_at - timedelta(minutes=5)

    def get_valid_token(self, platform: str) -> Optional[str]:
        """
        Get a valid access token, refreshing if necessary

        Args:
            platform: Platform name

        Returns:
            Valid access token or None
        """
        token_data = self.load_token(platform)

        if not token_data:
            return None

        # Check if token is expired
        if self.is_token_expired(token_data):
            print(f"🔄 Token expired for {platform}, refreshing...")

            if not token_data.get("refresh_token"):
                print(f"❌ No refresh token available for {platform}. Re-authorize required.")
                return None

            try:
                refreshed = self.refresh_access_token(
                    platform,
                    token_data["refresh_token"]
                )
                self.save_token(refreshed)
                return refreshed["access_token"]
            except Exception as e:
                print(f"❌ Failed to refresh token: {e}")
                return None

        return token_data["access_token"]


# Example usage functions
def start_oauth_flow(platform: str) -> None:
    """
    Start OAuth flow for a platform

    This will:
    1. Generate authorization URL
    2. Open browser for user to authorize
    3. Start local server to handle callback
    """
    oauth = OAuthManager()

    try:
        auth_url, state = oauth.generate_authorization_url(platform)

        print(f"\n🔐 Starting OAuth flow for {platform.upper()}")
        print("=" * 60)
        print("\nOpening browser for authorization...")
        print(f"\nIf the browser doesn't open, visit this URL:")
        print(f"\n{auth_url}\n")
        print("=" * 60)

        # Open browser
        webbrowser.open(auth_url)

        print(f"\n✅ After authorizing, you'll be redirected to localhost:8888")
        print(f"📝 The callback server will handle the rest automatically")
        print(f"\n💡 State token: {state[:16]}... (keep this safe)")

    except Exception as e:
        print(f"\n❌ Error starting OAuth flow: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python oauth.py <platform>")
        print("Platforms: linkedin, twitter")
        sys.exit(1)

    platform = sys.argv[1].lower()
    start_oauth_flow(platform)
