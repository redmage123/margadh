"""
Base agent module - Core agent infrastructure.

WHY: Exports base agent classes and protocols for agent implementations.

Usage:
    from agents.base import BaseAgent, AgentConfig, AgentRole, Task
"""

from agents.base.agent_config import (
    AgentConfig,
    CacheConfig,
    LLMConfig,
    MessageBusConfig,
    MonitoringConfig,
    create_executive_config,
    create_management_config,
    create_specialist_config,
)
from agents.base.agent_protocol import (
    AgentMessage,
    AgentProtocol,
    AgentResult,
    AgentRole,
    Task,
    TaskPriority,
    TaskStatus,
)
from agents.base.base_agent import BaseAgent

__all__ = [
    # Base Classes
    "BaseAgent",
    "AgentProtocol",
    # Configuration
    "AgentConfig",
    "LLMConfig",
    "MessageBusConfig",
    "CacheConfig",
    "MonitoringConfig",
    "create_executive_config",
    "create_management_config",
    "create_specialist_config",
    # Protocol Types
    "AgentRole",
    "Task",
    "TaskStatus",
    "TaskPriority",
    "AgentResult",
    "AgentMessage",
]
