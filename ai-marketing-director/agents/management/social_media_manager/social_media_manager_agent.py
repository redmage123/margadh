"""
Social Media Manager Agent - Management layer for coordinating social media specialists.

WHY: Orchestrates multi-platform social media campaigns across LinkedIn, Twitter, and Bluesky.
     Provides unified interface for content distribution and analytics aggregation.

HOW: Delegates tasks to specialist agents (LinkedIn, Twitter, Bluesky managers),
     coordinates cross-platform posting, aggregates analytics.

Supported Task Types:
- create_post: Post content to one or more platforms
- get_analytics: Aggregate analytics across platforms
- schedule_post: Schedule posts across platforms
- cross_post: Optimize and post content across all platforms

Implementation follows TDD - tests written first (RED), implementation (GREEN),
then refactored (REFACTOR).

Usage:
    from agents.management.social_media_manager import SocialMediaManagerAgent
    from agents.specialists import LinkedInManagerAgent, TwitterManagerAgent
    from agents.base import AgentConfig, AgentRole, Task

    config = AgentConfig(
        agent_id="social_media_001",
        role=AgentRole.SOCIAL_MEDIA_MANAGER,
    )

    # Create manager
    manager = SocialMediaManagerAgent(config=config)

    # Register specialist agents
    manager.register_specialist(AgentRole.LINKEDIN_MANAGER, linkedin_agent)
    manager.register_specialist(AgentRole.TWITTER_MANAGER, twitter_agent)
    manager.register_specialist(AgentRole.BLUESKY_MANAGER, bluesky_agent)

    # Execute multi-platform task
    task = Task(
        task_id="post_001",
        task_type="create_post",
        parameters={
            "content": "Exciting AI updates!",
            "platforms": ["linkedin", "twitter", "bluesky"]
        }
    )

    result = await manager.execute(task)
"""

from datetime import datetime
from typing import Any, Callable, Coroutine

from agents.base.base_agent import BaseAgent
from agents.base.agent_config import AgentConfig
from agents.base.agent_protocol import AgentRole, Task, TaskPriority, TaskStatus
from core.exceptions import AgentExecutionError, wrap_exception


class SocialMediaManagerAgent(BaseAgent):
    """
    Management-layer agent for coordinating social media specialists.

    WHY: Orchestrates multi-platform campaigns and aggregates results.
    HOW: Delegates to specialist agents, coordinates execution, aggregates data.

    Attributes:
        _specialists: Dictionary mapping platform roles to specialist agents
        _task_handlers: Dictionary mapping task types to handler methods (Strategy Pattern)
    """

    # Platform role mapping for delegation
    # WHY: Maps platform names to AgentRole for specialist lookup
    _PLATFORM_TO_ROLE: dict[str, AgentRole] = {
        "linkedin": AgentRole.LINKEDIN_MANAGER,
        "twitter": AgentRole.TWITTER_MANAGER,
        "bluesky": AgentRole.BLUESKY_MANAGER,
    }

    def __init__(self, config: AgentConfig):
        """
        Initialize Social Media Manager Agent.

        WHY: Sets up management layer for specialist coordination.
        HOW: Initializes base agent, creates specialist registry, sets up task handlers.

        Args:
            config: Agent configuration
        """
        super().__init__(config)

        # Specialist agent registry
        # WHY: Store references to specialist agents for delegation
        self._specialists: dict[AgentRole, BaseAgent] = {}

        # Strategy Pattern: Dictionary dispatch for task routing
        # WHY: Eliminates if/elif chains, makes adding new tasks easier (Open/Closed Principle)
        # HOW: Map task types to handler methods
        self._task_handlers: dict[
            str, Callable[[Task], Coroutine[Any, Any, dict[str, Any]]]
        ] = {
            "create_post": self._create_post,
            "get_analytics": self._get_analytics,
            "schedule_post": self._schedule_post,
            "cross_post": self._cross_post,
        }

    @property
    def config(self) -> AgentConfig:
        """
        Get agent configuration.

        WHY: Provides access to agent configuration.
        HOW: Returns stored config.

        Returns:
            Agent configuration
        """
        return self._config

    def register_specialist(self, role: AgentRole, agent: BaseAgent) -> None:
        """
        Register a specialist agent for delegation.

        WHY: Management layer needs references to specialists it coordinates.
        HOW: Stores specialist in registry by role.

        Args:
            role: Specialist agent role (e.g., LINKEDIN_MANAGER)
            agent: Specialist agent instance
        """
        self._specialists[role] = agent

    def has_specialist(self, role: AgentRole) -> bool:
        """
        Check if specialist is registered.

        WHY: Validation before delegating tasks.
        HOW: Checks if role exists in specialist registry.

        Args:
            role: Specialist agent role to check

        Returns:
            True if specialist is registered, False otherwise
        """
        return role in self._specialists

    async def validate_task(self, task: Task) -> bool:
        """
        Validate whether agent can execute the given task.

        WHY: Pre-execution validation prevents task assignment errors.
        HOW: Uses guard clauses for validation, checks task type and parameters.

        Args:
            task: Task to validate

        Returns:
            True if agent can execute task, False otherwise
        """
        # Guard clause: Check if task type is supported
        if task.task_type not in self._task_handlers:
            return False

        # Validate task-specific parameters using dictionary dispatch
        # WHY: Cleaner than if/elif chain, easier to extend
        validators: dict[str, Callable[[dict[str, Any]], bool]] = {
            "create_post": self._validate_create_post_params,
            "get_analytics": lambda params: "platforms" in params,
            "schedule_post": self._validate_schedule_post_params,
            "cross_post": lambda params: "content" in params,
        }

        validator = validators.get(task.task_type)
        if validator is None:
            return True  # No specific validation required

        return validator(task.parameters)

    def _validate_create_post_params(self, params: dict[str, Any]) -> bool:
        """
        Validate create_post task parameters.

        WHY: Ensure required fields present for post creation.
        HOW: Checks for content and platforms.

        Args:
            params: Task parameters

        Returns:
            True if valid, False otherwise
        """
        required_fields = {"content", "platforms"}
        return all(field in params for field in required_fields)

    def _validate_schedule_post_params(self, params: dict[str, Any]) -> bool:
        """
        Validate schedule_post task parameters.

        WHY: Ensure required fields present for scheduling.
        HOW: Checks for content, platforms, and schedule_time.

        Args:
            params: Task parameters

        Returns:
            True if valid, False otherwise
        """
        required_fields = {"content", "platforms", "schedule_time"}
        return all(field in params for field in required_fields)

    async def _execute_task(self, task: Task) -> dict[str, Any]:
        """
        Execute social media management task using Strategy Pattern.

        WHY: Core agent functionality - coordinates specialist agents.
        HOW: Uses dictionary dispatch to route to appropriate handler (no if/elif).

        Args:
            task: Task to execute

        Returns:
            Dict with task execution result

        Raises:
            AgentExecutionError: If task execution fails
        """
        # Strategy Pattern: Look up handler in dictionary
        handler = self._task_handlers.get(task.task_type)

        # Guard clause: Unknown task type
        if handler is None:
            raise AgentExecutionError(
                f"Unsupported task type: {task.task_type}",
                context={"agent_id": self.agent_id, "task_id": task.task_id},
            )

        # Execute handler
        try:
            return await handler(task)
        except Exception as e:
            raise wrap_exception(
                exc=e,
                wrapper_class=AgentExecutionError,
                message=f"Social Media Manager failed to execute task: {task.task_type}",
                context={
                    "agent_id": self.agent_id,
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                },
            ) from e

    async def _create_post(self, task: Task) -> dict[str, Any]:
        """
        Create post on one or more platforms.

        WHY: Primary coordination function - distribute content across platforms.
        HOW: Delegates to specialist agents for each platform.

        Args:
            task: Task with post parameters

        Returns:
            Dict with results from all platforms

        Raises:
            AgentExecutionError: If post creation fails
        """
        content = task.parameters["content"]
        platforms = task.parameters["platforms"]
        optimize = task.parameters.get("optimize", False)

        results = []

        # Delegate to each platform specialist
        # WHY: Each platform has unique requirements (char limits, formatting)
        # HOW: Create specialist-specific task and execute
        for platform in platforms:
            # Guard clause: Skip if specialist not registered
            role = self._PLATFORM_TO_ROLE.get(platform)
            if role is None or not self.has_specialist(role):
                continue

            specialist = self._specialists[role]

            # Create platform-specific task
            specialist_task = self._create_specialist_task(
                original_task=task,
                specialist_role=role,
                task_type=(
                    "create_post"
                    if platform == "linkedin"
                    else "create_tweet" if platform == "twitter" else "create_post"
                ),
                parameters={
                    (
                        "content"
                        if platform == "linkedin"
                        else "text" if platform == "twitter" else "content"
                    ): content,
                    "optimize": optimize,
                },
            )

            # Execute specialist task (with error handling)
            try:
                result = await specialist.execute(specialist_task)

                # Guard clause: Only include successful results
                if result.status == TaskStatus.COMPLETED:
                    results.append(result.result)
            except Exception:
                # Guard clause: Specialist failed, continue with other platforms
                # WHY: Graceful degradation - one platform failure shouldn't stop others
                continue

        return {
            "results": results,
            "platforms_posted": len(results),
            "requested_platforms": len(platforms),
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_id,
        }

    async def _get_analytics(self, task: Task) -> dict[str, Any]:
        """
        Get aggregated analytics from all platforms.

        WHY: Unified view of social media performance across platforms.
        HOW: Delegates to specialist agents, aggregates results.

        Args:
            task: Task requesting analytics

        Returns:
            Dict with aggregated analytics

        Raises:
            AgentExecutionError: If analytics retrieval fails
        """
        platforms = task.parameters["platforms"]

        analytics = []
        total_followers = 0

        # Collect analytics from each platform
        for platform in platforms:
            # Guard clause: Skip if specialist not registered
            role = self._PLATFORM_TO_ROLE.get(platform)
            if role is None or not self.has_specialist(role):
                continue

            specialist = self._specialists[role]

            # Create analytics task
            specialist_task = self._create_specialist_task(
                original_task=task,
                specialist_role=role,
                task_type="get_analytics",
                parameters={},
            )

            # Execute specialist task (with error handling)
            try:
                result = await specialist.execute(specialist_task)

                # Guard clause: Only include successful results
                if result.status == TaskStatus.COMPLETED:
                    analytics.append(result.result)
                    # Aggregate follower counts
                    total_followers += result.result.get("followers_count", 0)
            except Exception:
                # Guard clause: Specialist failed, continue with other platforms
                # WHY: Graceful degradation - one platform failure shouldn't stop others
                continue

        return {
            "analytics": analytics,
            "total_followers": total_followers,
            "platforms_count": len(analytics),
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_id,
        }

    async def _schedule_post(self, task: Task) -> dict[str, Any]:
        """
        Schedule post across platforms.

        WHY: Timing optimization for maximum engagement.
        HOW: Stores schedule info, will delegate to specialists at scheduled time.

        Args:
            task: Task with scheduling parameters

        Returns:
            Dict with schedule confirmation

        Raises:
            AgentExecutionError: If scheduling fails
        """
        content = task.parameters["content"]
        platforms = task.parameters["platforms"]
        schedule_time = task.parameters["schedule_time"]

        # Note: Actual scheduling would integrate with scheduler infrastructure
        # For now, return schedule confirmation

        return {
            "scheduled": True,
            "content": content,
            "platforms": platforms,
            "schedule_time": schedule_time,
            "task_id": task.task_id,
            "agent": self.agent_id,
        }

    async def _cross_post(self, task: Task) -> dict[str, Any]:
        """
        Cross-post content to all registered platforms with optimization.

        WHY: Maximize reach by posting to all platforms simultaneously.
        HOW: Delegates to all registered specialists with platform-specific optimization.

        Args:
            task: Task with content to cross-post

        Returns:
            Dict with results from all platforms

        Raises:
            AgentExecutionError: If cross-posting fails
        """
        content = task.parameters["content"]

        # Get all registered platform specialists
        platforms = [
            platform
            for platform, role in self._PLATFORM_TO_ROLE.items()
            if self.has_specialist(role)
        ]

        # Delegate to create_post with all platforms
        modified_task = Task(
            task_id=task.task_id,
            task_type="create_post",
            priority=task.priority,
            parameters={
                "content": content,
                "platforms": platforms,
                "optimize": True,  # Always optimize for cross-posting
            },
            assigned_to=task.assigned_to,
            assigned_by=task.assigned_by,
            created_at=task.created_at,
        )

        return await self._create_post(modified_task)

    def _create_specialist_task(
        self,
        original_task: Task,
        specialist_role: AgentRole,
        task_type: str,
        parameters: dict[str, Any],
    ) -> Task:
        """
        Create task for specialist agent (helper method).

        WHY: Centralize task creation logic for consistency.
        HOW: Creates new Task with specialist-specific parameters.

        Args:
            original_task: Original task received by manager
            specialist_role: Role of specialist to execute task
            task_type: Task type for specialist
            parameters: Specialist-specific parameters

        Returns:
            Task configured for specialist
        """
        return Task(
            task_id=f"{original_task.task_id}_{specialist_role.value}",
            task_type=task_type,
            priority=original_task.priority,
            parameters=parameters,
            assigned_to=specialist_role,
            assigned_by=self.role,
            created_at=datetime.now(),
        )

    async def stop(self) -> None:
        """
        Gracefully stop the agent.

        WHY: Clean shutdown with resource cleanup.
        HOW: Stops all registered specialist agents.
        """
        # Stop all registered specialists
        for specialist in self._specialists.values():
            await specialist.stop()

        # Clear specialist registry
        self._specialists.clear()

        # Call parent stop
        await super().stop()
