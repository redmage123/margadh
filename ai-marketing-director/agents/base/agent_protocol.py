"""
Agent Protocol - Interface definition for all AI Marketing Director agents.

WHY: Defines the contract that all agents must implement, enabling type safety
     and consistent behavior across the multiagent system.

HOW: Uses Python Protocol (structural subtyping) for interface definition.
     Agents implement this protocol without explicit inheritance.

Usage:
    from agents.base.agent_protocol import AgentProtocol

    class CopywriterAgent:
        '''Implements AgentProtocol via structural typing.'''

        async def execute(self, task: Task) -> AgentResult:
            # Implementation
            pass
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Protocol


class AgentRole(str, Enum):
    """
    Agent role enumeration.

    WHY: Provides type-safe agent role identification for routing and permissions.
    """

    # Executive Layer
    CMO = "cmo"
    VP_MARKETING = "vp_marketing"
    DIRECTOR_COMMS = "director_comms"

    # Management Layer
    CONTENT_MANAGER = "content_manager"
    SOCIAL_MEDIA_MANAGER = "social_media_manager"
    CAMPAIGN_MANAGER = "campaign_manager"

    # Specialist Layer
    COPYWRITER = "copywriter"
    SEO_SPECIALIST = "seo_specialist"
    DESIGNER = "designer"
    ANALYTICS_SPECIALIST = "analytics_specialist"
    EMAIL_SPECIALIST = "email_specialist"
    LINKEDIN_MANAGER = "linkedin_manager"
    TWITTER_MANAGER = "twitter_manager"
    BLUESKY_MANAGER = "bluesky_manager"
    MARKET_RESEARCH = "market_research"


class TaskStatus(str, Enum):
    """
    Task execution status.

    WHY: Standardizes task status across all agents for tracking and monitoring.
    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """
    Task priority levels.

    WHY: Enables priority-based task scheduling and execution.
    """

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass(frozen=True)
class Task:
    """
    Immutable task definition for agent execution.

    WHY: Immutable design ensures task data integrity during execution.
         Frozen dataclass prevents accidental modification.

    Attributes:
        task_id: Unique task identifier
        task_type: Type of task (e.g., "create_blog", "analyze_content")
        priority: Task priority level
        parameters: Task-specific parameters (immutable dict)
        assigned_to: Agent role assigned to execute task
        assigned_by: Agent role that assigned the task
        created_at: Task creation timestamp
        deadline: Optional task deadline
        context: Additional context for task execution
    """

    task_id: str
    task_type: str
    priority: TaskPriority
    parameters: dict[str, Any]
    assigned_to: AgentRole
    assigned_by: AgentRole | None
    created_at: datetime
    deadline: datetime | None = None
    context: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """
        Validate task after initialization.

        WHY: Ensures task data integrity at creation time.
        """
        if not self.task_id:
            raise ValueError("task_id cannot be empty")
        if not self.task_type:
            raise ValueError("task_type cannot be empty")


@dataclass(frozen=True)
class AgentResult:
    """
    Immutable result from agent task execution.

    WHY: Immutable design ensures result integrity for logging and auditing.
         Frozen dataclass prevents modification of execution results.

    Attributes:
        task_id: ID of the task that was executed
        status: Execution status
        result: Task execution result (success data)
        error: Error information (if status is FAILED)
        metadata: Execution metadata (duration, token usage, etc.)
        created_at: Result creation timestamp
    """

    task_id: str
    status: TaskStatus
    result: Any | None = None
    error: str | None = None
    metadata: dict[str, Any] | None = None
    created_at: datetime = datetime.now()

    def __post_init__(self) -> None:
        """
        Validate result after initialization.

        WHY: Ensures result data integrity.
        """
        if not self.task_id:
            raise ValueError("task_id cannot be empty")
        if self.status == TaskStatus.FAILED and not self.error:
            raise ValueError("error must be provided when status is FAILED")
        if self.status == TaskStatus.COMPLETED and self.result is None:
            raise ValueError("result must be provided when status is COMPLETED")


@dataclass(frozen=True)
class AgentMessage:
    """
    Immutable message for agent-to-agent communication.

    WHY: Immutable design ensures message integrity during async message passing.
         Supports message bus serialization/deserialization.

    Attributes:
        message_id: Unique message identifier
        from_agent: Sender agent role
        to_agent: Recipient agent role
        message_type: Type of message (e.g., "task_assignment", "status_update")
        payload: Message payload data
        priority: Message priority
        created_at: Message creation timestamp
        reply_to: Optional message ID this is replying to
    """

    message_id: str
    from_agent: AgentRole
    to_agent: AgentRole
    message_type: str
    payload: dict[str, Any]
    priority: TaskPriority
    created_at: datetime
    reply_to: str | None = None


class AgentProtocol(Protocol):
    """
    Protocol (interface) that all agents must implement.

    WHY: Defines the contract for agent behavior, enabling:
         - Type safety via structural subtyping
         - Consistent agent interface across the system
         - Easy testing via mock implementations
         - Pluggable agent architecture

    HOW: Python Protocol uses structural subtyping - any class implementing
         these methods satisfies the protocol without explicit inheritance.

    Usage:
        class MyAgent:
            '''Implements AgentProtocol automatically.'''

            @property
            def agent_id(self) -> str:
                return "my_agent_001"

            @property
            def role(self) -> AgentRole:
                return AgentRole.COPYWRITER

            async def execute(self, task: Task) -> AgentResult:
                # Implementation
                pass

            async def validate_task(self, task: Task) -> bool:
                # Implementation
                pass

            async def stop(self) -> None:
                # Implementation
                pass
    """

    @property
    def agent_id(self) -> str:
        """
        Get unique agent instance identifier.

        WHY: Enables tracking of specific agent instances for logging,
             monitoring, and debugging.

        Returns:
            Unique agent identifier (e.g., "copywriter_001")
        """
        ...

    @property
    def role(self) -> AgentRole:
        """
        Get agent's role in the organization.

        WHY: Determines agent's capabilities, permissions, and routing rules.

        Returns:
            Agent's role from AgentRole enum
        """
        ...

    @property
    def is_available(self) -> bool:
        """
        Check if agent is available to accept new tasks.

        WHY: Enables load balancing and prevents task assignment to busy agents.

        Returns:
            True if agent can accept new tasks, False otherwise
        """
        ...

    async def execute(self, task: Task) -> AgentResult:
        """
        Execute a task assigned to this agent.

        WHY: Core agent capability - performs the actual work.
        HOW: Async method supports concurrent task execution.

        Args:
            task: Task to execute

        Returns:
            Result of task execution

        Raises:
            AgentValidationError: If task validation fails
            AgentExecutionError: If task execution fails
        """
        ...

    async def validate_task(self, task: Task) -> bool:
        """
        Validate whether agent can execute the given task.

        WHY: Pre-execution validation prevents task assignment errors.
        HOW: Checks task type, parameters, and agent capabilities.

        Args:
            task: Task to validate

        Returns:
            True if agent can execute task, False otherwise
        """
        ...

    async def send_message(self, message: AgentMessage) -> None:
        """
        Send message to another agent via message bus.

        WHY: Enables inter-agent communication for collaboration.
        HOW: Publishes message to message bus for delivery.

        Args:
            message: Message to send

        Raises:
            AgentCommunicationError: If message delivery fails
        """
        ...

    async def receive_messages(self) -> list[AgentMessage]:
        """
        Receive pending messages from message bus.

        WHY: Enables agents to process incoming communications.
        HOW: Pulls messages from agent's inbox queue.

        Returns:
            List of pending messages (may be empty)

        Raises:
            AgentCommunicationError: If message retrieval fails
        """
        ...

    async def stop(self) -> None:
        """
        Gracefully stop the agent.

        WHY: Ensures clean shutdown with resource cleanup.
        HOW: Completes pending tasks, closes connections, releases resources.
        """
        ...
