"""
Agent Configuration - Type-safe configuration for all agents.

WHY: Provides validated, type-safe configuration using Pydantic.
     Ensures configuration errors are caught at startup, not runtime.

HOW: Uses Pydantic BaseModel for validation, type coercion, and defaults.

Usage:
    from agents.base.agent_config import AgentConfig, LLMConfig

    config = AgentConfig(
        agent_id="copywriter_001",
        role=AgentRole.COPYWRITER,
        llm_config=LLMConfig(
            provider="anthropic",
            model="claude-sonnet-3-5"
        )
    )
"""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from agents.base.agent_protocol import AgentRole


class LLMConfig(BaseModel):
    """
    LLM provider configuration.

    WHY: Centralizes LLM configuration with validation.
    HOW: Pydantic model with field validation.

    Attributes:
        provider: LLM provider ("anthropic" or "openai")
        model: Model identifier
        temperature: Sampling temperature (0.0-1.0)
        max_tokens: Maximum tokens to generate
        timeout: Request timeout in seconds
    """

    provider: Literal["anthropic", "openai"] = Field(
        default="anthropic", description="LLM provider to use"
    )

    model: str = Field(default="claude-sonnet-3-5", description="Model identifier")

    temperature: float = Field(
        default=0.7, ge=0.0, le=1.0, description="Sampling temperature for generation"
    )

    max_tokens: int = Field(
        default=4096, gt=0, description="Maximum tokens to generate"
    )

    timeout: int = Field(default=60, gt=0, description="Request timeout in seconds")

    @field_validator("model")
    @classmethod
    def validate_model(cls, value: str, info) -> str:
        """
        Validate model identifier matches provider.

        WHY: Prevents configuration errors (e.g., using GPT-4 with Anthropic).
        """
        provider = info.data.get("provider")

        if provider == "anthropic" and not value.startswith("claude"):
            raise ValueError(
                f"Model '{value}' is invalid for provider 'anthropic'. "
                "Expected model starting with 'claude'"
            )

        if provider == "openai" and not (
            value.startswith("gpt") or value.startswith("o1")
        ):
            raise ValueError(
                f"Model '{value}' is invalid for provider 'openai'. "
                "Expected model starting with 'gpt' or 'o1'"
            )

        return value

    class Config:
        """Pydantic configuration."""

        frozen = True  # Immutable after creation


class MessageBusConfig(BaseModel):
    """
    Message bus configuration.

    WHY: Configures Redis message bus for agent communication.
    HOW: Pydantic model with Redis connection settings.

    Attributes:
        redis_url: Redis connection URL
        queue_prefix: Prefix for agent queues
        max_retries: Maximum message delivery retries
        retry_delay: Delay between retries in seconds
        message_ttl: Message time-to-live in seconds
    """

    redis_url: str = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )

    queue_prefix: str = Field(
        default="agent", description="Prefix for agent message queues"
    )

    max_retries: int = Field(
        default=3, ge=0, description="Maximum message delivery retries"
    )

    retry_delay: int = Field(
        default=5, gt=0, description="Delay between retries in seconds"
    )

    message_ttl: int = Field(
        default=3600, gt=0, description="Message time-to-live in seconds"
    )

    class Config:
        """Pydantic configuration."""

        frozen = True  # Immutable after creation


class CacheConfig(BaseModel):
    """
    Cache configuration.

    WHY: Configures Redis cache for performance optimization.
    HOW: Pydantic model with cache settings.

    Attributes:
        enabled: Whether caching is enabled
        redis_url: Redis connection URL
        default_ttl: Default cache TTL in seconds
        key_prefix: Prefix for cache keys
    """

    enabled: bool = Field(default=True, description="Whether caching is enabled")

    redis_url: str = Field(
        default="redis://localhost:6379/1",
        description="Redis connection URL (different DB from message bus)",
    )

    default_ttl: int = Field(
        default=300, gt=0, description="Default cache TTL in seconds"
    )

    key_prefix: str = Field(default="cache", description="Prefix for cache keys")

    class Config:
        """Pydantic configuration."""

        frozen = True  # Immutable after creation


class MonitoringConfig(BaseModel):
    """
    Monitoring and observability configuration.

    WHY: Configures metrics, logging, and tracing for agents.
    HOW: Pydantic model with monitoring settings.

    Attributes:
        enable_metrics: Whether to collect Prometheus metrics
        enable_tracing: Whether to enable distributed tracing
        log_level: Logging level
        metrics_port: Port for Prometheus metrics endpoint
    """

    enable_metrics: bool = Field(
        default=True, description="Whether to collect Prometheus metrics"
    )

    enable_tracing: bool = Field(
        default=False, description="Whether to enable distributed tracing"
    )

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )

    metrics_port: int = Field(
        default=9090, gt=0, le=65535, description="Port for Prometheus metrics endpoint"
    )

    class Config:
        """Pydantic configuration."""

        frozen = True  # Immutable after creation


class AgentConfig(BaseModel):
    """
    Complete agent configuration.

    WHY: Provides validated, type-safe configuration for agent initialization.
         Immutable design ensures configuration consistency during agent lifecycle.

    HOW: Pydantic model composing all configuration sections.
         Frozen to prevent modification after creation.

    Attributes:
        agent_id: Unique agent instance identifier
        role: Agent's role in the organization
        llm_config: LLM provider configuration
        message_bus_config: Message bus configuration
        cache_config: Cache configuration
        monitoring_config: Monitoring configuration
        max_concurrent_tasks: Maximum concurrent tasks agent can execute
        task_timeout: Default task timeout in seconds
    """

    agent_id: str = Field(
        ...,  # Required field
        min_length=1,
        description="Unique agent instance identifier",
    )

    role: AgentRole = Field(
        ..., description="Agent's role in the organization"  # Required field
    )

    llm_config: LLMConfig = Field(
        default_factory=LLMConfig, description="LLM provider configuration"
    )

    message_bus_config: MessageBusConfig = Field(
        default_factory=MessageBusConfig, description="Message bus configuration"
    )

    cache_config: CacheConfig = Field(
        default_factory=CacheConfig, description="Cache configuration"
    )

    monitoring_config: MonitoringConfig = Field(
        default_factory=MonitoringConfig, description="Monitoring configuration"
    )

    max_concurrent_tasks: int = Field(
        default=5, gt=0, description="Maximum concurrent tasks agent can execute"
    )

    task_timeout: int = Field(
        default=300, gt=0, description="Default task timeout in seconds"
    )

    @field_validator("agent_id")
    @classmethod
    def validate_agent_id(cls, value: str) -> str:
        """
        Validate agent_id format.

        WHY: Ensures agent IDs follow naming convention (role_number).
        """
        if not value:
            raise ValueError("agent_id cannot be empty")

        # Agent ID should be lowercase alphanumeric with underscores
        if not all(c.isalnum() or c == "_" for c in value):
            raise ValueError(
                f"agent_id '{value}' contains invalid characters. "
                "Use only lowercase letters, numbers, and underscores"
            )

        return value

    class Config:
        """Pydantic configuration."""

        frozen = True  # Immutable after creation
        use_enum_values = False  # Keep enum types, don't convert to values


# Predefined configurations for different agent types
# WHY: Provides sensible defaults for each agent role


def create_executive_config(agent_id: str, role: AgentRole) -> AgentConfig:
    """
    Create configuration for executive-layer agents.

    WHY: Executive agents (CMO, VP, Director) use Claude Opus for strategic thinking.
    HOW: Returns AgentConfig with Opus model and higher token limits.

    Args:
        agent_id: Unique agent identifier
        role: Executive role (CMO, VP_MARKETING, DIRECTOR_COMMS)

    Returns:
        Configured AgentConfig for executive agent

    Example:
        config = create_executive_config("cmo_001", AgentRole.CMO)
    """
    return AgentConfig(
        agent_id=agent_id,
        role=role,
        llm_config=LLMConfig(
            provider="anthropic",
            model="claude-opus-3",
            temperature=0.8,  # Higher creativity for strategy
            max_tokens=8192,  # Longer outputs for strategic content
        ),
        max_concurrent_tasks=3,  # Fewer concurrent tasks for quality
    )


def create_management_config(agent_id: str, role: AgentRole) -> AgentConfig:
    """
    Create configuration for management-layer agents.

    WHY: Management agents (Content Manager, etc.) use Claude Sonnet for balance.
    HOW: Returns AgentConfig with Sonnet model and moderate settings.

    Args:
        agent_id: Unique agent identifier
        role: Management role

    Returns:
        Configured AgentConfig for management agent

    Example:
        config = create_management_config(
            "content_manager_001",
            AgentRole.CONTENT_MANAGER
        )
    """
    return AgentConfig(
        agent_id=agent_id,
        role=role,
        llm_config=LLMConfig(
            provider="anthropic",
            model="claude-sonnet-3-5",
            temperature=0.7,
            max_tokens=4096,
        ),
        max_concurrent_tasks=5,  # Moderate concurrency
    )


def create_specialist_config(agent_id: str, role: AgentRole) -> AgentConfig:
    """
    Create configuration for specialist-layer agents.

    WHY: Specialist agents use Claude Haiku for fast, efficient execution.
    HOW: Returns AgentConfig with Haiku model and higher concurrency.

    Args:
        agent_id: Unique agent identifier
        role: Specialist role

    Returns:
        Configured AgentConfig for specialist agent

    Example:
        config = create_specialist_config(
            "copywriter_001",
            AgentRole.COPYWRITER
        )
    """
    return AgentConfig(
        agent_id=agent_id,
        role=role,
        llm_config=LLMConfig(
            provider="anthropic",
            model="claude-haiku-3",
            temperature=0.7,
            max_tokens=4096,
        ),
        max_concurrent_tasks=10,  # Higher concurrency for specialists
    )
