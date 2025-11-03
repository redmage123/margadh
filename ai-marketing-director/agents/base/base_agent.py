"""
BaseAgent - Abstract base class for all AI Marketing Director agents.

WHY: Provides common functionality for all agents, ensuring consistent behavior
     and reducing code duplication across agent implementations.

HOW: Implements AgentProtocol using functional patterns and async operations.
     Subclasses override specific methods for custom behavior.

Usage:
    from agents.base import BaseAgent, AgentConfig
    from agents.base.agent_protocol import AgentRole

    class CopywriterAgent(BaseAgent):
        '''Custom copywriter agent implementation.'''

        async def _execute_task(self, task: Task) -> dict[str, Any]:
            # Override with custom execution logic
            content = await self._generate_with_llm(
                f"Write a blog about {task.parameters['topic']}"
            )
            return {"content": content}

    # Create and use agent
    config = AgentConfig(
        agent_id="copywriter_001",
        role=AgentRole.COPYWRITER
    )
    agent = CopywriterAgent(config=config)
    result = await agent.execute(task)
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from agents.base.agent_config import AgentConfig
from agents.base.agent_protocol import (
    AgentMessage,
    AgentResult,
    AgentRole,
    Task,
    TaskPriority,
    TaskStatus,
)
from core.exceptions import (
    AgentCommunicationError,
    AgentExecutionError,
    AgentValidationError,
    wrap_exception,
)


class BaseAgent(ABC):
    """
    Abstract base class for all agents.

    WHY: Provides common agent functionality while allowing customization.
         Implements AgentProtocol contract for type safety.

    HOW: Uses template method pattern - subclasses override _execute_task().
         Functional patterns: pure validation, immutable results.

    Attributes:
        _config: Agent configuration (immutable)
        _is_available: Whether agent can accept new tasks
        _current_tasks: Set of currently executing task IDs
        _message_bus: Message bus client (dependency injected)
        _llm_provider: LLM provider client (dependency injected)
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize base agent.

        WHY: Sets up agent with validated configuration and dependencies.
        HOW: Stores config, initializes state, sets up connections (lazy).

        Args:
            config: Validated agent configuration

        Raises:
            ValueError: If configuration is invalid
        """
        self._config = config
        self._is_available = True
        self._current_tasks: set[str] = set()

        # Lazy initialization of dependencies (will be set when needed)
        self._message_bus: Any = None
        self._llm_provider: Any = None

    # ========================================================================
    # AgentProtocol Properties
    # ========================================================================

    @property
    def agent_id(self) -> str:
        """
        Get unique agent instance identifier.

        WHY: Required by AgentProtocol for agent identification.

        Returns:
            Unique agent identifier from configuration
        """
        return self._config.agent_id

    @property
    def role(self) -> AgentRole:
        """
        Get agent's role in the organization.

        WHY: Required by AgentProtocol for role-based routing.

        Returns:
            Agent's role from configuration
        """
        return self._config.role

    @property
    def is_available(self) -> bool:
        """
        Check if agent is available to accept new tasks.

        WHY: Required by AgentProtocol for load balancing.
        HOW: Checks current task count against max concurrent tasks.

        Returns:
            True if agent can accept more tasks, False otherwise
        """
        if not self._is_available:
            return False

        max_tasks = self._config.max_concurrent_tasks
        return len(self._current_tasks) < max_tasks

    # ========================================================================
    # Task Validation (Pure Function)
    # ========================================================================

    async def validate_task(self, task: Task) -> bool:
        """
        Validate whether agent can execute the given task.

        WHY: Pre-execution validation prevents task assignment errors.
        HOW: Checks task assignment, type, and parameters (pure function).

        Args:
            task: Task to validate

        Returns:
            True if agent can execute task, False otherwise
        """
        # Check 1: Task must be assigned to this agent's role
        if task.assigned_to != self.role:
            return False

        # Check 2: Agent must be available
        if not self.is_available:
            return False

        # Check 3: Task must have required parameters
        # Subclasses can override _validate_task_parameters for custom validation
        return await self._validate_task_parameters(task)

    async def _validate_task_parameters(self, task: Task) -> bool:
        """
        Validate task parameters (override in subclasses).

        WHY: Allows subclasses to add custom parameter validation.
        HOW: Default implementation accepts all parameters.

        Args:
            task: Task to validate

        Returns:
            True if parameters are valid, False otherwise
        """
        # Default: accept all tasks
        # Subclasses override for custom validation
        return True

    # ========================================================================
    # Task Execution (Template Method Pattern)
    # ========================================================================

    async def execute(self, task: Task) -> AgentResult:
        """
        Execute a task assigned to this agent.

        WHY: Core agent capability - performs the actual work.
        HOW: Template method - validates, executes, returns result.
              Uses functional pattern: returns immutable result.

        Args:
            task: Task to execute

        Returns:
            Immutable result of task execution

        Raises:
            AgentValidationError: If task validation fails
            AgentExecutionError: If task execution fails
        """
        # Step 1: Validate task
        is_valid = await self.validate_task(task)
        if not is_valid:
            raise AgentValidationError(
                message=f"Task validation failed for {task.task_id}",
                context={
                    "agent_id": self.agent_id,
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                    "expected_role": self.role.value,
                    "actual_role": task.assigned_to.value,
                },
            )

        # Step 2: Mark agent as busy
        self._current_tasks.add(task.task_id)

        try:
            # Step 3: Execute task (subclass implements _execute_task)
            execution_start = datetime.now()
            result_data = await self._execute_task(task)
            execution_end = datetime.now()

            # Step 4: Create success result (immutable)
            execution_time = (execution_end - execution_start).total_seconds()
            return AgentResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                result=result_data,
                metadata={
                    "agent_id": self.agent_id,
                    "execution_time": execution_time,
                    "completed_at": execution_end.isoformat(),
                },
                created_at=execution_end,
            )

        except Exception as e:
            # Step 5: Handle execution errors
            raise wrap_exception(
                exc=e,
                wrapper_class=AgentExecutionError,
                message=f"Task execution failed for {task.task_id}",
                context={
                    "agent_id": self.agent_id,
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                },
            ) from e

        finally:
            # Step 6: Mark agent as available again
            self._current_tasks.discard(task.task_id)

    @abstractmethod
    async def _execute_task(self, task: Task) -> dict[str, Any]:
        """
        Execute task logic (implemented by subclasses).

        WHY: Template method - each agent type has custom execution logic.
        HOW: Subclass implements specific task execution behavior.

        Args:
            task: Task to execute

        Returns:
            Task result data (will be wrapped in AgentResult)

        Raises:
            Exception: Any execution errors (will be wrapped)
        """
        ...

    # ========================================================================
    # Agent-to-Agent Communication
    # ========================================================================

    async def send_message(self, message: AgentMessage) -> None:
        """
        Send message to another agent via message bus.

        WHY: Enables inter-agent communication for collaboration.
        HOW: Publishes message to message bus, wraps errors.

        Args:
            message: Message to send

        Raises:
            AgentCommunicationError: If message delivery fails
        """
        try:
            # Lazy initialize message bus if needed
            if self._message_bus is None:
                await self._initialize_message_bus()

            # Publish message
            await self._message_bus.publish(
                queue=f"{self._config.message_bus_config.queue_prefix}_{message.to_agent.value}",
                message=message,
            )

        except Exception as e:
            raise wrap_exception(
                exc=e,
                wrapper_class=AgentCommunicationError,
                message=f"Failed to send message {message.message_id}",
                context={
                    "agent_id": self.agent_id,
                    "message_id": message.message_id,
                    "from_agent": message.from_agent.value,
                    "to_agent": message.to_agent.value,
                },
            ) from e

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
        try:
            # Lazy initialize message bus if needed
            if self._message_bus is None:
                await self._initialize_message_bus()

            # Receive messages from inbox
            messages = await self._message_bus.receive(
                queue=f"{self._config.message_bus_config.queue_prefix}_{self.role.value}"
            )

            return messages if messages else []

        except Exception as e:
            raise wrap_exception(
                exc=e,
                wrapper_class=AgentCommunicationError,
                message="Failed to receive messages",
                context={"agent_id": self.agent_id},
            ) from e

    # ========================================================================
    # LLM Integration (Helper Method)
    # ========================================================================

    async def _generate_with_llm(
        self,
        prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Generate text using configured LLM provider.

        WHY: Provides common LLM generation functionality for all agents.
        HOW: Uses configured LLM provider (Claude, OpenAI, etc.).

        Args:
            prompt: Text prompt for generation
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            Generated text from LLM

        Raises:
            Exception: LLM API errors (wrapped by caller)
        """
        # Lazy initialize LLM provider if needed
        if self._llm_provider is None:
            await self._initialize_llm_provider()

        # Use config values if not overridden
        temp = (
            temperature
            if temperature is not None
            else self._config.llm_config.temperature
        )
        tokens = (
            max_tokens if max_tokens is not None else self._config.llm_config.max_tokens
        )

        # Generate text
        response = await self._llm_provider.generate(
            prompt=prompt, temperature=temp, max_tokens=tokens
        )

        return response

    # ========================================================================
    # Lifecycle Management
    # ========================================================================

    async def stop(self) -> None:
        """
        Gracefully stop the agent.

        WHY: Ensures clean shutdown with resource cleanup.
        HOW: Completes pending tasks, closes connections, releases resources.
        """
        # Mark as unavailable immediately
        self._is_available = False

        # Wait for current tasks to complete (with timeout)
        if self._current_tasks:
            # Give tasks time to complete
            for _ in range(10):  # Max 10 seconds
                if not self._current_tasks:
                    break
                await asyncio.sleep(1)

        # Close connections
        if self._message_bus is not None:
            await self._message_bus.close()

        if self._llm_provider is not None:
            await self._llm_provider.close()

    # ========================================================================
    # Lazy Initialization (Private Methods)
    # ========================================================================

    async def _initialize_message_bus(self) -> None:
        """
        Initialize message bus connection (lazy).

        WHY: Defers connection until needed, supports testing.
        HOW: Creates message bus client from config.
        """
        # Import here to avoid circular dependencies
        from infrastructure.message_bus import MessageBus

        self._message_bus = MessageBus(
            redis_url=self._config.message_bus_config.redis_url,
            queue_prefix=self._config.message_bus_config.queue_prefix,
        )

    async def _initialize_llm_provider(self) -> None:
        """
        Initialize LLM provider connection (lazy).

        WHY: Defers connection until needed, supports testing.
        HOW: Creates LLM client based on config provider.
        """
        # Import here to avoid circular dependencies
        if self._config.llm_config.provider == "anthropic":
            from infrastructure.llm import ClaudeLLM

            self._llm_provider = ClaudeLLM(config=self._config.llm_config)
        elif self._config.llm_config.provider == "openai":
            from infrastructure.llm import OpenAILLM

            self._llm_provider = OpenAILLM(config=self._config.llm_config)
        else:
            raise ValueError(
                f"Unsupported LLM provider: {self._config.llm_config.provider}"
            )
