# AI Marketing Director - Directory Structure

**Version**: 1.0
**Date**: 2025-11-03
**Status**: Complete Modular Hierarchy

---

## Overview

This document describes the complete directory structure for the AI Marketing Director project, organized for modularity, scalability, and maintainability.

## Complete Directory Tree

```
ai-marketing-director/
├── agents/                          # All 14 AI agents (3-tier hierarchy)
│   ├── base/                        # Base classes for agents
│   │   ├── __init__.py
│   │   ├── base_agent.py            # Abstract base agent class
│   │   ├── agent_protocol.py        # Protocol definitions
│   │   ├── agent_config.py          # Configuration models
│   │   ├── agent_state.py           # State management
│   │   └── agent_memory.py          # Memory management
│   ├── executive/                   # Executive layer (3 agents)
│   │   ├── __init__.py
│   │   ├── cmo/                     # CMO Agent
│   │   ├── vp_marketing/            # VP Marketing Agent
│   │   └── director_comms/          # Director of Communications
│   ├── management/                  # Management layer (3 agents)
│   │   ├── __init__.py
│   │   ├── content_manager/         # Content Manager Agent
│   │   ├── social_media_manager/    # Social Media Manager
│   │   └── campaign_manager/        # Campaign Manager
│   ├── specialists/                 # Specialist layer (8 agents)
│   │   ├── __init__.py
│   │   ├── copywriter/              # Copywriter Agent
│   │   ├── seo_specialist/          # SEO Specialist
│   │   ├── designer/                # Designer Agent
│   │   ├── analytics_specialist/    # Analytics Specialist
│   │   ├── email_specialist/        # Email Specialist
│   │   ├── linkedin_manager/        # LinkedIn Manager
│   │   ├── twitter_manager/         # Twitter Manager
│   │   └── market_research/         # Market Research Agent
│   └── README.md                    # Agent documentation
│
├── infrastructure/                  # Core infrastructure services
│   ├── __init__.py
│   ├── database/                    # PostgreSQL operations
│   │   ├── __init__.py
│   │   ├── connection.py            # Connection pool
│   │   ├── session.py               # Async session management
│   │   ├── repositories/            # Repository pattern
│   │   │   ├── __init__.py
│   │   │   ├── content_repository.py
│   │   │   ├── campaign_repository.py
│   │   │   ├── task_repository.py
│   │   │   └── user_repository.py
│   │   ├── models.py                # SQLAlchemy ORM models
│   │   └── migrations.py            # Migration helpers
│   ├── message_bus/                 # Redis message bus
│   │   ├── __init__.py
│   │   ├── message_bus.py           # Main implementation
│   │   ├── protocols.py             # Message protocols
│   │   ├── serialization.py         # Serialization
│   │   └── routing.py               # Message routing
│   ├── cache/                       # Redis caching
│   │   ├── __init__.py
│   │   ├── cache.py                 # Cache client
│   │   ├── strategies.py            # Caching strategies
│   │   ├── decorators.py            # @cached decorator
│   │   └── invalidation.py          # Invalidation patterns
│   ├── llm/                         # LLM providers
│   │   ├── __init__.py
│   │   ├── base_provider.py         # Abstract provider
│   │   ├── claude_provider.py       # Claude implementation
│   │   ├── openai_provider.py       # OpenAI implementation
│   │   ├── prompt_template.py       # Prompt templating
│   │   ├── token_counter.py         # Token tracking
│   │   └── rate_limiter.py          # Rate limiting
│   ├── integrations/                # Third-party integrations
│   │   ├── __init__.py
│   │   ├── base_integration.py      # Base integration class
│   │   ├── linkedin/                # LinkedIn API
│   │   │   ├── __init__.py
│   │   │   ├── client.py
│   │   │   ├── auth.py
│   │   │   └── schemas.py
│   │   ├── twitter/                 # Twitter/X API
│   │   │   ├── __init__.py
│   │   │   ├── client.py
│   │   │   ├── auth.py
│   │   │   └── schemas.py
│   │   ├── hubspot/                 # HubSpot CRM
│   │   │   ├── __init__.py
│   │   │   ├── client.py
│   │   │   └── schemas.py
│   │   ├── sendgrid/                # SendGrid email
│   │   │   ├── __init__.py
│   │   │   ├── client.py
│   │   │   └── templates.py
│   │   └── google_analytics/        # Google Analytics
│   │       ├── __init__.py
│   │       ├── client.py
│   │       └── schemas.py
│   ├── monitoring/                  # Observability
│   │   ├── __init__.py
│   │   ├── metrics.py               # Prometheus metrics
│   │   ├── logging.py               # Structured logging
│   │   ├── tracing.py               # Distributed tracing
│   │   └── alerts.py                # Alerting rules
│   └── README.md                    # Infrastructure docs
│
├── api/                             # FastAPI application
│   ├── __init__.py
│   ├── main.py                      # FastAPI app entry point
│   ├── routes/                      # API routes
│   │   ├── __init__.py
│   │   ├── health.py                # Health check endpoints
│   │   ├── content.py               # Content endpoints
│   │   ├── campaigns.py             # Campaign endpoints
│   │   ├── agents.py                # Agent management
│   │   ├── analytics.py             # Analytics endpoints
│   │   └── webhooks.py              # Webhook endpoints
│   ├── middleware/                  # API middleware
│   │   ├── __init__.py
│   │   ├── authentication.py        # JWT auth
│   │   ├── rate_limiting.py         # Rate limiting
│   │   ├── cors.py                  # CORS configuration
│   │   └── logging.py               # Request logging
│   ├── schemas/                     # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── content.py               # Content schemas
│   │   ├── campaign.py              # Campaign schemas
│   │   ├── agent.py                 # Agent schemas
│   │   └── common.py                # Shared schemas
│   └── dependencies/                # FastAPI dependencies
│       ├── __init__.py
│       ├── auth.py                  # Auth dependencies
│       ├── database.py              # DB session dependencies
│       └── services.py              # Service dependencies
│
├── core/                            # Core application modules
│   ├── __init__.py
│   ├── config/                      # Configuration
│   │   ├── __init__.py
│   │   ├── settings.py              # Pydantic settings
│   │   ├── database.py              # Database config
│   │   └── security.py              # Security config
│   ├── exceptions.py                # Custom exceptions ✅
│   ├── logging.py                   # Logging configuration
│   └── utils/                       # Utility functions
│       ├── __init__.py
│       ├── datetime_utils.py        # Date/time utilities
│       ├── string_utils.py          # String utilities
│       └── validation.py            # Validation helpers
│
├── services/                        # Business logic services
│   ├── __init__.py
│   ├── content/                     # Content services
│   │   ├── __init__.py
│   │   ├── content_service.py       # Content CRUD
│   │   ├── publishing_service.py    # Publishing logic
│   │   └── validation_service.py    # Content validation
│   ├── campaign/                    # Campaign services
│   │   ├── __init__.py
│   │   ├── campaign_service.py      # Campaign management
│   │   ├── optimization_service.py  # Campaign optimization
│   │   └── scheduling_service.py    # Campaign scheduling
│   ├── analytics/                   # Analytics services
│   │   ├── __init__.py
│   │   ├── analytics_service.py     # Data aggregation
│   │   ├── reporting_service.py     # Report generation
│   │   └── forecasting_service.py   # Forecasting
│   └── workflow/                    # Workflow services
│       ├── __init__.py
│       ├── workflow_engine.py       # Workflow orchestration
│       ├── task_queue.py            # Task queuing
│       └── state_machine.py         # State management
│
├── models/                          # Data models
│   ├── __init__.py
│   ├── domain/                      # Domain models (Pydantic)
│   │   ├── __init__.py
│   │   ├── content.py               # Content domain models
│   │   ├── campaign.py              # Campaign domain models
│   │   ├── agent.py                 # Agent domain models
│   │   └── task.py                  # Task domain models
│   └── database/                    # Database models (SQLAlchemy)
│       ├── __init__.py
│       ├── content.py               # Content ORM models
│       ├── campaign.py              # Campaign ORM models
│       ├── user.py                  # User ORM models
│       └── task.py                  # Task ORM models
│
├── tests/                           # All test types
│   ├── __init__.py
│   ├── conftest.py                  # Pytest configuration
│   ├── unit/                        # Unit tests (90%+ coverage)
│   │   ├── __init__.py
│   │   ├── agents/                  # Agent unit tests
│   │   │   ├── __init__.py
│   │   │   ├── test_base_agent.py
│   │   │   ├── test_cmo_agent.py
│   │   │   └── ...
│   │   ├── infrastructure/          # Infrastructure unit tests
│   │   │   ├── __init__.py
│   │   │   ├── test_database.py
│   │   │   ├── test_message_bus.py
│   │   │   └── ...
│   │   └── services/                # Service unit tests
│   │       ├── __init__.py
│   │       ├── test_content_service.py
│   │       └── ...
│   ├── integration/                 # Integration tests
│   │   ├── __init__.py
│   │   ├── agents/                  # Agent integration tests
│   │   │   ├── __init__.py
│   │   │   └── test_agent_communication.py
│   │   ├── infrastructure/          # Infrastructure integration tests
│   │   │   ├── __init__.py
│   │   │   ├── test_database_operations.py
│   │   │   └── test_redis_integration.py
│   │   └── api/                     # API integration tests
│   │       ├── __init__.py
│   │       └── test_api_routes.py
│   ├── e2e/                         # End-to-end tests
│   │   ├── __init__.py
│   │   └── scenarios/               # Complete workflows
│   │       ├── __init__.py
│   │       ├── test_content_workflow.py
│   │       └── test_campaign_workflow.py
│   ├── fixtures/                    # Test fixtures
│   │   ├── __init__.py
│   │   ├── agents.py                # Agent fixtures
│   │   ├── content.py               # Content fixtures
│   │   └── database.py              # Database fixtures
│   └── mocks/                       # Mock implementations
│       ├── __init__.py
│       ├── mock_llm.py              # Mock LLM provider
│       └── mock_integrations.py     # Mock integrations
│
├── scripts/                         # Utility scripts
│   ├── deployment/                  # Deployment scripts
│   │   ├── deploy.sh                # Main deployment script
│   │   └── rollback.sh              # Rollback script
│   ├── migrations/                  # Data migration scripts
│   │   └── migrate_data.py          # Data migration utilities
│   ├── data/                        # Data management scripts
│   │   ├── seed_database.py         # Database seeding
│   │   └── export_data.py           # Data export
│   └── monitoring/                  # Monitoring scripts
│       └── health_check.py          # Health check script
│
├── docs/                            # Documentation
│   ├── architecture/                # Architecture docs
│   │   ├── overview.md              # Architecture overview
│   │   ├── agents.md                # Agent architecture
│   │   ├── infrastructure.md        # Infrastructure design
│   │   └── diagrams/                # Architecture diagrams
│   ├── api/                         # API documentation
│   │   ├── openapi.yaml             # OpenAPI specification
│   │   └── endpoints.md             # Endpoint documentation
│   ├── guides/                      # User guides
│   │   ├── getting_started.md       # Getting started guide
│   │   ├── deployment.md            # Deployment guide
│   │   └── integrations/            # Integration guides
│   │       ├── linkedin.md
│   │       ├── twitter.md
│   │       └── hubspot.md
│   └── adr/                         # Architecture Decision Records
│       ├── 001-multiagent-architecture.md
│       ├── 002-message-bus-choice.md
│       └── 003-exception-handling.md
│
├── config/                          # Configuration files
│   ├── environments/                # Environment-specific configs
│   │   ├── development.env          # Development config
│   │   ├── staging.env              # Staging config
│   │   └── production.env           # Production config
│   └── schemas/                     # Configuration schemas
│       └── settings_schema.json     # Settings JSON schema
│
├── alembic/                         # Database migrations (Alembic)
│   ├── versions/                    # Migration versions
│   ├── env.py                       # Alembic environment
│   └── script.py.mako               # Migration template
│
├── data/                            # Data files
│   ├── seeds/                       # Seed data
│   │   ├── users.json               # User seed data
│   │   └── campaigns.json           # Campaign seed data
│   ├── exports/                     # Data exports
│   └── temp/                        # Temporary files
│
├── logs/                            # Log files (gitignored)
│   ├── application.log              # Application logs
│   ├── agents.log                   # Agent logs
│   └── errors.log                   # Error logs
│
├── .github/                         # GitHub configuration
│   └── workflows/                   # GitHub Actions
│       ├── test.yml                 # Test workflow
│       ├── lint.yml                 # Linting workflow
│       └── deploy.yml               # Deployment workflow
│
├── frontend/                        # React frontend (existing)
│   └── (existing frontend structure)
│
├── templates/                       # Development templates (existing)
│   └── (existing template structure)
│
├── .env.example                     # Environment variables template
├── .gitignore                       # Git ignore rules
├── alembic.ini                      # Alembic configuration
├── pytest.ini                       # Pytest configuration
├── pyproject.toml                   # Python project config (Black, isort)
├── requirements.txt                 # Python dependencies
├── requirements-dev.txt             # Development dependencies
├── README.md                        # Project README
├── DEVELOPMENT_STANDARDS.md         # Coding standards (v2.2)
├── SPECIFICATION.md                 # Software specification
├── MULTIAGENT_ARCHITECTURE.md       # Architecture design
├── DIRECTORY_STRUCTURE.md           # This file
└── docker-compose.yml               # Docker services config
```

---

## Directory Purposes

### `/agents/` - AI Agent Implementation
- **Purpose**: All 14 AI agents organized by tier (Executive, Management, Specialist)
- **Standards**: TDD, functional patterns, SOLID, exception wrapping
- **Testing**: Unit tests (90%+), integration tests, E2E scenarios

### `/infrastructure/` - Core Services
- **Purpose**: Database, message bus, cache, LLM providers, integrations
- **Standards**: Protocol-based interfaces, dependency injection, retry logic
- **Testing**: Mock external services in unit tests, real services in integration tests

### `/api/` - REST API Layer
- **Purpose**: FastAPI application with routes, middleware, schemas
- **Standards**: OpenAPI documentation, authentication, rate limiting
- **Testing**: API integration tests, endpoint validation

### `/core/` - Core Application
- **Purpose**: Configuration, exceptions, logging, utilities
- **Standards**: Centralized config, custom exception hierarchy
- **Key**: `exceptions.py` contains all custom exceptions

### `/services/` - Business Logic
- **Purpose**: Domain services for content, campaigns, analytics, workflows
- **Standards**: Pure functions where possible, repository pattern for data access
- **Testing**: Service unit tests with mocked repositories

### `/models/` - Data Models
- **Purpose**: Domain models (Pydantic) and database models (SQLAlchemy)
- **Standards**: Immutable domain models (`frozen=True`), type hints everywhere
- **Structure**: Separation between domain (business logic) and database (persistence)

### `/tests/` - All Test Types
- **Purpose**: Unit (90%+), integration, E2E, fixtures, mocks
- **Standards**: TDD, AAA pattern, independent tests
- **Structure**: Mirror source structure in test directories

### `/scripts/` - Utility Scripts
- **Purpose**: Deployment, migrations, data management, monitoring
- **Standards**: Idempotent operations, error handling
- **Usage**: Called manually or via CI/CD

### `/docs/` - Documentation
- **Purpose**: Architecture, API docs, guides, ADRs
- **Standards**: Markdown format, keep updated with code
- **Structure**: Organized by topic (architecture, API, guides, decisions)

### `/config/` - Configuration
- **Purpose**: Environment-specific configuration files
- **Standards**: Pydantic settings, environment variables
- **Security**: Never commit secrets (use .env.example template)

### `/alembic/` - Database Migrations
- **Purpose**: Version-controlled database schema changes
- **Standards**: Reversible migrations, tested before merge
- **Usage**: `alembic upgrade head` to apply migrations

---

## Key Files

### Core Configuration
- `pyproject.toml` - Python project config (Black, isort, coverage)
- `pytest.ini` - Pytest configuration (markers, coverage, parallel)
- `alembic.ini` - Database migration configuration
- `.env.example` - Environment variables template
- `requirements.txt` - Production dependencies
- `requirements-dev.txt` - Development dependencies

### Documentation
- `README.md` - Project overview and quick start
- `DEVELOPMENT_STANDARDS.md` - Mandatory coding standards (v2.2)
- `SPECIFICATION.md` - Complete software specification
- `MULTIAGENT_ARCHITECTURE.md` - Multiagent system design
- `DIRECTORY_STRUCTURE.md` - This file

### Entry Points
- `api/main.py` - FastAPI application entry point
- `alembic/env.py` - Database migration entry point
- `scripts/deployment/deploy.sh` - Deployment entry point

---

## Module Dependencies

```
┌─────────────────────────────────────────┐
│              API Layer                   │
│         (FastAPI routes)                 │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│          Services Layer                  │
│    (Business logic, workflows)           │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│          Agents Layer                    │
│  (14 agents in 3-tier hierarchy)         │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│      Infrastructure Layer                │
│ (Database, Cache, LLM, Integrations)     │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│           Core Layer                     │
│    (Config, Exceptions, Utils)           │
└──────────────────────────────────────────┘
```

**Dependency Rules**:
- Upper layers depend on lower layers
- Never the reverse (no circular dependencies)
- Use dependency injection for flexibility
- Use protocols for interface definitions

---

## Development Workflow

### 1. Set Up Environment
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys

# Set up database
alembic upgrade head

# Seed database
python scripts/data/seed_database.py
```

### 2. Create New Feature (TDD)
```bash
# 1. Write test first (RED)
# tests/unit/agents/test_new_agent.py

# 2. Run test (should fail)
pytest tests/unit/agents/test_new_agent.py -v

# 3. Write minimal code (GREEN)
# agents/specialists/new_agent/agent.py

# 4. Run test again (should pass)
pytest tests/unit/agents/test_new_agent.py -v

# 5. Refactor
# Improve code while keeping tests green

# 6. Run all tests
pytest
```

### 3. Pre-Commit Checks
```bash
# Format code
black . && isort .

# Lint
flake8 && pylint agents/ infrastructure/ services/

# Type check
mypy .

# Run tests
pytest --cov --cov-fail-under=80

# All must pass before commit
```

### 4. Create Database Migration
```bash
# Auto-generate migration
alembic revision --autogenerate -m "Add new table"

# Review migration in alembic/versions/

# Test migration
alembic upgrade head

# Test rollback
alembic downgrade -1
```

---

## Resources

- **Standards**: `DEVELOPMENT_STANDARDS.md`
- **Architecture**: `MULTIAGENT_ARCHITECTURE.md`
- **Specification**: `SPECIFICATION.md`
- **Templates**: `templates/README.md`
- **API Docs**: `docs/api/openapi.yaml`

---

**Version**: 1.0
**Last Updated**: 2025-11-03
**Status**: Complete and Ready for Implementation
