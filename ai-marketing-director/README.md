# AI Marketing Director v2.0

**The First Fully Autonomous Marketing Department Powered by AI**

Not a marketing tool. Not an assistant. **An entire marketing department.**

The AI Marketing Director is a revolutionary multiagent system that replaces traditional marketing teams with 14 specialized AI agents working collaboratively. Think of it as hiring a complete marketing department—CMO, managers, specialists—that works 24/7, never takes vacations, and costs a fraction of human staff.

## Architecture: Your Virtual Marketing Department

### 📊 Organizational Structure (14 Agents in 3 Tiers)

**Executive Layer** (Strategic Leadership):
- **CMO Agent**: Sets strategy, allocates budget, oversees performance
- **VP Marketing Agent**: Manages daily operations, coordinates teams
- **Director of Communications Agent**: Guards brand voice, approves messaging

**Management Layer** (Coordination & Quality):
- **Content Manager**: Oversees editorial calendar, content quality
- **Social Media Manager**: Platform strategy, engagement management
- **Campaign Manager**: Multi-channel campaigns, optimization

**Specialist Layer** (Execution & Expertise):
- **Copywriter**: Blog posts, case studies, thought leadership
- **SEO Specialist**: Keyword research, content optimization
- **Designer**: Visual assets, social graphics, infographics
- **Analytics Specialist**: Performance tracking, insights, reporting
- **Email Specialist**: Email campaigns, automation sequences
- **LinkedIn Manager**: LinkedIn content and engagement
- **Twitter Manager**: Twitter/X content and community
- **Market Research Agent**: Competitive intelligence, trends

### 🤝 How They Work Together

Agents collaborate like a real team:
- **Debate**: Agents discuss approaches and challenge each other
- **Peer Review**: Managers review specialist work before approval
- **Escalation**: Complex decisions escalate up the hierarchy
- **Learning**: Agents improve based on performance data

**Example Collaboration**:
```
Content Manager → Copywriter: "Write blog on AI ROI"
Copywriter → SEO Specialist: "What keywords should I target?"
SEO Specialist → Copywriter: "Focus on 'AI implementation costs'"
Copywriter → Designer: "Need header image on AI + ROI theme"
Copywriter → Content Manager: "Draft ready for review"
Content Manager → VP Marketing: "Approved, ready to publish"
VP Marketing → Social Media Manager: "Promote this blog"
```

### 🎯 Autonomy Levels

- **L4 (Fully Autonomous)**: 70% - Daily social posts, routine emails
- **L3 (Quick Approval)**: 20% - Blog posts (1-click approve)
- **L2 (Collaborative)**: 8% - Strategic campaigns
- **L1 (Human-Led)**: 2% - Crisis response, legal matters

## Features

### 🚀 Core Capabilities

- **🏢 Complete Marketing Department**: 14 specialized agents working as a team
- **🤝 Agent Collaboration**: Agents debate, negotiate, and improve each other's work
- **⚡ 10x Faster Execution**: Parallel workflows, no bottlenecks
- **🎯 Brand Voice Guardian**: Director of Comms ensures consistent messaging
- **📊 Real-Time Analytics**: Track every metric, optimize continuously
- **🔗 Platform Integrations**: LinkedIn, Twitter, HubSpot, Google Analytics
- **💰 Cost Efficient**: < $50 per content piece vs $500-1000 human cost
- **🤖 Powered by Claude**: Opus for strategy, Sonnet for execution, Haiku for routine

### 🎨 Multiagent Magic

- **Autonomous Decision-Making**: 80% of decisions happen without human input
- **Peer Review Process**: Managers approve specialist work
- **Debate & Negotiation**: Agents challenge each other for better outcomes
- **Escalation Protocols**: Complex decisions automatically escalate
- **Learning System**: Agents improve based on performance data
- **Role-Based Personalities**: Each agent has appropriate communication style

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your API keys

# Run the marketing director
python main.py
```

## Configuration

Set up your API keys in `.env`:
- `ANTHROPIC_API_KEY`: Claude API key
- `LINKEDIN_ACCESS_TOKEN`: LinkedIn API access
- `TWITTER_API_KEY`: Twitter API credentials
- `CRM_API_KEY`: HubSpot/Salesforce API key

## Usage

```bash
# Start the marketing director CLI
python main.py

# Run specific agent
python -m agents.strategy_agent

# Generate content
python main.py --task "create_linkedin_post" --topic "prompt engineering ROI"
```

## Third-Party Integrations

The system connects to external platforms for publishing and analytics:

### Supported Platforms

| Platform | Status | Authentication | Capabilities |
|----------|--------|----------------|--------------|
| **LinkedIn** | ✅ Ready | OAuth 2.0 | Post creation, analytics, scheduling |
| **Twitter/X** | ✅ Ready | OAuth 2.0 | Tweets, threads, engagement tracking |
| **HubSpot CRM** | ✅ Ready | API Key | Contact tracking, lead attribution |
| **Google Analytics** | ✅ Ready | Service Account | Traffic tracking, conversions |
| **SendGrid** | ✅ Ready | API Key | Email campaigns |

### How It Works

```python
from agents.social_media_agent import SocialMediaAgent

# Initialize agent (loads integrations automatically)
social = SocialMediaAgent()

# Generate and publish LinkedIn post
result = social.create_linkedin_post(
    topic="Why AI training matters",
    style="professional",
    publish=True  # Actually publishes to LinkedIn
)

# Get analytics
analytics = social.get_post_analytics(
    platform="linkedin",
    post_id=result["post_id"]
)
```

**Quick OAuth Setup:**
```bash
# 1. Configure OAuth credentials
../.venv/bin/python manage.py update-env

# 2. Authorize platforms
../.venv/bin/python manage.py authorize linkedin
../.venv/bin/python manage.py authorize twitter

# 3. Test connections
../.venv/bin/python manage.py test-integration linkedin

# 4. Try the demo
../.venv/bin/python demo_oauth.py
```

For detailed setup, see:
- **[OAUTH_README.md](OAUTH_README.md)** - Quick start guide
- **[OAUTH_SETUP_GUIDE.md](OAUTH_SETUP_GUIDE.md)** - Step-by-step instructions
- **[INTEGRATIONS_GUIDE.md](INTEGRATIONS_GUIDE.md)** - Technical details

## Project Status

🚧 **Phase 1**: Core infrastructure and Strategy Agent ✅ **COMPLETE**

## License

Proprietary - AI Elevate
