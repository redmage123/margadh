#!/usr/bin/env python3
"""
Management commands for AI Marketing Director

Usage:
    python manage.py authorize <platform>    - Start OAuth flow
    python manage.py test-integration <platform> - Test integration
    python manage.py list-tokens             - List stored tokens
    python manage.py revoke <platform>       - Revoke/delete token
"""
import sys
import os
import argparse
import threading
import time
from core.oauth import OAuthManager, start_oauth_flow
from core.oauth_server import start_callback_server


def cmd_authorize(args):
    """Authorize a platform via OAuth"""
    platform = args.platform.lower()

    print(f"\n{'='*60}")
    print(f"  AI MARKETING DIRECTOR - OAuth Authorization")
    print(f"{'='*60}\n")

    # Start callback server in background thread
    print("🚀 Starting OAuth callback server...")
    server_thread = threading.Thread(
        target=start_callback_server,
        args=(8888,),
        daemon=True
    )
    server_thread.start()

    # Give server time to start
    time.sleep(1)

    # Start OAuth flow (opens browser)
    start_oauth_flow(platform)

    print(f"\n⏳ Waiting for authorization...")
    print(f"   (This window will update once you authorize)")

    try:
        # Keep alive until user presses Ctrl+C
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n\n✅ Done! Token has been saved.")
        print(f"\n💡 Test your connection:")
        print(f"   python manage.py test-integration {platform}\n")


def cmd_test_integration(args):
    """Test an integration"""
    platform = args.platform.lower()

    print(f"\n🧪 Testing {platform.upper()} integration...")

    oauth = OAuthManager()
    token = oauth.get_valid_token(platform)

    if not token:
        print(f"❌ No valid token found for {platform}")
        print(f"\n💡 Authorize first:")
        print(f"   python manage.py authorize {platform}\n")
        return

    # Test the integration
    if platform == "linkedin":
        from integrations.linkedin import LinkedInIntegration

        try:
            linkedin = LinkedInIntegration(access_token=token)
            status = linkedin.test_connection()

            if status["status"] == "connected":
                print(f"✅ LinkedIn integration working!")
                print(f"   User ID: {status.get('user_id')}")
                print(f"   Organization: {status.get('organization_id', 'N/A')}")
            else:
                print(f"❌ LinkedIn test failed: {status.get('error')}")

        except Exception as e:
            print(f"❌ Error testing LinkedIn: {e}")

    elif platform == "twitter":
        from integrations.twitter import TwitterIntegration

        try:
            twitter = TwitterIntegration(bearer_token=token)
            status = twitter.test_connection()

            if status["status"] == "connected":
                print(f"✅ Twitter integration working!")
                print(f"   Username: @{status.get('username')}")
                print(f"   Followers: {status.get('followers', 0):,}")
            else:
                print(f"❌ Twitter test failed: {status.get('error')}")

        except Exception as e:
            print(f"❌ Error testing Twitter: {e}")

    else:
        print(f"❌ Unknown platform: {platform}")


def cmd_list_tokens(args):
    """List all stored tokens"""
    oauth = OAuthManager()

    print(f"\n📋 Stored OAuth Tokens")
    print(f"{'='*60}\n")

    import json
    tokens_file = ".oauth_tokens.json"

    if not os.path.exists(tokens_file):
        print("No tokens stored yet.\n")
        return

    with open(tokens_file, "r") as f:
        tokens = json.load(f)

    if not tokens:
        print("No tokens stored yet.\n")
        return

    for platform, token_data in tokens.items():
        print(f"🔑 {platform.upper()}")
        print(f"   Access Token: {token_data['access_token'][:20]}...")
        print(f"   Created: {token_data.get('created_at', 'Unknown')}")

        if token_data.get('expires_in'):
            print(f"   Expires in: {token_data['expires_in']} seconds")

        # Check if expired
        if oauth.is_token_expired(token_data):
            print(f"   ⚠️  Status: EXPIRED")
        else:
            print(f"   ✅ Status: VALID")

        print()


def cmd_revoke(args):
    """Revoke/delete a token"""
    platform = args.platform.lower()

    print(f"\n🗑️  Revoking {platform.upper()} token...")

    import json
    tokens_file = ".oauth_tokens.json"

    if not os.path.exists(tokens_file):
        print("No tokens to revoke.\n")
        return

    with open(tokens_file, "r") as f:
        tokens = json.load(f)

    if platform not in tokens:
        print(f"No token found for {platform}.\n")
        return

    # Remove token
    del tokens[platform]

    with open(tokens_file, "w") as f:
        json.dump(tokens, f, indent=2)

    print(f"✅ Token revoked for {platform}\n")


def cmd_update_env(args):
    """Update .env file with OAuth credentials"""
    print(f"\n⚙️  Configuring OAuth settings in .env...")

    env_updates = []

    # LinkedIn
    print(f"\n📘 LinkedIn OAuth Setup:")
    print(f"   1. Go to: https://www.linkedin.com/developers/apps")
    print(f"   2. Create new app (or select existing)")
    print(f"   3. Add redirect URI: http://localhost:8888/oauth/linkedin/callback")
    print(f"   4. Request scopes: w_member_social, r_basicprofile, r_organization_social")

    linkedin_client_id = input(f"\n   LinkedIn Client ID (or press Enter to skip): ").strip()
    if linkedin_client_id:
        linkedin_client_secret = input(f"   LinkedIn Client Secret: ").strip()
        env_updates.append(f"LINKEDIN_CLIENT_ID={linkedin_client_id}")
        env_updates.append(f"LINKEDIN_CLIENT_SECRET={linkedin_client_secret}")
        env_updates.append(f"LINKEDIN_REDIRECT_URI=http://localhost:8888/oauth/linkedin/callback")

    # Twitter
    print(f"\n🐦 Twitter OAuth Setup:")
    print(f"   1. Go to: https://developer.twitter.com/en/portal/dashboard")
    print(f"   2. Create project and app")
    print(f"   3. Enable OAuth 2.0")
    print(f"   4. Add callback URI: http://localhost:8888/oauth/twitter/callback")
    print(f"   5. Request scopes: tweet.read, tweet.write, users.read, offline.access")

    twitter_client_id = input(f"\n   Twitter Client ID (or press Enter to skip): ").strip()
    if twitter_client_id:
        twitter_client_secret = input(f"   Twitter Client Secret: ").strip()
        env_updates.append(f"TWITTER_CLIENT_ID={twitter_client_id}")
        env_updates.append(f"TWITTER_CLIENT_SECRET={twitter_client_secret}")
        env_updates.append(f"TWITTER_REDIRECT_URI=http://localhost:8888/oauth/twitter/callback")

    if env_updates:
        # Append to .env
        with open(".env", "a") as f:
            f.write("\n\n# OAuth Configuration\n")
            f.write("\n".join(env_updates))
            f.write("\n")

        print(f"\n✅ Updated .env file with OAuth credentials")
        print(f"\n💡 Next step: Authorize platforms")
        print(f"   python manage.py authorize linkedin")
        print(f"   python manage.py authorize twitter\n")
    else:
        print(f"\n⏭️  Skipped OAuth configuration\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="AI Marketing Director Management Commands",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Authorize command
    authorize_parser = subparsers.add_parser("authorize", help="Authorize a platform via OAuth")
    authorize_parser.add_argument("platform", choices=["linkedin", "twitter"], help="Platform to authorize")

    # Test integration command
    test_parser = subparsers.add_parser("test-integration", help="Test platform integration")
    test_parser.add_argument("platform", choices=["linkedin", "twitter"], help="Platform to test")

    # List tokens command
    subparsers.add_parser("list-tokens", help="List all stored OAuth tokens")

    # Revoke command
    revoke_parser = subparsers.add_parser("revoke", help="Revoke/delete a token")
    revoke_parser.add_argument("platform", choices=["linkedin", "twitter"], help="Platform to revoke")

    # Update env command
    subparsers.add_parser("update-env", help="Configure OAuth credentials in .env")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Route to command handler
    if args.command == "authorize":
        cmd_authorize(args)
    elif args.command == "test-integration":
        cmd_test_integration(args)
    elif args.command == "list-tokens":
        cmd_list_tokens(args)
    elif args.command == "revoke":
        cmd_revoke(args)
    elif args.command == "update-env":
        cmd_update_env(args)


if __name__ == "__main__":
    main()
