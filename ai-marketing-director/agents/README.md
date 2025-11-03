# Agents Directory

This directory contains all 14 AI agents organized in a 3-tier hierarchical structure.

## Structure

```
agents/
├── base/              # Base classes and shared utilities for all agents
├── executive/         # Executive layer (3 agents)
├── management/        # Management layer (3 agents)
└── specialists/       # Specialist layer (8 agents)
```

## Agent Organization

### Executive Layer (Strategic Leadership)
**Location**: `agents/executive/`

1. **CMO Agent** (`cmo/`)
   - **Role**: Chief Marketing Officer
   - **Responsibilities**: Overall strategy, budget allocation, performance oversight
   - **Model**: Claude Opus (strategic thinking)
   - **Autonomy**: L2-L3 (Collaborative/Consult & Execute)

2. **VP Marketing Agent** (`vp_marketing/`)
   - **Role**: Vice President of Marketing
   - **Responsibilities**: Day-to-day operations, team coordination
   - **Model**: Claude Opus (complex decision-making)
   - **Autonomy**: L3-L4 (Consult & Execute/Fully Autonomous)

3. **Director of Communications** (`director_comms/`)
   - **Role**: Brand Voice Guardian
   - **Responsibilities**: Brand messaging, PR, external communications
   - **Model**: Claude Sonnet (quality + speed)
   - **Autonomy**: L3 (Consult & Execute)

### Management Layer (Coordination & Quality)
**Location**: `agents/management/`

4. **Content Manager** (`content_manager/`)
   - **Role**: Editorial Oversight
   - **Responsibilities**: Content calendar, quality control, publishing approval
   - **Model**: Claude Sonnet
   - **Autonomy**: L3-L4

5. **Social Media Manager** (`social_media_manager/`)
   - **Role**: Social Strategy
   - **Responsibilities**: Platform management, engagement, posting schedule
   - **Model**: Claude Sonnet
   - **Autonomy**: L4 (Fully Autonomous for routine posts)

6. **Campaign Manager** (`campaign_manager/`)
   - **Role**: Multi-channel Campaigns
   - **Responsibilities**: Campaign execution, optimization, performance tracking
   - **Model**: Claude Sonnet
   - **Autonomy**: L3-L4

### Specialist Layer (Execution & Expertise)
**Location**: `agents/specialists/`

7. **Copywriter** (`copywriter/`)
   - **Specialization**: Content creation
   - **Output**: Blog posts, articles, case studies
   - **Model**: Claude Sonnet

8. **SEO Specialist** (`seo_specialist/`)
   - **Specialization**: Search optimization
   - **Output**: Keyword research, content optimization
   - **Model**: Claude Haiku (fast analysis)

9. **Designer** (`designer/`)
   - **Specialization**: Visual content
   - **Output**: Graphics, infographics, social images
   - **Model**: Claude Sonnet + Image generation APIs

10. **Analytics Specialist** (`analytics_specialist/`)
    - **Specialization**: Performance tracking
    - **Output**: Reports, insights, forecasts
    - **Model**: Claude Sonnet

11. **Email Specialist** (`email_specialist/`)
    - **Specialization**: Email marketing
    - **Output**: Email campaigns, automation sequences
    - **Model**: Claude Haiku

12. **LinkedIn Manager** (`linkedin_manager/`)
    - **Specialization**: LinkedIn content
    - **Output**: Professional posts, articles
    - **Model**: Claude Haiku

13. **Twitter Manager** (`twitter_manager/`)
    - **Specialization**: Twitter/X content
    - **Output**: Tweets, threads
    - **Model**: Claude Haiku

14. **Market Research** (`market_research/`)
    - **Specialization**: Competitive intelligence
    - **Output**: Trend analysis, competitor research
    - **Model**: Claude Sonnet

## Base Classes

**Location**: `agents/base/`

### Core Components

1. **`base_agent.py`**
   - Abstract base class for all agents
   - Defines common interface and behavior
   - Implements dependency injection

2. **`agent_protocol.py`**
   - Protocol definitions for agent interfaces
   - Ensures type safety across agent interactions

3. **`agent_config.py`**
   - Configuration models for agents
   - LLM settings, permissions, autonomy levels

4. **`agent_state.py`**
   - State management for agents
   - Handles agent lifecycle (active, busy, idle)

5. **`agent_memory.py`**
   - Short-term and long-term memory for agents
   - Context management across conversations

## Agent File Structure

Each agent directory follows this structure:

```
agent_name/
├── __init__.py              # Agent module exports
├── agent.py                 # Main agent class
├── config.py                # Agent-specific configuration
├── prompts.py               # LLM prompts and templates
├── validators.py            # Input/output validation
├── schemas.py               # Pydantic models for agent I/O
└── README.md                # Agent-specific documentation
```

## Development Standards

All agent code MUST follow:
- ✅ TDD (tests before implementation)
- ✅ Pure functions where possible
- ✅ Immutable data structures
- ✅ Type hints everywhere
- ✅ SOLID principles
- ✅ No nested loops or ifs

**Reference**: `DEVELOPMENT_STANDARDS.md`

## Agent Communication

Agents communicate via **Message Bus** (Redis):

```python
from infrastructure.message_bus import MessageBus

# Send message
await message_bus.publish(
    queue="copywriter_tasks",
    message={
        "from": "content_manager",
        "to": "copywriter",
        "type": "task_assignment",
        "payload": {"topic": "AI ROI"}
    }
)

# Receive message
message = await message_bus.subscribe(
    queue="content_manager_inbox",
    timeout=30
)
```

## Testing

Each agent requires:

1. **Unit Tests** (`tests/unit/agents/<agent_name>/`)
   - Test agent logic in isolation
   - Mock all dependencies (LLM, database, message bus)

2. **Integration Tests** (`tests/integration/agents/<agent_name>/`)
   - Test agent with real dependencies
   - Test agent-to-agent communication

3. **E2E Tests** (`tests/e2e/scenarios/`)
   - Test complete workflows involving multiple agents

## Implementation Priority

**Phase 1** (Current):
- [ ] Base agent classes
- [ ] CMO Agent
- [ ] Content Manager
- [ ] Copywriter

**Phase 2**:
- [ ] VP Marketing Agent
- [ ] Director of Communications
- [ ] SEO Specialist
- [ ] Designer

**Phase 3**:
- [ ] Social Media Manager
- [ ] LinkedIn Manager
- [ ] Twitter Manager
- [ ] Analytics Specialist

**Phase 4**:
- [ ] Campaign Manager
- [ ] Email Specialist
- [ ] Market Research Agent

## Quick Start

```python
# Example: Creating and using an agent
from agents.specialists.copywriter import CopywriterAgent
from infrastructure.llm import ClaudeLLM
from infrastructure.message_bus import MessageBus

# Initialize dependencies
llm = ClaudeLLM(model="claude-sonnet-3-5")
message_bus = MessageBus(redis_url="redis://localhost:6379")

# Create agent
copywriter = CopywriterAgent(
    llm=llm,
    message_bus=message_bus
)

# Execute task
result = await copywriter.create_blog_post(
    topic="Why AI Reduces Marketing Costs",
    word_count=1500,
    target_audience="B2B SaaS companies"
)
```

## Resources

- **Architecture**: `../MULTIAGENT_ARCHITECTURE.md`
- **Standards**: `../DEVELOPMENT_STANDARDS.md`
- **Specification**: `../SPECIFICATION.md`
- **Agent Templates**: `../templates/example_agent.py`
