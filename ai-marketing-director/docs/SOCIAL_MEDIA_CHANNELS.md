# Social Media Channels Configuration

## Overview

The AI Marketing Director supports automated content management across multiple social media platforms. This document outlines the configured channels and their capabilities.

## Supported Platforms

### 1. LinkedIn (with Navigator Support) ✅

**Status**: Integrated
**Agent**: `LinkedInManagerAgent`
**Premium Features**: LinkedIn Navigator Premium Access

#### Capabilities

**Standard Features:**
- Post creation and scheduling
- Profile analytics
- Connection management
- Company page management
- Engagement tracking

**LinkedIn Navigator Premium Features:**
- ✨ **Advanced Lead Search**: Filter by title, company size, industry, location
- ✨ **InMail Messaging**: Direct messaging to prospects outside network
- ✨ **Sales Insights**: AI-powered lead recommendations
- ✨ **Enhanced Analytics**: Unlimited profile views and advanced metrics
- ✨ **Lead List Management**: Save and organize prospect lists

#### Configuration

```python
from infrastructure.integrations.linkedin import LinkedInClient

client = LinkedInClient(
    access_token="your_linkedin_access_token",
    has_navigator=True  # Enable Navigator features
)
```

#### Navigator Benefits for Marketing

1. **Lead Generation**: Advanced search filters help identify ideal prospects
2. **Outreach**: InMail enables direct communication with decision-makers
3. **Intelligence**: Sales insights provide market trends and competitor intel
4. **Efficiency**: Automated workflows with Navigator API integration

---

### 2. Bluesky ✅

**Status**: Newly Integrated
**Agent**: `BlueskyManagerAgent`
**Protocol**: AT Protocol (Decentralized)

#### Capabilities

**Core Features:**
- Post creation (300 character limit)
- Threaded posts (Bluesky threads)
- Hashtag optimization
- Profile analytics
- Content search

**AI-Powered Features:**
- LLM-optimized post generation
- Hashtag research and suggestions
- Content tone optimization
- Audience targeting

#### Configuration

```python
from infrastructure.integrations.bluesky import BlueskyClient

client = BlueskyClient(
    handle="company.bsky.social",
    app_password="your_app_password"  # Not your account password!
)
```

#### Why Bluesky?

1. **Early Adopter Advantage**: Growing platform with engaged tech community
2. **Decentralized**: AT Protocol enables unique integration possibilities
3. **Tech Audience**: Strong presence of developers, AI/ML practitioners
4. **Open Protocol**: Future-proof integration with open standards

---

### 3. Twitter/X

**Status**: Integration Scaffold Ready
**Agent**: `TwitterManagerAgent`
**API**: Twitter API v2

#### Planned Capabilities

- Tweet creation and scheduling
- Thread creation
- Engagement tracking
- Trending topic monitoring
- Audience analytics

---

## Agent Roles

### Specialist Layer Social Media Agents

1. **`LINKEDIN_MANAGER`** (`linkedin_manager`)
   - Professional networking and B2B marketing
   - Lead generation and nurturing
   - Thought leadership content

2. **`BLUESKY_MANAGER`** (`bluesky_manager`)
   - Decentralized social engagement
   - Tech community outreach
   - Early adopter audience

3. **`TWITTER_MANAGER`** (`twitter_manager`)
   - Real-time engagement
   - Trending topic participation
   - Community management

### Management Layer

**`SOCIAL_MEDIA_MANAGER`** (`social_media_manager`)
- Coordinates all social media agents
- Cross-platform content strategy
- Performance analytics aggregation

---

## Usage Examples

### Posting to Bluesky

```python
from agents.specialists.bluesky_manager import BlueskyManagerAgent
from agents.base import AgentConfig, AgentRole, Task, TaskPriority

# Initialize agent
config = AgentConfig(
    agent_id="bluesky_001",
    role=AgentRole.BLUESKY_MANAGER,
)

agent = BlueskyManagerAgent(
    config=config,
    bluesky_handle="company.bsky.social",
    bluesky_app_password="app-specific-password"
)

# Create post
task = Task(
    task_id="post_001",
    task_type="create_post",
    priority=TaskPriority.NORMAL,
    parameters={
        "content": "Excited to announce our latest AI-powered marketing insights!",
        "tags": ["AI", "Marketing", "Innovation"],
        "optimize": True  # Use LLM to optimize content
    },
    assigned_to=AgentRole.BLUESKY_MANAGER,
    assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
    created_at=datetime.now()
)

result = await agent.execute(task)
```

### LinkedIn Navigator Lead Search

```python
from infrastructure.integrations.linkedin import LinkedInClient

async with LinkedInClient(
    access_token="token",
    has_navigator=True
) as client:
    # Search for marketing directors at mid-size companies
    leads = await client.search_leads(
        title="Marketing Director",
        company_size="1001-5000",
        industry="Technology",
        location="San Francisco Bay Area",
        limit=50
    )

    # Send personalized InMail
    for lead in leads:
        await client.send_inmail(
            recipient_id=lead["id"],
            subject="Innovative Marketing Automation",
            message=personalized_message
        )
```

---

## API Keys and Authentication

### Required Credentials

1. **LinkedIn**
   - OAuth2 Access Token
   - Navigator subscription credentials

2. **Bluesky**
   - Handle (e.g., `company.bsky.social`)
   - App-specific password (generate in Bluesky settings)

3. **Twitter/X**
   - API Key
   - API Secret
   - Access Token
   - Access Token Secret

### Environment Variables

```bash
# LinkedIn
LINKEDIN_ACCESS_TOKEN=your_token
LINKEDIN_HAS_NAVIGATOR=true

# Bluesky
BLUESKY_HANDLE=company.bsky.social
BLUESKY_APP_PASSWORD=your_app_password

# Twitter
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_TOKEN_SECRET=your_secret
```

---

## Content Strategy Guidelines

### Platform-Specific Best Practices

#### LinkedIn
- **Length**: 1,300-1,900 characters optimal
- **Format**: Professional, value-driven content
- **Frequency**: 1-2 posts per day
- **Best Times**: Tuesday-Thursday, 8-10 AM
- **Content Types**: Industry insights, company news, thought leadership
- **Navigator**: Use for targeted B2B outreach and lead generation

#### Bluesky
- **Length**: Up to 300 characters
- **Format**: Conversational, tech-savvy
- **Frequency**: 3-5 posts per day
- **Best Times**: Evenings and weekends (tech audience)
- **Content Types**: Quick updates, technical insights, community engagement
- **Threads**: Use for longer-form content

#### Twitter/X
- **Length**: Up to 280 characters (or longer with subscription)
- **Format**: Concise, engaging, timely
- **Frequency**: 3-5 tweets per day
- **Best Times**: Peak engagement varies by audience
- **Content Types**: News, updates, conversations, threads

---

## Analytics and Metrics

### Tracked Metrics

1. **Engagement**
   - Likes, comments, shares
   - Click-through rates
   - Engagement rate percentage

2. **Reach**
   - Impressions
   - Follower growth
   - Profile visits

3. **Conversion** (Navigator)
   - Lead generation
   - InMail response rates
   - Connection acceptance rates

4. **Content Performance**
   - Best performing content types
   - Optimal posting times
   - Hashtag effectiveness

---

## Roadmap

### Phase 1 (Current)
- ✅ Bluesky integration complete
- ✅ LinkedIn with Navigator support
- ✅ Agent role definitions

### Phase 2 (Upcoming)
- 🔄 Twitter/X full integration
- 🔄 Instagram integration
- 🔄 Facebook/Meta integration

### Phase 3 (Future)
- 📋 TikTok integration
- 📋 YouTube Shorts integration
- 📋 Cross-platform content recycling
- 📋 AI-powered A/B testing

---

## Notes for Development Team

1. **Bluesky App Passwords**: Must be generated in Bluesky settings, not account password
2. **LinkedIn Navigator**: Requires active subscription, check availability before using Navigator-only features
3. **Rate Limits**: Each platform has different rate limits, implement backoff strategies
4. **Content Guidelines**: Each platform has community guidelines, ensure compliance
5. **Testing**: Use sandbox/test accounts for development and testing

---

## Support and Resources

- **Bluesky Documentation**: https://docs.bsky.app/
- **LinkedIn API**: https://learn.microsoft.com/en-us/linkedin/
- **Twitter API**: https://developer.twitter.com/en/docs
- **AT Protocol**: https://atproto.com/

---

**Last Updated**: 2025-11-03
**Maintained By**: AI Marketing Director Development Team
