"""
Custom exception hierarchy for AI Marketing Director.

WHY: Wraps base exceptions with domain context, providing better error tracking
     and logging while preventing leakage of implementation details.

HOW: All custom exceptions inherit from MarketingDirectorError base class.
     Each exception wraps the original exception and adds context.

Usage:
    from core.exceptions import DatabaseError

    try:
        result = db.query(...)
    except SQLAlchemyError as e:
        raise DatabaseError(
            message="Failed to query database",
            original_exception=e,
            context={"query": "...", "params": {...}}
        ) from e
"""

from datetime import datetime
from typing import Any


class MarketingDirectorError(Exception):
    """
    Base exception for all AI Marketing Director errors.

    WHY: Provides common interface for all custom exceptions with context preservation.

    Attributes:
        message: Human-readable error message
        original_exception: Original exception that was wrapped
        context: Additional context (agent_id, content_id, operation, etc.)
        timestamp: When the error occurred
    """

    def __init__(
        self,
        message: str,
        original_exception: Exception | None = None,
        context: dict[str, Any] | None = None,
    ):
        """
        Initialize exception with context.

        WHY: Captures error message, original exception, and domain context.

        Args:
            message: Human-readable error message
            original_exception: Original exception being wrapped (optional)
            context: Additional context dict (optional)
        """
        super().__init__(message)
        self.message = message
        self.original_exception = original_exception
        self.context = context or {}
        self.timestamp = datetime.now()

    def __str__(self) -> str:
        """
        String representation of exception.

        WHY: Provides detailed error information for logging.
        """
        base_msg = self.message

        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            base_msg = f"{base_msg} [context: {context_str}]"

        if self.original_exception:
            base_msg = f"{base_msg} [original: {type(self.original_exception).__name__}: {str(self.original_exception)}]"

        return base_msg


# ============================================================================
# Infrastructure Exceptions
# ============================================================================


class DatabaseError(MarketingDirectorError):
    """
    Database operation errors.

    WHY: Wraps database-specific errors (SQLAlchemy, psycopg2, etc.)
         with domain context.

    Use for:
    - Connection failures
    - Query errors
    - Transaction rollbacks
    - Data integrity violations
    """


class MessageBusError(MarketingDirectorError):
    """
    Message bus communication errors.

    WHY: Wraps Redis/message bus errors with agent communication context.

    Use for:
    - Failed message delivery
    - Queue connection errors
    - Serialization failures
    - Timeout errors
    """


class LLMProviderError(MarketingDirectorError):
    """
    LLM provider errors (API failures, rate limits).

    WHY: Wraps LLM SDK errors (Anthropic, OpenAI) with generation context.

    Use for:
    - API rate limits
    - API timeouts
    - Invalid API keys
    - Model errors
    - Response parsing errors
    """


class CacheError(MarketingDirectorError):
    """
    Cache operation errors.

    WHY: Wraps Redis cache errors with caching context.

    Use for:
    - Cache connection failures
    - Serialization errors
    - Cache invalidation errors
    """


class IntegrationError(MarketingDirectorError):
    """
    Third-party integration errors.

    WHY: Wraps external API errors (LinkedIn, Twitter, HubSpot) with context.

    Use for:
    - OAuth failures
    - API authentication errors
    - API rate limits
    - Invalid API responses
    - Network errors
    """


# ============================================================================
# Agent Exceptions
# ============================================================================


class AgentError(MarketingDirectorError):
    """
    Base exception for agent errors.

    WHY: Provides common base for all agent-related errors.
    """


class AgentValidationError(AgentError):
    """
    Agent input/output validation errors.

    WHY: Indicates invalid input to agent or invalid output from agent.

    Use for:
    - Missing required parameters
    - Invalid parameter types
    - Invalid parameter values
    - Invalid agent output format
    """


class AgentExecutionError(AgentError):
    """
    Agent execution failures.

    WHY: Indicates agent failed to complete its task.

    Use for:
    - LLM generation failures
    - Workflow execution failures
    - Internal agent logic errors
    """


class AgentCommunicationError(AgentError):
    """
    Agent-to-agent communication errors.

    WHY: Indicates failure in inter-agent communication.

    Use for:
    - Message delivery failures
    - Message format errors
    - Agent not responding
    """


# ============================================================================
# Business Logic Exceptions
# ============================================================================


class ContentError(MarketingDirectorError):
    """
    Content-related errors.

    WHY: Wraps content creation/management errors with business context.

    Use for:
    - Content validation failures
    - Content generation errors
    - Content publishing errors
    """


class CampaignError(MarketingDirectorError):
    """
    Campaign-related errors.

    WHY: Wraps campaign management errors with business context.

    Use for:
    - Campaign creation errors
    - Campaign execution failures
    - Campaign validation errors
    """


class WorkflowError(MarketingDirectorError):
    """
    Workflow execution errors.

    WHY: Indicates failure in multi-step workflow execution.

    Use for:
    - Workflow step failures
    - Workflow timeout errors
    - Workflow validation errors
    """


class AuthenticationError(MarketingDirectorError):
    """
    Authentication errors.

    WHY: Indicates user authentication failures.

    Use for:
    - Invalid credentials
    - Expired tokens
    - Missing authentication
    """


class AuthorizationError(MarketingDirectorError):
    """
    Authorization/permission errors.

    WHY: Indicates user lacks required permissions.

    Use for:
    - Insufficient permissions
    - Role-based access control violations
    """


class ValidationError(MarketingDirectorError):
    """
    Data validation errors.

    WHY: Indicates invalid data that failed validation.

    Use for:
    - Schema validation failures
    - Business rule violations
    - Data integrity violations
    """


class ConfigurationError(MarketingDirectorError):
    """
    Configuration errors.

    WHY: Indicates system configuration issues.

    Use for:
    - Missing configuration
    - Invalid configuration values
    - Configuration file errors
    """


# ============================================================================
# Utility Functions
# ============================================================================


def wrap_exception(
    exc: Exception,
    wrapper_class: type[MarketingDirectorError],
    message: str,
    context: dict[str, Any] | None = None,
) -> MarketingDirectorError:
    """
    Utility function to wrap exceptions.

    WHY: Provides consistent exception wrapping pattern.
    HOW: Creates new custom exception wrapping the original.

    Args:
        exc: Original exception to wrap
        wrapper_class: Custom exception class to use
        message: Error message for wrapped exception
        context: Additional context dict

    Returns:
        Wrapped custom exception

    Example:
        try:
            db.query(...)
        except SQLAlchemyError as e:
            raise wrap_exception(
                e,
                DatabaseError,
                "Failed to query database",
                {"table": "content", "operation": "select"}
            ) from e
    """
    return wrapper_class(
        message=message, original_exception=exc, context=context or {}
    )
