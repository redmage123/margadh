# ADR-005: Exception Wrapping Standard (Golden Rule #7)

**Date**: 2025-11-03
**Status**: Accepted and Enforced
**Decision Makers**: AI Elevate Engineering Team
**Related Documents**: [DEVELOPMENT_STANDARDS.md](../../DEVELOPMENT_STANDARDS.md), [core/exceptions.py](../../core/exceptions.py)

---

## Context

Python applications integrate with multiple external systems (Redis, PostgreSQL, LLM APIs, social media APIs, etc.). Each system has its own exception types and error formats. We need to decide how to handle exceptions in a consistent, maintainable way that:

1. **Preserves Error Context**: Don't lose original error information
2. **Provides Consistent Interface**: Application code sees consistent exception types
3. **Enables Debugging**: Errors contain enough information to diagnose issues
4. **Supports Error Handling**: Different error types can be handled differently
5. **Maintains Stack Traces**: Original stack trace preserved for debugging

### Problem Statement

**Without Standard Exception Handling**:
```python
# Agent code must handle provider-specific exceptions
try:
    response = redis_client.get("key")
except redis.exceptions.ConnectionError as e:
    # Redis-specific handling
    pass
except redis.exceptions.TimeoutError as e:
    # Redis-specific handling
    pass

try:
    result = anthropic_client.messages.create(...)
except anthropic.RateLimitError as e:
    # Anthropic-specific handling
    pass
except anthropic.APIError as e:
    # Anthropic-specific handling
    pass
```

**Problems**:
- Agent code coupled to external libraries
- Cannot swap Redis for another cache without changing agent code
- Difficult to add retry logic consistently
- Error logging inconsistent across integrations

---

## Decision

We will implement **Golden Rule #7: Always Wrap Exceptions** - a standardized exception wrapping pattern for all external integrations.

### Exception Hierarchy

```python
# Base exception for all application errors
class MarketingDirectorError(Exception):
    """Base exception for AI Marketing Director"""

# Category exceptions (inherit from base)
class AgentError(MarketingDirectorError):
    """Errors from agent operations"""

class IntegrationError(MarketingDirectorError):
    """Errors from external integrations"""

class InfrastructureError(MarketingDirectorError):
    """Errors from infrastructure components"""

# Specific exceptions (inherit from category)
class AgentValidationError(AgentError):
    """Agent task validation failed"""

class AgentExecutionError(AgentError):
    """Agent task execution failed"""

class MessageBusError(InfrastructureError):
    """Message bus operation failed"""

class LLMProviderError(IntegrationError):
    """LLM provider operation failed"""
```

### Exception Wrapping Pattern

**The `wrap_exception` Utility**:
```python
def wrap_exception(
    exc: Exception,
    wrapper_class: Type[MarketingDirectorError],
    message: str,
    context: dict[str, Any] | None = None,
) -> MarketingDirectorError:
    """
    Wrap external exception in application exception.

    WHY: Provides consistent exception interface and preserves context.
    HOW: Creates wrapper exception with original as cause.

    Args:
        exc: Original exception to wrap
        wrapper_class: Application exception class to wrap with
        message: Human-readable error message
        context: Additional context for debugging

    Returns:
        Wrapped exception with original as __cause__
    """
    wrapped = wrapper_class(message)
    wrapped.__cause__ = exc  # Preserve original exception
    wrapped.context = context or {}  # Add debugging context
    return wrapped
```

### Standard Usage Pattern

**Integration Layer (Always Wrap)**:
```python
class BlueskyClient:
    """Bluesky integration client."""

    async def create_post(self, text: str) -> dict:
        """Create post on Bluesky."""
        try:
            # Call external library
            response = await self._client.send_post(text)
            return response

        except atproto.exceptions.AuthError as e:
            # Wrap authentication errors
            raise wrap_exception(
                exc=e,
                wrapper_class=IntegrationError,
                message="Bluesky authentication failed",
                context={
                    "platform": "bluesky",
                    "handle": self._handle,
                    "operation": "create_post"
                }
            ) from e

        except atproto.exceptions.RateLimitError as e:
            # Wrap rate limit errors
            raise wrap_exception(
                exc=e,
                wrapper_class=IntegrationError,
                message="Bluesky rate limit exceeded",
                context={
                    "platform": "bluesky",
                    "operation": "create_post",
                    "retry_after": e.retry_after
                }
            ) from e

        except Exception as e:
            # Catch-all for unexpected errors
            raise wrap_exception(
                exc=e,
                wrapper_class=IntegrationError,
                message="Unexpected error creating Bluesky post",
                context={
                    "platform": "bluesky",
                    "operation": "create_post",
                    "text_length": len(text)
                }
            ) from e
```

**Agent Layer (Handle Wrapped Exceptions)**:
```python
class BlueskyManagerAgent(BaseAgent):
    """Bluesky management agent."""

    async def _create_post(self, task: Task) -> dict:
        """Create post on Bluesky."""
        try:
            # Integration layer raises IntegrationError
            post = await self._bluesky_client.create_post(
                text=task.parameters["content"]
            )
            return {"status": "success", "post_uri": post["uri"]}

        except IntegrationError as e:
            # Handle integration errors
            logger.error(
                "Failed to create Bluesky post",
                extra={
                    "error": str(e),
                    "cause": str(e.__cause__),
                    "context": e.context
                }
            )

            # Re-wrap as agent error
            raise wrap_exception(
                exc=e,
                wrapper_class=AgentExecutionError,
                message=f"Bluesky Manager failed to create post: {e}",
                context={
                    "agent": self.agent_id,
                    "task_id": task.task_id,
                    "original_context": e.context
                }
            ) from e
```

---

## Alternatives Considered

### Alternative 1: Re-raise Original Exceptions
**Description**: Don't wrap, just re-raise original exceptions

**Pros**:
- No wrapping overhead
- Simplest implementation
- Stack traces point directly to source

**Cons**:
- Couples application to external library exception types
- Cannot swap libraries without changing exception handling
- Inconsistent error interfaces across integrations
- Difficult to add retry logic
- **Rejected**: Too tightly coupled to external libraries

### Alternative 2: Convert to String Messages
**Description**: Catch exceptions and convert to string error messages

**Pros**:
- Simple error handling
- No exception hierarchy needed

**Cons**:
- Loses original exception type (cannot handle differently)
- Loses stack trace (debugging nightmare)
- Cannot add structured context
- **Rejected**: Loses too much debugging information

### Alternative 3: Try/Except in Every Method
**Description**: Let each method handle exceptions individually

**Pros**:
- Maximum flexibility
- No enforced pattern

**Cons**:
- Inconsistent error handling across codebase
- Exception handling code duplicated everywhere
- Easy to forget to wrap exceptions
- Difficult to maintain
- **Rejected**: Not maintainable at scale

### Alternative 4: Result Types (No Exceptions)
**Description**: Use Result[T, E] types instead of exceptions (Rust-style)

**Pros**:
- Explicit error handling
- Forces callers to handle errors
- No exception performance overhead

**Cons**:
- Not idiomatic Python
- Significant code changes required
- Steeper learning curve
- Interop difficult with exception-based libraries
- **Rejected**: Too radical departure from Python idioms

---

## Consequences

### Positive Consequences

✅ **Decoupling**: Application code decoupled from external library exceptions
✅ **Consistency**: All integrations expose same exception types
✅ **Context Preservation**: Original exception and stack trace preserved
✅ **Structured Context**: Additional debugging context attached to exceptions
✅ **Maintainability**: Easy to swap integrations (exception interface unchanged)
✅ **Error Handling**: Different error types handled differently (auth vs rate limit)
✅ **Debugging**: Rich context helps diagnose issues quickly
✅ **Testability**: Easy to mock and test exception handling

### Negative Consequences

⚠️ **Wrapping Overhead**: Small performance cost (negligible for I/O operations)
⚠️ **Extra Code**: Must write wrapping code for each integration
⚠️ **Stack Traces Longer**: Wrapped exceptions have longer stack traces
⚠️ **Discipline Required**: Developers must remember to wrap consistently

### Mitigation Strategies

**For Wrapping Overhead**:
- Measured: < 0.1ms overhead (negligible for network operations)
- Only wrap at integration boundaries (not internal code)

**For Extra Code**:
- Provide `wrap_exception` utility (one-liner)
- Include in templates and examples
- Code reviews enforce wrapping

**For Stack Traces**:
- Use `from e` syntax to preserve original traceback
- Logging captures both wrapped and original exception

**For Discipline**:
- Mandatory in code reviews
- Lint rule to detect unwrapped external exceptions (future)
- TDD ensures exception handling tested

---

## Implementation Guidelines

### When to Wrap

**ALWAYS Wrap** (Integration Boundaries):
- External API calls (Anthropic, OpenAI, LinkedIn, etc.)
- Database operations (PostgreSQL, Redis)
- File system operations
- Network operations
- Third-party library calls

**DON'T Wrap** (Internal Code):
- Application exceptions (already wrapped)
- Built-in Python exceptions in internal code (ValueError, TypeError)
- Exceptions from our own modules

### Context Dictionary Guidelines

**Essential Context** (always include):
- `operation`: What operation was being performed
- `component`: Which component failed (e.g., "bluesky_client")

**Useful Context** (include when relevant):
- Request parameters (sanitized, no secrets)
- Entity IDs (task_id, content_id, agent_id)
- Timing information (when operation started)
- Retry information (attempt number, max retries)

**Example**:
```python
context = {
    "operation": "create_post",
    "platform": "bluesky",
    "handle": "company.bsky.social",  # OK
    "text_length": 250,  # OK
    "attempt": 2,  # OK
    "max_attempts": 3,  # OK
    # "app_password": "secret"  # NEVER include secrets!
}
```

---

## Error Handling Patterns

### Pattern 1: Catch, Wrap, Re-raise

```python
try:
    result = external_library.operation()
except ExternalError as e:
    raise wrap_exception(
        exc=e,
        wrapper_class=IntegrationError,
        message="Operation failed",
        context={"operation": "..."}
    ) from e
```

### Pattern 2: Catch, Log, Wrap, Re-raise

```python
try:
    result = external_library.operation()
except ExternalError as e:
    logger.error(f"Operation failed: {e}", extra={"context": {...}})
    raise wrap_exception(...) from e
```

### Pattern 3: Catch, Retry, Then Wrap

```python
for attempt in range(max_retries):
    try:
        result = external_library.operation()
        return result
    except ExternalError as e:
        if attempt == max_retries - 1:
            # Last attempt, wrap and raise
            raise wrap_exception(
                exc=e,
                wrapper_class=IntegrationError,
                message="Operation failed after retries",
                context={
                    "attempts": max_retries,
                    "operation": "..."
                }
            ) from e
        else:
            # Retry
            await asyncio.sleep(retry_delay)
```

### Pattern 4: Multiple Exception Types

```python
try:
    result = external_library.operation()
except ExternalAuthError as e:
    # Authentication error (don't retry)
    raise wrap_exception(
        exc=e,
        wrapper_class=IntegrationError,
        message="Authentication failed",
        context={"error_type": "auth"}
    ) from e
except ExternalRateLimitError as e:
    # Rate limit (can retry later)
    raise wrap_exception(
        exc=e,
        wrapper_class=IntegrationError,
        message="Rate limit exceeded",
        context={
            "error_type": "rate_limit",
            "retry_after": e.retry_after
        }
    ) from e
except Exception as e:
    # Catch-all for unexpected errors
    raise wrap_exception(
        exc=e,
        wrapper_class=IntegrationError,
        message="Unexpected error",
        context={"error_type": "unknown"}
    ) from e
```

---

## Testing Exception Handling

### Unit Tests

```python
@pytest.mark.unit
async def test_bluesky_create_post_auth_error():
    """Test authentication error is wrapped correctly"""

    # Mock external library to raise auth error
    mock_client = AsyncMock()
    mock_client.send_post.side_effect = atproto.exceptions.AuthError(
        "Invalid credentials"
    )

    client = BlueskyClient(
        handle="test",
        app_password="test",
        _client=mock_client
    )

    # Should wrap in IntegrationError
    with pytest.raises(IntegrationError) as exc_info:
        await client.create_post("test post")

    # Verify wrapped exception
    assert "authentication failed" in str(exc_info.value).lower()
    assert exc_info.value.context["platform"] == "bluesky"
    assert isinstance(exc_info.value.__cause__, atproto.exceptions.AuthError)
```

### Integration Tests

```python
@pytest.mark.integration
async def test_bluesky_create_post_real_auth_error():
    """Test real authentication error"""

    client = BlueskyClient(
        handle="invalid@test.com",
        app_password="invalid_password"
    )

    # Real API call with invalid credentials
    with pytest.raises(IntegrationError) as exc_info:
        await client.create_post("test post")

    # Verify error details
    assert "authentication" in str(exc_info.value).lower()
    assert exc_info.value.context is not None
```

---

## Metrics & Monitoring

### Error Metrics

```python
# Counter for wrapped exceptions by type
wrapped_exceptions_total = Counter(
    "wrapped_exceptions_total",
    "Total wrapped exceptions",
    ["exception_type", "component", "operation"]
)

# Histogram for error context size
error_context_size_bytes = Histogram(
    "error_context_size_bytes",
    "Size of error context dictionary",
    ["exception_type"]
)

# Usage in wrap_exception
def wrap_exception(...) -> MarketingDirectorError:
    wrapped = wrapper_class(message)
    wrapped.__cause__ = exc
    wrapped.context = context or {}

    # Track metrics
    wrapped_exceptions_total.labels(
        exception_type=wrapper_class.__name__,
        component=context.get("component", "unknown"),
        operation=context.get("operation", "unknown")
    ).inc()

    return wrapped
```

### Alerting

```yaml
alerts:
  - name: HighIntegrationErrorRate
    condition: rate(wrapped_exceptions_total{exception_type="IntegrationError"}[5m]) > 10
    severity: warning
    message: "High rate of integration errors"

  - name: AuthenticationFailures
    condition: rate(wrapped_exceptions_total{operation="authenticate"}[5m]) > 5
    severity: critical
    message: "Multiple authentication failures detected"
```

---

## Real-World Examples

### Example 1: Bluesky Client (Phase 2)

Before wrapping:
```python
# Exposed atproto exceptions directly
async def create_post(self, text: str):
    return await self._client.send_post(text)
    # Could raise: atproto.exceptions.AuthError,
    #              atproto.exceptions.RateLimitError, etc.
```

After wrapping:
```python
async def create_post(self, text: str):
    try:
        return await self._client.send_post(text)
    except Exception as e:
        raise wrap_exception(
            exc=e,
            wrapper_class=IntegrationError,
            message="Failed to create Bluesky post",
            context={"platform": "bluesky", "operation": "create_post"}
        ) from e
```

### Example 2: Message Bus (Phase 2)

```python
async def publish(self, channel: str, message: dict):
    """Publish message to channel."""
    try:
        await self._redis.publish(channel, json.dumps(message))
    except redis.ConnectionError as e:
        raise wrap_exception(
            exc=e,
            wrapper_class=MessageBusError,
            message="Failed to publish message (connection error)",
            context={
                "component": "message_bus",
                "operation": "publish",
                "channel": channel
            }
        ) from e
    except redis.TimeoutError as e:
        raise wrap_exception(
            exc=e,
            wrapper_class=MessageBusError,
            message="Failed to publish message (timeout)",
            context={
                "component": "message_bus",
                "operation": "publish",
                "channel": channel,
                "timeout_ms": self._timeout_ms
            }
        ) from e
```

---

## References

- **Pattern**: Exception Translator pattern (EIP)
- **Practice**: Domain-Driven Design exception boundaries
- **Python**: PEP 3134 - Exception Chaining and Embedded Tracebacks
- **Book**: "Release It!" - Michael Nygard (exception handling in production)

---

## Related ADRs

- [ADR-002: TDD Methodology](./ADR-002-tdd-methodology.md) - TDD ensures exception handling tested
- [ADR-003: Redis Message Bus Pattern](./ADR-003-redis-message-bus-pattern.md) - Uses exception wrapping
- [ADR-004: Multi-Provider LLM Abstraction](./ADR-004-multi-provider-llm-abstraction.md) - Uses exception wrapping

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-03 | AI Marketing Director Team | Initial ADR documenting exception wrapping standard (Golden Rule #7) |

---

**Status**: Enforced in Phase 1-2
**Compliance**: Mandatory for all integration code
**Next Review**: Ongoing (every code review)
