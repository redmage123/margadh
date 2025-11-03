"""Social Media Agent for automated social media management"""
from openai import OpenAI
from typing import Dict, List, Optional
from datetime import datetime
from config.settings import settings
from core.brand_voice import brand_voice

# Import integrations
try:
    from integrations.linkedin import LinkedInIntegration
    from integrations.twitter import TwitterIntegration
    INTEGRATIONS_AVAILABLE = True
except ImportError:
    INTEGRATIONS_AVAILABLE = False


class SocialMediaAgent:
    """
    Social Media Agent responsible for:
    - Creating platform-specific posts (LinkedIn, Twitter)
    - Publishing to social platforms
    - Tracking engagement metrics
    - Suggesting optimal posting times
    """

    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key or settings.openai_api_key)
        self.model = settings.default_model
        self.brand_prompt = brand_voice.get_system_prompt("linkedin")

        # Initialize integrations if credentials available
        self.linkedin = None
        self.twitter = None

        if INTEGRATIONS_AVAILABLE:
            if settings.linkedin_access_token:
                self.linkedin = LinkedInIntegration(
                    access_token=settings.linkedin_access_token
                )

            if settings.twitter_api_key:
                self.twitter = TwitterIntegration(
                    bearer_token=settings.twitter_api_key
                )

    def create_linkedin_post(
        self,
        topic: str,
        style: str = "professional",
        include_cta: bool = True,
        publish: bool = False
    ) -> Dict:
        """
        Generate and optionally publish a LinkedIn post

        Args:
            topic: Topic to write about
            style: Writing style (professional, casual, thought_leadership)
            include_cta: Whether to include call-to-action
            publish: If True, publish to LinkedIn immediately

        Returns:
            Dict containing the generated post and publication status
        """
        system_prompt = f"""{brand_voice.get_system_prompt('linkedin')}

You are creating a LinkedIn post for AI Elevate.

Style: {style}
Topic: {topic}

Requirements:
- Keep it between 1200-1500 characters (LinkedIn optimal length)
- Use line breaks for readability
- Include 3-5 relevant hashtags at the end
- {'Include a clear call-to-action linking to ai-elevate.ai' if include_cta else 'No CTA needed'}
- Use "Join the AI Elevation Movement" as signature phrase
- Make it engaging and valuable to enterprise decision-makers
"""

        user_prompt = f"""Create a LinkedIn post about: {topic}

The post should:
1. Start with a hook that grabs attention
2. Provide valuable insights or data
3. Be concise but impactful
4. Include relevant hashtags
5. {'End with a CTA' if include_cta else 'Wrap up with key takeaway'}

Generate ONLY the post text, no additional commentary."""

        response = self.client.chat.completions.create(
            model=self.model,
            max_completion_tokens=settings.max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
        )

        post_text = response.choices[0].message.content.strip()

        result = {
            "platform": "linkedin",
            "topic": topic,
            "text": post_text,
            "character_count": len(post_text),
            "created_at": datetime.now().isoformat(),
            "status": "draft",
            "agent": "social_media_agent",
        }

        # Optionally publish to LinkedIn
        if publish and self.linkedin:
            try:
                published = self.linkedin.create_post(
                    text=post_text,
                    visibility="PUBLIC"
                )
                result["published"] = True
                result["post_id"] = published["id"]
                result["post_url"] = published["url"]
                result["status"] = "published"
            except Exception as e:
                result["published"] = False
                result["error"] = str(e)
                result["status"] = "failed"
        elif publish and not self.linkedin:
            result["error"] = "LinkedIn integration not configured"
            result["status"] = "failed"

        return result

    def create_twitter_thread(
        self,
        topic: str,
        thread_length: int = 5,
        publish: bool = False
    ) -> Dict:
        """
        Generate and optionally publish a Twitter thread

        Args:
            topic: Topic for the thread
            thread_length: Number of tweets in thread
            publish: If True, publish to Twitter immediately

        Returns:
            Dict containing thread tweets and publication status
        """
        system_prompt = f"""{brand_voice.get_system_prompt('linkedin')}

You are creating a Twitter thread for AI Elevate.

Requirements:
- Each tweet must be under 280 characters
- First tweet should hook readers and indicate thread with "🧵"
- Last tweet should include CTA with ai-elevate.ai
- Use clear numbering (1/, 2/, 3/, etc.)
- Make each tweet valuable on its own
- Use relevant hashtags sparingly (1-2 per thread)
"""

        user_prompt = f"""Create a {thread_length}-tweet thread about: {topic}

Format as a numbered list, one tweet per line:
1/ [First tweet with hook and thread indicator 🧵]
2/ [Second tweet]
...
{thread_length}/ [Final tweet with CTA]

Generate ONLY the tweets, no additional commentary."""

        response = self.client.chat.completions.create(
            model=self.model,
            max_completion_tokens=settings.max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
        )

        thread_text = response.choices[0].message.content.strip()

        # Parse tweets from response
        tweets = [
            line.split('/', 1)[1].strip() if '/' in line else line.strip()
            for line in thread_text.split('\n')
            if line.strip() and not line.strip().startswith('#')
        ]

        result = {
            "platform": "twitter",
            "topic": topic,
            "tweets": tweets,
            "tweet_count": len(tweets),
            "created_at": datetime.now().isoformat(),
            "status": "draft",
            "agent": "social_media_agent",
        }

        # Optionally publish to Twitter
        if publish and self.twitter:
            try:
                published_thread = self.twitter.create_thread(tweets)
                result["published"] = True
                result["thread_results"] = published_thread
                result["status"] = "published"
            except Exception as e:
                result["published"] = False
                result["error"] = str(e)
                result["status"] = "failed"
        elif publish and not self.twitter:
            result["error"] = "Twitter integration not configured"
            result["status"] = "failed"

        return result

    def get_post_analytics(
        self,
        platform: str,
        post_id: str
    ) -> Dict:
        """
        Fetch analytics for a published post

        Args:
            platform: "linkedin" or "twitter"
            post_id: Platform-specific post ID

        Returns:
            Dict with engagement metrics
        """
        try:
            if platform == "linkedin" and self.linkedin:
                analytics = self.linkedin.get_post_analytics(post_id)
                return {
                    "platform": "linkedin",
                    "post_id": post_id,
                    "analytics": analytics,
                    "fetched_at": datetime.now().isoformat()
                }

            elif platform == "twitter" and self.twitter:
                metrics = self.twitter.get_tweet_metrics(post_id)
                return {
                    "platform": "twitter",
                    "post_id": post_id,
                    "analytics": metrics,
                    "fetched_at": datetime.now().isoformat()
                }

            else:
                return {
                    "error": f"{platform.title()} integration not configured",
                    "platform": platform,
                    "post_id": post_id
                }

        except Exception as e:
            return {
                "error": str(e),
                "platform": platform,
                "post_id": post_id
            }

    def check_integration_status(self) -> Dict:
        """
        Check status of all social media integrations

        Returns:
            Dict with integration status for each platform
        """
        status = {
            "linkedin": {
                "configured": self.linkedin is not None,
                "connected": False
            },
            "twitter": {
                "configured": self.twitter is not None,
                "connected": False
            }
        }

        # Test LinkedIn connection
        if self.linkedin:
            try:
                linkedin_test = self.linkedin.test_connection()
                status["linkedin"]["connected"] = linkedin_test["status"] == "connected"
                status["linkedin"]["details"] = linkedin_test
            except Exception as e:
                status["linkedin"]["error"] = str(e)

        # Test Twitter connection
        if self.twitter:
            try:
                twitter_test = self.twitter.test_connection()
                status["twitter"]["connected"] = twitter_test["status"] == "connected"
                status["twitter"]["details"] = twitter_test
            except Exception as e:
                status["twitter"]["error"] = str(e)

        return status


# Example CLI usage
if __name__ == "__main__":
    import json
    import sys

    agent = SocialMediaAgent()

    print("🎯 AI Elevate Social Media Agent")
    print("=" * 50)

    # Check integration status
    print("\n📊 Integration Status:")
    status = agent.check_integration_status()
    print(json.dumps(status, indent=2))

    # Example: Generate LinkedIn post (draft only)
    print("\n💼 Generating LinkedIn Post...")
    linkedin_post = agent.create_linkedin_post(
        topic="Why prompt engineering frameworks boost AI ROI",
        style="professional",
        include_cta=True,
        publish=False  # Set to True to actually publish
    )
    print(json.dumps(linkedin_post, indent=2))

    # Example: Generate Twitter thread (draft only)
    print("\n🐦 Generating Twitter Thread...")
    twitter_thread = agent.create_twitter_thread(
        topic="5 mistakes companies make when implementing AI",
        thread_length=6,
        publish=False  # Set to True to actually publish
    )
    print(json.dumps(twitter_thread, indent=2))
