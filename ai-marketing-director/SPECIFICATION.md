# AI Marketing Director - Software Specification & Design Document

**Version**: 2.0
**Date**: 2025-11-03
**Organization**: AI Elevate
**Status**: Major Architecture Redesign - Multiagent Department
**Paradigm Shift**: From Marketing Tool → Autonomous Marketing Department

---

## 🚨 MAJOR PARADIGM SHIFT (v1.0 → v2.0)

### From Marketing Tool → Marketing Department

**What Changed:**
- **v1.0**: AI agents assisted human marketers (tool paradigm)
- **v2.0**: AI agents ARE the marketing department (autonomous paradigm)

| Aspect | v1.0 (Tool) | v2.0 (Department) |
|--------|-------------|-------------------|
| **Role** | Marketing assistant | Complete marketing team |
| **Structure** | 1 orchestrator + 5 utility agents | 14 role-based agents in 3-tier org |
| **Decision Making** | Human approves everything | 80% autonomous decisions |
| **Communication** | Tool → Human | Agent ↔ Agent collaboration |
| **Autonomy** | Low (waits for human) | High (self-organizing team) |
| **Workflow** | Sequential human-gated | Parallel agent collaboration |
| **Personality** | Generic agents | Role-specific personalities |
| **Team Dynamics** | None | Debate, negotiation, peer review |

**Key Innovation**: Agents don't just execute tasks—they collaborate, disagree, debate solutions, and improve each other's work. Just like a real marketing team.

**Reference**: See [MULTIAGENT_ARCHITECTURE.md](./MULTIAGENT_ARCHITECTURE.md) for complete details.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Overview](#2-system-overview)
   - 2.4 [Development Standards](#24-development-standards) ⭐ **MANDATORY**
3. [Architecture Design](#3-architecture-design)
4. [Component Specifications](#4-component-specifications)
5. [Data Models](#5-data-models)
6. [API Specifications](#6-api-specifications)
7. [Integration Specifications](#7-integration-specifications)
8. [User Interface](#8-user-interface)
9. [Security & Privacy](#9-security--privacy)
10. [Deployment Architecture](#10-deployment-architecture)
11. [Testing Strategy](#11-testing-strategy)
12. [Implementation Roadmap](#12-implementation-roadmap)
13. [Appendices](#13-appendices)

---

## 1. Executive Summary

### 1.1 Purpose

**NEW VISION (v2.0)**: The AI Marketing Director is no longer just a tool—it IS the marketing department.

The AI Marketing Director is a fully autonomous marketing department powered by collaborative AI agents. Instead of assisting human marketers, it replaces the traditional marketing team structure with specialized AI agents that work together like a real organization. The system leverages Claude (Anthropic) to create a complete marketing department with executives, managers, and specialists who collaborate, make decisions, and execute campaigns with minimal human oversight.

### 1.2 Scope

**NEW ORGANIZATIONAL MODEL**:

The system creates an entire marketing department with three organizational layers:

**Executive Layer** (Strategy & Leadership):
- CMO Agent: Overall strategy, budget, performance oversight
- VP Marketing Agent: Day-to-day operations, team coordination
- Director of Communications: Brand voice, messaging, PR

**Management Layer** (Coordination & Quality):
- Content Manager: Editorial strategy, content calendar, quality control
- Social Media Manager: Social strategy, platform management
- Campaign Manager: Multi-channel campaigns, optimization

**Specialist Layer** (Execution & Expertise):
- Copywriter, SEO Specialist, Designer, Analytics Specialist
- Email Specialist, LinkedIn Manager, Twitter Manager
- Market Research Agent

**Total Team Size**: 14 specialized agents working collaboratively

**Autonomy Levels**:
- L4 (Fully Autonomous): 70% of operations
- L3 (Consult & Execute): 20% of operations
- L2 (Collaborative): 8% of operations
- L1 (Human-Led): 2% of operations (legal, crisis)

**Out of Scope** (Future Enhancements):
- Paid advertising management (Google Ads, LinkedIn Ads)
- SEO technical optimization beyond content
- Website development
- Video production
- Direct sales automation

### 1.3 Success Criteria

**Autonomy & Efficiency**:
- **Agent Autonomy**: 80%+ of decisions made without human intervention
- **Task Completion Rate**: 95%+ success rate on assigned tasks
- **Execution Speed**: 10x faster than traditional human teams
- **Cost Efficiency**: < $50 per content piece (vs $500-1000 human cost)

**Output & Quality**:
- **Content Output**: 50+ high-quality pieces per week
- **Brand Voice Consistency**: 95%+ across all content
- **SEO Performance**: 85%+ optimization scores
- **Publishing Velocity**: < 24 hours from ideation to publication

**Business Impact**:
- **Lead Generation**: 100+ marketing qualified leads per month
- **Engagement Rate**: 5%+ across social channels
- **Cost per Lead**: < $100 (vs $200-400 industry average)
- **ROI**: 5x return on investment within 6 months
- **Human Oversight**: < 2 hours/day of human involvement

**Team Collaboration**:
- **Inter-Agent Collaboration**: Agents successfully work together on 95%+ of complex projects
- **Escalation Rate**: < 10% of decisions escalated to humans
- **Conflict Resolution**: Agents resolve 90%+ of disagreements autonomously

### 1.4 Stakeholders

**AI Agent Team** (Primary Operators):
| Agent Role | Responsibility | Decision Authority |
|-----------|---------------|-------------------|
| CMO Agent | Strategic direction, budget allocation | Final marketing strategy |
| VP Marketing Agent | Daily operations, team coordination | Campaign and content approval |
| Director of Comms Agent | Brand voice, messaging | External communications |
| Content Manager Agent | Editorial oversight | Content publishing |
| Social Media Manager Agent | Social strategy | Platform content |
| Campaign Manager Agent | Campaign execution | Campaign tactics |
| Specialist Agents (8) | Domain expertise | Specialized decisions |

**Human Oversight** (Strategic & Exceptional):
| Role | Responsibility | Approval Authority |
|------|---------------|-------------------|
| Executive Sponsor | Strategic vision, final escalations | Legal, crisis, major budget changes |
| Technical Owner | System maintenance, agent performance | Infrastructure, agent configuration |
| Brand Guardian (optional) | Periodic brand voice audits | Override on brand violations |

**Key Paradigm Shift**:
- AI agents handle 80-90% of all marketing operations autonomously
- Humans set strategic direction and handle exceptional cases
- Agents collaborate, debate, and make decisions like a real team

---

## 2. System Overview

### 2.1 High-Level Architecture (Multiagent Department Model)

```
┌─────────────────────────────────────────────────────────────┐
│                  HUMAN INTERFACE LAYER                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Web UI      │  │   Chat UI    │  │  Mobile App  │      │
│  │  (Monitoring)│  │  (Strategy)  │  │  (Approval)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↕ (Strategic Input & Escalations)
┌─────────────────────────────────────────────────────────────┐
│                   EXECUTIVE AGENT LAYER                      │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ CMO Agent   │  │   VP          │  │ Director of  │      │
│  │ (Strategy & │  │   Marketing   │  │ Communications│     │
│  │  Budget)    │  │   Agent       │  │  Agent        │      │
│  │             │  │  (Operations) │  │ (Brand Voice) │      │
│  └─────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↕ (Direction & Approval)
┌─────────────────────────────────────────────────────────────┐
│                   MANAGEMENT AGENT LAYER                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Content    │  │ Social Media │  │   Campaign   │     │
│  │   Manager    │  │   Manager    │  │   Manager    │     │
│  │   Agent      │  │   Agent      │  │   Agent      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↕ (Coordination & Tasks)
┌─────────────────────────────────────────────────────────────┐
│                   SPECIALIST AGENT LAYER                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │Copy-    │  │   SEO   │  │Designer │  │Analytics│       │
│  │writer   │  │Specialist│  │  Agent  │  │Specialist│       │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │ Email   │  │LinkedIn │  │ Twitter │  │ Market  │       │
│  │Specialist│  │ Manager │  │ Manager │  │Research │       │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
└─────────────────────────────────────────────────────────────┘
                            ↕ (Execution & Data)
┌─────────────────────────────────────────────────────────────┐
│            AGENT COMMUNICATION & ORCHESTRATION               │
│  ┌────────────────────────────────────────────────────┐     │
│  │      Message Bus (Redis Streams & Pub/Sub)         │     │
│  │  - Agent-to-agent messaging                        │     │
│  │  - Event streaming                                 │     │
│  │  - Collaboration protocols                         │     │
│  │  - Decision tracking                               │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                    INTEGRATION LAYER                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │LinkedIn  │  │ Twitter  │  │ HubSpot  │  │ Analytics│   │
│  │   API    │  │   API    │  │   CRM    │  │   API    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │PostgreSQL│  │  Redis   │  │  Vector  │  │   S3     │   │
│  │(Content &│  │(Messages │  │    DB    │  │ (Assets) │   │
│  │ Tasks)   │  │ & Cache) │  │(Knowledge│  │          │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                     CORE SERVICES                            │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │Brand Voice │  │  Claude    │  │  Logging & │            │
│  │ & Rules    │  │  APIs      │  │  Metrics   │            │
│  │ Engine     │  │(Opus/Sonnet│  │(Prometheus)│            │
│  └────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────────────────────────────────────────┘

KEY ARCHITECTURAL CHANGES:
- 14 autonomous agents organized in 3-tier hierarchy
- Agents communicate directly via message bus
- No central "orchestrator" - decisions emerge from collaboration
- Humans interface at executive level for strategy
- 80%+ autonomous decision-making
```

### 2.2 Technology Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| **AI/LLM** | Claude (Anthropic) + OpenAI | Superior reasoning, long context, brand safety; Multi-provider support |
| **Agent Framework** | Custom BaseAgent + LangGraph | TDD-tested agent framework; Production-ready orchestration |
| **Backend** | Python 3.12+ | AI/ML ecosystem, rapid development |
| **API Framework** | FastAPI | High performance, async support, auto-documentation |
| **Database** | PostgreSQL 15+ | Robust relational DB, JSON support |
| **Cache/Message Bus** | Redis 7+ | Pub/Sub messaging, session management, rate limiting |
| **Social Media APIs** | atproto (Bluesky), linkedin-api | AT Protocol for decentralized social, LinkedIn Marketing API |
| **Vector DB** | Pinecone/Weaviate | Semantic search, content similarity |
| **Task Queue** | Celery | Background job processing |
| **Frontend** | React + Next.js | Modern, SEO-friendly, fast |
| **Deployment** | Docker + K8s | Scalability, portability |
| **Cloud** | AWS/GCP | Reliability, global availability |
| **Monitoring** | Prometheus + Grafana | Metrics, alerting, dashboards |
| **Logging** | ELK Stack | Centralized logging, debugging |
| **Testing** | pytest + black + mypy | TDD framework, formatting, type checking |

### 2.3 Design Principles

1. **Human-in-the-Loop**: All content requires human review before publication
2. **Brand Consistency**: Enforce AI Elevate brand voice across all content
3. **Modularity**: Each agent is independent and replaceable
4. **Scalability**: Handle increased load without architectural changes
5. **Security First**: API keys, data encryption, access control
6. **Observability**: Comprehensive logging, metrics, tracing
7. **Fail-Safe**: Graceful degradation, retries, fallbacks

### 2.4 Development Standards

**All code MUST follow the mandatory development standards** defined in [DEVELOPMENT_STANDARDS.md](./DEVELOPMENT_STANDARDS.md).

#### 2.4.1 Core Requirements

**Test-Driven Development (TDD)**:
- ✅ All code written using Red-Green-Refactor cycle
- ✅ Tests written BEFORE implementation
- ✅ No code committed without corresponding tests

**Five Required Test Types**:
1. **Unit Tests**: 90%+ code coverage, mocked dependencies
2. **Integration Tests**: Real dependencies (database, message bus, APIs)
3. **End-to-End Tests**: Complete user workflows in staging environment
4. **Lint Tests**: black, flake8, pylint, mypy must all pass
5. **Regression Tests**: One test per bug fix, never deleted

**Code Quality Standards**:
- ✅ **Pythonic Code**: Use comprehensions, map/filter, type hints, f-strings
- ✅ **No Nested For Loops**: Use list comprehensions or itertools
- ✅ **No Nested Ifs**: Use guard clauses or strategy pattern
- ✅ **Functional Patterns**: Pure functions, immutability, composition, declarative style
- ✅ **SOLID Principles**: Every class follows SRP, OCP, LSP, ISP, DIP
- ✅ **Explicit Comments**: Explain WHAT, WHY, and HOW in every function

**Documentation Requirements**:
- ✅ Type hints on all functions and methods
- ✅ Docstrings with WHY and HOW explanations
- ✅ Inline comments for complex logic
- ✅ Architecture Decision Records (ADRs) for major decisions

#### 2.4.2 Templates and Examples

Developers must use the provided templates when creating new code:

**Test Templates** (`templates/tests/`):
- `test_unit_template.py`: Unit test structure with fixtures and mocks
- `test_integration_template.py`: Integration test patterns with real services
- `test_e2e_template.py`: End-to-end workflow testing

**Configuration Files** (`templates/`):
- `pytest.ini`: Pytest configuration with markers and coverage
- `.pylintrc`: Code quality checks and naming conventions
- `.flake8`: PEP 8 style enforcement
- `mypy.ini`: Type checking configuration
- `pyproject.toml`: Black formatter and isort settings

**Code Examples** (`templates/`):
- `example_agent.py`: Complete agent following all standards
- `example_tdd_workflow.md`: Step-by-step TDD process

#### 2.4.3 Pre-Commit Checklist

Before committing code, developers must run:

```bash
# 1. Format code
black . && isort .

# 2. Lint checks
flake8 && pylint agents/ infrastructure/

# 3. Type checks
mypy .

# 4. Run tests
pytest

# 5. Coverage check
pytest --cov --cov-fail-under=80
```

**All checks must pass** before code can be committed.

#### 2.4.4 Continuous Integration

GitHub Actions CI/CD enforces standards automatically:
- ❌ Pull requests **BLOCKED** if any lint/test fails
- ❌ Deployment **BLOCKED** if coverage < 80%
- ❌ Merging **BLOCKED** if type checks fail

**Reference Documents**:
- **[DEVELOPMENT_STANDARDS.md](./DEVELOPMENT_STANDARDS.md)**: Complete mandatory standards (~12,000 words)
- **[templates/README.md](./templates/README.md)**: Template usage guide
- **[MULTIAGENT_ARCHITECTURE.md](./MULTIAGENT_ARCHITECTURE.md)**: Architecture patterns for agents

---

## 3. Architecture Design

### 3.1 Multi-Agent Architecture

The system uses a **hierarchical multi-agent architecture** where:

1. **Orchestrator Agent** acts as the central coordinator
2. **Specialized Agents** handle domain-specific tasks
3. **Agents communicate** through a message bus (Redis)
4. **State is persisted** in PostgreSQL
5. **Results are cached** for performance

#### 3.1.1 Agent Communication Flow

```
User Request
     ↓
Orchestrator Agent
     ↓
Task Planning & Breakdown
     ↓
┌─────────┬─────────┬─────────┐
↓         ↓         ↓         ↓
Strategy  Content   Social    Campaign
Agent     Agent     Agent     Agent
↓         ↓         ↓         ↓
└─────────┴─────────┴─────────┘
     ↓
Result Aggregation
     ↓
Human Review Queue
     ↓
Approval/Rejection
     ↓
Publication/Iteration
```

### 3.2 Data Flow Architecture

```
┌─────────────┐
│ User Input  │
└──────┬──────┘
       ↓
┌──────────────────┐
│  Orchestrator    │
│  - Parse intent  │
│  - Create tasks  │
└──────┬───────────┘
       ↓
┌──────────────────┐
│  Task Queue      │
│  (Redis/Celery)  │
└──────┬───────────┘
       ↓
┌──────────────────┐
│  Agent Execution │
│  - Retrieve ctx  │
│  - Call LLM      │
│  - Process result│
└──────┬───────────┘
       ↓
┌──────────────────┐
│  Result Storage  │
│  (PostgreSQL)    │
└──────┬───────────┘
       ↓
┌──────────────────┐
│  Review Queue    │
│  (Human approval)│
└──────┬───────────┘
       ↓
┌──────────────────┐
│  Publication     │
│  (External APIs) │
└──────────────────┘
```

### 3.3 Security Architecture

```
┌─────────────────────────────────────────┐
│         API Gateway / Load Balancer      │
│  - Rate limiting                         │
│  - DDoS protection                       │
│  - SSL/TLS termination                   │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│         Authentication Layer             │
│  - JWT tokens                            │
│  - API key validation                    │
│  - Role-based access control (RBAC)     │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│         Application Layer                │
│  - Input validation                      │
│  - SQL injection prevention              │
│  - XSS protection                        │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│         Data Layer                       │
│  - Encryption at rest                    │
│  - Encryption in transit                 │
│  - Secrets management (AWS Secrets Mgr)  │
└─────────────────────────────────────────┘
```

---

## 4. Component Specifications

### 4.0 CMO Agent (Chief Marketing Officer - Executive Layer)

**Purpose**: Top-level executive supervisory agent providing strategic oversight, resource allocation, and coordination across all marketing activities.

**Role in Hierarchy**: Executive Layer - supervises all management-layer agents (Campaign Manager, Social Media Manager, Content Manager).

**Responsibilities**:
- Define and maintain overall marketing strategy aligned with business objectives
- Approve/reject campaign proposals based on strategic alignment and resource availability
- Allocate marketing budget across campaigns and channels
- Monitor consolidated performance metrics across all marketing activities
- Coordinate multi-campaign marketing initiatives and cross-functional projects
- Generate executive-level reports and insights for stakeholders
- Set priorities and resolve conflicts between competing marketing initiatives
- Maintain strategic state (goals, budgets, priorities, approved strategies)

**Supported Task Types**:

1. **create_marketing_strategy**: Define overall marketing objectives, target audiences, and strategic initiatives
2. **approve_campaign**: Review campaign proposals and approve/reject based on strategic criteria
3. **allocate_budget**: Distribute marketing budget across campaigns, channels, and time periods
4. **monitor_performance**: Aggregate and analyze performance data from all management agents
5. **coordinate_initiative**: Orchestrate multi-campaign initiatives requiring cross-functional coordination
6. **generate_executive_report**: Create high-level marketing performance summaries for stakeholders
7. **set_priorities**: Establish priority levels for campaigns and resolve resource conflicts
8. **review_manager_performance**: Evaluate management agent effectiveness and adjust delegation strategies

**Key Methods**:

```python
class CMOAgent(BaseAgent):
    """
    Executive-layer agent for strategic marketing oversight.

    WHY: Provides unified strategic direction and resource coordination.
    HOW: Supervises management agents, maintains strategy state, delegates execution.
    """

    async def _create_marketing_strategy(
        self,
        task: Task
    ) -> dict[str, Any]:
        """
        WHY: Establish strategic foundation for all marketing activities.
        HOW: Analyzes objectives, creates strategy, stores in state.
        """

    async def _approve_campaign(
        self,
        task: Task
    ) -> dict[str, Any]:
        """
        WHY: Ensure campaigns align with strategy and resources.
        HOW: Fetches campaign details from Campaign Manager, evaluates, approves/rejects.
        """

    async def _allocate_budget(
        self,
        task: Task
    ) -> dict[str, Any]:
        """
        WHY: Optimize resource allocation across marketing activities.
        HOW: Analyzes priorities, ROI, distributes budget, tracks allocations.
        """

    async def _monitor_performance(
        self,
        task: Task
    ) -> dict[str, Any]:
        """
        WHY: Track overall marketing effectiveness and identify issues.
        HOW: Aggregates metrics from all management agents, generates insights.
        """

    async def _coordinate_initiative(
        self,
        task: Task
    ) -> dict[str, Any]:
        """
        WHY: Synchronize multi-campaign efforts for maximum impact.
        HOW: Delegates coordinated tasks to multiple managers, tracks progress.
        """

    async def _generate_executive_report(
        self,
        task: Task
    ) -> dict[str, Any]:
        """
        WHY: Provide stakeholders with strategic marketing insights.
        HOW: Collects data from all layers, analyzes trends, formats report.
        """

    async def _set_priorities(
        self,
        task: Task
    ) -> dict[str, Any]:
        """
        WHY: Guide resource allocation and resolve conflicts.
        HOW: Evaluates strategic importance, sets priority levels, notifies managers.
        """
```

**State Management**:
- **Marketing Strategy**: Current strategy document (objectives, target audiences, key initiatives)
- **Budget Allocations**: Total budget, per-campaign allocations, remaining budget
- **Campaign Approvals**: Approved campaigns, pending approvals, rejected campaigns with reasons
- **Priority Matrix**: Campaign priorities, resource allocation priorities
- **Performance Baselines**: KPIs, targets, historical performance data
- **Manager Registry**: References to all management-layer agents for delegation

**Delegation Pattern**:

```python
# CMO maintains registry of management agents
self._managers: dict[AgentRole, BaseAgent] = {
    AgentRole.CAMPAIGN_MANAGER: campaign_manager_instance,
    AgentRole.SOCIAL_MEDIA_MANAGER: social_media_manager_instance,
    AgentRole.CONTENT_MANAGER: content_manager_instance,
}

# Delegates through management layer (never directly to specialists)
async def _approve_campaign(self, task: Task):
    # Get campaign details FROM Campaign Manager
    campaign_manager = self._managers[AgentRole.CAMPAIGN_MANAGER]
    status_task = self._create_manager_task(...)
    campaign_data = await campaign_manager.execute(status_task)

    # Make approval decision
    approval = self._evaluate_campaign(campaign_data)

    # Delegate launch THROUGH Campaign Manager
    if approval["approved"]:
        launch_task = self._create_manager_task(...)
        result = await campaign_manager.execute(launch_task)
```

**Architecture Compliance**:
- ✅ **Strategy Pattern**: Dictionary dispatch for all task types (zero if/elif chains)
- ✅ **Guard Clauses**: Early returns for validation, no nested ifs
- ✅ **Full Type Hints**: All methods fully typed with return types
- ✅ **WHY/HOW Documentation**: Every method documents reasoning and implementation
- ✅ **Exception Wrapping**: All external calls wrapped with AgentExecutionError
- ✅ **Graceful Degradation**: Continues operating if individual managers fail
- ✅ **TDD Methodology**: Tests written first (RED-GREEN-REFACTOR)

**Error Handling**:
- Wrap all manager execution calls in try-except blocks
- Continue with partial results if some managers fail
- Track failed delegations for later retry or escalation
- Never propagate manager failures to human unless critical

**Strategic Decision Making**:

```python
def _evaluate_campaign(self, campaign_data: dict[str, Any]) -> dict[str, Any]:
    """
    WHY: Ensure campaigns meet strategic criteria before approval.
    HOW: Evaluates against strategy, budget, priorities, returns decision.

    Strategic Criteria:
    - Alignment with current marketing strategy
    - Budget availability and ROI projections
    - Priority relative to other campaigns
    - Resource availability and timing
    - Risk assessment and brand safety
    """
```

**Integration with Management Layer**:

```
CMO Agent
    │
    ├─> Campaign Manager (campaign lifecycle, multi-channel coordination)
    ├─> Social Media Manager (social media strategy, platform coordination)
    ├─> Content Manager (content strategy, editorial oversight)
    ├─> Email Specialist (email campaign strategy)
    └─> Analytics Specialist (consolidated reporting, insights)
```

**Future Enhancements**:
- Machine learning for budget optimization
- Predictive analytics for campaign performance
- A/B testing strategies across campaigns
- Automated strategy adjustment based on performance
- Integration with VP Marketing and Director of Communications agents

---

### 4.1 Orchestrator Agent

**Purpose**: Central coordinator for all marketing automation tasks

**Responsibilities**:
- Parse user requests and determine intent
- Break down complex objectives into discrete tasks
- Route tasks to appropriate specialized agents
- Manage task dependencies and execution order
- Aggregate results from multiple agents
- Handle errors and retries
- Maintain workflow state

**Key Methods**:

```python
class OrchestratorAgent:
    def plan_marketing_initiative(
        self,
        objective: str,
        timeframe: str
    ) -> MarketingPlan

    def create_task(
        self,
        task_type: TaskType,
        description: str,
        priority: TaskPriority
    ) -> Task

    def execute_workflow(
        self,
        workflow: Workflow
    ) -> WorkflowResult

    def suggest_next_actions(
        self,
        context: str
    ) -> List[Action]
```

**State Management**:
- Task queue (pending, in-progress, completed)
- Workflow state (active workflows, dependencies)
- Agent availability (which agents are busy)

**Error Handling**:
- Retry failed tasks up to 3 times
- Escalate to human after 3 failures
- Log all errors with context
- Graceful degradation if agents unavailable

### 4.2 Strategy Agent

**Purpose**: Market research, competitive analysis, strategic recommendations

**Responsibilities**:
- Analyze market trends and opportunities
- Conduct competitor analysis
- Suggest content topics based on trends
- Provide strategic marketing recommendations
- Identify audience insights

**Key Methods**:

```python
class StrategyAgent:
    def analyze_market_trends(
        self,
        industry: str,
        timeframe: str = "current"
    ) -> TrendsAnalysis

    def analyze_competitor(
        self,
        competitor_name: str,
        competitor_url: Optional[str] = None
    ) -> CompetitorAnalysis

    def suggest_content_topics(
        self,
        content_type: ContentType,
        count: int = 5,
        based_on: Optional[str] = None
    ) -> List[TopicSuggestion]

    def strategic_recommendation(
        self,
        context: str,
        goals: List[str]
    ) -> StrategyRecommendation
```

**Data Sources**:
- Web search for market trends
- Competitor websites and content
- Industry reports and studies
- Internal performance data

**Output Format**:
- Structured JSON with analysis
- Confidence scores for recommendations
- Supporting evidence and citations
- Actionable next steps

### 4.3 Content Manager Agent (Management Layer)

**Purpose**: Management-layer agent coordinating content creation, ensuring quality, and managing editorial calendar.

**Role in Hierarchy**: Management Layer - supervises specialist agents (Copywriter, SEO Specialist, Designer) and coordinates with Campaign and Social Media Managers.

**Responsibilities**:
- Manage content strategy and editorial calendar
- Coordinate content creation across specialist agents
- Ensure content quality and brand consistency
- Track content performance and ROI
- Brief specialists on content requirements
- Review and approve content before publishing
- Optimize content for engagement and SEO
- Manage content library and versioning

**Supported Task Types**:

1. **create_content**: Coordinate specialists to create content
2. **review_content**: Review and approve/reject content for quality
3. **schedule_content**: Add content to editorial calendar
4. **generate_content_ideas**: Generate content ideas aligned with strategy
5. **optimize_content**: Optimize existing content for SEO/engagement
6. **get_content_performance**: Track content metrics across channels
7. **manage_content_calendar**: Manage editorial calendar and deadlines
8. **brief_specialists**: Create detailed content briefs for specialists

**Key Methods**:

```python
class ContentManagerAgent(BaseAgent):
    """
    Management-layer agent for content coordination.

    WHY: Provides unified content strategy and quality control.
    HOW: Coordinates specialists, manages calendar, enforces standards.
    """

    async def _create_content(
        self,
        task: Task
    ) -> dict[str, Any]:
        """
        WHY: Coordinate multi-specialist content creation.
        HOW: Delegates to Copywriter, SEO, Designer; manages workflow.
        """

    async def _review_content(
        self,
        task: Task
    ) -> dict[str, Any]:
        """
        WHY: Ensure content meets quality and brand standards.
        HOW: Reviews against criteria, approves/rejects/requests revisions.
        """

    async def _schedule_content(
        self,
        task: Task
    ) -> dict[str, Any]:
        """
        WHY: Plan content publication for optimal timing.
        HOW: Adds to editorial calendar, checks conflicts, sets deadlines.
        """

    async def _generate_content_ideas(
        self,
        task: Task
    ) -> dict[str, Any]:
        """
        WHY: Align content creation with marketing strategy.
        HOW: Analyzes trends, audience needs, campaign objectives.
        """

    async def _optimize_content(
        self,
        task: Task
    ) -> dict[str, Any]:
        """
        WHY: Improve performance of existing content.
        HOW: Delegates to SEO Specialist for optimization.
        """

    async def _get_content_performance(
        self,
        task: Task
    ) -> dict[str, Any]:
        """
        WHY: Track content effectiveness and ROI.
        HOW: Aggregates metrics from all channels, calculates ROI.
        """

    async def _manage_content_calendar(
        self,
        task: Task
    ) -> dict[str, Any]:
        """
        WHY: Organize content production and publication.
        HOW: Manages calendar state, deadlines, dependencies.
        """

    async def _brief_specialists(
        self,
        task: Task
    ) -> dict[str, Any]:
        """
        WHY: Provide clear direction for content creation.
        HOW: Creates detailed briefs with requirements, goals, constraints.
        """
```

**State Management**:
- **Editorial Calendar**: Scheduled content, deadlines, publication dates
- **Content Library**: Created, published, archived content with metadata
- **Content Briefs**: Active briefs for specialists
- **Quality Standards**: Brand voice criteria, SEO requirements, style guidelines
- **Performance Data**: Content metrics, engagement rates, conversion data
- **Specialist Registry**: References to Copywriter, SEO, Designer agents

**Delegation Pattern**:

```python
# Content Manager maintains registry of specialist agents
self._specialists: dict[AgentRole, BaseAgent] = {
    AgentRole.COPYWRITER: copywriter_instance,
    AgentRole.SEO_SPECIALIST: seo_specialist_instance,
    AgentRole.DESIGNER: designer_instance,
}

# Delegates content creation through specialist layer
async def _create_content(self, task: Task):
    # Delegate to Copywriter for draft
    copywriter = self._specialists[AgentRole.COPYWRITER]
    draft_task = self._create_specialist_task(...)
    draft = await copywriter.execute(draft_task)

    # Delegate to SEO Specialist for optimization
    seo = self._specialists[AgentRole.SEO_SPECIALIST]
    seo_task = self._create_specialist_task(...)
    optimized = await seo.execute(seo_task)

    # Store in content library
    content_id = self._store_content(optimized)

    return {"content_id": content_id, "status": "ready_for_review"}
```

**Content Lifecycle States**:

```python
CONTENT_STATES = {
    "draft": "Initial draft created by Copywriter",
    "review": "Under review by Content Manager",
    "revision": "Needs revision - sent back to specialists",
    "approved": "Approved for publishing",
    "scheduled": "Scheduled for publication",
    "published": "Published to channels",
    "archived": "Archived content"
}
```

**Architecture Compliance**:
- ✅ **Strategy Pattern**: Dictionary dispatch for all task types (zero if/elif chains)
- ✅ **Guard Clauses**: Early returns for validation, no nested ifs
- ✅ **Full Type Hints**: All methods fully typed with return types
- ✅ **WHY/HOW Documentation**: Every method documents reasoning and implementation
- ✅ **Exception Wrapping**: All external calls wrapped with AgentExecutionError
- ✅ **Graceful Degradation**: Continues operating if individual specialists fail
- ✅ **TDD Methodology**: Tests written first (RED-GREEN-REFACTOR)

**Error Handling**:
- Wrap all specialist execution calls in try-except blocks
- Continue with partial content if some specialists fail
- Log failed delegations for later retry
- Never block content pipeline due to specialist failures

**Quality Assurance Criteria**:

```python
def _evaluate_content_quality(self, content: dict[str, Any]) -> dict[str, Any]:
    """
    WHY: Ensure content meets brand and quality standards.
    HOW: Evaluates against multiple criteria, returns pass/fail.

    Quality Criteria:
    - Brand voice consistency (score > 70/100)
    - Readability (Flesch-Kincaid grade level appropriate)
    - SEO optimization (keyword density, meta tags present)
    - Grammar and spelling (zero critical errors)
    - Content structure (proper headings, formatting)
    - Call-to-action present (if required)
    """
```

**Integration with Other Managers**:

```
Content Manager
    │
    ├─> Campaign Manager (receives content requests for campaigns)
    ├─> Social Media Manager (provides content for social posts)
    ├─> Copywriter (delegates writing tasks)
    ├─> SEO Specialist (delegates optimization)
    └─> Designer (delegates visual creation)
```

**Future Enhancements**:
- AI-powered content idea generation
- Automated A/B testing for content variations
- Content personalization for audience segments
- Integration with CMS (WordPress, HubSpot)
- Automated content repurposing across formats
- Content gap analysis and opportunity identification

### 4.4 Social Media Agent

**Purpose**: Create and manage social media content

**Responsibilities**:
- Generate platform-specific posts (LinkedIn, Twitter)
- Schedule content publication
- Monitor engagement and mentions
- Suggest optimal posting times
- Create content calendars

**Key Methods**:

```python
class SocialMediaAgent:
    def create_linkedin_post(
        self,
        topic: str,
        style: PostStyle = PostStyle.PROFESSIONAL,
        include_cta: bool = True,
        hashtags: List[str] = None
    ) -> LinkedInPost

    def create_twitter_thread(
        self,
        topic: str,
        thread_length: int = 5
    ) -> TwitterThread

    def suggest_content_calendar(
        self,
        duration: str = "1 month",
        frequency: int = 3  # posts per week
    ) -> ContentCalendar

    def analyze_engagement(
        self,
        platform: Platform,
        post_ids: List[str]
    ) -> EngagementAnalysis
```

**Platform Specifications**:

| Platform | Max Length | Optimal Length | Best Times | Hashtag Count |
|----------|-----------|----------------|------------|---------------|
| LinkedIn | 3000 chars | 1200-1500 | Tue-Thu 9am-11am | 3-5 |
| Twitter/X | 280 chars | 100-250 | Wed-Fri 9am-3pm | 1-2 |

**Engagement Tracking**:
- Likes, comments, shares
- Click-through rates
- Follower growth
- Best performing content types
- Optimal posting schedule

### 4.5 Campaign Agent

**Purpose**: Email marketing and nurture campaigns

**Responsibilities**:
- Design email sequences
- Segment audiences
- Personalize content
- A/B test variations
- Track campaign performance

**Key Methods**:

```python
class CampaignAgent:
    def create_email_sequence(
        self,
        campaign_goal: str,
        audience_segment: str,
        sequence_length: int = 5
    ) -> EmailSequence

    def segment_audience(
        self,
        criteria: Dict[str, Any]
    ) -> AudienceSegment

    def generate_ab_test(
        self,
        base_email: Email,
        test_variants: List[str]  # subject, cta, body
    ) -> ABTest

    def analyze_campaign_performance(
        self,
        campaign_id: str
    ) -> CampaignMetrics
```

**Email Sequence Types**:
1. **Welcome Series**: New subscriber onboarding
2. **Nurture Series**: Move prospects through funnel
3. **Re-engagement**: Win back inactive subscribers
4. **Product Launch**: Announce new offerings
5. **Event Promotion**: Webinar/conference registration

**Metrics Tracked**:
- Open rate
- Click-through rate (CTR)
- Conversion rate
- Unsubscribe rate
- Revenue per email

### 4.6 Analytics Specialist Agent (Specialist Layer)

**Layer**: Specialist Layer (Execution & Expertise)
**Role**: Data analysis, performance tracking, insights generation
**Reports To**: CMO, Campaign Manager, Social Media Manager, Content Manager

**Purpose**: Provide comprehensive analytics, performance tracking, and data-driven insights across all marketing channels.

**WHY**: Unified analytics capability ensures data-driven decision-making across all management layers, tracks campaign effectiveness, and provides actionable insights for optimization.

**Architecture Compliance**:
- ✅ Strategy Pattern (dictionary dispatch for task routing)
- ✅ Guard clauses only (no nested ifs)
- ✅ Full type hints on all methods
- ✅ WHY/HOW documentation
- ✅ Exception wrapping with `AgentExecutionError`
- ✅ Graceful degradation
- ✅ TDD methodology

---

#### 4.6.1 Core Responsibilities

1. **Performance Tracking**: Track metrics across all marketing channels (web, social, campaigns)
2. **Report Generation**: Create comprehensive analytical reports for management agents
3. **KPI Monitoring**: Monitor key performance indicators against targets
4. **Audience Analysis**: Analyze audience demographics, behavior, and engagement
5. **Conversion Tracking**: Track conversion funnels and attribution
6. **Data Integration**: Integrate with Google Analytics, social media APIs, internal database
7. **Insights Generation**: Generate data-driven insights and recommendations
8. **Real-Time Monitoring**: Track ongoing campaign performance in real-time

---

#### 4.6.2 Task Types (Strategy Pattern)

The Analytics Specialist supports 8 task types using Strategy Pattern (zero if/elif chains):

```python
class AnalyticsSpecialistAgent(BaseAgent):
    """
    Specialist-layer agent for analytics and performance tracking.

    WHY: Provides unified analytics capability across all marketing channels.
    HOW: Integrates with external APIs (Google Analytics, social media) and
         internal database to track, analyze, and report on marketing performance.
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize Analytics Specialist Agent.

        WHY: Set up analytics integrations and task handler registry.
        HOW: Initializes external API clients, caching system, and
             registers task handlers using Strategy Pattern.
        """
        super().__init__(config)

        # External integrations
        self._google_analytics_client: Optional[GoogleAnalyticsClient] = None
        self._social_media_clients: dict[str, Any] = {}

        # Caching for API rate limiting
        self._analytics_cache: dict[str, tuple[datetime, dict[str, Any]]] = {}
        self._cache_ttl_minutes: int = 30

        # Metrics storage
        self._tracked_metrics: dict[str, dict[str, Any]] = {}

        # Strategy Pattern: Dictionary dispatch (zero if/elif chains)
        self._task_handlers: dict[
            str, Callable[[Task], Coroutine[Any, Any, dict[str, Any]]]
        ] = {
            "track_campaign_performance": self._track_campaign_performance,
            "generate_report": self._generate_report,
            "analyze_audience": self._analyze_audience,
            "monitor_kpis": self._monitor_kpis,
            "track_conversions": self._track_conversions,
            "get_social_analytics": self._get_social_analytics,
            "get_web_analytics": self._get_web_analytics,
            "generate_insights": self._generate_insights,
        }
```

---

#### 4.6.3 Task Type Specifications

##### 1. track_campaign_performance

**Purpose**: Track comprehensive metrics for specific campaigns.

**Parameters**:
```python
{
    "campaign_id": str,              # Campaign to track
    "metrics": List[str],            # Metrics to track (impressions, clicks, conversions, ROI)
    "date_range": str,               # Date range (e.g., "last_7_days", "2025-01-01_2025-01-31")
}
```

**Returns**:
```python
{
    "campaign_id": str,
    "metrics": {
        "impressions": int,
        "clicks": int,
        "ctr": float,              # Click-through rate
        "conversions": int,
        "conversion_rate": float,
        "cost": float,
        "cpc": float,              # Cost per click
        "roi": float,              # Return on investment
    },
    "date_range": str,
    "timestamp": str,
}
```

**Implementation**:
```python
async def _track_campaign_performance(self, task: Task) -> dict[str, Any]:
    """
    Track performance metrics for a specific campaign.

    WHY: Provides campaign managers with performance data for optimization.
    HOW: Aggregates metrics from multiple sources (web analytics, social media,
         internal database) and calculates derived metrics (CTR, ROI).
    """
    campaign_id = task.parameters["campaign_id"]
    metrics = task.parameters.get("metrics", ["impressions", "clicks", "conversions"])
    date_range = task.parameters["date_range"]

    # Guard clause: Validate campaign exists
    if not self._campaign_exists(campaign_id):
        return {
            "error": f"Campaign {campaign_id} not found",
            "campaign_id": campaign_id,
        }

    # Aggregate metrics from multiple sources
    aggregated_metrics = await self._aggregate_campaign_metrics(
        campaign_id=campaign_id,
        metrics=metrics,
        date_range=date_range
    )

    return {
        "campaign_id": campaign_id,
        "metrics": aggregated_metrics,
        "date_range": date_range,
        "timestamp": datetime.now().isoformat(),
    }
```

##### 2. generate_report

**Purpose**: Generate comprehensive analytical reports.

**Parameters**:
```python
{
    "report_type": str,          # "executive_dashboard", "campaign_performance", "content_performance"
    "date_range": str,           # Date range for report
    "include_charts": bool,      # Whether to include visualization data
}
```

**Returns**:
```python
{
    "report_id": str,
    "report_type": str,
    "summary": {
        "key_metrics": dict[str, Any],
        "highlights": List[str],
        "concerns": List[str],
    },
    "detailed_data": dict[str, Any],
    "recommendations": List[str],
    "generated_at": str,
}
```

##### 3. analyze_audience

**Purpose**: Analyze audience demographics, behavior, and segments.

**Parameters**:
```python
{
    "analysis_type": str,        # "demographics", "behavior", "interests"
    "date_range": str,
    "segments": List[str],       # Optional audience segments
}
```

**Returns**:
```python
{
    "demographics": {
        "age_distribution": dict[str, float],
        "gender_distribution": dict[str, float],
        "location_distribution": dict[str, float],
    },
    "behavior": {
        "device_usage": dict[str, float],
        "visit_frequency": dict[str, int],
        "engagement_patterns": dict[str, Any],
    },
    "interests": List[dict[str, Any]],
    "segments": dict[str, dict[str, Any]],
}
```

##### 4. monitor_kpis

**Purpose**: Monitor key performance indicators against targets.

**Parameters**:
```python
{
    "kpi_names": List[str],      # KPIs to monitor
    "targets": dict[str, float], # Target values for KPIs
    "alert_threshold": float,    # % deviation to trigger alert (e.g., 0.1 = 10%)
}
```

**Returns**:
```python
{
    "kpis": {
        "kpi_name": {
            "current_value": float,
            "target_value": float,
            "variance": float,      # % difference from target
            "status": str,          # "on_track", "at_risk", "below_target"
        }
    },
    "alerts": List[dict[str, Any]],  # KPIs that need attention
    "timestamp": str,
}
```

##### 5. track_conversions

**Purpose**: Track conversion funnels and attribution.

**Parameters**:
```python
{
    "funnel_name": str,          # Conversion funnel to track
    "date_range": str,
    "attribution_model": str,    # "first_touch", "last_touch", "linear"
}
```

**Returns**:
```python
{
    "funnel_name": str,
    "stages": {
        "stage_name": {
            "count": int,
            "conversion_rate": float,  # % to next stage
            "drop_off_rate": float,
        }
    },
    "attribution": dict[str, dict[str, Any]],
    "total_conversions": int,
}
```

##### 6. get_social_analytics

**Purpose**: Retrieve social media analytics across platforms.

**Parameters**:
```python
{
    "platforms": List[str],      # ["linkedin", "twitter", "bluesky"]
    "metrics": List[str],        # ["engagement", "reach", "followers"]
    "date_range": str,
}
```

**Returns**:
```python
{
    "platforms": {
        "platform_name": {
            "followers": int,
            "engagement_rate": float,
            "reach": int,
            "impressions": int,
            "top_posts": List[dict[str, Any]],
        }
    },
    "aggregated": {
        "total_followers": int,
        "avg_engagement_rate": float,
        "total_reach": int,
    },
}
```

##### 7. get_web_analytics

**Purpose**: Retrieve website analytics from Google Analytics.

**Parameters**:
```python
{
    "metrics": List[str],        # ["sessions", "pageviews", "bounceRate"]
    "dimensions": List[str],     # ["page", "source", "device"]
    "date_range": str,
}
```

**Returns**:
```python
{
    "metrics": dict[str, Any],
    "dimensions": dict[str, dict[str, Any]],
    "top_pages": List[dict[str, Any]],
    "traffic_sources": dict[str, int],
    "date_range": str,
}
```

##### 8. generate_insights

**Purpose**: Generate data-driven insights and recommendations.

**Parameters**:
```python
{
    "focus_area": str,           # "campaigns", "content", "audience"
    "date_range": str,
}
```

**Returns**:
```python
{
    "insights": List[{
        "title": str,
        "description": str,
        "impact": str,           # "high", "medium", "low"
        "supporting_data": dict[str, Any],
    }],
    "recommendations": List[{
        "action": str,
        "rationale": str,
        "expected_impact": str,
        "priority": str,
    }],
}
```

---

#### 4.6.4 Integration Points

**External APIs**:
- **Google Analytics API**: Website traffic, user behavior, conversions
- **LinkedIn Analytics API**: Post engagement, follower growth, demographics
- **Twitter Analytics API**: Tweet performance, audience insights
- **Bluesky Analytics**: Post metrics (when available)

**Internal Database**:
- Campaign metadata and performance
- Content performance metrics
- Historical analytics data

**Caching Strategy**:
```python
async def _get_cached_or_fetch(
    self,
    cache_key: str,
    fetch_fn: Callable[[], Coroutine[Any, Any, dict[str, Any]]]
) -> dict[str, Any]:
    """
    Get data from cache or fetch fresh data.

    WHY: Reduces API calls and respects rate limits.
    HOW: Checks cache with TTL, returns cached data if fresh,
         otherwise fetches and caches new data.
    """
    # Guard clause: Check cache
    if cache_key in self._analytics_cache:
        cached_time, cached_data = self._analytics_cache[cache_key]
        time_elapsed = datetime.now() - cached_time

        if time_elapsed < timedelta(minutes=self._cache_ttl_minutes):
            return cached_data

    # Fetch fresh data
    try:
        fresh_data = await fetch_fn()
        self._analytics_cache[cache_key] = (datetime.now(), fresh_data)
        return fresh_data
    except Exception as e:
        # Graceful degradation: Return stale cache if available
        if cache_key in self._analytics_cache:
            _, stale_data = self._analytics_cache[cache_key]
            return {**stale_data, "warning": "Using stale cached data"}

        raise AgentExecutionError(
            agent_id=self.agent_id,
            task_id="unknown",
            message=f"Failed to fetch analytics data: {str(e)}",
            original_exception=e
        )
```

---

#### 4.6.5 Key Metrics Tracked

**Campaign Metrics**:
```python
CAMPAIGN_METRICS = {
    "impressions": "Number of times content was displayed",
    "clicks": "Number of clicks on content",
    "ctr": "Click-through rate (clicks/impressions)",
    "conversions": "Number of conversions",
    "conversion_rate": "Conversion rate (conversions/clicks)",
    "cost": "Total campaign cost",
    "cpc": "Cost per click",
    "cpa": "Cost per acquisition",
    "roi": "Return on investment",
    "engagement_rate": "Social media engagement rate",
}
```

**Audience Metrics**:
```python
AUDIENCE_METRICS = {
    "demographics": "Age, gender, location distribution",
    "interests": "Audience interests and affinities",
    "devices": "Device usage (mobile, desktop, tablet)",
    "behavior": "User behavior patterns",
    "segments": "Audience segments and personas",
}
```

**Content Metrics**:
```python
CONTENT_METRICS = {
    "views": "Total content views",
    "time_on_page": "Average time spent on content",
    "scroll_depth": "How far users scroll",
    "shares": "Social media shares",
    "comments": "Number of comments",
    "bounce_rate": "% of single-page sessions",
}
```

**Web Analytics Metrics**:
```python
WEB_METRICS = {
    "sessions": "Total website sessions",
    "users": "Unique users",
    "pageviews": "Total page views",
    "bounce_rate": "% of single-page sessions",
    "avg_session_duration": "Average session duration",
    "pages_per_session": "Average pages per session",
}
```

---

#### 4.6.6 Graceful Degradation

**Strategy**: Analytics Specialist continues operating even when external APIs fail.

```python
async def _aggregate_campaign_metrics(
    self,
    campaign_id: str,
    metrics: List[str],
    date_range: str
) -> dict[str, Any]:
    """
    Aggregate metrics from multiple sources with graceful degradation.

    WHY: Ensures partial results even if some sources fail.
    HOW: Attempts to fetch from all sources, logs failures, returns
         aggregated data from successful sources.
    """
    aggregated = {}
    errors = []

    # Try Google Analytics
    try:
        web_data = await self._fetch_web_analytics(campaign_id, date_range)
        aggregated.update(web_data)
    except Exception as e:
        errors.append(f"Google Analytics unavailable: {str(e)}")

    # Try social media APIs
    try:
        social_data = await self._fetch_social_analytics(campaign_id, date_range)
        aggregated.update(social_data)
    except Exception as e:
        errors.append(f"Social media analytics unavailable: {str(e)}")

    # Always try internal database
    try:
        db_data = await self._fetch_database_metrics(campaign_id, date_range)
        aggregated.update(db_data)
    except Exception as e:
        errors.append(f"Database unavailable: {str(e)}")

    # Add warnings if any sources failed
    if errors:
        aggregated["warnings"] = errors
        aggregated["partial_data"] = True

    return aggregated
```

---

#### 4.6.7 Testing Strategy

**Unit Tests** (12+ tests):
- All 8 task types with mocked external APIs
- Caching logic verification
- Graceful degradation scenarios
- Metric calculation accuracy
- API failure handling

**Integration Tests** (6+ tests):
- Full workflows with real database, mocked external APIs
- Cross-source data aggregation
- Report generation with multiple data sources
- Real-time KPI monitoring
- Cache performance under load

**Example Test**:
```python
@pytest.mark.asyncio
async def test_track_campaign_performance(
    self, agent_config, mock_google_analytics, mock_social_apis
):
    """Test tracking campaign performance with multiple data sources."""
    agent = AnalyticsSpecialistAgent(config=agent_config)
    agent._google_analytics_client = mock_google_analytics
    agent._social_media_clients = mock_social_apis

    task = Task(
        task_type="track_campaign_performance",
        parameters={
            "campaign_id": "campaign_001",
            "metrics": ["impressions", "clicks", "conversions"],
            "date_range": "last_7_days",
        }
    )

    result = await agent.execute(task)

    assert result.status == TaskStatus.COMPLETED
    assert "metrics" in result.result
    assert result.result["metrics"]["impressions"] > 0
    mock_google_analytics.get_analytics.assert_called()
```

---

#### 4.6.8 Performance Considerations

**Caching**:
- Cache TTL: 30 minutes for most analytics data
- Cache key format: `{source}:{metric}:{date_range}`
- Cache invalidation: On-demand when fresh data required

**Rate Limiting**:
- Google Analytics: 10 queries per second
- Social Media APIs: Platform-specific limits
- Batch queries when possible to minimize API calls

**Data Freshness**:
- Real-time metrics: No caching (campaign monitoring)
- Daily metrics: 30-minute cache
- Historical metrics: 24-hour cache

---

#### 4.6.9 Coordination with Management Agents

```python
# CMO requests executive dashboard
cmo -> analytics_specialist.generate_report(
    report_type="executive_dashboard",
    date_range="Q1_2025"
)

# Campaign Manager tracks campaign performance
campaign_manager -> analytics_specialist.track_campaign_performance(
    campaign_id="campaign_001",
    metrics=["impressions", "conversions", "roi"]
)

# Social Media Manager gets social analytics
social_media_manager -> analytics_specialist.get_social_analytics(
    platforms=["linkedin", "twitter"],
    date_range="last_30_days"
)

# Content Manager tracks content performance
content_manager -> analytics_specialist.get_web_analytics(
    metrics=["pageviews", "time_on_page", "bounce_rate"],
    dimensions=["page"]
)
```

---

### 4.7 Copywriter Specialist Agent (Specialist Layer)

**Layer**: Specialist Layer (Execution & Expertise)
**Role**: Content creation, brand voice consistency, multi-format writing
**Reports To**: Content Manager, Campaign Manager, Social Media Manager

**Purpose**: Create high-quality written content across multiple formats while maintaining brand voice consistency.

**WHY**: Specialized writing expertise ensures high-quality, on-brand content creation at scale across all marketing channels.

**Architecture Compliance**:
- ✅ Strategy Pattern (dictionary dispatch for task routing)
- ✅ Guard clauses only (no nested ifs)
- ✅ Full type hints on all methods
- ✅ WHY/HOW documentation
- ✅ Exception wrapping with `AgentExecutionError`
- ✅ Graceful degradation
- ✅ TDD methodology

---

#### 4.7.1 Core Responsibilities

1. **Content Creation**: Write blog posts, social media posts, emails, case studies, product descriptions
2. **Brand Voice Consistency**: Maintain and enforce brand voice across all content
3. **Multi-Format Writing**: Adapt writing style for different content types and channels
4. **Content Variation**: Generate multiple versions for A/B testing
5. **Quality Validation**: Check content against readability and brand standards
6. **Rewriting**: Rewrite existing content with new tone or style
7. **Headline Generation**: Create compelling headlines and subject lines
8. **LLM Integration**: Use Claude for content generation with custom prompts

---

#### 4.7.2 Task Types (Strategy Pattern)

The Copywriter Specialist supports 8 task types using Strategy Pattern (zero if/elif chains):

```python
class CopywriterSpecialistAgent(BaseAgent):
    """
    Specialist-layer agent for content creation and writing.

    WHY: Provides specialized writing expertise for all marketing content.
    HOW: Uses LLM (Claude) with brand voice guidelines to generate high-quality content.
    """

    def __init__(self, config: AgentConfig, brand_voice: Optional[BrandVoiceGuidelines] = None):
        """
        Initialize Copywriter Specialist Agent.

        WHY: Set up LLM integration, brand voice, and task handler registry.
        HOW: Initializes LLM client, loads brand guidelines, and
             registers task handlers using Strategy Pattern.
        """
        super().__init__(config)

        # LLM integration
        self._llm_client: Optional[LLMClient] = None

        # Brand voice configuration
        self._brand_voice: Optional[BrandVoiceGuidelines] = brand_voice

        # Content templates
        self._content_templates: dict[str, str] = {}

        # Quality thresholds
        self._min_brand_voice_score: float = 70.0
        self._min_readability_score: float = 60.0

        # Strategy Pattern: Dictionary dispatch (zero if/elif chains)
        self._task_handlers: dict[
            str, Callable[[Task], Coroutine[Any, Any, dict[str, Any]]]
        ] = {
            "write_blog_post": self._write_blog_post,
            "write_social_post": self._write_social_post,
            "write_email": self._write_email,
            "write_case_study": self._write_case_study,
            "write_product_description": self._write_product_description,
            "generate_headlines": self._generate_headlines,
            "rewrite_content": self._rewrite_content,
            "validate_brand_voice": self._validate_brand_voice_task,
        }
```

---

#### 4.7.3 Task Type Specifications

##### 1. write_blog_post

**Purpose**: Create long-form blog content with SEO optimization.

**Parameters**:
```python
{
    "topic": str,                    # Blog post topic
    "target_audience": str,          # Target reader audience
    "word_count": int,               # Desired word count (default: 1000)
    "keywords": List[str],           # SEO keywords to include
    "tone": str,                     # Optional tone override ("professional", "casual", etc.)
    "include_sections": List[str],   # Optional section requirements
}
```

**Returns**:
```python
{
    "content": str,                  # Generated blog post (markdown)
    "word_count": int,               # Actual word count
    "content_type": str,             # "blog_post"
    "brand_voice_score": float,      # Brand alignment score (0-100)
    "readability_score": float,      # Readability score (0-100)
    "reading_time": str,             # Estimated reading time
    "keywords_used": List[str],      # Keywords included in content
}
```

**Implementation**:
```python
async def _write_blog_post(self, task: Task) -> dict[str, Any]:
    """
    Write blog post using LLM with brand voice.

    WHY: Provides long-form content for thought leadership and SEO.
    HOW: Builds LLM prompt with brand voice context, generates content,
         validates quality against brand standards.
    """
    topic = task.parameters["topic"]
    target_audience = task.parameters["target_audience"]
    word_count = task.parameters.get("word_count", 1000)
    keywords = task.parameters.get("keywords", [])

    # Guard clause: Check LLM availability
    if not self._llm_client:
        return {
            "error": "LLM client not configured",
            "content": ""
        }

    # Build prompt with brand voice context
    prompt = self._build_blog_post_prompt(
        topic=topic,
        target_audience=target_audience,
        word_count=word_count,
        keywords=keywords
    )

    # Generate content with LLM
    try:
        response = await self._llm_client.generate(
            prompt=prompt,
            max_tokens=word_count * 2,  # Buffer for markdown
            temperature=0.7
        )

        content = response.text

        # Validate brand voice
        brand_score = await self._validate_brand_voice(content)

        # Calculate readability
        readability_score = self._calculate_readability(content)

        return {
            "content": content,
            "word_count": len(content.split()),
            "content_type": "blog_post",
            "brand_voice_score": brand_score,
            "readability_score": readability_score,
            "reading_time": self._calculate_reading_time(content),
            "keywords_used": self._extract_keywords_used(content, keywords)
        }
    except Exception as e:
        raise AgentExecutionError(
            agent_id=self.agent_id,
            task_id=task.task_id,
            message=f"Failed to generate blog post: {str(e)}",
            original_exception=e
        )
```

##### 2. write_social_post

**Purpose**: Create platform-specific social media posts.

**Parameters**:
```python
{
    "platform": str,             # "linkedin", "twitter", "facebook", "instagram"
    "message_type": str,         # "announcement", "question", "tip", "story"
    "topic": str,                # Post topic or theme
    "call_to_action": str,       # Optional CTA
    "character_limit": int,      # Platform-specific limit
}
```

**Returns**:
```python
{
    "content": str,              # Generated post text
    "character_count": int,      # Length of post
    "platform": str,             # Target platform
    "hashtags": List[str],       # Suggested hashtags
    "emoji_suggestions": List[str],  # Suggested emojis
}
```

##### 3. write_email

**Purpose**: Create email marketing copy.

**Parameters**:
```python
{
    "email_type": str,           # "promotional", "newsletter", "welcome", "nurture"
    "subject_line_count": int,   # Number of subject line variations (default: 3)
    "body_word_count": int,      # Target body word count
    "call_to_action": str,       # Primary CTA
    "personalization_fields": List[str],  # Fields for personalization
}
```

**Returns**:
```python
{
    "subject_lines": List[str],  # Multiple subject line options
    "preview_text": str,         # Email preview text
    "body_html": str,            # HTML email body
    "body_text": str,            # Plain text version
    "cta_text": str,             # Call-to-action text
}
```

##### 4. write_case_study

**Purpose**: Create customer success stories.

**Parameters**:
```python
{
    "customer_name": str,        # Customer/company name
    "industry": str,             # Customer industry
    "challenge": str,            # Problem customer faced
    "solution": str,             # How product/service solved it
    "results": dict[str, Any],   # Quantifiable results/metrics
    "quote": Optional[str],      # Customer testimonial quote
}
```

**Returns**:
```python
{
    "content": str,              # Full case study (markdown)
    "word_count": int,           # Length of case study
    "structure": {
        "challenge": str,        # Challenge section
        "solution": str,         # Solution section
        "results": str,          # Results section
        "testimonial": str,      # Customer quote section
    }
}
```

##### 5. write_product_description

**Purpose**: Create compelling product descriptions.

**Parameters**:
```python
{
    "product_name": str,         # Product name
    "features": List[str],       # Key product features
    "benefits": List[str],       # Customer benefits
    "target_audience": str,      # Target customer
    "length": str,               # "short" (50 words), "medium" (150), "long" (300)
}
```

**Returns**:
```python
{
    "short_description": str,    # Brief description (50 words)
    "long_description": str,     # Detailed description
    "features_list": str,        # Formatted features list
    "benefits_list": str,        # Formatted benefits list
}
```

##### 6. generate_headlines

**Purpose**: Generate multiple headline variations.

**Parameters**:
```python
{
    "topic": str,                # Headline topic
    "headline_type": str,        # "blog", "email_subject", "ad", "social"
    "count": int,                # Number of variations (default: 5)
    "character_limit": int,      # Optional character limit
}
```

**Returns**:
```python
{
    "headlines": List[{
        "text": str,             # Headline text
        "character_count": int,  # Length
        "appeal_type": str,      # "curiosity", "urgency", "benefit", etc.
    }]
}
```

##### 7. rewrite_content

**Purpose**: Rewrite existing content with new tone or style.

**Parameters**:
```python
{
    "original_content": str,     # Content to rewrite
    "new_tone": str,             # Desired tone ("professional", "casual", "friendly")
    "new_style": str,            # Style adjustments ("shorter", "longer", "simpler")
    "preserve_meaning": bool,    # Keep original meaning (default: True)
}
```

**Returns**:
```python
{
    "rewritten_content": str,    # New version of content
    "changes_summary": str,      # Description of changes made
    "word_count_change": int,    # Difference in word count
}
```

##### 8. validate_brand_voice

**Purpose**: Check content against brand voice guidelines.

**Parameters**:
```python
{
    "content": str,              # Content to validate
    "content_type": str,         # Type of content being validated
}
```

**Returns**:
```python
{
    "brand_voice_score": float,  # Overall score (0-100)
    "tone_analysis": {
        "detected_tone": List[str],
        "matches_guidelines": bool,
    },
    "vocabulary_analysis": {
        "preferred_words_used": int,
        "avoided_words_found": List[str],
    },
    "readability_score": float,  # Readability score (0-100)
    "recommendations": List[str], # Improvement suggestions
}
```

---

#### 4.7.4 Brand Voice Configuration

**Brand Voice Guidelines Structure**:
```python
class BrandVoiceGuidelines:
    """Configuration for brand voice consistency."""

    tone_attributes: List[str]       # ["professional", "friendly", "authoritative"]
    personality_traits: List[str]    # ["helpful", "innovative", "trustworthy"]
    vocabulary_do: List[str]         # Encouraged words/phrases
    vocabulary_dont: List[str]       # Words/phrases to avoid
    sentence_structure: str          # "short and punchy" vs "flowing and descriptive"
    reading_level: str               # "general", "technical", "executive"

    def to_prompt_context(self) -> str:
        """Convert guidelines to LLM prompt context."""
        return f"""
        Brand Voice Guidelines:
        - Tone: {', '.join(self.tone_attributes)}
        - Personality: {', '.join(self.personality_traits)}
        - Use words like: {', '.join(self.vocabulary_do[:10])}
        - Avoid words like: {', '.join(self.vocabulary_dont[:10])}
        - Writing style: {self.sentence_structure}
        - Target reading level: {self.reading_level}
        """
```

---

#### 4.7.5 Content Quality Validation

**Quality Metrics**:
```python
async def _validate_brand_voice(self, content: str) -> float:
    """
    Validate content against brand voice guidelines.

    WHY: Ensures content consistency with brand identity.
    HOW: Analyzes tone, vocabulary, style, and readability.

    Returns:
        Brand voice score (0-100)
    """
    score = 0.0

    # Tone analysis (40 points)
    tone_score = self._analyze_tone(content)
    score += tone_score * 0.4

    # Vocabulary check (30 points)
    vocab_score = self._check_vocabulary(content)
    score += vocab_score * 0.3

    # Readability (30 points)
    readability = self._calculate_readability(content)
    score += readability * 0.3

    return score

def _calculate_readability(self, content: str) -> float:
    """
    Calculate readability score using Flesch Reading Ease.

    WHY: Ensures content is accessible to target audience.
    HOW: Analyzes sentence length and syllable complexity.

    Returns:
        Readability score (0-100, higher is easier to read)
    """
    # Implementation uses Flesch Reading Ease formula
    # Score 60-70 = standard (8th-9th grade level)
    # Score 70-80 = fairly easy (7th grade level)
    # Score 80-90 = easy (6th grade level)
```

---

#### 4.7.6 Integration Points

**Content Manager Workflow**:
```python
# Content Manager delegates content creation to Copywriter
content_manager -> copywriter.write_blog_post(
    topic="AI in Marketing",
    target_audience="Marketing Directors",
    word_count=1500,
    keywords=["AI", "marketing", "automation"]
)

# Content Manager requests content rewrite
content_manager -> copywriter.rewrite_content(
    original_content=draft_content,
    new_tone="more professional",
    new_style="shorter paragraphs"
)
```

**Campaign Manager Workflow**:
```python
# Campaign Manager requests campaign copy
campaign_manager -> copywriter.write_email(
    email_type="promotional",
    subject_line_count=5,
    call_to_action="Start Free Trial"
)
```

**Social Media Manager Workflow**:
```python
# Social Media Manager requests platform-specific posts
social_media_manager -> copywriter.write_social_post(
    platform="linkedin",
    message_type="announcement",
    topic="Product Launch"
)
```

---

#### 4.7.7 LLM Prompt Engineering

**Blog Post Prompt Template**:
```python
def _build_blog_post_prompt(
    self, topic: str, target_audience: str, word_count: int, keywords: List[str]
) -> str:
    """Build LLM prompt for blog post generation."""

    brand_context = ""
    if self._brand_voice:
        brand_context = self._brand_voice.to_prompt_context()

    return f"""
    You are a professional copywriter creating a blog post.

    {brand_context}

    Topic: {topic}
    Target Audience: {target_audience}
    Target Word Count: {word_count} words
    SEO Keywords to include: {', '.join(keywords)}

    Requirements:
    1. Create an engaging introduction that hooks the reader
    2. Use clear, scannable subheadings (H2 and H3)
    3. Include practical examples and actionable insights
    4. Naturally incorporate the SEO keywords
    5. End with a strong conclusion and call-to-action
    6. Write in markdown format with proper formatting

    Generate the blog post:
    """
```

---

#### 4.7.8 Testing Strategy

**Unit Tests** (12+ tests):
- All 8 task types with mocked LLM
- Brand voice validation
- Readability calculations
- Keyword extraction
- Error handling (LLM failures)

**Integration Tests** (6+ tests):
- Full content creation workflows
- Brand voice consistency across content types
- Multi-format content generation
- Content quality validation
- Rewriting workflows

**Example Test**:
```python
@pytest.mark.asyncio
async def test_write_blog_post_with_brand_voice(
    self, agent_config, mock_llm_client, brand_guidelines
):
    """Test blog post creation with brand voice validation."""
    agent = CopywriterSpecialistAgent(
        config=agent_config,
        brand_voice=brand_guidelines
    )
    agent._llm_client = mock_llm_client

    task = Task(
        task_type="write_blog_post",
        parameters={
            "topic": "AI in Marketing",
            "target_audience": "Marketing Directors",
            "word_count": 1000,
            "keywords": ["AI", "marketing", "automation"]
        }
    )

    result = await agent.execute(task)

    assert result.status == TaskStatus.COMPLETED
    assert "content" in result.result
    assert result.result["brand_voice_score"] >= 70.0
    assert len(result.result["keywords_used"]) > 0
```

---

#### 4.7.9 Performance Considerations

**LLM Token Usage**:
- Blog posts: ~2000-4000 tokens
- Social posts: ~100-300 tokens
- Emails: ~500-1000 tokens
- Case studies: ~2000-3000 tokens

**Caching Strategy**:
- Cache brand voice prompts (reused across calls)
- Cache content templates
- No caching of generated content (always fresh)

**Error Handling**:
- LLM timeout: Return error with partial content if available
- Rate limiting: Implement exponential backoff
- Quality threshold failures: Return content with warnings

---

#### 4.7.10 Coordination with Other Specialists

```python
# Copywriter → SEO Specialist
# Copywriter creates draft, passes to SEO for optimization
copywriter_result = await copywriter.execute(blog_task)
seo_task = Task(task_type="optimize_content", parameters={
    "content": copywriter_result.result["content"],
    "keywords": ["AI", "marketing"]
})

# Copywriter → Designer
# Copywriter creates content, Designer creates visuals
copywriter_result = await copywriter.execute(blog_task)
designer_task = Task(task_type="create_featured_image", parameters={
    "content_topic": task.parameters["topic"],
    "content_tone": "professional"
})
```

---

### 4.8 SEO Specialist Agent (Specialist Layer)

**Role**: SEO Specialist
**Layer**: Specialist Layer
**Reports To**: Content Manager, Campaign Manager
**Coordinates With**: Copywriter Specialist, Analytics Specialist

#### 4.8.1 Purpose

**WHY**: Provides specialized SEO (Search Engine Optimization) expertise to improve organic search visibility and rankings.

**HOW**: Conducts keyword research, optimizes content for search engines, analyzes SERP competition, generates meta descriptions, tracks rankings, and provides SEO recommendations using external SEO tools and AI-powered analysis.

The SEO Specialist bridges the gap between content creation and search engine performance, ensuring all content is optimized for discoverability and rankings.

#### 4.8.2 Capabilities

The SEO Specialist Agent provides these specialized capabilities:

1. **Keyword Research**
   - Research relevant keywords for content topics
   - Analyze keyword difficulty and search volume
   - Identify long-tail keyword opportunities
   - Competitive keyword analysis
   - Keyword clustering and mapping

2. **Content SEO Optimization**
   - Analyze content SEO quality
   - Optimize keyword usage and density
   - Improve content structure for SEO
   - Suggest content improvements
   - Calculate SEO scores

3. **SERP Analysis**
   - Analyze search engine results pages
   - Identify ranking factors for top results
   - Competitive content gap analysis
   - Calculate opportunity scores
   - Track SERP features (featured snippets, PAA)

4. **Meta Content Generation**
   - Generate SEO-optimized meta descriptions
   - Create compelling title tags
   - Optimize for click-through rate
   - A/B test variations
   - Character count optimization

5. **Internal Linking Strategy**
   - Suggest internal linking opportunities
   - Optimize site architecture
   - Distribute page authority
   - Create topic clusters
   - Fix broken links

6. **SEO Auditing**
   - Audit content for SEO issues
   - Identify technical SEO problems
   - Check mobile-friendliness
   - Validate structured data
   - Performance optimization recommendations

7. **Ranking Tracking**
   - Monitor keyword rankings over time
   - Track ranking changes and trends
   - Competitor ranking analysis
   - SERP volatility detection
   - Geographic ranking tracking

8. **SEO Reporting**
   - Generate comprehensive SEO reports
   - Organic traffic analysis
   - Conversion tracking from organic search
   - ROI calculations for SEO efforts
   - Actionable recommendations

#### 4.8.3 Task Types

The SEO Specialist handles these task types using **Strategy Pattern** (dictionary dispatch):

```python
class SEOSpecialistAgent(BaseAgent):
    """
    Specialist-layer agent for SEO and search optimization.

    WHY: Provides specialized SEO expertise for improving organic search visibility.
    HOW: Uses external SEO tools, Search Console data, and AI analysis to optimize
         content, research keywords, and track performance.
    """

    def __init__(self, config: AgentConfig):
        super().__init__(config)

        # External SEO tool clients
        self._search_console_client: Optional[SearchConsoleClient] = None
        self._semrush_client: Optional[SEMrushClient] = None
        self._ahrefs_client: Optional[AhrefsClient] = None

        # LLM for AI-powered analysis
        self._llm_client: Optional[LLMClient] = None

        # Caching for API rate limiting (24-hour TTL)
        self._keyword_cache: dict[str, tuple[datetime, dict[str, Any]]] = {}
        self._serp_cache: dict[str, tuple[datetime, dict[str, Any]]] = {}
        self._cache_ttl_hours: int = 24

        # Keyword database
        self._keyword_research: dict[str, dict[str, Any]] = {}
        self._ranking_history: dict[str, list[dict[str, Any]]] = {}

        # Strategy Pattern: Dictionary dispatch for task routing
        self._task_handlers: dict[
            str, Callable[[Task], Coroutine[Any, Any, dict[str, Any]]]
        ] = {
            "keyword_research": self._keyword_research_task,
            "optimize_content": self._optimize_content,
            "analyze_serp": self._analyze_serp,
            "generate_meta_descriptions": self._generate_meta_descriptions,
            "suggest_internal_links": self._suggest_internal_links,
            "audit_seo": self._audit_seo,
            "track_rankings": self._track_rankings,
            "generate_seo_report": self._generate_seo_report,
        }

    async def _execute_task(self, task: Task) -> dict[str, Any]:
        """
        Execute task using Strategy Pattern.

        WHY: Eliminates if/elif chains for better maintainability.
        HOW: Uses dictionary dispatch to route to appropriate handler.
        """
        # Guard clause: Check if task type is supported
        if task.task_type not in self._task_handlers:
            raise AgentExecutionError(
                agent_id=self.agent_id,
                task_id=task.task_id,
                message=f"Unsupported task type: {task.task_type}"
            )

        handler = self._task_handlers[task.task_type]

        # Execute handler with exception wrapping
        try:
            return await handler(task)
        except Exception as e:
            raise AgentExecutionError(
                agent_id=self.agent_id,
                task_id=task.task_id,
                message=f"Task execution failed: {str(e)}",
                original_exception=e
            )
```

##### Task Type 1: keyword_research

Research and analyze keywords for content topics.

**Parameters:**
- `topic` (required): Content topic for keyword research
- `target_audience` (optional): Target audience for keyword selection
- `language` (optional): Language for keywords (default: "en")
- `location` (optional): Geographic location for keyword data
- `count` (optional): Number of keywords to return (default: 20)

**Returns:**
```python
{
    "primary_keywords": [
        {
            "keyword": "AI marketing tools",
            "search_volume": 8100,
            "difficulty": 65,
            "cpc": 12.50,
            "intent": "commercial"
        },
        # ... more primary keywords
    ],
    "secondary_keywords": [...],
    "long_tail_keywords": [...],
    "recommendations": [
        "Target 'AI marketing automation' as primary focus keyword",
        "Include long-tail variations for content sections",
        "Consider 'marketing AI tools' as secondary target"
    ],
    "topic": "AI Marketing Tools",
    "total_search_volume": 50000,
    "average_difficulty": 58.5
}
```

**Example:**
```python
keyword_task = Task(
    task_type="keyword_research",
    parameters={
        "topic": "AI Marketing Tools",
        "target_audience": "Marketing Directors",
        "language": "en",
        "count": 20
    },
    assigned_to=AgentRole.SEO_SPECIALIST,
    assigned_by=AgentRole.CONTENT_MANAGER
)
```

##### Task Type 2: optimize_content

Optimize existing content for target keywords.

**Parameters:**
- `content` (required): Content text to optimize
- `target_keywords` (required): List of keywords to optimize for
- `content_type` (optional): Type of content (blog_post, landing_page, etc.)

**Returns:**
```python
{
    "optimized": True,
    "current_score": 72.5,
    "potential_score": 88.0,
    "suggestions": [
        {
            "category": "keyword_usage",
            "issue": "Primary keyword appears only once",
            "recommendation": "Include 'AI marketing tools' 3-4 more times naturally",
            "priority": "high"
        },
        {
            "category": "content_structure",
            "issue": "Missing H2 heading with target keyword",
            "recommendation": "Add H2 heading: 'Top AI Marketing Tools for 2025'",
            "priority": "medium"
        },
        {
            "category": "readability",
            "issue": "Average sentence length too high (25 words)",
            "recommendation": "Break long sentences for better readability",
            "priority": "medium"
        }
    ],
    "issues_found": 5,
    "keyword_density": {
        "AI marketing tools": 0.8,  # Percentage
        "marketing automation": 1.2
    },
    "recommended_changes": [
        "Add keyword to first paragraph",
        "Include keyword in one H2 heading",
        "Add keyword variation in conclusion"
    ]
}
```

##### Task Type 3: analyze_serp

Analyze search engine results page for target keyword.

**Parameters:**
- `keyword` (required): Target keyword to analyze
- `location` (optional): Geographic location for SERP (default: "US")
- `device` (optional): Device type (desktop, mobile) (default: "desktop")

**Returns:**
```python
{
    "keyword": "AI marketing tools",
    "location": "US",
    "top_results": [
        {
            "position": 1,
            "url": "https://example.com/ai-marketing-tools",
            "title": "15 Best AI Marketing Tools for 2025",
            "domain_authority": 72,
            "word_count": 3500,
            "content_type": "listicle",
            "has_featured_snippet": False
        },
        # ... more results
    ],
    "competition_level": "high",  # high, medium, low
    "content_gaps": [
        "Most results don't cover AI for email marketing",
        "Limited coverage of pricing comparisons",
        "Few results include video content"
    ],
    "ranking_factors": {
        "avg_word_count": 2800,
        "avg_domain_authority": 68,
        "common_content_types": ["listicle", "guide", "comparison"],
        "avg_backlinks": 450
    },
    "opportunity_score": 65,  # 0-100, higher = better opportunity
    "recommendations": [
        "Create comprehensive guide with 2500+ words",
        "Include pricing comparison table",
        "Add video demonstrations",
        "Target featured snippet with FAQ section"
    ]
}
```

##### Task Type 4: generate_meta_descriptions

Generate SEO-optimized meta descriptions and title tags.

**Parameters:**
- `content` (required): Content to generate meta description for
- `target_keywords` (required): Keywords to include
- `variations` (optional): Number of variations to generate (default: 3)

**Returns:**
```python
{
    "meta_descriptions": [
        {
            "text": "Discover 15 powerful AI marketing tools that streamline campaigns, boost ROI, and automate content creation. Compare features & pricing.",
            "character_count": 145,
            "keyword_included": True,
            "ctr_score": 85  # Estimated CTR score
        },
        # ... more variations
    ],
    "title_tags": [
        {
            "text": "15 Best AI Marketing Tools for 2025 | Features & Pricing",
            "character_count": 58,
            "keyword_included": True,
            "ctr_score": 88
        },
        # ... more variations
    ],
    "recommendations": [
        "Use variation #1 for highest estimated CTR",
        "Test variations with A/B testing",
        "Include year '2025' to show freshness"
    ]
}
```

##### Task Type 5: suggest_internal_links

Suggest internal linking opportunities for content.

**Parameters:**
- `content_id` (required): ID of content to suggest links for
- `content` (required): Content text
- `max_suggestions` (optional): Maximum links to suggest (default: 5)

**Returns:**
```python
{
    "suggestions": [
        {
            "anchor_text": "marketing automation",
            "target_url": "/blog/marketing-automation-guide",
            "relevance_score": 92,
            "context": "Use in paragraph 3 when discussing automation benefits",
            "reason": "Highly relevant content that adds value"
        },
        # ... more suggestions
    ],
    "topic_cluster": {
        "pillar_page": "/marketing-tools",
        "cluster_pages": [
            "/blog/email-marketing-tools",
            "/blog/social-media-tools",
            "/blog/analytics-tools"
        ]
    },
    "architecture_recommendations": [
        "Create pillar page for 'Marketing Tools' topic",
        "Link all tool reviews to pillar page",
        "Add breadcrumb navigation"
    ]
}
```

##### Task Type 6: audit_seo

Audit content for SEO issues and opportunities.

**Parameters:**
- `content_id` (optional): Specific content to audit
- `url` (optional): URL to audit
- `scope` (optional): Audit scope (on_page, technical, both) (default: "both")

**Returns:**
```python
{
    "overall_score": 75.5,
    "issues": [
        {
            "severity": "high",
            "category": "on_page",
            "issue": "Missing meta description",
            "affected_pages": ["/blog/post-1", "/blog/post-2"],
            "fix": "Add meta descriptions to all pages"
        },
        {
            "severity": "medium",
            "category": "technical",
            "issue": "Slow page load time (4.2s)",
            "affected_pages": ["/"],
            "fix": "Optimize images and enable caching"
        }
    ],
    "opportunities": [
        {
            "category": "content",
            "opportunity": "Add FAQ schema markup",
            "estimated_impact": "high",
            "effort": "low"
        }
    ],
    "technical_issues": [
        "3 pages with 404 errors",
        "Mobile responsiveness issues on 2 pages",
        "Missing XML sitemap"
    ],
    "recommendations": [
        "Fix high-priority issues first (missing meta descriptions)",
        "Implement FAQ schema for featured snippets",
        "Improve site speed with image optimization"
    ]
}
```

##### Task Type 7: track_rankings

Monitor keyword rankings over time.

**Parameters:**
- `keywords` (required): List of keywords to track
- `location` (optional): Geographic location (default: "US")
- `device` (optional): Device type (default: "desktop")

**Returns:**
```python
{
    "rankings": [
        {
            "keyword": "AI marketing tools",
            "current_position": 12,
            "previous_position": 15,
            "change": +3,
            "url": "/blog/ai-marketing-tools",
            "search_volume": 8100,
            "trend": "improving"
        },
        # ... more keywords
    ],
    "summary": {
        "total_keywords": 50,
        "improved": 28,
        "declined": 12,
        "stable": 10,
        "top_3": 8,
        "top_10": 15,
        "top_20": 22
    },
    "alerts": [
        "Keyword 'marketing automation' dropped 8 positions",
        "New ranking for 'AI email marketing' in position 18"
    ],
    "recommendations": [
        "Update content for declining keywords",
        "Capitalize on improving trends with more content",
        "Refresh content for keywords stuck at position 11-20"
    ]
}
```

##### Task Type 8: generate_seo_report

Generate comprehensive SEO performance report.

**Parameters:**
- `date_range` (required): Date range for report (e.g., "last_30_days")
- `include_charts` (optional): Include visualization data (default: True)
- `report_type` (optional): Type of report (summary, detailed) (default: "summary")

**Returns:**
```python
{
    "report_id": "seo_report_2025_11",
    "period": "2025-10-01 to 2025-11-01",
    "organic_traffic": {
        "sessions": 45000,
        "change_percent": 12.5,
        "new_users": 38000,
        "returning_users": 7000
    },
    "keyword_performance": {
        "total_keywords_ranking": 450,
        "new_keywords": 35,
        "lost_keywords": 12,
        "top_10_keywords": 78,
        "avg_position": 18.5
    },
    "content_performance": [
        {
            "url": "/blog/ai-marketing-tools",
            "sessions": 5200,
            "avg_position": 8,
            "keywords_ranking": 25
        },
        # ... more content
    ],
    "conversions": {
        "total": 450,
        "conversion_rate": 1.0,
        "revenue": 45000
    },
    "recommendations": [
        "Focus on improving rankings for positions 11-20",
        "Update top-performing content with fresh data",
        "Expand keyword targeting in email marketing topic"
    ],
    "action_items": [
        {
            "priority": "high",
            "action": "Optimize 5 pages stuck at position 11-15",
            "estimated_impact": "15% traffic increase"
        }
    ]
}
```

#### 4.8.4 State Management

The SEO Specialist maintains these state components:

```python
class SEOSpecialistAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)

        # Keyword research database
        self._keyword_research: dict[str, dict[str, Any]] = {}
        # Format: {
        #     "topic_key": {
        #         "topic": "AI Marketing",
        #         "keywords": [...],
        #         "researched_at": datetime,
        #         "search_volume": 50000
        #     }
        # }

        # Ranking history
        self._ranking_history: dict[str, list[dict[str, Any]]] = {}
        # Format: {
        #     "keyword": [
        #         {
        #             "position": 12,
        #             "url": "/blog/post",
        #             "checked_at": datetime
        #         }
        #     ]
        # }

        # SERP cache (24-hour TTL)
        self._serp_cache: dict[str, tuple[datetime, dict[str, Any]]] = {}

        # Keyword cache (24-hour TTL)
        self._keyword_cache: dict[str, tuple[datetime, dict[str, Any]]] = {}

        # SEO audit results
        self._audit_results: dict[str, dict[str, Any]] = {}

        # Content SEO scores
        self._content_scores: dict[str, float] = {}
```

#### 4.8.5 External Integrations

The SEO Specialist integrates with these external services:

**Google Search Console API:**
- Fetch search analytics data
- Monitor rankings and CTR
- Identify indexing issues
- Submit sitemaps

**SEMrush API:**
- Keyword research and difficulty
- SERP analysis
- Competitor analysis
- Backlink data

**Ahrefs API (Optional):**
- Additional keyword data
- Backlink analysis
- Content gap analysis
- Domain authority metrics

**AI/LLM (Claude):**
- Content optimization suggestions
- Meta description generation
- SEO recommendation synthesis
- Competitive analysis insights

#### 4.8.6 Coordination Examples

**With Content Manager:**
```python
# Content Manager requests keyword research for editorial calendar
content_manager -> seo_specialist.keyword_research(
    topic="AI Marketing Trends 2025",
    target_audience="Marketing Directors"
)

# Content Manager requests SEO audit before publishing
content_manager -> seo_specialist.audit_seo(
    content_id="blog_001",
    scope="on_page"
)
```

**With Copywriter Specialist:**
```python
# Copywriter requests keyword research for blog post
copywriter -> seo_specialist.keyword_research(
    topic="Marketing Automation",
    content_type="blog_post"
)

# Copywriter requests content optimization review
copywriter -> seo_specialist.optimize_content(
    content="...",
    target_keywords=["marketing automation", "workflow automation"]
)

# Copywriter requests meta descriptions
copywriter -> seo_specialist.generate_meta_descriptions(
    content="...",
    target_keywords=["marketing automation"]
)
```

**With Campaign Manager:**
```python
# Campaign Manager requests SEO performance report
campaign_manager -> seo_specialist.generate_seo_report(
    date_range="last_30_days",
    campaign_id="campaign_001"
)

# Campaign Manager requests ranking tracking
campaign_manager -> seo_specialist.track_rankings(
    keywords=campaign_keywords
)
```

**With Analytics Specialist:**
```python
# SEO Specialist requests organic traffic data
seo_specialist -> analytics_specialist.get_web_analytics(
    metrics=["organic_sessions", "organic_conversions"],
    date_range="last_90_days"
)
```

#### 4.8.7 SEO Score Calculation

The SEO Specialist calculates comprehensive SEO scores:

```python
def _calculate_seo_score(
    self,
    content: str,
    target_keywords: list[str]
) -> float:
    """
    Calculate comprehensive SEO quality score for content.

    WHY: Provides quantitative measure of content SEO optimization.
    HOW: Analyzes multiple SEO factors with weighted scoring.

    Returns:
        SEO score (0-100)
    """
    score = 0.0

    # Keyword optimization (30 points)
    keyword_score = self._score_keyword_usage(content, target_keywords)
    score += keyword_score * 0.30

    # Content quality (25 points)
    quality_score = self._score_content_quality(content)
    score += quality_score * 0.25

    # Readability (20 points)
    readability_score = self._score_readability(content)
    score += readability_score * 0.20

    # Structure (15 points) - headings, paragraphs, lists
    structure_score = self._score_content_structure(content)
    score += structure_score * 0.15

    # Keyword density (10 points) - optimal range 1-2%
    density_score = self._score_keyword_density(content, target_keywords)
    score += density_score * 0.10

    return min(score, 100.0)

def _score_keyword_usage(
    self,
    content: str,
    target_keywords: list[str]
) -> float:
    """
    Score keyword usage in content.

    WHY: Keywords must appear naturally throughout content.
    HOW: Checks keyword placement in strategic locations.
    """
    score = 0.0
    content_lower = content.lower()

    for keyword in target_keywords:
        keyword_lower = keyword.lower()

        # Check first paragraph (important for SEO)
        first_para = content_lower[:500]
        if keyword_lower in first_para:
            score += 25.0

        # Check headings
        if keyword_lower in self._extract_headings(content).lower():
            score += 25.0

        # Check last paragraph
        last_para = content_lower[-500:]
        if keyword_lower in last_para:
            score += 15.0

        # Check URL slug (if available)
        # score += 10.0 if in URL

        # Check overall presence
        count = content_lower.count(keyword_lower)
        if count >= 3:
            score += 25.0
        elif count >= 1:
            score += 15.0

    return min(score / len(target_keywords), 100.0)
```

#### 4.8.8 Caching Strategy

To respect API rate limits and reduce costs, the SEO Specialist implements caching:

```python
async def _get_cached_or_fetch_keywords(
    self,
    cache_key: str,
    fetch_fn: Callable[[], Coroutine[Any, Any, dict[str, Any]]]
) -> dict[str, Any]:
    """
    Get keyword data from cache or fetch fresh data with 24-hour TTL.

    WHY: Reduces API calls and costs for SEO tool APIs.
    HOW: Caches keyword research for 24 hours, as data doesn't change frequently.
    """
    # Guard clause: Check cache
    if cache_key in self._keyword_cache:
        cached_time, cached_data = self._keyword_cache[cache_key]
        time_elapsed = datetime.now() - cached_time

        if time_elapsed < timedelta(hours=self._cache_ttl_hours):
            return {**cached_data, "cached": True}

    # Fetch fresh data
    try:
        fresh_data = await fetch_fn()
        self._keyword_cache[cache_key] = (datetime.now(), fresh_data)
        return fresh_data
    except Exception as e:
        # Graceful degradation: Return stale cache if available
        if cache_key in self._keyword_cache:
            _, stale_data = self._keyword_cache[cache_key]
            return {
                **stale_data,
                "cached": True,
                "warning": "Using stale cached data due to API failure"
            }

        raise AgentExecutionError(
            agent_id=self.agent_id,
            task_id="unknown",
            message=f"Failed to fetch keyword data: {str(e)}",
            original_exception=e
        )
```

#### 4.8.9 Architecture Compliance

**Strategy Pattern:**
```python
# ✅ CORRECT: Dictionary dispatch
self._task_handlers = {
    "keyword_research": self._keyword_research_task,
    "optimize_content": self._optimize_content,
    # ... other handlers
}

# ❌ WRONG: if/elif chains
if task.task_type == "keyword_research":
    return await self._keyword_research_task(task)
elif task.task_type == "optimize_content":
    return await self._optimize_content(task)
```

**Guard Clauses:**
```python
# ✅ CORRECT: Guard clause for early return
async def _optimize_content(self, task: Task) -> dict[str, Any]:
    content = task.parameters.get("content")

    # Guard clause: Validate content exists
    if not content:
        return {"error": "Content is required", "optimized": False}

    # Guard clause: Check if already optimized
    score = self._calculate_seo_score(content, keywords)
    if score >= 90.0:
        return {"optimized": False, "reason": "Already well-optimized", "score": score}

    # Main logic here
    return await self._perform_optimization(content, keywords)

# ❌ WRONG: Nested if statements
async def _optimize_content(self, task: Task) -> dict[str, Any]:
    content = task.parameters.get("content")

    if content:
        score = self._calculate_seo_score(content, keywords)
        if score < 90.0:
            # Deep nesting
            return await self._perform_optimization(content, keywords)
```

**Exception Wrapping:**
```python
# ✅ CORRECT: Wrap external API calls
try:
    keyword_data = await self._semrush_client.keyword_research(topic)
except Exception as e:
    raise AgentExecutionError(
        agent_id=self.agent_id,
        task_id=task.task_id,
        message=f"SEMrush API failed: {str(e)}",
        original_exception=e
    )

# ❌ WRONG: Let exceptions propagate
keyword_data = await self._semrush_client.keyword_research(topic)
```

---

### 4.9 Designer Specialist Agent (Specialist Layer)

**Role**: Designer Specialist
**Layer**: Specialist Layer
**Reports To**: Content Manager, Social Media Manager, Campaign Manager
**Coordinates With**: Copywriter Specialist, SEO Specialist

#### 4.9.1 Purpose

**WHY**: Provides specialized visual design expertise to create compelling graphics and ensure brand consistency across all marketing channels.

**HOW**: Generates visual assets using AI image generation tools, creates platform-specific graphics, designs marketing materials, and ensures brand compliance using configurable brand guidelines.

The Designer Specialist bridges the gap between content creation and visual presentation, ensuring all content has professional, on-brand visual elements.

#### 4.9.2 Capabilities

The Designer Specialist Agent provides these specialized capabilities:

1. **Social Media Graphics**
   - Generate platform-specific graphics (LinkedIn, Twitter, Instagram, Facebook)
   - Create post images with optimal dimensions
   - Design profile banners and headers
   - Generate story and carousel graphics
   - Add text overlays and branding

2. **Blog and Content Images**
   - Create featured images for blog posts
   - Generate inline images and illustrations
   - Design hero images and headers
   - Create thumbnail images
   - Generate data visualizations

3. **Marketing Materials**
   - Design advertising banners and creatives
   - Create email marketing headers
   - Generate promotional graphics
   - Design landing page visuals
   - Create campaign-specific assets

4. **Infographics and Data Viz**
   - Design data-driven infographics
   - Create charts and graphs
   - Generate comparison visuals
   - Design process diagrams
   - Create timeline graphics

5. **Brand Consistency**
   - Enforce brand color palette
   - Apply brand fonts and typography
   - Ensure logo usage compliance
   - Maintain visual style consistency
   - Validate brand guideline adherence

6. **Design Variations**
   - Generate A/B test variations
   - Create color scheme alternatives
   - Design layout variations
   - Generate style variations
   - Test different compositions

7. **Image Optimization**
   - Compress images for web
   - Convert to optimal formats (WebP, PNG, JPG)
   - Resize for platform requirements
   - Optimize file sizes
   - Generate responsive versions

8. **Design Recommendations**
   - Suggest design improvements
   - Recommend color palettes
   - Provide composition feedback
   - Identify accessibility issues
   - Track design performance

#### 4.9.3 Task Types

The Designer Specialist handles these task types using **Strategy Pattern** (dictionary dispatch):

```python
class DesignerSpecialistAgent(BaseAgent):
    """
    Specialist-layer agent for visual design and asset creation.

    WHY: Provides specialized design expertise for creating professional visuals.
    HOW: Uses AI image generation tools with brand guidelines to create
         platform-optimized graphics and marketing materials.
    """

    def __init__(self, config: AgentConfig, brand_guidelines: Optional[BrandGuidelines] = None):
        super().__init__(config)

        # AI image generation clients
        self._dalle_client: Optional[DALLEClient] = None
        self._midjourney_client: Optional[MidjourneyClient] = None
        self._stable_diffusion_client: Optional[StableDiffusionClient] = None

        # Brand guidelines
        self._brand_guidelines: Optional[BrandGuidelines] = brand_guidelines

        # Design template library
        self._templates: dict[str, DesignTemplate] = {}

        # Generated assets cache
        self._asset_cache: dict[str, GeneratedAsset] = {}

        # Platform specifications
        self._platform_specs: dict[str, dict[str, dict[str, int]]] = self._load_platform_specs()

        # Strategy Pattern: Dictionary dispatch for task routing
        self._task_handlers: dict[
            str, Callable[[Task], Coroutine[Any, Any, dict[str, Any]]]
        ] = {
            "generate_social_graphic": self._generate_social_graphic,
            "generate_blog_image": self._generate_blog_image,
            "create_infographic": self._create_infographic,
            "generate_ad_creative": self._generate_ad_creative,
            "design_email_header": self._design_email_header,
            "create_thumbnail": self._create_thumbnail,
            "generate_design_variations": self._generate_design_variations,
            "optimize_image": self._optimize_image,
        }

    async def _execute_task(self, task: Task) -> dict[str, Any]:
        """
        Execute task using Strategy Pattern.

        WHY: Eliminates if/elif chains for better maintainability.
        HOW: Uses dictionary dispatch to route to appropriate handler.
        """
        # Guard clause: Check if task type is supported
        if task.task_type not in self._task_handlers:
            raise AgentExecutionError(
                agent_id=self.agent_id,
                task_id=task.task_id,
                message=f"Unsupported task type: {task.task_type}"
            )

        handler = self._task_handlers[task.task_type]

        # Execute handler with exception wrapping
        try:
            return await handler(task)
        except Exception as e:
            raise AgentExecutionError(
                agent_id=self.agent_id,
                task_id=task.task_id,
                message=f"Task execution failed: {str(e)}",
                original_exception=e
            )
```

##### Task Type 1: generate_social_graphic

Generate platform-specific social media graphics.

**Parameters:**
- `platform` (required): Platform name (linkedin, twitter, instagram, facebook)
- `content_topic` (required): Topic or subject of the graphic
- `graphic_type` (optional): Type of graphic (post, story, banner, profile) (default: "post")
- `style` (optional): Visual style (professional, casual, bold, minimal) (default: "professional")
- `include_text` (optional): Include text overlay (default: False)
- `text_content` (optional): Text to overlay on image

**Returns:**
```python
{
    "image_url": "https://cdn.example.com/graphics/linkedin_post_001.webp",
    "image_path": "/var/assets/graphics/linkedin_post_001.webp",
    "platform": "linkedin",
    "graphic_type": "post",
    "dimensions": {
        "width": 1200,
        "height": 627
    },
    "file_size_kb": 145,
    "format": "webp",
    "brand_compliance_score": 92.5,
    "optimization_applied": True,
    "generation_time_ms": 3500
}
```

**Example:**
```python
social_graphic_task = Task(
    task_type="generate_social_graphic",
    parameters={
        "platform": "linkedin",
        "content_topic": "AI Marketing Automation",
        "graphic_type": "post",
        "style": "professional",
        "include_text": True,
        "text_content": "Transform Your Marketing with AI"
    },
    assigned_to=AgentRole.DESIGNER,
    assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER
)
```

##### Task Type 2: generate_blog_image

Generate featured images for blog posts.

**Parameters:**
- `blog_title` (required): Title of the blog post
- `blog_summary` (required): Brief summary of content
- `keywords` (optional): SEO keywords to incorporate visually
- `style` (optional): Visual style (default: "professional")
- `image_type` (optional): Type (featured, hero, inline) (default: "featured")

**Returns:**
```python
{
    "image_url": "https://cdn.example.com/blog/featured_ai_marketing_001.webp",
    "image_path": "/var/assets/blog/featured_ai_marketing_001.webp",
    "image_type": "featured",
    "dimensions": {
        "width": 1200,
        "height": 630
    },
    "file_size_kb": 180,
    "format": "webp",
    "brand_compliance_score": 95.0,
    "seo_optimized": True,
    "alt_text": "Illustration showing AI-powered marketing automation dashboard",
    "suggestions": [
        "Consider adding brand logo for recognition",
        "Image aligns well with content topic"
    ]
}
```

##### Task Type 3: create_infographic

Design data-driven infographics.

**Parameters:**
- `title` (required): Infographic title
- `data` (required): Data to visualize (dict or list)
- `chart_type` (required): Type of visualization (bar, pie, line, comparison, timeline)
- `color_scheme` (optional): Color scheme (brand, monochrome, vibrant) (default: "brand")
- `layout` (optional): Layout style (vertical, horizontal, grid) (default: "vertical")

**Returns:**
```python
{
    "infographic_url": "https://cdn.example.com/infographics/marketing_roi_001.png",
    "infographic_path": "/var/assets/infographics/marketing_roi_001.png",
    "title": "Marketing Automation ROI",
    "chart_type": "bar",
    "dimensions": {
        "width": 800,
        "height": 1200
    },
    "file_size_kb": 320,
    "format": "png",
    "data_visualized": {
        "ROI Increase": "150%",
        "Time Saved": "40%",
        "Efficiency Gain": "200%"
    },
    "brand_compliance_score": 90.0,
    "accessibility": {
        "color_contrast": "AAA",
        "readable_fonts": True
    }
}
```

##### Task Type 4: generate_ad_creative

Create advertising graphics and banners.

**Parameters:**
- `ad_type` (required): Type of ad (banner, display, social, native)
- `size` (required): Ad size (leaderboard, rectangle, skyscraper, custom)
- `message` (required): Primary message/headline
- `call_to_action` (required): CTA text
- `product_image` (optional): URL to product image
- `brand_elements` (optional): Include logo, colors, etc. (default: True)

**Returns:**
```python
{
    "ad_creative_url": "https://cdn.example.com/ads/leaderboard_001.webp",
    "ad_creative_path": "/var/assets/ads/leaderboard_001.webp",
    "ad_type": "banner",
    "size": "leaderboard",
    "dimensions": {
        "width": 728,
        "height": 90
    },
    "message": "Transform Your Marketing",
    "cta": "Start Free Trial",
    "file_size_kb": 85,
    "format": "webp",
    "brand_compliance_score": 93.0,
    "estimated_ctr": "high",
    "variations_available": 3
}
```

##### Task Type 5: design_email_header

Generate email marketing headers.

**Parameters:**
- `email_type` (required): Type of email (newsletter, promotional, transactional)
- `subject` (required): Email subject line
- `theme` (optional): Visual theme (default: "brand")
- `include_logo` (optional): Include brand logo (default: True)

**Returns:**
```python
{
    "header_url": "https://cdn.example.com/email/header_newsletter_001.png",
    "header_path": "/var/assets/email/header_newsletter_001.png",
    "email_type": "newsletter",
    "dimensions": {
        "width": 600,
        "height": 200
    },
    "file_size_kb": 95,
    "format": "png",
    "brand_compliance_score": 94.0,
    "mobile_optimized": True,
    "email_client_compatible": ["gmail", "outlook", "apple_mail"]
}
```

##### Task Type 6: create_thumbnail

Generate video or content thumbnails.

**Parameters:**
- `content_type` (required): Type of content (video, podcast, webinar)
- `title` (required): Content title
- `duration` (optional): Content duration (for display)
- `style` (optional): Thumbnail style (default: "engaging")
- `include_play_button` (optional): Add play button overlay (default: True)

**Returns:**
```python
{
    "thumbnail_url": "https://cdn.example.com/thumbnails/webinar_001.jpg",
    "thumbnail_path": "/var/assets/thumbnails/webinar_001.jpg",
    "content_type": "webinar",
    "dimensions": {
        "width": 1280,
        "height": 720
    },
    "file_size_kb": 125,
    "format": "jpg",
    "includes_play_button": True,
    "brand_compliance_score": 91.0,
    "estimated_click_rate": "high"
}
```

##### Task Type 7: generate_design_variations

Create multiple design variations for A/B testing.

**Parameters:**
- `base_design_id` (required): ID of base design to create variations from
- `variation_count` (optional): Number of variations (default: 3)
- `variation_types` (optional): Types of variations (color, layout, style) (default: ["color", "layout", "style"])

**Returns:**
```python
{
    "base_design_id": "design_001",
    "variations": [
        {
            "variation_id": "var_001",
            "type": "color",
            "image_url": "https://cdn.example.com/variations/var_001.webp",
            "description": "Blue color scheme variation",
            "brand_compliance_score": 90.0
        },
        {
            "variation_id": "var_002",
            "type": "layout",
            "image_url": "https://cdn.example.com/variations/var_002.webp",
            "description": "Center-aligned layout variation",
            "brand_compliance_score": 88.0
        },
        {
            "variation_id": "var_003",
            "type": "style",
            "image_url": "https://cdn.example.com/variations/var_003.webp",
            "description": "Minimal style variation",
            "brand_compliance_score": 92.0
        }
    ],
    "total_variations": 3,
    "ready_for_ab_test": True,
    "recommended_variation": "var_003"
}
```

##### Task Type 8: optimize_image

Optimize images for web performance.

**Parameters:**
- `image_url` (required): URL or path to source image
- `target_format` (optional): Target format (webp, png, jpg) (default: "webp")
- `quality` (optional): Quality percentage (1-100) (default: 85)
- `max_width` (optional): Maximum width in pixels
- `max_height` (optional): Maximum height in pixels

**Returns:**
```python
{
    "optimized_url": "https://cdn.example.com/optimized/image_001.webp",
    "optimized_path": "/var/assets/optimized/image_001.webp",
    "original_size_kb": 850,
    "optimized_size_kb": 145,
    "compression_ratio": "83%",
    "format": "webp",
    "dimensions": {
        "width": 1200,
        "height": 630
    },
    "quality_score": 85,
    "optimization_applied": [
        "format_conversion",
        "compression",
        "resize"
    ]
}
```

#### 4.9.4 State Management

The Designer Specialist maintains these state components:

```python
class DesignerSpecialistAgent(BaseAgent):
    def __init__(self, config: AgentConfig, brand_guidelines: Optional[BrandGuidelines] = None):
        super().__init__(config)

        # Generated assets database
        self._generated_assets: dict[str, GeneratedAsset] = {}
        # Format: {
        #     "asset_id": GeneratedAsset(
        #         id="asset_001",
        #         type="social_graphic",
        #         url="...",
        #         created_at=datetime,
        #         brand_score=92.5
        #     )
        # }

        # Design variations tracking
        self._design_variations: dict[str, list[str]] = {}
        # Format: {
        #     "base_design_id": ["var_001", "var_002", "var_003"]
        # }

        # Brand compliance scores
        self._brand_scores: dict[str, float] = {}

        # Template library
        self._templates: dict[str, DesignTemplate] = {}

        # Platform specifications (loaded from config)
        self._platform_specs: dict[str, dict[str, dict[str, int]]] = {}
```

#### 4.9.5 External Integrations

The Designer Specialist integrates with these external services:

**DALL-E API (OpenAI):**
- AI image generation
- Style transfer
- Image editing
- Variation generation

**Midjourney API (Optional):**
- High-quality image generation
- Artistic styles
- Complex compositions

**Stable Diffusion API (Optional):**
- Open-source image generation
- Custom model training
- Cost-effective alternative

**Image Optimization:**
- WebP conversion
- PNG/JPG compression
- Responsive image generation
- Format optimization

#### 4.9.6 Coordination Examples

**With Content Manager:**
```python
# Content Manager requests featured image for blog post
content_manager -> designer.generate_blog_image(
    blog_title="AI Marketing Trends 2025",
    blog_summary="Comprehensive guide to emerging AI trends in marketing",
    keywords=["AI", "marketing", "automation"]
)

# Content Manager requests infographic for data report
content_manager -> designer.create_infographic(
    title="Q4 Marketing Performance",
    data={"Leads": 1500, "Conversions": 450, "ROI": 250},
    chart_type="bar"
)
```

**With Social Media Manager:**
```python
# Social Media Manager requests platform-specific graphics
social_media_manager -> designer.generate_social_graphic(
    platform="linkedin",
    content_topic="Product Launch Announcement",
    include_text=True,
    text_content="Introducing Our New AI Platform"
)

# Request variations for A/B testing
social_media_manager -> designer.generate_design_variations(
    base_design_id="social_001",
    variation_count=3,
    variation_types=["color", "layout"]
)
```

**With Campaign Manager:**
```python
# Campaign Manager requests ad creative
campaign_manager -> designer.generate_ad_creative(
    ad_type="banner",
    size="leaderboard",
    message="Transform Your Marketing with AI",
    call_to_action="Start Free Trial"
)

# Request email header for campaign
campaign_manager -> designer.design_email_header(
    email_type="promotional",
    subject="Exclusive Offer: 30% Off AI Tools",
    theme="sale"
)
```

**With Copywriter:**
```python
# Copywriter requests visual for blog post
copywriter -> designer.generate_blog_image(
    blog_title=blog_post.title,
    blog_summary=blog_post.summary,
    style="professional"
)
```

#### 4.9.7 Brand Guidelines Structure

The Designer enforces comprehensive brand guidelines:

```python
class BrandGuidelines:
    """Brand guidelines for consistent visual design."""

    def __init__(
        self,
        primary_colors: list[str],
        secondary_colors: list[str],
        fonts: dict[str, str],
        logo_usage: dict[str, Any],
        visual_style: str,
        imagery_style: str
    ):
        self.primary_colors = primary_colors  # ["#1E40AF", "#3B82F6", "#60A5FA"]
        self.secondary_colors = secondary_colors  # ["#F59E0B", "#10B981", "#8B5CF6"]
        self.fonts = fonts  # {"heading": "Montserrat Bold", "body": "Open Sans"}
        self.logo_usage = logo_usage  # Placement, size, clearspace rules
        self.visual_style = visual_style  # "modern", "minimal", "bold", "playful"
        self.imagery_style = imagery_style  # "photography", "illustration", "mixed", "abstract"
        self.spacing_rules = {"padding": "20px", "margin": "40px"}
        self.corner_radius = "8px"  # For rounded corners
        self.shadow_style = "0 4px 6px rgba(0, 0, 0, 0.1)"

    def to_prompt_context(self) -> str:
        """
        Convert guidelines to AI image generation prompt context.

        WHY: Provides AI with brand constraints for consistent output.
        HOW: Formats guidelines as natural language prompt context.
        """
        return f"""
        Brand Visual Guidelines:
        - Primary colors: {', '.join(self.primary_colors)}
        - Secondary colors: {', '.join(self.secondary_colors)}
        - Visual style: {self.visual_style}
        - Imagery style: {self.imagery_style}
        - Mood: professional, modern, trustworthy, innovative
        - Avoid: cluttered layouts, low-contrast colors, outdated styles
        """

    def validate_design(self, image: Image) -> dict[str, Any]:
        """
        Validate design compliance with brand guidelines.

        WHY: Ensures generated designs meet brand standards.
        HOW: Analyzes colors, composition, style.
        """
        validation = {
            "color_compliance": self._check_color_palette(image),
            "composition_quality": self._check_composition(image),
            "style_consistency": self._check_style(image),
            "overall_score": 0.0
        }

        # Calculate overall score (weighted average)
        validation["overall_score"] = (
            validation["color_compliance"] * 0.40 +
            validation["composition_quality"] * 0.30 +
            validation["style_consistency"] * 0.30
        )

        return validation
```

#### 4.9.8 Platform Specifications

The Designer maintains platform-specific dimension requirements:

```python
PLATFORM_SPECS = {
    "linkedin": {
        "post": {"width": 1200, "height": 627, "format": "jpg"},
        "profile_banner": {"width": 1584, "height": 396, "format": "jpg"},
        "company_logo": {"width": 300, "height": 300, "format": "png"},
        "story": {"width": 1080, "height": 1920, "format": "jpg"}
    },
    "twitter": {
        "post": {"width": 1200, "height": 675, "format": "jpg"},
        "header": {"width": 1500, "height": 500, "format": "jpg"},
        "profile": {"width": 400, "height": 400, "format": "jpg"}
    },
    "instagram": {
        "post": {"width": 1080, "height": 1080, "format": "jpg"},
        "story": {"width": 1080, "height": 1920, "format": "jpg"},
        "carousel": {"width": 1080, "height": 1080, "format": "jpg"},
        "reels": {"width": 1080, "height": 1920, "format": "mp4"}
    },
    "facebook": {
        "post": {"width": 1200, "height": 630, "format": "jpg"},
        "cover": {"width": 820, "height": 312, "format": "jpg"},
        "profile": {"width": 180, "height": 180, "format": "jpg"}
    },
    "blog": {
        "featured_image": {"width": 1200, "height": 630, "format": "webp"},
        "inline_image": {"width": 800, "height": 450, "format": "webp"},
        "thumbnail": {"width": 400, "height": 225, "format": "webp"}
    },
    "email": {
        "header": {"width": 600, "height": 200, "format": "png"},
        "banner": {"width": 600, "height": 300, "format": "png"}
    },
    "ads": {
        "leaderboard": {"width": 728, "height": 90, "format": "jpg"},
        "rectangle": {"width": 300, "height": 250, "format": "jpg"},
        "skyscraper": {"width": 160, "height": 600, "format": "jpg"},
        "mobile_banner": {"width": 320, "height": 50, "format": "jpg"}
    }
}
```

#### 4.9.9 Image Quality Validation

The Designer implements comprehensive quality checks:

```python
async def _validate_brand_compliance(self, image: Image) -> float:
    """
    Validate image compliance with brand guidelines.

    WHY: Ensures generated images match brand standards.
    HOW: Analyzes color palette, composition, style using computer vision.

    Returns:
        Brand compliance score (0-100)
    """
    score = 0.0

    # Analyze color palette (40 points)
    color_score = await self._analyze_color_compliance(image)
    score += color_score * 0.40

    # Check composition quality (30 points)
    composition_score = self._analyze_composition(image)
    score += composition_score * 0.30

    # Validate style consistency (30 points)
    style_score = self._analyze_style_consistency(image)
    score += style_score * 0.30

    return min(score, 100.0)

def _analyze_color_compliance(self, image: Image) -> float:
    """
    Analyze color palette compliance with brand colors.

    WHY: Brand colors are critical for visual identity.
    HOW: Extracts dominant colors and compares to brand palette.
    """
    # Guard clause: No brand guidelines
    if not self._brand_guidelines:
        return 100.0  # No guidelines to validate against

    # Extract dominant colors from image
    dominant_colors = self._extract_dominant_colors(image, count=5)

    # Check if dominant colors align with brand colors
    brand_colors = (
        self._brand_guidelines.primary_colors +
        self._brand_guidelines.secondary_colors
    )

    # Calculate color similarity score
    matching_colors = 0
    for dominant_color in dominant_colors:
        for brand_color in brand_colors:
            if self._color_similarity(dominant_color, brand_color) > 0.8:
                matching_colors += 1
                break

    # Score based on percentage of matching colors
    return (matching_colors / len(dominant_colors)) * 100.0

def _analyze_composition(self, image: Image) -> float:
    """
    Analyze image composition quality.

    WHY: Good composition improves visual appeal and engagement.
    HOW: Checks rule of thirds, balance, focal points, negative space.
    """
    score = 0.0

    # Check aspect ratio appropriateness (25 points)
    aspect_ratio = image.width / image.height
    ideal_ratios = [1.0, 1.91, 0.8, 16/9]  # Square, LinkedIn, Portrait, Widescreen

    closest_ratio = min(ideal_ratios, key=lambda x: abs(x - aspect_ratio))
    if abs(closest_ratio - aspect_ratio) < 0.1:
        score += 25.0
    elif abs(closest_ratio - aspect_ratio) < 0.3:
        score += 15.0

    # Check for focal point (25 points)
    has_clear_focal_point = self._detect_focal_point(image)
    if has_clear_focal_point:
        score += 25.0

    # Check balance (25 points)
    is_balanced = self._check_visual_balance(image)
    if is_balanced:
        score += 25.0

    # Check negative space (25 points)
    has_adequate_spacing = self._check_negative_space(image)
    if has_adequate_spacing:
        score += 25.0

    return score
```

#### 4.9.10 Architecture Compliance

**Strategy Pattern:**
```python
# ✅ CORRECT: Dictionary dispatch
self._task_handlers = {
    "generate_social_graphic": self._generate_social_graphic,
    "generate_blog_image": self._generate_blog_image,
    # ... other handlers
}

# ❌ WRONG: if/elif chains
if task.task_type == "generate_social_graphic":
    return await self._generate_social_graphic(task)
elif task.task_type == "generate_blog_image":
    return await self._generate_blog_image(task)
```

**Guard Clauses:**
```python
# ✅ CORRECT: Guard clause for early return
async def _generate_social_graphic(self, task: Task) -> dict[str, Any]:
    platform = task.parameters.get("platform")

    # Guard clause: Validate platform
    if platform not in self._platform_specs:
        return {"error": f"Unsupported platform: {platform}", "image_url": None}

    # Guard clause: Check if image generator available
    if not self._dalle_client:
        return {"error": "Image generator not configured", "image_url": None}

    # Main logic here
    return await self._generate_image(task)

# ❌ WRONG: Nested if statements
async def _generate_social_graphic(self, task: Task) -> dict[str, Any]:
    platform = task.parameters.get("platform")

    if platform in self._platform_specs:
        if self._dalle_client:
            # Deep nesting
            return await self._generate_image(task)
```

**Exception Wrapping:**
```python
# ✅ CORRECT: Wrap external API calls
try:
    image = await self._dalle_client.generate(prompt=prompt, size=size)
except Exception as e:
    raise AgentExecutionError(
        agent_id=self.agent_id,
        task_id=task.task_id,
        message=f"DALL-E API failed: {str(e)}",
        original_exception=e
    )

# ❌ WRONG: Let exceptions propagate
image = await self._dalle_client.generate(prompt=prompt, size=size)
```

---

### 4.10 Email Specialist Agent (Specialist Layer)

The **Email Specialist Agent** is a specialist-layer agent providing email marketing capabilities including campaign creation, delivery, A/B testing, list segmentation, performance tracking, and automation workflows.

**Agent Role:** `AgentRole.EMAIL_SPECIALIST`

**Supervised By:** Campaign Manager, Content Manager

**Coordinates With:** Copywriter Specialist (email copy), Designer Specialist (email headers/templates), Analytics Specialist (performance data)

**External Integrations:** SendGrid API, Mailchimp API, HubSpot Email API

#### Architecture

```python
class EmailSpecialistAgent(BaseAgent):
    """
    Specialist-layer agent for email marketing and automation.

    WHY: Provides specialized email campaign management, delivery, and optimization.
    HOW: Uses email service provider APIs (SendGrid, Mailchimp) with templates,
         segmentation, A/B testing, and performance tracking.
    """

    def __init__(
        self,
        config: AgentConfig,
        sender_name: str = "Company Name",
        sender_email: str = "marketing@example.com",
        reply_to_email: str = "reply@example.com"
    ):
        super().__init__(config)

        # Email service provider clients
        self._esp_client: Optional[SendGridClient] = None
        self._template_engine: Optional[TemplateEngine] = None

        # Sender configuration
        self._sender_name: str = sender_name
        self._sender_email: str = sender_email
        self._reply_to_email: str = reply_to_email

        # Email template cache
        self._template_cache: dict[str, EmailTemplate] = {}

        # Performance tracking cache (30-minute TTL)
        self._performance_cache: dict[str, tuple[dict[str, Any], datetime]] = {}
        self._cache_ttl = timedelta(minutes=30)

        # Strategy Pattern: Dictionary dispatch for task routing
        self._task_handlers: dict[
            str, Callable[[Task], Coroutine[Any, Any, dict[str, Any]]]
        ] = {
            "create_email_campaign": self._create_email_campaign,
            "send_email": self._send_email,
            "schedule_email": self._schedule_email,
            "create_email_template": self._create_email_template,
            "segment_email_list": self._segment_email_list,
            "ab_test_email": self._ab_test_email,
            "track_email_performance": self._track_email_performance,
            "create_drip_campaign": self._create_drip_campaign,
        }

        self.logger.info(
            f"Email Specialist initialized: {self.agent_id}",
            extra={"sender_email": sender_email}
        )

    async def _execute_task(self, task: Task) -> dict[str, Any]:
        """
        Execute email-related task using Strategy Pattern.

        WHY: Routes tasks to appropriate handlers without if/elif chains.
        HOW: Uses dictionary dispatch for clean task delegation.
        """
        # Guard clause: Check if task type is supported
        handler = self._task_handlers.get(task.task_type)
        if not handler:
            raise ValueError(f"Unsupported task type: {task.task_type}")

        # Guard clause: Validate task before execution
        if not await self.validate_task(task):
            raise ValueError(f"Task validation failed for {task.task_id}")

        try:
            # Execute task handler
            result = await handler(task)
            return result

        except Exception as e:
            raise AgentExecutionError(
                agent_id=self.agent_id,
                task_id=task.task_id,
                message=f"Email task execution failed: {str(e)}",
                original_exception=e
            )

    async def validate_task(self, task: Task) -> bool:
        """
        Validate task parameters before execution.

        WHY: Ensures tasks have required parameters for successful execution.
        HOW: Checks for required fields based on task type.
        """
        required_params = {
            "create_email_campaign": ["campaign_name", "subject_line", "recipient_list_id"],
            "send_email": ["campaign_id"],
            "schedule_email": ["campaign_id", "send_time"],
            "create_email_template": ["template_name", "subject_line", "html_content"],
            "segment_email_list": ["list_id", "segment_name", "criteria"],
            "ab_test_email": ["campaign_id", "test_type", "variant_a", "variant_b"],
            "track_email_performance": ["campaign_id"],
            "create_drip_campaign": ["campaign_name", "trigger_event", "email_sequence"],
        }

        # Guard clause: Check if task type is known
        if task.task_type not in required_params:
            return False

        # Check required parameters
        for param in required_params[task.task_type]:
            if param not in task.parameters:
                self.logger.warning(
                    f"Missing required parameter: {param}",
                    extra={"task_id": task.task_id, "task_type": task.task_type}
                )
                return False

        return True
```

#### Task Type 1: Create Email Campaign

**Purpose:** Create and configure email campaign with template, recipient list, and settings.

**Parameters:**
- `campaign_name` (str): Name of the email campaign
- `subject_line` (str): Email subject line
- `recipient_list_id` (str): ID of recipient list or segment
- `template_id` (str, optional): ID of email template to use
- `html_content` (str, optional): HTML email content (if not using template)
- `text_content` (str, optional): Plain text email content
- `preheader` (str, optional): Email preheader text
- `personalization_fields` (dict, optional): Fields for personalization

**Returns:**
```python
{
    "campaign_id": "campaign_12345",
    "campaign_name": "Product Launch Announcement",
    "subject_line": "Introducing Our New AI-Powered Platform",
    "recipient_count": 5000,
    "spam_score": 2.1,
    "deliverability_status": "passed",
    "preview_url": "https://esp.example.com/preview/campaign_12345",
    "status": "draft"
}
```

**Implementation:**
```python
async def _create_email_campaign(self, task: Task) -> dict[str, Any]:
    """
    Create and configure email campaign.

    WHY: Enables structured email campaign creation with templates and segmentation.
    HOW: Uses ESP API to create campaign with template, list, and settings.
    """
    campaign_name = task.parameters["campaign_name"]
    template_id = task.parameters.get("template_id")
    subject_line = task.parameters["subject_line"]
    recipient_list_id = task.parameters["recipient_list_id"]
    html_content = task.parameters.get("html_content")
    text_content = task.parameters.get("text_content")

    # Guard clause: Validate ESP client is available
    if not self._esp_client:
        return {"error": "Email service provider not configured", "campaign_id": None}

    # Guard clause: Validate either template or content provided
    if not template_id and not html_content:
        return {"error": "Either template_id or html_content required"}

    # Guard clause: Validate template exists if provided
    if template_id and not await self._template_exists(template_id):
        return {"error": f"Template {template_id} not found", "campaign_id": None}

    try:
        # Create campaign via ESP
        campaign = await self._esp_client.create_campaign(
            name=campaign_name,
            subject=subject_line,
            template_id=template_id,
            html_content=html_content,
            text_content=text_content,
            list_id=recipient_list_id,
            from_name=self._sender_name,
            from_email=self._sender_email,
            reply_to=self._reply_to_email
        )

        # Check spam score
        spam_score = await self._check_spam_score(campaign.preview_html)

        # Validate deliverability
        deliverability_check = await self._validate_deliverability(campaign)

        self.logger.info(
            f"Email campaign created: {campaign.id}",
            extra={
                "campaign_name": campaign_name,
                "recipients": campaign.recipient_count,
                "spam_score": spam_score
            }
        )

        return {
            "campaign_id": campaign.id,
            "campaign_name": campaign_name,
            "subject_line": subject_line,
            "recipient_count": campaign.recipient_count,
            "spam_score": spam_score,
            "deliverability_status": deliverability_check["status"],
            "preview_url": campaign.preview_url,
            "status": "draft"
        }

    except Exception as e:
        raise AgentExecutionError(
            agent_id=self.agent_id,
            task_id=task.task_id,
            message=f"Failed to create email campaign: {str(e)}",
            original_exception=e
        )
```

#### Task Type 2: Send Email

**Purpose:** Send email campaign to recipients immediately.

**Parameters:**
- `campaign_id` (str): ID of campaign to send
- `test_mode` (bool, optional): Send to test list only

**Returns:**
```python
{
    "campaign_id": "campaign_12345",
    "status": "sending",
    "sent_count": 5000,
    "send_time": "2025-11-03T10:30:00Z",
    "estimated_delivery": "2025-11-03T10:35:00Z"
}
```

**Implementation:**
```python
async def _send_email(self, task: Task) -> dict[str, Any]:
    """
    Send email campaign to recipients.

    WHY: Delivers email to recipient list immediately.
    HOW: Uses ESP API to trigger campaign send.
    """
    campaign_id = task.parameters["campaign_id"]
    test_mode = task.parameters.get("test_mode", False)

    # Guard clause: Validate ESP client
    if not self._esp_client:
        return {"error": "Email service provider not configured"}

    # Guard clause: Validate campaign exists
    campaign = await self._get_campaign(campaign_id)
    if not campaign:
        return {"error": f"Campaign {campaign_id} not found"}

    try:
        # Send campaign
        send_result = await self._esp_client.send_campaign(
            campaign_id=campaign_id,
            test_mode=test_mode
        )

        self.logger.info(
            f"Email campaign sent: {campaign_id}",
            extra={
                "sent_count": send_result.sent_count,
                "test_mode": test_mode
            }
        )

        return {
            "campaign_id": campaign_id,
            "status": "sending",
            "sent_count": send_result.sent_count,
            "send_time": send_result.send_time.isoformat(),
            "estimated_delivery": send_result.estimated_delivery.isoformat()
        }

    except Exception as e:
        raise AgentExecutionError(
            agent_id=self.agent_id,
            task_id=task.task_id,
            message=f"Failed to send email: {str(e)}",
            original_exception=e
        )
```

#### Task Type 3: Schedule Email

**Purpose:** Schedule email campaign for future delivery.

**Parameters:**
- `campaign_id` (str): ID of campaign to schedule
- `send_time` (str): ISO format datetime for send time
- `timezone` (str, optional): Timezone for send time (default: UTC)

**Returns:**
```python
{
    "campaign_id": "campaign_12345",
    "status": "scheduled",
    "scheduled_send_time": "2025-11-05T09:00:00Z",
    "recipient_count": 5000
}
```

#### Task Type 4: Create Email Template

**Purpose:** Create reusable email template with personalization support.

**Parameters:**
- `template_name` (str): Name of template
- `subject_line` (str): Default subject line
- `html_content` (str): HTML template content
- `text_content` (str): Plain text template content
- `personalization_fields` (list[str]): List of personalization fields (e.g., ["first_name", "company"])
- `category` (str): Template category (newsletter, promotional, transactional)

**Returns:**
```python
{
    "template_id": "template_789",
    "template_name": "Product Launch Template",
    "category": "promotional",
    "personalization_fields": ["first_name", "company", "product_name"],
    "created_at": "2025-11-03T10:00:00Z"
}
```

#### Task Type 5: Segment Email List

**Purpose:** Segment email list based on criteria for targeted messaging.

**Parameters:**
- `list_id` (str): ID of email list to segment
- `segment_name` (str): Name for the segment
- `criteria` (dict): Segmentation criteria (e.g., {"engagement": "active", "location": "US"})

**Returns:**
```python
{
    "segment_id": "segment_456",
    "segment_name": "Active US Subscribers",
    "list_id": "list_123",
    "subscriber_count": 1250,
    "criteria": {"engagement": "active", "location": "US"},
    "created_at": "2025-11-03T10:00:00Z"
}
```

**Implementation:**
```python
async def _segment_email_list(self, task: Task) -> dict[str, Any]:
    """
    Segment email list based on criteria.

    WHY: Enables targeted messaging to specific audience segments.
    HOW: Applies filters to subscriber list and creates segment.
    """
    list_id = task.parameters["list_id"]
    segment_name = task.parameters["segment_name"]
    criteria = task.parameters["criteria"]

    # Guard clause: Validate list exists
    email_list = await self._get_list(list_id)
    if not email_list:
        return {"error": f"List {list_id} not found"}

    try:
        # Build segmentation query
        query_conditions = []

        for key, value in criteria.items():
            if key == "engagement":
                if value == "active":
                    query_conditions.append("opened_last_30_days = true")
                elif value == "inactive":
                    query_conditions.append("opened_last_90_days = false")
                elif value == "new":
                    query_conditions.append("subscription_date > DATE_SUB(NOW(), INTERVAL 30 DAY)")
            elif key == "location":
                query_conditions.append(f"country = '{value}'")
            elif key == "industry":
                query_conditions.append(f"industry = '{value}'")
            else:
                query_conditions.append(f"{key} = '{value}'")

        # Create segment via ESP
        segment = await self._esp_client.create_segment(
            list_id=list_id,
            name=segment_name,
            conditions=query_conditions
        )

        self.logger.info(
            f"Email list segmented: {segment.id}",
            extra={
                "segment_name": segment_name,
                "subscriber_count": segment.subscriber_count
            }
        )

        return {
            "segment_id": segment.id,
            "segment_name": segment_name,
            "list_id": list_id,
            "subscriber_count": segment.subscriber_count,
            "criteria": criteria,
            "created_at": segment.created_at.isoformat()
        }

    except Exception as e:
        raise AgentExecutionError(
            agent_id=self.agent_id,
            task_id=task.task_id,
            message=f"Failed to segment email list: {str(e)}",
            original_exception=e
        )
```

#### Task Type 6: A/B Test Email

**Purpose:** Create A/B test for email campaign to optimize performance.

**Parameters:**
- `campaign_id` (str): ID of campaign to test
- `test_type` (str): Type of test (subject_line, content, send_time)
- `variant_a` (Any): First variant (subject line, content ID, or send time)
- `variant_b` (Any): Second variant
- `test_size_percent` (int, optional): Percentage of list for test (default: 20)
- `winning_metric` (str, optional): Metric to determine winner (open_rate, click_rate, conversion_rate)

**Returns:**
```python
{
    "ab_test_id": "test_999",
    "campaign_id": "campaign_12345",
    "test_type": "subject_line",
    "variant_a": {"subject_line": "Transform Your Marketing Today"},
    "variant_b": {"subject_line": "Revolutionize Your Marketing Strategy"},
    "test_size_percent": 20,
    "test_recipients": 1000,
    "winner_selection": "automatic",
    "status": "scheduled"
}
```

#### Task Type 7: Track Email Performance

**Purpose:** Track email campaign performance metrics and analytics.

**Parameters:**
- `campaign_id` (str): ID of campaign to track
- `include_link_clicks` (bool, optional): Include individual link click data

**Returns:**
```python
{
    "campaign_id": "campaign_12345",
    "campaign_name": "Product Launch",
    "sent": 5000,
    "delivered": 4950,
    "opens": 2475,
    "unique_opens": 2200,
    "clicks": 742,
    "unique_clicks": 650,
    "bounces": 50,
    "spam_complaints": 5,
    "unsubscribes": 15,
    "open_rate": 44.44,
    "click_rate": 14.99,
    "bounce_rate": 1.0,
    "unsubscribe_rate": 0.30,
    "click_to_open_rate": 29.55,
    "revenue": 15000.00,
    "timestamp": "2025-11-03T15:00:00Z"
}
```

**Implementation:**
```python
async def _track_email_performance(self, task: Task) -> dict[str, Any]:
    """
    Track email campaign performance metrics.

    WHY: Provides insights for optimization and ROI measurement.
    HOW: Fetches analytics from ESP API and calculates key metrics.
    """
    campaign_id = task.parameters["campaign_id"]

    # Check cache first (30-minute TTL)
    cache_key = f"performance_{campaign_id}"
    if cache_key in self._performance_cache:
        cached_data, cached_time = self._performance_cache[cache_key]
        if datetime.now() - cached_time < self._cache_ttl:
            cached_data["cached"] = True
            return cached_data

    # Guard clause: Validate campaign exists
    campaign = await self._get_campaign(campaign_id)
    if not campaign:
        return {"error": f"Campaign {campaign_id} not found"}

    try:
        # Fetch performance data from ESP
        stats = await self._esp_client.get_campaign_stats(campaign_id)

        # Calculate derived metrics
        open_rate = (stats.opens / stats.delivered) * 100 if stats.delivered > 0 else 0
        click_rate = (stats.clicks / stats.delivered) * 100 if stats.delivered > 0 else 0
        bounce_rate = (stats.bounces / stats.sent) * 100 if stats.sent > 0 else 0
        unsubscribe_rate = (stats.unsubscribes / stats.delivered) * 100 if stats.delivered > 0 else 0
        click_to_open_rate = (stats.clicks / stats.opens) * 100 if stats.opens > 0 else 0

        result = {
            "campaign_id": campaign_id,
            "campaign_name": campaign.name,
            "sent": stats.sent,
            "delivered": stats.delivered,
            "opens": stats.opens,
            "unique_opens": stats.unique_opens,
            "clicks": stats.clicks,
            "unique_clicks": stats.unique_clicks,
            "bounces": stats.bounces,
            "spam_complaints": stats.spam_complaints,
            "unsubscribes": stats.unsubscribes,
            "open_rate": round(open_rate, 2),
            "click_rate": round(click_rate, 2),
            "bounce_rate": round(bounce_rate, 2),
            "unsubscribe_rate": round(unsubscribe_rate, 2),
            "click_to_open_rate": round(click_to_open_rate, 2),
            "revenue": stats.revenue if hasattr(stats, 'revenue') else 0,
            "timestamp": datetime.now().isoformat(),
            "cached": False
        }

        # Cache result
        self._performance_cache[cache_key] = (result, datetime.now())

        return result

    except Exception as e:
        raise AgentExecutionError(
            agent_id=self.agent_id,
            task_id=task.task_id,
            message=f"Failed to track email performance: {str(e)}",
            original_exception=e
        )
```

#### Task Type 8: Create Drip Campaign

**Purpose:** Create automated drip campaign workflow with timed email sequence.

**Parameters:**
- `campaign_name` (str): Name of drip campaign
- `trigger_event` (str): Event that triggers campaign (subscription, purchase, download)
- `email_sequence` (list[dict]): List of emails with delays
  - Each email: `{"template_id": str, "delay_days": int, "subject_line": str, "condition": str (optional)}`

**Returns:**
```python
{
    "drip_campaign_id": "drip_555",
    "campaign_name": "Welcome Series",
    "trigger_event": "subscription",
    "email_count": 5,
    "workflow_steps": [
        {"step_number": 1, "template_id": "welcome_1", "delay_days": 0},
        {"step_number": 2, "template_id": "features_intro", "delay_days": 3},
        {"step_number": 3, "template_id": "case_study", "delay_days": 7}
    ],
    "status": "active",
    "created_at": "2025-11-03T10:00:00Z"
}
```

#### State Management

The Email Specialist maintains several types of state:

1. **Template Cache:** Frequently used email templates cached in memory
2. **Performance Cache:** Campaign performance data cached with 30-minute TTL
3. **ESP Client:** Connection to email service provider API
4. **Sender Configuration:** Default sender name, email, reply-to

```python
# Example state structure
{
    "_template_cache": {
        "template_123": EmailTemplate(...),
        "template_456": EmailTemplate(...)
    },
    "_performance_cache": {
        "performance_campaign_12345": (
            {"open_rate": 45.2, "click_rate": 15.1, ...},
            datetime(2025, 11, 3, 14, 30, 0)
        )
    },
    "_esp_client": SendGridClient(...),
    "_sender_name": "Company Name",
    "_sender_email": "marketing@example.com"
}
```

#### Coordination Examples

**Example 1: Campaign Manager requests email campaign**
```python
# Campaign Manager delegates email campaign creation
campaign_manager -> email_specialist.create_email_campaign(
    campaign_name="Q4 Product Launch",
    subject_line="Introducing Our Revolutionary AI Platform",
    recipient_list_id="segment_enterprise",
    template_id="product_launch_template"
)

# Email Specialist creates campaign
email_specialist -> {
    "campaign_id": "campaign_12345",
    "recipient_count": 5000,
    "deliverability_status": "passed"
}

# Campaign Manager delegates sending
campaign_manager -> email_specialist.send_email(
    campaign_id="campaign_12345"
)

# Email Specialist sends campaign
email_specialist -> ESP API -> Sends 5000 emails
```

**Example 2: Content Manager requests newsletter with visual assets**
```python
# Content Manager coordinates with Copywriter and Designer
content_manager -> copywriter.write_email(...)
content_manager -> designer.design_email_header(...)

# Content Manager delegates to Email Specialist
content_manager -> email_specialist.create_email_campaign(
    campaign_name="Monthly Newsletter",
    subject_line="Marketing Insights - November 2025",
    html_content="<html>...</html>",  # Includes copy and header
    recipient_list_id="newsletter_subscribers"
)

# Email Specialist creates and validates campaign
email_specialist -> {
    "campaign_id": "campaign_67890",
    "spam_score": 1.8,
    "deliverability_status": "passed"
}
```

**Example 3: A/B testing optimization workflow**
```python
# Campaign Manager requests A/B test
campaign_manager -> email_specialist.ab_test_email(
    campaign_id="campaign_12345",
    test_type="subject_line",
    variant_a="Transform Your Marketing Today",
    variant_b="Revolutionize Your Marketing Strategy",
    test_size_percent=20
)

# Email Specialist creates A/B test
email_specialist -> ESP API -> Creates test with 1000 recipients

# After test completes, Email Specialist tracks performance
email_specialist.track_email_performance(campaign_id="campaign_12345")
-> {
    "winning_variant": "variant_b",
    "variant_a_open_rate": 38.5,
    "variant_b_open_rate": 45.2
}

# ESP automatically sends winning variant to remaining 80%
```

**Example 4: Drip campaign automation**
```python
# Content Manager requests onboarding drip campaign
content_manager -> email_specialist.create_drip_campaign(
    campaign_name="Customer Onboarding",
    trigger_event="subscription",
    email_sequence=[
        {
            "template_id": "welcome_email",
            "delay_days": 0,
            "subject_line": "Welcome to Our Platform!"
        },
        {
            "template_id": "getting_started",
            "delay_days": 2,
            "subject_line": "Get Started with Your First Project"
        },
        {
            "template_id": "advanced_features",
            "delay_days": 7,
            "subject_line": "Unlock Advanced Features",
            "condition": "opened_previous"
        },
        {
            "template_id": "case_study",
            "delay_days": 14,
            "subject_line": "How Companies Like Yours Succeed"
        }
    ]
)

# Email Specialist creates automation workflow
email_specialist -> ESP API -> Creates triggered automation

# When user subscribes:
user subscribes -> ESP triggers workflow -> Sends 4 emails over 14 days
```

#### Architecture Compliance

The Email Specialist follows all architecture standards:

**Strategy Pattern (Zero if/elif chains):**
```python
# ✅ CORRECT: Strategy Pattern with dictionary dispatch
self._task_handlers = {
    "create_email_campaign": self._create_email_campaign,
    "send_email": self._send_email,
    "schedule_email": self._schedule_email,
    "create_email_template": self._create_email_template,
    "segment_email_list": self._segment_email_list,
    "ab_test_email": self._ab_test_email,
    "track_email_performance": self._track_email_performance,
    "create_drip_campaign": self._create_drip_campaign,
}

handler = self._task_handlers.get(task.task_type)
result = await handler(task)

# ❌ WRONG: if/elif chains
if task.task_type == "create_email_campaign":
    result = await self._create_email_campaign(task)
elif task.task_type == "send_email":
    result = await self._send_email(task)
# ... more elif statements
```

**Guard Clauses (No nested ifs):**
```python
# ✅ CORRECT: Guard clauses with early returns
async def _send_email(self, task: Task) -> dict[str, Any]:
    campaign_id = task.parameters["campaign_id"]

    # Guard clause: Validate ESP client
    if not self._esp_client:
        return {"error": "Email service provider not configured"}

    # Guard clause: Validate campaign exists
    campaign = await self._get_campaign(campaign_id)
    if not campaign:
        return {"error": f"Campaign {campaign_id} not found"}

    # Main logic
    send_result = await self._esp_client.send_campaign(campaign_id=campaign_id)
    return {"campaign_id": campaign_id, "status": "sending"}

# ❌ WRONG: Nested if statements
async def _send_email(self, task: Task) -> dict[str, Any]:
    if self._esp_client:
        campaign = await self._get_campaign(campaign_id)
        if campaign:
            send_result = await self._esp_client.send_campaign(campaign_id)
            return {"status": "sending"}
```

**Exception Wrapping:**
```python
# ✅ CORRECT: Wrap external API calls with AgentExecutionError
try:
    campaign = await self._esp_client.create_campaign(...)
    return {"campaign_id": campaign.id}
except Exception as e:
    raise AgentExecutionError(
        agent_id=self.agent_id,
        task_id=task.task_id,
        message=f"Failed to create email campaign: {str(e)}",
        original_exception=e
    )

# ❌ WRONG: Let exceptions propagate
campaign = await self._esp_client.create_campaign(...)
```

---

## 5. Data Models

### 5.1 Core Entities

#### Task Model

```python
class Task(BaseModel):
    id: str  # UUID
    type: TaskType  # Enum: market_research, content_creation, etc.
    title: str
    description: str
    priority: TaskPriority  # Enum: low, medium, high, urgent
    status: TaskStatus  # Enum: queued, in_progress, completed, failed
    assigned_agent: str
    created_by: str  # User ID
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    dependencies: List[str]  # Task IDs that must complete first
    context: Dict[str, Any]  # Additional context for the task
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    retry_count: int = 0
    max_retries: int = 3
```

#### Content Model

```python
class Content(BaseModel):
    id: str
    type: ContentType  # blog, linkedin, email, case_study, whitepaper
    title: str
    body: str  # Markdown or HTML
    author: str
    target_audience: str
    keywords: List[str]
    metadata: Dict[str, Any]

    # Quality scores
    brand_voice_score: float  # 0-100
    seo_score: float
    readability_score: float

    # Workflow
    status: ContentStatus  # draft, review, approved, rejected, published
    created_at: datetime
    reviewed_at: Optional[datetime]
    reviewed_by: Optional[str]
    published_at: Optional[datetime]

    # Performance (post-publication)
    views: int = 0
    engagements: int = 0
    conversions: int = 0

    # Relations
    campaign_id: Optional[str]
    tags: List[str]
```

#### Campaign Model

```python
class Campaign(BaseModel):
    id: str
    name: str
    type: CampaignType  # email, social, integrated
    objective: str
    target_audience: AudienceSegment

    # Timeline
    start_date: date
    end_date: date

    # Content
    content_pieces: List[str]  # Content IDs

    # Metrics
    target_metrics: Dict[str, float]
    actual_metrics: Dict[str, float]

    # Budget
    budget: Optional[float]
    spend: Optional[float]

    # Status
    status: CampaignStatus  # planning, active, paused, completed
    created_by: str
    created_at: datetime
```

#### Competitor Model

```python
class Competitor(BaseModel):
    id: str
    name: str
    website_url: str
    industry: str

    # Analysis
    positioning: str
    value_props: List[str]
    strengths: List[str]
    weaknesses: List[str]

    # Content strategy
    content_types: List[str]
    posting_frequency: Dict[str, int]  # platform -> posts/week

    # Tracking
    last_analyzed: datetime
    analysis_history: List[Dict[str, Any]]
```

#### User Model

```python
class User(BaseModel):
    id: str
    email: str
    name: str
    role: UserRole  # admin, marketing_director, content_manager, viewer

    # Preferences
    notification_preferences: Dict[str, bool]
    default_brand_voice: str

    # Activity
    created_at: datetime
    last_login: datetime
    tasks_created: int
    approvals_made: int
```

### 5.2 Database Schema

```sql
-- Tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    priority VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    assigned_agent VARCHAR(100),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    dependencies JSONB DEFAULT '[]',
    context JSONB DEFAULT '{}',
    result JSONB,
    error_message TEXT,
    retry_count INT DEFAULT 0,
    max_retries INT DEFAULT 3,
    INDEX idx_status (status),
    INDEX idx_priority (priority),
    INDEX idx_created_at (created_at)
);

-- Content table
CREATE TABLE content (
    id UUID PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    body TEXT NOT NULL,
    author VARCHAR(200),
    target_audience VARCHAR(200),
    keywords TEXT[],
    metadata JSONB DEFAULT '{}',
    brand_voice_score DECIMAL(5,2),
    seo_score DECIMAL(5,2),
    readability_score DECIMAL(5,2),
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    reviewed_at TIMESTAMP,
    reviewed_by UUID REFERENCES users(id),
    published_at TIMESTAMP,
    views INT DEFAULT 0,
    engagements INT DEFAULT 0,
    conversions INT DEFAULT 0,
    campaign_id UUID REFERENCES campaigns(id),
    tags TEXT[],
    INDEX idx_type (type),
    INDEX idx_status (status),
    INDEX idx_published_at (published_at)
);

-- Campaigns table
CREATE TABLE campaigns (
    id UUID PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    type VARCHAR(50) NOT NULL,
    objective TEXT,
    target_audience JSONB,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    target_metrics JSONB DEFAULT '{}',
    actual_metrics JSONB DEFAULT '{}',
    budget DECIMAL(10,2),
    spend DECIMAL(10,2),
    status VARCHAR(20) NOT NULL,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_status (status),
    INDEX idx_dates (start_date, end_date)
);

-- Competitors table
CREATE TABLE competitors (
    id UUID PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    website_url VARCHAR(500),
    industry VARCHAR(100),
    positioning TEXT,
    value_props JSONB DEFAULT '[]',
    strengths JSONB DEFAULT '[]',
    weaknesses JSONB DEFAULT '[]',
    content_types JSONB DEFAULT '[]',
    posting_frequency JSONB DEFAULT '{}',
    last_analyzed TIMESTAMP,
    analysis_history JSONB DEFAULT '[]',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    role VARCHAR(50) NOT NULL,
    notification_preferences JSONB DEFAULT '{}',
    default_brand_voice VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login TIMESTAMP,
    tasks_created INT DEFAULT 0,
    approvals_made INT DEFAULT 0
);

-- Analytics events table
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),  -- content, campaign, task
    entity_id UUID,
    properties JSONB DEFAULT '{}',
    occurred_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_event_type (event_type),
    INDEX idx_entity (entity_type, entity_id),
    INDEX idx_occurred_at (occurred_at)
);
```

---

## 6. API Specifications

### 6.1 RESTful API Endpoints

**Base URL**: `https://api.ai-elevate.ai/v1`

#### Authentication

All API requests require authentication via JWT token:

```
Authorization: Bearer <jwt_token>
```

#### Strategy Agent Endpoints

```
POST /strategy/market-trends
GET  /strategy/market-trends/:id
POST /strategy/competitor-analysis
GET  /strategy/competitors
POST /strategy/content-topics
POST /strategy/recommendations
```

**Example: Analyze Market Trends**

```http
POST /strategy/market-trends
Content-Type: application/json
Authorization: Bearer <token>

{
  "industry": "enterprise AI training",
  "timeframe": "current",
  "focus_areas": ["prompt engineering", "LLM adoption"]
}

Response (200 OK):
{
  "id": "trend_abc123",
  "analysis": {
    "key_trends": [...],
    "opportunities": [...],
    "content_angles": [...],
    "competitive_landscape": {...}
  },
  "created_at": "2025-11-03T10:30:00Z",
  "status": "completed"
}
```

#### Content Agent Endpoints

```
POST /content/blog-posts
GET  /content/blog-posts/:id
PUT  /content/blog-posts/:id
DELETE /content/blog-posts/:id
POST /content/blog-posts/:id/approve
POST /content/blog-posts/:id/reject
POST /content/case-studies
POST /content/whitepapers
POST /content/validate
```

**Example: Generate Blog Post**

```http
POST /content/blog-posts
Content-Type: application/json

{
  "topic": "Why 80% of AI Implementations Fail",
  "target_audience": "enterprise_leaders",
  "keywords": ["AI implementation", "enterprise AI", "AI ROI"],
  "target_length": 1500,
  "tone": "professional"
}

Response (201 Created):
{
  "id": "blog_xyz789",
  "title": "Why 80% of AI Implementations Fail (And How to Be in the 20%)",
  "body": "...",
  "brand_voice_score": 92.5,
  "seo_score": 88.0,
  "readability_score": 65.2,
  "status": "review",
  "created_at": "2025-11-03T10:35:00Z"
}
```

#### Social Media Agent Endpoints

```
POST /social/linkedin/posts
POST /social/twitter/tweets
POST /social/content-calendar
GET  /social/analytics
POST /social/schedule
```

#### Campaign Agent Endpoints

```
POST /campaigns
GET  /campaigns
GET  /campaigns/:id
PUT  /campaigns/:id
POST /campaigns/:id/email-sequences
GET  /campaigns/:id/metrics
POST /campaigns/:id/ab-tests
```

#### Analytics Agent Endpoints

```
GET  /analytics/dashboard
POST /analytics/reports
GET  /analytics/trends
POST /analytics/recommendations
GET  /analytics/forecasts
```

### 6.2 WebSocket API

Real-time updates for task progress and notifications:

```
wss://api.ai-elevate.ai/v1/ws
```

**Events**:
- `task.created`
- `task.started`
- `task.progress`
- `task.completed`
- `task.failed`
- `content.ready_for_review`
- `content.approved`
- `content.published`

**Example WebSocket Message**:

```json
{
  "event": "task.progress",
  "data": {
    "task_id": "task_123",
    "progress": 65,
    "message": "Generating blog post content...",
    "timestamp": "2025-11-03T10:40:00Z"
  }
}
```

### 6.3 Webhook Configuration

Allow external systems to receive notifications:

```
POST /webhooks
GET  /webhooks
DELETE /webhooks/:id
```

**Webhook Payload Example**:

```json
{
  "event": "content.published",
  "timestamp": "2025-11-03T11:00:00Z",
  "data": {
    "content_id": "blog_xyz789",
    "type": "blog",
    "title": "Why 80% of AI Implementations Fail",
    "url": "https://ai-elevate.ai/blog/why-ai-implementations-fail",
    "published_at": "2025-11-03T11:00:00Z"
  }
}
```

---

## 7. Integration Specifications

### 7.1 LinkedIn Integration

**API**: LinkedIn Marketing Developer Platform
**Authentication**: OAuth 2.0
**Scope Required**: `w_member_social`, `r_basicprofile`, `r_organization_social`

**Capabilities**:
- Create and publish posts
- Schedule posts
- Retrieve engagement metrics
- Fetch company page analytics

**Rate Limits**:
- 500 requests per user per day
- 100 requests per app per day (for organization endpoints)

**Implementation**:

```python
class LinkedInIntegration:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.linkedin.com/v2"

    def create_post(
        self,
        text: str,
        visibility: str = "PUBLIC"
    ) -> Dict[str, Any]:
        """Create a LinkedIn post"""

    def get_post_analytics(
        self,
        post_id: str
    ) -> Dict[str, Any]:
        """Retrieve engagement metrics for a post"""
```

### 7.2 Twitter/X Integration

**API**: Twitter API v2
**Authentication**: OAuth 2.0 + Bearer Token
**Scope Required**: `tweet.read`, `tweet.write`, `users.read`

**Capabilities**:
- Post tweets and threads
- Schedule tweets
- Retrieve engagement metrics
- Monitor mentions

**Rate Limits**:
- 300 tweets per 3-hour window
- 50 requests per 15 minutes (read endpoints)

**Implementation**:

```python
class TwitterIntegration:
    def __init__(self, bearer_token: str):
        self.bearer_token = bearer_token
        self.base_url = "https://api.twitter.com/2"

    def create_tweet(
        self,
        text: str,
        reply_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """Post a tweet"""

    def create_thread(
        self,
        tweets: List[str]
    ) -> List[Dict[str, Any]]:
        """Post a thread of tweets"""
```

### 7.3 CRM Integration (HubSpot)

**API**: HubSpot CRM API
**Authentication**: API Key or OAuth 2.0
**Key Objects**: Contacts, Companies, Deals

**Capabilities**:
- Track content engagement by contact
- Attribute conversions to content
- Segment audiences for campaigns
- Sync lead data

**Implementation**:

```python
class HubSpotIntegration:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.hubapi.com"

    def track_content_engagement(
        self,
        contact_email: str,
        content_id: str,
        engagement_type: str
    ) -> None:
        """Track when a contact engages with content"""

    def get_audience_segment(
        self,
        criteria: Dict[str, Any]
    ) -> List[Contact]:
        """Retrieve contacts matching criteria"""
```

### 7.4 Google Analytics Integration

**API**: Google Analytics Data API (GA4)
**Authentication**: Service Account or OAuth 2.0
**Metrics**: Sessions, Users, Conversions, Events

**Capabilities**:
- Track website traffic from content
- Measure conversion paths
- Analyze user behavior
- Attribution reporting

**Implementation**:

```python
class GoogleAnalyticsIntegration:
    def __init__(self, credentials_path: str):
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )
        self.client = BetaAnalyticsDataClient(credentials=self.credentials)

    def get_content_performance(
        self,
        content_url: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Get performance metrics for a content piece"""
```

### 7.5 Email Service Provider (SendGrid)

**API**: SendGrid Web API v3
**Authentication**: API Key
**Capabilities**: Send emails, track opens/clicks, manage lists

**Implementation**:

```python
class SendGridIntegration:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = SendGridAPIClient(api_key)

    def send_campaign_email(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        track_engagement: bool = True
    ) -> Dict[str, Any]:
        """Send a campaign email"""
```

---

## 8. User Interface

### 8.1 CLI Interface

**Current Implementation**: ✅ Complete
**Location**: `main.py`

**Commands**:
```bash
# Interactive mode
python main.py interactive

# Market analysis
python main.py trends --industry "enterprise AI"

# Competitor analysis
python main.py competitor --competitor "Coursera" --url "https://coursera.com"

# Content topics
python main.py topics --content-type linkedin --count 5

# Campaign planning
python main.py plan --objective "Generate 50 leads" --timeframe "1 month"
```

### 8.2 Web Dashboard (Phase 2)

**Framework**: React + Next.js + TailwindCSS
**State Management**: Redux Toolkit
**Charts**: Recharts or Chart.js

**Pages**:

1. **Dashboard** (`/dashboard`)
   - Overview metrics (KPIs)
   - Recent activity feed
   - Pending approvals
   - Quick actions

2. **Content Library** (`/content`)
   - All content pieces
   - Filters (type, status, date)
   - Search functionality
   - Performance metrics

3. **Content Editor** (`/content/new`, `/content/:id/edit`)
   - Rich text editor (TipTap or Slate)
   - Live preview
   - SEO score display
   - Brand voice validation
   - Save as draft / Submit for review

4. **Campaigns** (`/campaigns`)
   - Active campaigns
   - Campaign builder
   - Performance tracking
   - A/B test results

5. **Analytics** (`/analytics`)
   - Traffic sources
   - Content performance
   - Channel breakdown
   - Conversion funnels
   - Custom reports

6. **Social Media** (`/social`)
   - Content calendar view
   - Post scheduler
   - Engagement metrics
   - Mentions monitoring

7. **Competitors** (`/competitors`)
   - Competitor list
   - Analysis history
   - Content gap analysis
   - Positioning map

8. **Settings** (`/settings`)
   - Brand voice configuration
   - API integrations
   - User management
   - Notification preferences

**UI Components**:

```typescript
// Task approval card
interface ApprovalCard {
  task: Task;
  content: Content;
  onApprove: () => void;
  onReject: (reason: string) => void;
  onEdit: () => void;
}

// Content performance widget
interface PerformanceWidget {
  contentId: string;
  metrics: {
    views: number;
    engagement: number;
    conversions: number;
    roi: number;
  };
  trend: "up" | "down" | "stable";
}

// Campaign progress tracker
interface CampaignProgress {
  campaignId: string;
  progress: number;  // 0-100
  milestones: Milestone[];
  status: CampaignStatus;
}
```

---

## 9. Security & Privacy

### 9.1 Authentication & Authorization

**Authentication Method**: JWT (JSON Web Tokens)
**Token Expiry**: 24 hours
**Refresh Tokens**: 30 days

**Role-Based Access Control (RBAC)**:

| Role | Permissions |
|------|-------------|
| **Admin** | Full system access, user management, API key management |
| **Marketing Director** | Approve content, create campaigns, view all analytics |
| **Content Manager** | Create/edit content, view analytics for own content |
| **Viewer** | Read-only access to content and analytics |

**Implementation**:

```python
class Permission(Enum):
    VIEW_CONTENT = "view:content"
    CREATE_CONTENT = "create:content"
    APPROVE_CONTENT = "approve:content"
    DELETE_CONTENT = "delete:content"
    VIEW_ANALYTICS = "view:analytics"
    MANAGE_USERS = "manage:users"
    MANAGE_INTEGRATIONS = "manage:integrations"

class Role(Enum):
    ADMIN = [all permissions]
    MARKETING_DIRECTOR = [
        Permission.VIEW_CONTENT,
        Permission.CREATE_CONTENT,
        Permission.APPROVE_CONTENT,
        Permission.VIEW_ANALYTICS
    ]
    CONTENT_MANAGER = [
        Permission.VIEW_CONTENT,
        Permission.CREATE_CONTENT,
        Permission.VIEW_ANALYTICS
    ]
    VIEWER = [
        Permission.VIEW_CONTENT,
        Permission.VIEW_ANALYTICS
    ]
```

### 9.2 Data Protection

**Encryption**:
- **At Rest**: AES-256 encryption for database
- **In Transit**: TLS 1.3 for all API communications
- **Secrets**: AWS Secrets Manager or HashiCorp Vault

**Data Retention**:
- Content: Indefinite (archival)
- Tasks: 90 days (then archived)
- Analytics events: 2 years
- Logs: 30 days

**PII Handling**:
- Email addresses encrypted in database
- User data minimization
- GDPR compliance (right to deletion, data export)

### 9.3 API Security

**Rate Limiting**:
```python
# Per user
@rate_limit("100/hour")
@rate_limit("1000/day")

# Per endpoint
@rate_limit("10/minute", scope="content:create")
```

**Input Validation**:
- Pydantic models for request validation
- SQL injection prevention (parameterized queries)
- XSS protection (content sanitization)
- File upload restrictions (size, type)

**API Key Management**:
- API keys stored hashed in database
- Key rotation policy: 90 days
- Ability to revoke keys immediately
- Audit log of key usage

### 9.4 Compliance

**GDPR** (General Data Protection Regulation):
- User consent for data processing
- Data portability (export user data)
- Right to be forgotten (delete user data)
- Data processing agreements with third parties

**SOC 2** (System and Organization Controls):
- Security policies and procedures
- Access control and authentication
- Change management
- Incident response plan

**Privacy Policy**:
- Transparent data collection practices
- Third-party data sharing disclosure
- Cookie policy
- Contact information for privacy inquiries

---

## 10. Deployment Architecture

### 10.1 Infrastructure Overview

```
┌─────────────────────────────────────────────────────┐
│              Cloud Provider (AWS/GCP)                │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐   │
│  │   Load     │  │    CDN     │  │    WAF     │   │
│  │  Balancer  │  │ (CloudFront│  │(CloudFlare)│   │
│  └─────┬──────┘  └────────────┘  └────────────┘   │
│        │                                            │
│  ┌─────▼────────────────────────────────────┐     │
│  │     Kubernetes Cluster (EKS/GKE)         │     │
│  │                                           │     │
│  │  ┌──────────┐  ┌──────────┐  ┌────────┐ │     │
│  │  │   API    │  │  Worker  │  │  Web   │ │     │
│  │  │  Pods    │  │   Pods   │  │  Pods  │ │     │
│  │  │ (FastAPI)│  │ (Celery) │  │(Next.js│ │     │
│  │  └────┬─────┘  └────┬─────┘  └────┬───┘ │     │
│  └───────┼─────────────┼─────────────┼─────┘     │
│          │             │             │            │
│  ┌───────▼─────────────▼─────────────▼─────┐     │
│  │           Service Mesh (Istio)           │     │
│  └──────────────────────────────────────────┘     │
│          │             │             │            │
│  ┌───────▼──┐  ┌──────▼────┐  ┌─────▼─────┐     │
│  │PostgreSQL│  │   Redis   │  │    S3     │     │
│  │   (RDS)  │  │(ElastiCache│  │ (Storage) │     │
│  └──────────┘  └───────────┘  └───────────┘     │
│                                                    │
│  ┌────────────────────────────────────────┐      │
│  │   Observability Stack                  │      │
│  │  - Prometheus (metrics)                │      │
│  │  - Grafana (dashboards)                │      │
│  │  - ELK Stack (logs)                    │      │
│  │  - Jaeger (tracing)                    │      │
│  └────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────┘
```

### 10.2 Container Architecture

**Docker Images**:

1. **API Service**
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Worker Service**
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["celery", "-A", "core.celery", "worker", "--loglevel=info"]
```

3. **Web Frontend**
```dockerfile
FROM node:20-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

### 10.3 Kubernetes Configuration

**Deployment Example** (API Service):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: marketing-director-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: marketing-director-api
  template:
    metadata:
      labels:
        app: marketing-director-api
    spec:
      containers:
      - name: api
        image: ai-elevate/marketing-director-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: anthropic
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

**Service Definition**:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: marketing-director-api
spec:
  selector:
    app: marketing-director-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 10.4 Scaling Strategy

**Horizontal Pod Autoscaler**:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: marketing-director-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: marketing-director-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Database Scaling**:
- **Read Replicas**: 2 read replicas for analytics queries
- **Connection Pooling**: PgBouncer (max 100 connections)
- **Caching**: Redis for frequently accessed data (90% cache hit rate target)

**CDN Strategy**:
- Static assets served via CloudFront/CloudFlare
- Cache published content (TTL: 24 hours)
- Purge cache on content updates

### 10.5 Disaster Recovery

**Backup Strategy**:
- Database: Daily automated backups, 30-day retention
- Critical data: Real-time replication to secondary region
- Configuration: Version controlled in Git

**Recovery Objectives**:
- **RTO** (Recovery Time Objective): 4 hours
- **RPO** (Recovery Point Objective): 1 hour

**Failover Plan**:
1. Automated health checks detect outage
2. DNS updated to point to backup region
3. Read replicas promoted to primary
4. Application pods scaled up in backup region
5. Monitoring confirms service restoration

---

## 11. Testing Strategy

**⚠️ IMPORTANT**: All testing must follow the mandatory standards in [DEVELOPMENT_STANDARDS.md](./DEVELOPMENT_STANDARDS.md) and use the templates in [templates/](./templates/).

### 11.1 Testing Pyramid

```
       ┌─────────────┐
       │     E2E     │  10% - Full user workflows
       ├─────────────┤
       │ Integration │  20% - API, database, external services
       ├─────────────┤
       │    Unit     │  70% - Individual functions and classes
       └─────────────┘
```

**Testing Requirements**:
- ✅ All 5 test types required: Unit, Integration, E2E, Lint, Regression
- ✅ TDD methodology: Tests written BEFORE code
- ✅ 80%+ overall code coverage (90%+ for unit tests)
- ✅ Use provided templates from `templates/tests/`

### 11.2 Unit Testing

**Template**: Use `templates/tests/test_unit_template.py` as starting point

**Framework**: pytest
**Coverage Target**: 80%+
**Mock External Services**: Yes (Anthropic API, LinkedIn API, etc.)

**Example Tests**:

```python
# tests/agents/test_strategy_agent.py
import pytest
from unittest.mock import Mock, patch
from agents.strategy_agent import StrategyAgent

class TestStrategyAgent:
    @pytest.fixture
    def agent(self):
        return StrategyAgent(api_key="test_key")

    @patch('agents.strategy_agent.anthropic.Anthropic')
    def test_analyze_market_trends(self, mock_anthropic, agent):
        """Test market trends analysis returns expected structure"""
        # Setup mock
        mock_response = Mock()
        mock_response.content = [Mock(text="Market analysis here")]
        mock_anthropic.return_value.messages.create.return_value = mock_response

        # Execute
        result = agent.analyze_market_trends("enterprise AI")

        # Assert
        assert "analysis" in result
        assert "timestamp" in result
        assert result["agent"] == "strategy_agent"
        assert result["task"] == "market_trends"

    def test_suggest_content_topics_validates_input(self, agent):
        """Test that invalid content type raises error"""
        with pytest.raises(ValueError):
            agent.suggest_content_topics(content_type="invalid", count=5)
```

### 11.3 Integration Testing

**Test External Integrations**:

```python
# tests/integrations/test_linkedin.py
import pytest
from integrations.linkedin import LinkedInIntegration

@pytest.mark.integration
class TestLinkedInIntegration:
    @pytest.fixture
    def linkedin(self):
        return LinkedInIntegration(access_token=os.getenv("LINKEDIN_TEST_TOKEN"))

    def test_create_post(self, linkedin):
        """Test creating a LinkedIn post (uses test account)"""
        post = linkedin.create_post(
            text="Test post from AI Marketing Director",
            visibility="CONNECTIONS"
        )

        assert post["id"] is not None
        assert post["status"] == "published"

        # Cleanup
        linkedin.delete_post(post["id"])
```

### 11.4 End-to-End Testing

**Framework**: Playwright or Selenium
**Scenarios**:

1. **Content Creation Workflow**
   - User requests blog post via CLI
   - System generates content
   - User reviews and approves
   - Content is published
   - Analytics tracked

2. **Campaign Launch Workflow**
   - User creates campaign
   - System generates email sequence
   - User approves emails
   - Emails are scheduled
   - Performance tracked

**Example E2E Test**:

```python
# tests/e2e/test_content_workflow.py
import pytest
from playwright.sync_api import sync_playwright

@pytest.mark.e2e
def test_complete_content_workflow():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Login
        page.goto("https://app.ai-elevate.ai/login")
        page.fill("#email", "test@ai-elevate.ai")
        page.fill("#password", "test_password")
        page.click("button[type=submit]")

        # Create content
        page.goto("https://app.ai-elevate.ai/content/new")
        page.select_option("#content-type", "blog")
        page.fill("#topic", "Why AI Training Matters")
        page.click("#generate")

        # Wait for generation
        page.wait_for_selector(".content-preview", timeout=60000)

        # Approve
        page.click("#approve-button")

        # Verify published
        assert page.inner_text(".status-badge") == "Published"

        browser.close()
```

### 11.5 Performance Testing

**Tool**: Locust or k6
**Scenarios**:

1. **Concurrent Content Generation**
   - 50 users generating content simultaneously
   - Target: < 30s response time

2. **API Load Test**
   - 1000 requests/second
   - Target: < 200ms p95 latency

**Example Load Test**:

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between

class MarketingDirectorUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def generate_linkedin_post(self):
        self.client.post("/social/linkedin/posts", json={
            "topic": "AI productivity tips",
            "style": "professional"
        })

    @task(2)
    def get_analytics(self):
        self.client.get("/analytics/dashboard?timeframe=7days")

    @task(1)
    def market_trends(self):
        self.client.post("/strategy/market-trends", json={
            "industry": "enterprise AI"
        })
```

### 11.6 Security Testing

**Tools**: OWASP ZAP, Bandit (Python security linter)
**Tests**:
- SQL injection attempts
- XSS vulnerability scanning
- Authentication bypass attempts
- API rate limit validation
- Secrets exposure scanning

---

## 12. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-3) ✅ **COMPLETE**

**Status**: ✅ Complete

**Deliverables**:
- [x] Project structure and configuration
- [x] Strategy Agent (market research, competitor analysis)
- [x] Orchestrator Agent (task management, planning)
- [x] Brand Voice Management System
- [x] CLI interface
- [x] Basic documentation

**Effort**: 2-3 weeks
**Team**: 1 developer

---

### Phase 2: Infrastructure & Integrations (Weeks 4-7) ✅ **COMPLETE**

**Status**: ✅ Complete

**Goals**:
- Implement core infrastructure components (Message Bus, LLM Provider)
- Add initial social media platform integrations
- Build agent communication framework
- Establish TDD practices with comprehensive test coverage

**Deliverables**:
- [x] **Message Bus Infrastructure** (`infrastructure/message_bus/`)
  - [x] Redis-based message bus implementation
  - [x] Pub/Sub pattern for agent communication
  - [x] Message routing and queuing
  - [x] Unit tests with 100% coverage
  - [x] Integration tests with real Redis
- [x] **LLM Provider Infrastructure** (`infrastructure/llm/`)
  - [x] Multi-provider abstraction layer
  - [x] Anthropic (Claude) integration
  - [x] OpenAI integration
  - [x] Provider switching capability
  - [x] Token tracking and cost management
  - [x] Comprehensive test coverage
- [x] **Base Agent Framework** (`agents/base/`)
  - [x] BaseAgent abstract class
  - [x] Agent protocol and interfaces
  - [x] Task execution patterns
  - [x] Message handling capabilities
  - [x] Agent lifecycle management
  - [x] Full unit test coverage
- [x] **Bluesky Integration** (`infrastructure/integrations/bluesky/`)
  - [x] AT Protocol client implementation
  - [x] Post creation (300 char limit)
  - [x] Threaded posts support
  - [x] Profile analytics
  - [x] Content search capabilities
- [x] **Bluesky Manager Agent** (`agents/specialists/bluesky_manager/`)
  - [x] Create post task type
  - [x] Create thread task type
  - [x] Optimize post task type
  - [x] Get analytics task type
  - [x] Research hashtags task type
  - [x] LLM-powered content optimization
- [x] **LinkedIn Navigator Integration** (`infrastructure/integrations/linkedin/`)
  - [x] Standard LinkedIn API client
  - [x] Navigator premium features support
  - [x] Advanced lead search
  - [x] InMail messaging
  - [x] Sales insights
  - [x] Feature detection (has_navigator property)
- [x] **Documentation**
  - [x] SOCIAL_MEDIA_CHANNELS.md - Platform guide
  - [x] BLUESKY_LINKEDIN_INTEGRATION.md - Implementation details
  - [x] Updated agent protocol with BLUESKY_MANAGER role

**Test Coverage**:
- ✅ **72 passing tests** across all components
- ✅ **81% overall code coverage** (exceeds 80% target)
- ✅ Unit tests: 90%+ coverage on critical paths
- ✅ Integration tests: Redis, LLM providers, agents
- ✅ All tests follow TDD methodology (RED-GREEN-REFACTOR)

**Effort**: 4 weeks
**Team**: 1 developer

**Success Metrics**:
- ✅ Message bus successfully routes messages between agents
- ✅ LLM providers integrate seamlessly with fallback support
- ✅ Base agent framework supports all specialist agents
- ✅ 81% test coverage achieved (exceeds 80% target)
- ✅ Bluesky and LinkedIn Navigator integrations functional
- ✅ All code follows mandatory development standards

---

### Phase 3: Social Media & Campaigns (Weeks 8-11)

**Status**: 🚧 Not Started

**Goals**:
- Implement Social Media Agent
- Implement Campaign Agent
- Integrate with LinkedIn and Twitter APIs
- Build email campaign functionality

**Deliverables**:
- [ ] Social Media Agent
  - [ ] LinkedIn post generation
  - [ ] Twitter/X thread creation
  - [ ] Content calendar generation
  - [ ] Optimal timing recommendations
- [ ] Campaign Agent
  - [ ] Email sequence builder
  - [ ] Audience segmentation
  - [ ] A/B testing framework
  - [ ] Personalization engine
- [ ] Platform Integrations
  - [ ] LinkedIn API integration
  - [ ] Twitter API integration
  - [ ] SendGrid email integration
- [ ] Scheduling system (Celery tasks)
- [ ] Integration tests

**Effort**: 3-4 weeks
**Team**: 2 developers

**Success Metrics**:
- Successfully post to LinkedIn and Twitter
- Create 3 complete email sequences
- Schedule 20 social posts across platforms
- Achieve 3%+ engagement rate on social posts

---

### Phase 4: Analytics & Optimization (Weeks 12-14)

**Status**: 🚧 Not Started

**Goals**:
- Implement Analytics Agent
- Integrate with Google Analytics and CRM
- Build performance dashboards
- Enable data-driven optimization

**Deliverables**:
- [ ] Analytics Agent
  - [ ] Performance tracking
  - [ ] Trend identification
  - [ ] Optimization recommendations
  - [ ] Forecasting models
- [ ] Integrations
  - [ ] Google Analytics 4 integration
  - [ ] HubSpot CRM integration
  - [ ] Custom event tracking
- [ ] Reporting system
  - [ ] Daily/weekly/monthly reports
  - [ ] Custom report builder
  - [ ] Export functionality (PDF, CSV)
- [ ] Analytics database schema
- [ ] Data pipeline (ETL)

**Effort**: 2-3 weeks
**Team**: 1-2 developers (1 backend, 1 data engineer)

**Success Metrics**:
- Track 95%+ of content performance
- Generate weekly performance reports
- Provide 5+ actionable optimization recommendations per week
- Achieve 70%+ accuracy on performance forecasts

---

### Phase 5: Web Dashboard (Weeks 15-20)

**Status**: 🚧 Not Started

**Goals**:
- Build production-ready web dashboard
- Implement user authentication and authorization
- Create intuitive UX for all agent functions
- Enable team collaboration

**Deliverables**:
- [ ] Frontend application (React + Next.js)
  - [ ] Dashboard homepage
  - [ ] Content library and editor
  - [ ] Campaign management
  - [ ] Analytics dashboards
  - [ ] Social media scheduler
  - [ ] Settings and configuration
- [ ] User authentication (Auth0 or custom JWT)
- [ ] Real-time updates (WebSockets)
- [ ] Responsive design (mobile-friendly)
- [ ] Accessibility (WCAG 2.1 AA)
- [ ] E2E tests (Playwright)

**Effort**: 5-6 weeks
**Team**: 2 frontend developers, 1 designer

**Success Metrics**:
- < 3s page load time
- 95%+ Lighthouse performance score
- Support 50+ concurrent users
- < 5 minutes to complete key workflows

---

### Phase 6: Production Hardening (Weeks 21-24)

**Status**: 🚧 Not Started

**Goals**:
- Prepare system for production deployment
- Implement comprehensive monitoring
- Ensure security and compliance
- Optimize performance

**Deliverables**:
- [ ] Production deployment
  - [ ] Kubernetes cluster setup
  - [ ] CI/CD pipeline (GitHub Actions)
  - [ ] Infrastructure as Code (Terraform)
  - [ ] Blue-green deployment
- [ ] Monitoring & observability
  - [ ] Prometheus metrics
  - [ ] Grafana dashboards
  - [ ] ELK stack for logging
  - [ ] Jaeger for tracing
  - [ ] Alerting (PagerDuty)
- [ ] Security hardening
  - [ ] Security audit (penetration testing)
  - [ ] Secrets rotation
  - [ ] API rate limiting
  - [ ] GDPR compliance review
- [ ] Performance optimization
  - [ ] Database query optimization
  - [ ] Caching strategy
  - [ ] CDN configuration
  - [ ] Load testing
- [ ] Documentation
  - [ ] API documentation (OpenAPI/Swagger)
  - [ ] User guides
  - [ ] Runbooks for operations

**Effort**: 3-4 weeks
**Team**: 2 developers, 1 DevOps engineer, 1 security specialist

**Success Metrics**:
- 99.9% uptime SLA
- < 500ms API response time (p95)
- < 1% error rate
- Pass security audit with no critical issues

---

### Timeline Summary

| Phase | Duration | Status | Start Week | End Week |
|-------|----------|--------|------------|----------|
| Phase 1: Foundation | 3 weeks | ✅ Complete | Week 1 | Week 3 |
| Phase 2: Infrastructure & Integrations | 4 weeks | ✅ Complete | Week 4 | Week 7 |
| Phase 3: Social & Campaigns | 4 weeks | 🚧 Not Started | Week 8 | Week 11 |
| Phase 4: Analytics | 3 weeks | 🚧 Not Started | Week 12 | Week 14 |
| Phase 5: Web Dashboard | 6 weeks | 🚧 Not Started | Week 15 | Week 20 |
| Phase 6: Production | 4 weeks | 🚧 Not Started | Week 21 | Week 24 |
| **Total** | **24 weeks** | **Phase 1-2 Complete** | | **~6 months** |

**Team Requirements**:
- **Phase 1**: 1 backend developer
- **Phase 2-4**: 2 backend developers
- **Phase 5**: 2 frontend developers, 1 designer
- **Phase 6**: 2 developers, 1 DevOps, 1 security specialist

---

## 13. Appendices

### 13.1 Glossary

| Term | Definition |
|------|------------|
| **Agent** | An AI-powered module that performs specific marketing tasks |
| **Brand Voice** | The consistent personality and tone used across all content |
| **Human-in-the-Loop** | Workflow requiring human review before final action |
| **LLM** | Large Language Model (e.g., Claude, GPT-4) |
| **Orchestrator** | Central agent that coordinates other agents |
| **Task** | A discrete unit of work assigned to an agent |
| **MQL** | Marketing Qualified Lead |
| **SQL** | Sales Qualified Lead |

### 13.2 References

- Anthropic Claude API Documentation: https://docs.anthropic.com/
- LangGraph Documentation: https://langchain-ai.github.io/langgraph/
- LinkedIn Marketing API: https://docs.microsoft.com/en-us/linkedin/marketing/
- Twitter API v2: https://developer.twitter.com/en/docs/twitter-api
- HubSpot API: https://developers.hubspot.com/
- Google Analytics Data API: https://developers.google.com/analytics/devguides/reporting/data/v1

### 13.3 Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 2.2 | 2025-11-03 | AI Marketing Director Team | Updated Phase 2 to reflect Infrastructure & Integrations completion (Message Bus, LLM Provider, Bluesky, LinkedIn Navigator); Added test coverage statistics (72 tests, 81% coverage); Updated technology stack with new dependencies |
| 2.1 | 2025-11-03 | AI Marketing Director Team | Added functional design patterns requirement (pure functions, immutability, composition) |
| 2.0 | 2025-11-03 | AI Marketing Director Team | Major architecture redesign - multiagent department model with 14 agents; Added mandatory development standards (TDD, SOLID, 5 test types); Added templates and examples |
| 1.0 | 2025-11-03 | AI Marketing Director Team | Initial specification |

---

**Document Status**: Draft
**Next Review**: 2025-11-10
**Owner**: AI Elevate Engineering Team

---

*This document is confidential and proprietary to AI Elevate. Unauthorized distribution is prohibited.*
