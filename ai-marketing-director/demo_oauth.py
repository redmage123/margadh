#!/usr/bin/env python3
"""
Demo: OAuth Integration and Social Media Posting

This script demonstrates the complete OAuth flow and social media integration.

Run this after completing OAuth setup to test everything works.
"""
from agents.social_media_agent import SocialMediaAgent
from core.oauth import OAuthManager
import json


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_oauth_status():
    """Check OAuth integration status"""
    print_section("1. OAuth Integration Status")

    social = SocialMediaAgent()
    status = social.check_integration_status()

    print("LinkedIn:")
    if status["linkedin"]["configured"]:
        print(f"  ✅ Configured")
        if status["linkedin"]["connected"]:
            details = status["linkedin"]["details"]
            print(f"  ✅ Connected")
            print(f"     User ID: {details.get('user_id', 'N/A')}")
        else:
            print(f"  ❌ Not connected")
            print(f"     Error: {status['linkedin'].get('error', 'Unknown')}")
    else:
        print(f"  ❌ Not configured")
        print(f"     Run: python manage.py update-env")

    print("\nTwitter:")
    if status["twitter"]["configured"]:
        print(f"  ✅ Configured")
        if status["twitter"]["connected"]:
            details = status["twitter"]["details"]
            print(f"  ✅ Connected")
            print(f"     Username: @{details.get('username', 'N/A')}")
            print(f"     Followers: {details.get('followers', 0):,}")
        else:
            print(f"  ❌ Not connected")
            print(f"     Error: {status['twitter'].get('error', 'Unknown')}")
    else:
        print(f"  ❌ Not configured")
        print(f"     Run: python manage.py update-env")


def demo_generate_content():
    """Generate sample social media content"""
    print_section("2. Content Generation (GPT-5)")

    social = SocialMediaAgent()

    # Generate LinkedIn post
    print("🔹 Generating LinkedIn post...")
    linkedin_post = social.create_linkedin_post(
        topic="The ROI of AI training in enterprises",
        style="professional",
        include_cta=True,
        publish=False  # Draft only for demo
    )

    print(f"\nGenerated LinkedIn Post:")
    print(f"─" * 60)
    print(linkedin_post["text"])
    print(f"─" * 60)
    print(f"Character count: {linkedin_post['character_count']}")
    print(f"Status: {linkedin_post['status']}")

    # Generate Twitter thread
    print(f"\n🔹 Generating Twitter thread...")
    twitter_thread = social.create_twitter_thread(
        topic="5 AI implementation mistakes to avoid",
        thread_length=5,
        publish=False  # Draft only for demo
    )

    print(f"\nGenerated Twitter Thread:")
    print(f"─" * 60)
    for i, tweet in enumerate(twitter_thread["tweets"], 1):
        print(f"{i}. {tweet}")
        print()
    print(f"─" * 60)
    print(f"Total tweets: {twitter_thread['tweet_count']}")
    print(f"Status: {twitter_thread['status']}")


def demo_publish_workflow():
    """Show the publish workflow (simulated)"""
    print_section("3. Publishing Workflow")

    print("📝 Step-by-step publishing process:\n")

    print("1️⃣  Generate content")
    print("    → Agent creates draft using GPT-5")
    print("    → Content follows AI Elevate brand voice")
    print()

    print("2️⃣  Human review")
    print("    → Marketing team reviews draft")
    print("    → Can edit or regenerate")
    print()

    print("3️⃣  Approve & publish")
    print("    → Click 'Publish' button")
    print("    → OAuth token loaded from secure storage")
    print("    → API call made to LinkedIn/Twitter")
    print()

    print("4️⃣  Confirmation")
    print("    → Post ID returned")
    print("    → URL to view post")
    print("    → Stored for analytics tracking")
    print()

    print("5️⃣  Analytics (automatic)")
    print("    → System fetches engagement hourly")
    print("    → Tracks likes, comments, shares")
    print("    → Reports in dashboard")


def demo_token_management():
    """Show token management"""
    print_section("4. Token Management")

    oauth = OAuthManager()

    print("📋 Stored tokens:\n")

    import os
    if os.path.exists(".oauth_tokens.json"):
        with open(".oauth_tokens.json", "r") as f:
            tokens = json.load(f)

        for platform, token_data in tokens.items():
            print(f"🔑 {platform.upper()}")
            print(f"   Access Token: {token_data['access_token'][:20]}...")
            print(f"   Created: {token_data.get('created_at', 'Unknown')}")

            if oauth.is_token_expired(token_data):
                print(f"   ⚠️  Status: EXPIRED - will auto-refresh")
            else:
                print(f"   ✅ Status: VALID")
            print()
    else:
        print("No tokens stored yet.")
        print("\n💡 Authorize platforms:")
        print("   python manage.py authorize linkedin")
        print("   python manage.py authorize twitter")


def demo_security():
    """Explain security features"""
    print_section("5. Security Features")

    print("🔐 How your credentials are protected:\n")

    print("✅ OAuth 2.0")
    print("   → Never stores passwords")
    print("   → Uses industry-standard authorization")
    print("   → Scoped permissions (only what's needed)")
    print()

    print("✅ Token Storage")
    print("   → Tokens encrypted at rest (production)")
    print("   → Separate from source code")
    print("   → .oauth_tokens.json in .gitignore")
    print()

    print("✅ Automatic Refresh")
    print("   → Tokens refreshed before expiry")
    print("   → No manual intervention needed")
    print("   → Refresh tokens rotated regularly")
    print()

    print("✅ Scope Limitation")
    print("   → Only requests necessary permissions")
    print("   → Can't access DMs or private data")
    print("   → Revocable anytime via platform")


def main():
    """Run the demo"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║    AI MARKETING DIRECTOR - OAuth Integration Demo        ║
║                                                           ║
║    This demo shows how OAuth enables secure social       ║
║    media publishing for AI Elevate                       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)

    try:
        # 1. Check OAuth status
        demo_oauth_status()

        # 2. Generate content
        demo_generate_content()

        # 3. Show publishing workflow
        demo_publish_workflow()

        # 4. Token management
        demo_token_management()

        # 5. Security features
        demo_security()

        # Summary
        print_section("Summary")
        print("✅ OAuth setup allows secure social media integration")
        print("✅ GPT-5 generates brand-consistent content")
        print("✅ Human-in-the-loop ensures quality control")
        print("✅ Analytics tracked automatically")
        print()
        print("🚀 Ready to start using the AI Marketing Director!")
        print()
        print("📖 Next steps:")
        print("   1. Review generated content above")
        print("   2. Authorize platforms if not already done")
        print("   3. Try publishing a post")
        print()

    except KeyboardInterrupt:
        print("\n\n✋ Demo interrupted.")
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        print("\n💡 Make sure you've completed OAuth setup:")
        print("   python manage.py authorize linkedin")
        print("   python manage.py authorize twitter")


if __name__ == "__main__":
    main()
