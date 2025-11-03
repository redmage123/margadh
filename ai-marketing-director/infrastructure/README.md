# Infrastructure Directory

Core infrastructure services and integrations for the AI Marketing Director system.

## Structure

```
infrastructure/
├── database/              # PostgreSQL database layer
├── message_bus/           # Redis message bus for agent communication
├── cache/                 # Redis caching layer
├── llm/                   # LLM providers (Claude, OpenAI)
├── integrations/          # Third-party platform integrations
├── monitoring/            # Observability (metrics, logging, tracing)
└── __init__.py
```

## Components

### 1. Database (`database/`)

**Purpose**: PostgreSQL database operations with async support.

**Files**:
```
database/
├── __init__.py
├── connection.py          # Database connection pool
├── session.py             # Async session management
├── repositories/          # Repository pattern implementations
│   ├── content_repository.py
│   ├── campaign_repository.py
│   ├── task_repository.py
│   └── user_repository.py
├── models.py              # SQLAlchemy ORM models
└── migrations.py          # Migration helpers
```

**Example**:
```python
from infrastructure.database import Database

db = Database(connection_string="postgresql://localhost/marketing")

# Use repository pattern
from infrastructure.database.repositories import ContentRepository

content_repo = ContentRepository(db)
content = await content_repo.get_by_id(content_id)
await content_repo.save(content)
```

**Standards**:
- ✅ Use repository pattern (not direct ORM calls)
- ✅ Async/await for all operations
- ✅ Type hints on all methods
- ✅ Pure functions for queries

---

### 2. Message Bus (`message_bus/`)

**Purpose**: Redis-based message bus for agent-to-agent communication.

**Files**:
```
message_bus/
├── __init__.py
├── message_bus.py         # Main message bus implementation
├── protocols.py           # Message protocols and schemas
├── serialization.py       # Message serialization/deserialization
└── routing.py             # Message routing logic
```

**Message Format**:
```python
{
    "id": "msg_123",
    "from": "content_manager",
    "to": "copywriter",
    "type": "task_assignment",
    "priority": "normal",
    "timestamp": "2025-11-03T10:30:00Z",
    "payload": {
        "topic": "AI Marketing ROI",
        "word_count": 1500
    }
}
```

**Example**:
```python
from infrastructure.message_bus import MessageBus

bus = MessageBus(redis_url="redis://localhost:6379")

# Publish
await bus.publish(
    queue="copywriter_tasks",
    message={"type": "create_blog", "payload": {...}}
)

# Subscribe
message = await bus.subscribe(
    queue="content_manager_inbox",
    timeout=30
)
```

---

### 3. Cache (`cache/`)

**Purpose**: Redis caching layer for performance optimization.

**Files**:
```
cache/
├── __init__.py
├── cache.py               # Cache client
├── strategies.py          # Caching strategies (TTL, LRU)
├── decorators.py          # @cached decorator
└── invalidation.py        # Cache invalidation patterns
```

**Example**:
```python
from infrastructure.cache import Cache, cached

cache = Cache(redis_url="redis://localhost:6379")

# Manual caching
await cache.set("key", value, ttl=3600)
value = await cache.get("key")

# Decorator
@cached(ttl=3600, key_prefix="content")
async def get_content(content_id: str) -> Content:
    return await db.get_content(content_id)
```

---

### 4. LLM (`llm/`)

**Purpose**: LLM provider abstractions (Claude, OpenAI, etc.)

**Files**:
```
llm/
├── __init__.py
├── base_provider.py       # Abstract LLM provider
├── claude_provider.py     # Anthropic Claude implementation
├── openai_provider.py     # OpenAI implementation
├── prompt_template.py     # Prompt templating
├── token_counter.py       # Token usage tracking
└── rate_limiter.py        # Rate limiting for API calls
```

**Example**:
```python
from infrastructure.llm import ClaudeLLM

llm = ClaudeLLM(
    api_key="sk-ant-...",
    model="claude-sonnet-3-5",
    max_tokens=4096
)

response = await llm.generate(
    prompt="Write a blog post about AI ROI",
    temperature=0.7
)
```

**Standards**:
- ✅ Use Protocol pattern for provider interface
- ✅ Implement retry logic with exponential backoff
- ✅ Track token usage for cost monitoring
- ✅ Handle rate limits gracefully

---

### 5. Integrations (`integrations/`)

**Purpose**: Third-party platform integrations.

**Structure**:
```
integrations/
├── __init__.py
├── base_integration.py    # Abstract integration base
├── linkedin/              # LinkedIn integration
├── twitter/               # Twitter/X integration
├── hubspot/               # HubSpot CRM integration
├── sendgrid/              # SendGrid email integration
└── google_analytics/      # Google Analytics integration
```

#### LinkedIn Integration
**Location**: `integrations/linkedin/`

```python
from infrastructure.integrations.linkedin import LinkedInClient

linkedin = LinkedInClient(access_token="...")

# Create post
post_id = await linkedin.create_post(
    text="Great article on AI marketing!",
    visibility="PUBLIC"
)

# Get analytics
analytics = await linkedin.get_post_analytics(post_id)
```

#### Twitter Integration
**Location**: `integrations/twitter/`

```python
from infrastructure.integrations.twitter import TwitterClient

twitter = TwitterClient(bearer_token="...")

# Create tweet
tweet_id = await twitter.create_tweet(
    text="Check out our latest blog post!"
)

# Create thread
thread_ids = await twitter.create_thread([
    "Tweet 1...",
    "Tweet 2...",
    "Tweet 3..."
])
```

#### HubSpot Integration
**Location**: `integrations/hubspot/`

```python
from infrastructure.integrations.hubspot import HubSpotClient

hubspot = HubSpotClient(api_key="...")

# Track engagement
await hubspot.track_content_engagement(
    contact_email="user@example.com",
    content_id="blog_123",
    engagement_type="view"
)
```

---

### 6. Monitoring (`monitoring/`)

**Purpose**: Observability - metrics, logging, tracing.

**Files**:
```
monitoring/
├── __init__.py
├── metrics.py             # Prometheus metrics
├── logging.py             # Structured logging
├── tracing.py             # Distributed tracing (Jaeger)
└── alerts.py              # Alerting rules
```

**Example**:
```python
from infrastructure.monitoring import metrics, logger

# Metrics
metrics.counter("content_created", labels={"type": "blog"})
metrics.histogram("content_generation_time", 2.5)

# Logging
logger.info("Content created", extra={
    "content_id": "blog_123",
    "agent": "copywriter"
})

# Tracing
with tracer.start_span("generate_content") as span:
    span.set_attribute("topic", topic)
    content = await generate_content(topic)
```

---

## Development Standards

All infrastructure code MUST:
- ✅ Use dependency injection
- ✅ Define Protocol interfaces
- ✅ Implement retry logic with exponential backoff
- ✅ Handle errors gracefully (no crashes)
- ✅ Log all operations (structured logging)
- ✅ Track metrics (Prometheus)
- ✅ Use async/await for I/O operations
- ✅ Follow functional patterns (pure functions where possible)

## Testing Requirements

Each infrastructure component requires:

1. **Unit Tests** (`tests/unit/infrastructure/<component>/`)
   - Mock external services (Redis, PostgreSQL, APIs)
   - Test error handling
   - Test retry logic

2. **Integration Tests** (`tests/integration/infrastructure/<component>/`)
   - Test with real services (test Redis, test PostgreSQL)
   - Test failure scenarios
   - Test performance under load

## Configuration

Configuration is managed via environment variables:

```python
# config/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 10

    # Redis
    REDIS_URL: str
    REDIS_MAX_CONNECTIONS: int = 50

    # LLM
    ANTHROPIC_API_KEY: str
    ANTHROPIC_MODEL: str = "claude-sonnet-3-5"

    # Integrations
    LINKEDIN_ACCESS_TOKEN: str | None = None
    TWITTER_BEARER_TOKEN: str | None = None

    class Config:
        env_file = ".env"
```

## Error Handling

All infrastructure components use custom exceptions:

```python
from core.exceptions import (
    DatabaseError,
    MessageBusError,
    LLMProviderError,
    IntegrationError,
    CacheError
)

# Usage
try:
    content = await db.get_content(content_id)
except DatabaseError as e:
    logger.error("Database error", exc_info=e)
    raise
```

## Resources

- **Database Schema**: `alembic/versions/`
- **API Documentation**: `docs/api/`
- **Integration Guides**: `docs/guides/integrations/`
- **Development Standards**: `../DEVELOPMENT_STANDARDS.md`
