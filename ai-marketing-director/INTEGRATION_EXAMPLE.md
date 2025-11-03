# Integration Example - Complete Workflow

## How Third-Party Apps Connect: A Real Example

Let's walk through a complete example of creating and publishing a LinkedIn post.

### Step 1: User Request

```bash
python main.py social linkedin --topic "AI ROI" --publish
```

### Step 2: Social Media Agent Flow

```
User Command
    ↓
main.py routes to Social Media Agent
    ↓
SocialMediaAgent.create_linkedin_post()
    ↓
Calls GPT-5 to generate post content
    ↓
GPT-5 returns optimized LinkedIn post
    ↓
If publish=True:
    ↓
LinkedInIntegration.create_post()
    ↓
Makes HTTPS request to LinkedIn API
    ↓
LinkedIn API creates post
    ↓
Returns post ID and URL
    ↓
User gets confirmation with link
```

### Step 3: Code Flow (Detailed)

```python
# 1. User runs command
$ python main.py social linkedin --topic "AI ROI" --publish

# 2. main.py calls Social Media Agent
from agents.social_media_agent import SocialMediaAgent

agent = SocialMediaAgent()
result = agent.create_linkedin_post(
    topic="AI ROI",
    publish=True
)

# 3. Agent generates content with GPT-5
response = self.client.chat.completions.create(
    model="gpt-5",
    messages=[
        {"role": "system", "content": brand_prompt},
        {"role": "user", "content": "Create LinkedIn post about AI ROI"}
    ]
)
post_text = response.choices[0].message.content

# 4. Agent publishes via LinkedIn Integration
from integrations.linkedin import LinkedInIntegration

linkedin = LinkedInIntegration(access_token="oauth_token")
published = linkedin.create_post(
    text=post_text,
    visibility="PUBLIC"
)

# 5. LinkedIn Integration makes API call
import requests

response = requests.post(
    "https://api.linkedin.com/v2/ugcPosts",
    headers={"Authorization": f"Bearer {access_token}"},
    json={
        "author": "urn:li:person:me",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": post_text}
            }
        }
    }
)

# 6. Return result to user
{
    "id": "urn:li:share:123456",
    "platform": "linkedin",
    "text": "80% of AI implementations fail...",
    "url": "https://www.linkedin.com/feed/update/urn:li:share:123456",
    "created_at": "2025-11-03T15:30:00Z",
    "status": "published"
}
```

## Authentication Example

### LinkedIn OAuth 2.0 Setup

```python
# 1. Create LinkedIn app at https://www.linkedin.com/developers/apps
# 2. Add redirect URI: https://your-domain.com/oauth/callback
# 3. Request scopes: w_member_social, r_basicprofile

# 4. User clicks "Connect LinkedIn" in dashboard
# Browser redirects to:
https://www.linkedin.com/oauth/v2/authorization?
    response_type=code&
    client_id=YOUR_CLIENT_ID&
    redirect_uri=https://your-domain.com/oauth/callback&
    scope=w_member_social%20r_basicprofile

# 5. User approves

# 6. LinkedIn redirects back:
https://your-domain.com/oauth/callback?code=AUTH_CODE

# 7. Exchange code for access token
import requests

response = requests.post(
    "https://www.linkedin.com/oauth/v2/accessToken",
    data={
        "grant_type": "authorization_code",
        "code": "AUTH_CODE",
        "client_id": "YOUR_CLIENT_ID",
        "client_secret": "YOUR_CLIENT_SECRET",
        "redirect_uri": "https://your-domain.com/oauth/callback"
    }
)

access_token = response.json()["access_token"]

# 8. Save encrypted token in database
from cryptography.fernet import Fernet

cipher = Fernet(encryption_key)
encrypted_token = cipher.encrypt(access_token.encode())

db.save({
    "user_id": current_user.id,
    "platform": "linkedin",
    "access_token": encrypted_token,
    "expires_at": datetime.now() + timedelta(days=60)
})

# 9. Use for API calls
linkedin = LinkedInIntegration(access_token=access_token)
```

## Complete Use Case: Automated Social Media Campaign

### Scenario
User wants to launch a social media campaign about a new training program.

```python
from agents.orchestrator import OrchestratorAgent
from agents.strategy_agent import StrategyAgent
from agents.social_media_agent import SocialMediaAgent

# 1. Plan the campaign
orchestrator = OrchestratorAgent()
plan = orchestrator.plan_marketing_initiative(
    objective="Launch new prompt engineering course",
    timeframe="2 weeks"
)

# 2. Get content topic suggestions
strategy = StrategyAgent()
topics = strategy.suggest_content_topics(
    content_type="linkedin",
    count=5,
    based_on="new course launch"
)

# 3. Generate social media posts
social = SocialMediaAgent()

# LinkedIn post
linkedin_post = social.create_linkedin_post(
    topic=topics["topics"][0]["title"],
    style="professional",
    include_cta=True,
    publish=False  # Draft for review
)

# Twitter thread
twitter_thread = social.create_twitter_thread(
    topic=topics["topics"][0]["title"],
    thread_length=5,
    publish=False  # Draft for review
)

# 4. Human reviews and approves in dashboard

# 5. Publish after approval
if user_approves:
    # Publish LinkedIn
    linkedin_result = social.create_linkedin_post(
        topic=topics["topics"][0]["title"],
        publish=True  # Actually publish
    )

    # Publish Twitter thread
    twitter_result = social.create_twitter_thread(
        topic=topics["topics"][0]["title"],
        publish=True  # Actually publish
    )

# 6. Track analytics
from agents.analytics_agent import AnalyticsAgent

analytics = AnalyticsAgent()

# Wait 24 hours, then fetch metrics
linkedin_metrics = social.get_post_analytics(
    platform="linkedin",
    post_id=linkedin_result["post_id"]
)

twitter_metrics = social.get_post_analytics(
    platform="twitter",
    post_id=twitter_result["thread_results"][0]["id"]
)

# 7. Generate performance report
report = analytics.generate_performance_report(
    timeframe="7 days",
    channels=["linkedin", "twitter"],
    metrics=["engagement", "reach", "clicks"]
)
```

## Integration Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   USER INTERACTION                       │
│                                                          │
│  CLI: python main.py social linkedin --publish          │
│  Web: Click "Publish to LinkedIn" button               │
│  API: POST /social/linkedin/posts                      │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              SOCIAL MEDIA AGENT                         │
│                                                          │
│  1. Receive request (topic, style, platform)           │
│  2. Generate content with GPT-5                        │
│  3. Validate brand voice                               │
│  4. If publish=True → Call integration                 │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│          LINKEDIN INTEGRATION                           │
│                                                          │
│  1. Load access token from secure storage              │
│  2. Check rate limits                                   │
│  3. Prepare API request                                 │
│  4. Make HTTPS call to LinkedIn API                     │
│  5. Handle response/errors                              │
│  6. Update rate limit tracking                          │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              LINKEDIN API                               │
│       (api.linkedin.com/v2/ugcPosts)                    │
│                                                          │
│  1. Authenticate request                                │
│  2. Validate post data                                  │
│  3. Create post on LinkedIn                             │
│  4. Return post ID and URL                              │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              RESULT TRACKING                            │
│                                                          │
│  1. Store post ID in database                           │
│  2. Schedule analytics fetch                            │
│  3. Return success to user                              │
│  4. Display confirmation with link                      │
└─────────────────────────────────────────────────────────┘
```

## Security Flow

```
┌─────────────────────────────────────────────────────────┐
│             CREDENTIAL STORAGE                          │
│                                                          │
│  Database (PostgreSQL):                                 │
│  ┌──────────────────────────────────────────────┐      │
│  │ id | user_id | platform  | encrypted_token  │      │
│  ├──────────────────────────────────────────────┤      │
│  │ 1  | 101     | linkedin  | gAAAAA...        │      │
│  │ 2  | 101     | twitter   | gAAAAA...        │      │
│  └──────────────────────────────────────────────┘      │
│                                                          │
│  Encryption Key (AWS Secrets Manager):                  │
│  ┌──────────────────────────────────────────────┐      │
│  │ FERNET_ENCRYPTION_KEY: xxxx-yyyy-zzzz        │      │
│  └──────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────┘
            │
            ↓
┌─────────────────────────────────────────────────────────┐
│          INTEGRATION INITIALIZATION                     │
│                                                          │
│  from cryptography.fernet import Fernet                 │
│                                                          │
│  # 1. Fetch encryption key from AWS                     │
│  cipher = Fernet(get_encryption_key())                  │
│                                                          │
│  # 2. Load encrypted token from DB                      │
│  encrypted = db.get_token(user_id, platform)            │
│                                                          │
│  # 3. Decrypt                                            │
│  access_token = cipher.decrypt(encrypted)               │
│                                                          │
│  # 4. Initialize integration                             │
│  linkedin = LinkedInIntegration(access_token)           │
└─────────────────────────────────────────────────────────┘
```

## Error Handling Flow

```python
try:
    # Attempt to publish
    linkedin.create_post(text="Post content")

except AuthenticationError:
    # Token expired or invalid
    → Refresh OAuth token
    → Retry once
    → If still fails: Notify user to re-authorize

except RateLimitError as e:
    # Hit API rate limit
    → Queue post for later
    → Schedule retry after e.retry_after seconds
    → Notify user of delay

except APIError as e:
    # LinkedIn API error
    → Log error with full context
    → Retry up to 3 times with exponential backoff
    → If still fails: Mark as failed, notify user

except NetworkError:
    # Network connectivity issue
    → Retry with exponential backoff
    → Max 3 retries
    → Fail gracefully

finally:
    # Always log the attempt
    → Save to audit log
    → Update metrics
    → Update user notification
```

## Testing Integrations

```bash
# Test connection to LinkedIn
python -c "
from integrations.linkedin import LinkedInIntegration
import os

linkedin = LinkedInIntegration(
    access_token=os.getenv('LINKEDIN_ACCESS_TOKEN')
)

status = linkedin.test_connection()
print(status)
"

# Expected output:
{
  "status": "connected",
  "platform": "LinkedIn",
  "user_id": "abc123",
  "organization_id": "xyz789",
  "rate_limit": {
    "rate_limit_remaining": 495,
    "rate_limit_reset": "2025-11-04T00:00:00Z"
  }
}
```

## Next Steps

1. **Set up OAuth** for LinkedIn and Twitter
2. **Configure API keys** in `.env`
3. **Test connections** with `test_connection()`
4. **Start creating content** with Social Media Agent
5. **Monitor analytics** with Analytics Agent

For detailed setup instructions, see [INTEGRATIONS_GUIDE.md](INTEGRATIONS_GUIDE.md)
