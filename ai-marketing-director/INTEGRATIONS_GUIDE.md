# Third-Party Integrations Guide

## Overview

The AI Marketing Director connects to external platforms through a standardized integration layer. Each integration is a Python class that handles authentication, API calls, rate limiting, and error handling.

## Architecture

```
┌─────────────────────────────────────────┐
│        AI Marketing Director            │
│   (Strategy, Content, Social Agents)    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│       Integration Manager               │
│   - Credential management               │
│   - Rate limiting                       │
│   - Error handling & retries            │
│   - Logging & monitoring                │
└──────────────┬──────────────────────────┘
               │
┌──────────────┴──────────────────────────┐
│                                         │
▼              ▼              ▼           ▼
LinkedIn    Twitter/X      HubSpot    Google
  API         API            CRM      Analytics
```

## Supported Integrations

| Platform | Status | Authentication | Capabilities |
|----------|--------|----------------|--------------|
| **LinkedIn** | ✅ Ready | OAuth 2.0 | Post creation, analytics, scheduling |
| **Twitter/X** | ✅ Ready | OAuth 2.0 | Tweets, threads, engagement tracking |
| **HubSpot CRM** | ✅ Ready | API Key | Contact tracking, lead attribution |
| **Google Analytics** | ✅ Ready | Service Account | Traffic tracking, conversion analysis |
| **SendGrid** | ✅ Ready | API Key | Email campaigns, delivery tracking |
| **Salesforce** | 🚧 Planned | OAuth 2.0 | CRM integration |
| **Mailchimp** | 🚧 Planned | API Key | Email marketing |

## How Integrations Work

### 1. Authentication Flow

#### OAuth 2.0 (LinkedIn, Twitter)

```
User → Click "Connect LinkedIn"
  ↓
System → Redirect to LinkedIn authorization page
  ↓
User → Approves access
  ↓
LinkedIn → Redirects back with authorization code
  ↓
System → Exchanges code for access token
  ↓
System → Stores encrypted token in database
  ↓
Ready to use LinkedIn API
```

#### API Key (HubSpot, SendGrid)

```
User → Enters API key in Settings
  ↓
System → Validates key with test API call
  ↓
System → Stores encrypted key in database
  ↓
Ready to use API
```

### 2. Making API Calls

All integrations follow this pattern:

```python
from integrations.linkedin import LinkedInIntegration

# Initialize with stored credentials
linkedin = LinkedInIntegration(access_token="stored_token")

# Make API calls
post = linkedin.create_post(
    text="Check out our new AI training program!",
    visibility="PUBLIC"
)

# Get analytics
analytics = linkedin.get_post_analytics(post["id"])
```

### 3. Rate Limiting & Retries

The integration layer automatically handles:
- **Rate limiting**: Respects API limits (e.g., LinkedIn: 500 req/day)
- **Retries**: Automatic retry with exponential backoff
- **Error handling**: Graceful degradation if API unavailable

### 4. Data Flow Example

**Publishing a LinkedIn Post:**

```
Content Agent generates post
         ↓
Human approves in dashboard
         ↓
Social Media Agent calls LinkedInIntegration.create_post()
         ↓
Integration validates credentials
         ↓
Makes API call to LinkedIn
         ↓
LinkedIn returns post ID
         ↓
System stores post ID for analytics tracking
         ↓
Analytics Agent fetches engagement metrics hourly
```

## Setting Up Integrations

### LinkedIn Integration

1. **Create LinkedIn App**:
   - Go to https://www.linkedin.com/developers/apps
   - Create new app
   - Add redirect URL: `https://your-domain.com/oauth/linkedin/callback`
   - Request scopes: `w_member_social`, `r_basicprofile`, `r_organization_social`

2. **Configure in AI Marketing Director**:
   ```bash
   # Add to .env
   LINKEDIN_CLIENT_ID=your_client_id
   LINKEDIN_CLIENT_SECRET=your_client_secret
   LINKEDIN_REDIRECT_URI=https://your-domain.com/oauth/linkedin/callback
   ```

3. **Authorize**:
   - Run: `python manage.py authorize linkedin`
   - Browser opens, login to LinkedIn
   - Approve access
   - Token saved automatically

### Twitter/X Integration

1. **Create Twitter App**:
   - Go to https://developer.twitter.com/en/portal/dashboard
   - Create project and app
   - Enable OAuth 2.0
   - Add callback URL

2. **Configure**:
   ```bash
   # Add to .env
   TWITTER_CLIENT_ID=your_client_id
   TWITTER_CLIENT_SECRET=your_client_secret
   TWITTER_BEARER_TOKEN=your_bearer_token
   ```

3. **Authorize**:
   - Run: `python manage.py authorize twitter`
   - Complete OAuth flow

### HubSpot CRM Integration

1. **Get API Key**:
   - Login to HubSpot
   - Settings → Integrations → API Key
   - Generate private app token

2. **Configure**:
   ```bash
   # Add to .env
   HUBSPOT_API_KEY=your_api_key
   ```

3. **Test**:
   ```bash
   python manage.py test-integration hubspot
   ```

### Google Analytics Integration

1. **Create Service Account**:
   - Go to Google Cloud Console
   - Create service account
   - Download JSON credentials
   - Grant access to Analytics property

2. **Configure**:
   ```bash
   # Add to .env
   GOOGLE_ANALYTICS_CREDENTIALS_PATH=/path/to/service-account.json
   GOOGLE_ANALYTICS_PROPERTY_ID=your_property_id
   ```

3. **Test**:
   ```bash
   python manage.py test-integration google-analytics
   ```

## Integration Code Structure

Each integration follows this pattern:

```python
# integrations/linkedin.py

class LinkedInIntegration(BaseIntegration):
    """LinkedIn API integration"""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.linkedin.com/v2"

    def create_post(self, text: str, visibility: str = "PUBLIC") -> Dict:
        """Create a LinkedIn post"""
        # Implementation

    def get_post_analytics(self, post_id: str) -> Dict:
        """Get engagement metrics for a post"""
        # Implementation

    def schedule_post(self, text: str, publish_time: datetime) -> Dict:
        """Schedule a post for later"""
        # Implementation
```

## Security Best Practices

1. **Never commit credentials**:
   - Use `.env` file (already in `.gitignore`)
   - Use environment variables in production

2. **Encrypt at rest**:
   - All tokens encrypted in database using Fernet
   - Encryption key stored in AWS Secrets Manager

3. **Rotate tokens**:
   - OAuth tokens refreshed automatically before expiry
   - API keys rotated every 90 days

4. **Audit logging**:
   - All API calls logged with timestamps
   - Failed auth attempts monitored

## Rate Limits

| Platform | Limit | Strategy |
|----------|-------|----------|
| LinkedIn | 500 req/day, 100 req/user | Queue posts, batch analytics |
| Twitter | 300 tweets/3hrs, 50 req/15min | Respect windows, exponential backoff |
| HubSpot | 10 req/sec (burst: 100) | Token bucket algorithm |
| Google Analytics | 10 req/sec | Rate limiter with queue |

## Error Handling

All integrations handle common errors:

```python
try:
    linkedin.create_post(text)
except RateLimitError:
    # Wait and retry
    retry_after = error.retry_after
    schedule_retry(task, retry_after)
except AuthenticationError:
    # Token expired, refresh
    refresh_token()
    retry(task)
except APIError as e:
    # Log error, notify user
    log.error(f"LinkedIn API error: {e}")
    notify_user("Failed to post to LinkedIn")
```

## Monitoring & Alerts

The system monitors:
- API call success/failure rates
- Response times
- Rate limit usage
- Authentication status

Alerts sent via:
- Email
- Slack webhook
- Dashboard notifications

## Testing Integrations

```bash
# Test all integrations
python manage.py test-integrations

# Test specific integration
python manage.py test-integration linkedin

# Dry run (don't actually post)
python main.py social linkedin --text "Test post" --dry-run
```

## Troubleshooting

### "Authentication failed"
- Check token hasn't expired
- Verify scopes are correct
- Re-authorize: `python manage.py authorize <platform>`

### "Rate limit exceeded"
- Check usage in dashboard
- Reduce posting frequency
- Upgrade API tier if needed

### "API endpoint not found"
- Verify API version compatibility
- Check integration code is up to date
- Review platform's changelog

## Adding New Integrations

To add a new third-party integration:

1. **Create integration class**:
   ```bash
   cp integrations/linkedin.py integrations/your_platform.py
   ```

2. **Implement required methods**:
   - `__init__()`
   - `authenticate()`
   - `post()` / `create()` / `send()`
   - `get_analytics()`

3. **Add configuration**:
   - Update `.env.example`
   - Update `config/settings.py`

4. **Write tests**:
   ```bash
   # tests/integrations/test_your_platform.py
   pytest tests/integrations/test_your_platform.py
   ```

5. **Document**:
   - Add to this guide
   - Update SPECIFICATION.md

## API Documentation Links

- **LinkedIn**: https://docs.microsoft.com/en-us/linkedin/marketing/
- **Twitter**: https://developer.twitter.com/en/docs/twitter-api
- **HubSpot**: https://developers.hubspot.com/docs/api/overview
- **Google Analytics**: https://developers.google.com/analytics/devguides/reporting/data/v1
- **SendGrid**: https://docs.sendgrid.com/api-reference

## Support

For integration issues:
1. Check logs: `tail -f logs/integrations.log`
2. Test connection: `python manage.py test-integration <platform>`
3. Review API status: Check platform status page
4. Contact support: Issues tab on GitHub
