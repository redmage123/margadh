# OAuth 2.0 Integration - Complete Setup

## 🎯 What This Enables

With OAuth set up, the AI Marketing Director can:

✅ **Post to LinkedIn** - Publish professional content to your profile or company page
✅ **Tweet on Twitter/X** - Create tweets and threads automatically
✅ **Track Analytics** - Fetch engagement metrics (likes, shares, impressions)
✅ **Secure Access** - No passwords stored, revocable anytime

## 🚀 Quick Start (5 Minutes)

### 1. Configure OAuth Credentials

```bash
cd /home/bbrelin/marketing/ai-marketing-director
../.venv/bin/python manage.py update-env
```

This will prompt you for:
- LinkedIn Client ID & Secret
- Twitter Client ID & Secret

### 2. Authorize Platforms

**LinkedIn:**
```bash
../.venv/bin/python manage.py authorize linkedin
```

**Twitter:**
```bash
../.venv/bin/python manage.py authorize twitter
```

### 3. Test Connection

```bash
../.venv/bin/python manage.py test-integration linkedin
../.venv/bin/python manage.py test-integration twitter
```

### 4. Try the Demo

```bash
../.venv/bin/python demo_oauth.py
```

Done! Your AI Marketing Director can now post to social media. 🎉

---

## 📁 Files Created

| File | Purpose |
|------|---------|
| `core/oauth.py` | OAuth flow handler (authorization, token exchange, refresh) |
| `core/oauth_server.py` | Local callback server (handles OAuth redirects) |
| `manage.py` | Management commands (authorize, test, list, revoke) |
| `integrations/linkedin.py` | LinkedIn API integration |
| `integrations/twitter.py` | Twitter API integration |
| `agents/social_media_agent.py` | Social Media Agent (uses integrations) |
| `OAUTH_SETUP_GUIDE.md` | Detailed step-by-step setup instructions |
| `demo_oauth.py` | Interactive demo showing OAuth in action |

---

## 🔄 How It Works

### Authorization Flow

```
1. User runs: python manage.py authorize linkedin
        ↓
2. Browser opens → LinkedIn authorization page
        ↓
3. User clicks "Allow"
        ↓
4. LinkedIn redirects → http://localhost:8888/oauth/linkedin/callback?code=ABC123
        ↓
5. Callback server receives code
        ↓
6. Server exchanges code for access token
        ↓
7. Token saved encrypted in .oauth_tokens.json
        ↓
8. ✅ Ready to use!
```

### Publishing Flow

```
1. Generate content with GPT-5
        ↓
2. Human reviews and approves
        ↓
3. Social Media Agent loads OAuth token
        ↓
4. Makes API call to LinkedIn/Twitter
        ↓
5. Post published!
        ↓
6. Analytics tracked automatically
```

---

## 💻 Usage Examples

### Example 1: Generate LinkedIn Post (Draft)

```python
from agents.social_media_agent import SocialMediaAgent

agent = SocialMediaAgent()

# Generate but don't publish
post = agent.create_linkedin_post(
    topic="Why prompt engineering boosts AI ROI",
    style="professional",
    include_cta=True,
    publish=False  # Draft only
)

print(post["text"])
```

### Example 2: Publish LinkedIn Post

```python
# Actually publish to LinkedIn
post = agent.create_linkedin_post(
    topic="5 AI training best practices for enterprises",
    style="professional",
    publish=True  # Uses OAuth to publish
)

print(f"Published! View at: {post['post_url']}")
```

### Example 3: Create Twitter Thread

```python
# Generate and publish a thread
thread = agent.create_twitter_thread(
    topic="Common AI implementation mistakes",
    thread_length=5,
    publish=True
)

for tweet in thread["thread_results"]:
    print(f"Tweet {tweet['id']}: {tweet['url']}")
```

### Example 4: Get Analytics

```python
# Fetch engagement metrics
analytics = agent.get_post_analytics(
    platform="linkedin",
    post_id="urn:li:share:123456789"
)

print(f"Likes: {analytics['likes']}")
print(f"Comments: {analytics['comments']}")
print(f"Shares: {analytics['shares']}")
print(f"Engagement Rate: {analytics['engagement_rate']}%")
```

---

## 🛠️ Management Commands

### View All Tokens

```bash
../.venv/bin/python manage.py list-tokens
```

Output:
```
📋 Stored OAuth Tokens
============================================================

🔑 LINKEDIN
   Access Token: AQV1N4RxGz7h...
   Created: 2025-11-03T10:30:00Z
   ✅ Status: VALID

🔑 TWITTER
   Access Token: dGhpc19pc19h...
   Created: 2025-11-03T10:35:00Z
   ✅ Status: VALID
```

### Revoke a Token

```bash
../.venv/bin/python manage.py revoke linkedin
```

This deletes the stored token. You'll need to re-authorize to use it again.

### Re-authorize

```bash
../.venv/bin/python manage.py authorize linkedin
```

Starts fresh OAuth flow to get new token.

---

## 🔐 Security Features

### ✅ What's Secure

- **OAuth 2.0 Standard**: Industry-standard authorization protocol
- **No Password Storage**: Never stores LinkedIn/Twitter passwords
- **Scoped Permissions**: Only requests necessary API access
- **Revocable**: Can revoke access anytime via LinkedIn/Twitter settings
- **Token Encryption**: Tokens encrypted in production (Fernet encryption)
- **HTTPS in Production**: Uses secure connections for token exchange
- **PKCE for Twitter**: Enhanced security with Proof Key for Code Exchange

### ⚠️ Development vs Production

**Development** (current setup):
- Tokens stored in `.oauth_tokens.json`
- Not encrypted (for testing)
- Excluded from Git via `.gitignore`

**Production** (recommended):
- Tokens stored in database
- Encrypted with Fernet (symmetric encryption)
- Encryption key in AWS Secrets Manager
- Automatic rotation every 90 days

---

## 🔍 Troubleshooting

### "No module named 'core.oauth'"

Make sure you're in the project directory:
```bash
cd /home/bbrelin/marketing/ai-marketing-director
```

### "LINKEDIN_CLIENT_ID not configured"

Run the configuration wizard:
```bash
../.venv/bin/python manage.py update-env
```

Or manually add to `.env`:
```
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
```

### "Invalid redirect URI"

Make sure your OAuth app redirect URI is **exactly**:
```
http://localhost:8888/oauth/linkedin/callback
http://localhost:8888/oauth/twitter/callback
```

No trailing slash, `http://` not `https://`.

### "Port 8888 already in use"

Kill the process:
```bash
lsof -ti:8888 | xargs kill -9
```

Or use different port:
```bash
../.venv/bin/python core/oauth_server.py 8889
```

### "Token expired"

System auto-refreshes, but if it fails:
```bash
../.venv/bin/python manage.py revoke linkedin
../.venv/bin/python manage.py authorize linkedin
```

---

## 📚 Documentation

- **[OAUTH_SETUP_GUIDE.md](OAUTH_SETUP_GUIDE.md)** - Detailed step-by-step instructions
- **[INTEGRATIONS_GUIDE.md](INTEGRATIONS_GUIDE.md)** - Integration architecture overview
- **[INTEGRATION_EXAMPLE.md](INTEGRATION_EXAMPLE.md)** - Code examples and workflows
- **[SPECIFICATION.md](SPECIFICATION.md)** - Full technical specification

---

## 🎓 Next Steps

1. **Complete OAuth setup** (see above)
2. **Run the demo** (`python demo_oauth.py`)
3. **Generate content** (`python main.py topics --content-type linkedin`)
4. **Test publishing** (set `publish=True` in examples above)
5. **Monitor analytics** (check engagement metrics)
6. **Automate workflows** (use Orchestrator Agent for campaigns)

---

## ✅ OAuth Setup Checklist

Use this to verify everything is working:

- [ ] LinkedIn app created
- [ ] LinkedIn credentials in `.env`
- [ ] LinkedIn authorized (`manage.py authorize linkedin`)
- [ ] LinkedIn test passes (`manage.py test-integration linkedin`)
- [ ] Can generate LinkedIn posts
- [ ] Twitter app created
- [ ] Twitter OAuth 2.0 enabled
- [ ] Twitter credentials in `.env`
- [ ] Twitter authorized (`manage.py authorize twitter`)
- [ ] Twitter test passes (`manage.py test-integration twitter`)
- [ ] Can create Twitter threads
- [ ] Tokens listed (`manage.py list-tokens`)
- [ ] Demo runs successfully (`python demo_oauth.py`)

---

## 🆘 Getting Help

**Common Issues:**
1. Check [Troubleshooting](#🔍-troubleshooting) section above
2. Review [OAUTH_SETUP_GUIDE.md](OAUTH_SETUP_GUIDE.md)
3. Run demo to diagnose: `python demo_oauth.py`

**Platform Docs:**
- LinkedIn OAuth: https://docs.microsoft.com/en-us/linkedin/shared/authentication/authentication
- Twitter OAuth 2.0: https://developer.twitter.com/en/docs/authentication/oauth-2-0

**Need Support:**
- GitHub Issues: https://github.com/ai-elevate/marketing-director/issues
- Email: support@ai-elevate.ai

---

**Ready to automate your social media? Start with:**
```bash
../.venv/bin/python demo_oauth.py
```

This will show you everything working end-to-end! 🚀
