# OAuth Setup Guide - Step by Step

This guide walks you through setting up OAuth 2.0 authentication for LinkedIn and Twitter so the AI Marketing Director can post on your behalf.

## 🎯 Overview

OAuth allows the AI Marketing Director to:
- Post content to LinkedIn and Twitter
- Fetch analytics and engagement metrics
- Access your social media accounts **securely** (no password sharing)

## 📋 Prerequisites

- LinkedIn account (personal or company page)
- Twitter/X account
- 10-15 minutes

---

## 🔷 Part 1: LinkedIn OAuth Setup

### Step 1: Create LinkedIn App

1. **Go to LinkedIn Developers**
   - Visit: https://www.linkedin.com/developers/apps
   - Click "Create app"

2. **Fill in App Details**
   ```
   App name: AI Marketing Director
   LinkedIn Page: [Select your company page]
   Privacy policy URL: https://ai-elevate.ai/privacy
   App logo: [Upload AI Elevate logo]
   ```

3. **Click "Create app"**

### Step 2: Configure OAuth Settings

1. **Navigate to "Auth" tab**

2. **Add Redirect URLs**
   ```
   http://localhost:8888/oauth/linkedin/callback
   ```
   Click "Add redirect URL" and save

3. **Request API Scopes**
   - Go to "Products" tab
   - Request access to:
     - ✅ **Sign In with LinkedIn using OpenID Connect**
     - ✅ **Share on LinkedIn**
     - ✅ **Marketing Developer Platform** (if available)

4. **Get Credentials**
   - Go back to "Auth" tab
   - Copy **Client ID**
   - Copy **Client Secret** (click "Show" first)

### Step 3: Add to AI Marketing Director

1. **Run configuration command**
   ```bash
   cd /home/bbrelin/marketing/ai-marketing-director
   ../.venv/bin/python manage.py update-env
   ```

2. **Enter LinkedIn credentials when prompted**
   ```
   LinkedIn Client ID: [paste your client ID]
   LinkedIn Client Secret: [paste your client secret]
   ```

3. **Or manually edit `.env` file**
   ```bash
   # OAuth Configuration - LinkedIn
   LINKEDIN_CLIENT_ID=your_client_id_here
   LINKEDIN_CLIENT_SECRET=your_client_secret_here
   LINKEDIN_REDIRECT_URI=http://localhost:8888/oauth/linkedin/callback
   ```

### Step 4: Authorize LinkedIn

1. **Run authorization command**
   ```bash
   ../.venv/bin/python manage.py authorize linkedin
   ```

2. **What happens:**
   - Browser opens automatically
   - You'll see LinkedIn authorization page
   - Click "Allow" to grant access
   - Browser redirects to success page
   - Token saved automatically

3. **Expected output:**
   ```
   🌐 OAuth callback server started on http://localhost:8888
   📡 Waiting for authorization callback...

   🔐 Starting OAuth flow for LINKEDIN
   ============================================================

   Opening browser for authorization...

   ✅ After authorizing, you'll be redirected to localhost:8888

   ✅ Successfully authorized linkedin!
   📝 Access token: abc123xyz...
   💾 Token saved to .oauth_tokens.json
   ```

### Step 5: Test LinkedIn Connection

```bash
../.venv/bin/python manage.py test-integration linkedin
```

**Expected output:**
```
🧪 Testing LINKEDIN integration...
✅ LinkedIn integration working!
   User ID: abc123xyz
   Organization: AI Elevate
```

---

## 🐦 Part 2: Twitter/X OAuth Setup

### Step 1: Create Twitter App

1. **Sign up for Twitter Developer Account**
   - Visit: https://developer.twitter.com/en/portal/petition/essential/basic-info
   - Fill out application (takes ~5 minutes)
   - Wait for approval (usually instant for basic access)

2. **Create a Project and App**
   - Go to: https://developer.twitter.com/en/portal/dashboard
   - Click "Create Project"
   - Project name: `AI Marketing Director`
   - Use case: `Making a bot`
   - Click "Next" → Create App
   - App name: `ai-marketing-director` (must be unique)

### Step 2: Configure OAuth 2.0

1. **Navigate to your app settings**
   - Click on your app name
   - Go to "Settings" tab

2. **Enable OAuth 2.0**
   - Scroll to "User authentication settings"
   - Click "Set up"

3. **Configure OAuth 2.0 settings**
   ```
   App permissions:
   ✅ Read and write

   Type of App:
   ✅ Web App, Automated App or Bot

   App info:
   Callback URI: http://localhost:8888/oauth/twitter/callback
   Website URL: https://ai-elevate.ai
   ```

4. **Save settings**

5. **Get Credentials**
   - Go to "Keys and tokens" tab
   - Under "OAuth 2.0 Client ID and Client Secret":
   - Copy **Client ID**
   - Copy **Client Secret**

### Step 3: Add to AI Marketing Director

1. **Run configuration command** (if you haven't already)
   ```bash
   ../.venv/bin/python manage.py update-env
   ```

2. **Enter Twitter credentials when prompted**
   ```
   Twitter Client ID: [paste your client ID]
   Twitter Client Secret: [paste your client secret]
   ```

3. **Or manually edit `.env` file**
   ```bash
   # OAuth Configuration - Twitter
   TWITTER_CLIENT_ID=your_client_id_here
   TWITTER_CLIENT_SECRET=your_client_secret_here
   TWITTER_REDIRECT_URI=http://localhost:8888/oauth/twitter/callback
   ```

### Step 4: Authorize Twitter

1. **Run authorization command**
   ```bash
   ../.venv/bin/python manage.py authorize twitter
   ```

2. **What happens:**
   - Browser opens to Twitter authorization page
   - Click "Authorize app"
   - Redirected to success page
   - Token saved

3. **Expected output:**
   ```
   🌐 OAuth callback server started on http://localhost:8888
   🔐 Starting OAuth flow for TWITTER
   Opening browser for authorization...

   ✅ Successfully authorized twitter!
   💾 Token saved to .oauth_tokens.json
   ```

### Step 5: Test Twitter Connection

```bash
../.venv/bin/python manage.py test-integration twitter
```

**Expected output:**
```
🧪 Testing TWITTER integration...
✅ Twitter integration working!
   Username: @AIElevate
   Followers: 1,234
```

---

## 🔧 Common Issues & Troubleshooting

### ❌ "Invalid redirect URI"

**Problem:** OAuth provider says redirect URI doesn't match

**Solution:**
1. Make sure redirect URI in app settings **exactly** matches:
   - LinkedIn: `http://localhost:8888/oauth/linkedin/callback`
   - Twitter: `http://localhost:8888/oauth/twitter/callback`
2. No trailing slash
3. Use `http://` not `https://` for localhost

### ❌ "Port 8888 already in use"

**Problem:** Another service is using port 8888

**Solution:**
```bash
# Kill process on port 8888
lsof -ti:8888 | xargs kill -9

# Or use a different port
../.venv/bin/python core/oauth_server.py 8889
```

Then update redirect URIs to use new port.

### ❌ "Scopes not granted"

**Problem:** App doesn't have required permissions

**Solution:**
- **LinkedIn**: Request "Share on LinkedIn" product access
- **Twitter**: Ensure "Read and write" permissions are enabled

### ❌ "Token expired"

**Problem:** Access token is no longer valid

**Solution:**
The system automatically refreshes tokens. If it fails:
```bash
# Re-authorize
../.venv/bin/python manage.py revoke linkedin
../.venv/bin/python manage.py authorize linkedin
```

### ❌ "Browser doesn't open"

**Problem:** `webbrowser.open()` fails on headless servers

**Solution:**
1. Copy the authorization URL from terminal
2. Open it manually in your browser
3. Complete authorization
4. Callback will still work

---

## 🎯 Quick Start Commands

```bash
# One-time setup
../.venv/bin/python manage.py update-env

# Authorize platforms
../.venv/bin/python manage.py authorize linkedin
../.venv/bin/python manage.py authorize twitter

# Test connections
../.venv/bin/python manage.py test-integration linkedin
../.venv/bin/python manage.py test-integration twitter

# List tokens
../.venv/bin/python manage.py list-tokens

# Revoke/re-authorize
../.venv/bin/python manage.py revoke linkedin
../.venv/bin/python manage.py authorize linkedin
```

---

## 🔐 Security Best Practices

### ✅ DO:
- Store `.env` file securely
- Add `.oauth_tokens.json` to `.gitignore` (already done)
- Use HTTPS in production (not localhost)
- Rotate tokens every 90 days
- Request only scopes you need

### ❌ DON'T:
- Commit OAuth credentials to Git
- Share Client Secret publicly
- Use production tokens in development
- Grant access to untrusted applications

---

## 📊 Using OAuth Tokens in Agents

Once authorized, agents automatically use tokens:

```python
from agents.social_media_agent import SocialMediaAgent

# Initialize (loads tokens automatically)
social = SocialMediaAgent()

# Create and publish LinkedIn post
result = social.create_linkedin_post(
    topic="AI productivity tips",
    style="professional",
    publish=True  # Uses OAuth token to publish
)

print(f"Published: {result['url']}")
```

---

## 🔄 Token Lifecycle

```
┌─────────────────────────────────────────┐
│  1. User authorizes app                 │
│     (via manage.py authorize)           │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  2. App receives access token           │
│     + refresh token (60-90 day expiry)  │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  3. Token stored encrypted              │
│     (.oauth_tokens.json)                │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  4. Agent uses token for API calls      │
│     (automatic in Social Media Agent)   │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  5. Token expires                       │
│     (typically after 60 days)           │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  6. System auto-refreshes token         │
│     (using refresh token)               │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  7. If refresh fails, user              │
│     re-authorizes (step 1)              │
└─────────────────────────────────────────┘
```

---

## 📚 Next Steps

After completing OAuth setup:

1. **Test posting**
   ```bash
   ../.venv/bin/python -m agents.social_media_agent
   ```

2. **Generate content**
   ```bash
   ../.venv/bin/python main.py topics --content-type linkedin --count 3
   ```

3. **Create and publish a post**
   ```python
   from agents.social_media_agent import SocialMediaAgent

   agent = SocialMediaAgent()
   agent.create_linkedin_post(
       topic="Enterprise AI training best practices",
       publish=True
   )
   ```

4. **Check analytics**
   ```python
   agent.get_post_analytics(platform="linkedin", post_id="your_post_id")
   ```

---

## 🆘 Need Help?

- **LinkedIn OAuth Docs**: https://docs.microsoft.com/en-us/linkedin/shared/authentication/authentication
- **Twitter OAuth Docs**: https://developer.twitter.com/en/docs/authentication/oauth-2-0
- **Check logs**: `tail -f logs/oauth.log`
- **GitHub Issues**: https://github.com/ai-elevate/marketing-director/issues

---

## ✅ Verification Checklist

- [ ] LinkedIn app created
- [ ] LinkedIn redirect URI configured
- [ ] LinkedIn credentials in `.env`
- [ ] LinkedIn authorized successfully
- [ ] LinkedIn test passes
- [ ] Twitter app created
- [ ] Twitter OAuth 2.0 enabled
- [ ] Twitter redirect URI configured
- [ ] Twitter credentials in `.env`
- [ ] Twitter authorized successfully
- [ ] Twitter test passes
- [ ] Tokens stored securely
- [ ] `.oauth_tokens.json` in `.gitignore`

Once all checked, you're ready to use the Social Media Agent! 🎉
