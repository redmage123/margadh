"""
Campaign Manager Agent - Management layer for orchestrating marketing campaigns.

WHY: Coordinates multi-channel marketing campaigns across all management-layer agents.
     Provides unified campaign lifecycle management and performance tracking.

HOW: Manages campaign state, delegates to management agents (Social Media, Content, Email),
     aggregates campaign results and analytics.

Supported Task Types:
- create_campaign: Create new marketing campaign
- launch_campaign: Launch campaign and coordinate execution
- pause_campaign: Pause active campaign
- resume_campaign: Resume paused campaign
- get_campaign_status: Get current campaign status
- get_campaign_analytics: Get campaign performance analytics

Implementation follows TDD - tests written first (RED), implementation (GREEN),
then refactored (REFACTOR).

Usage:
    from agents.management.campaign_manager import CampaignManagerAgent
    from agents.management import SocialMediaManagerAgent
    from agents.base import AgentConfig, AgentRole, Task

    config = AgentConfig(
        agent_id="campaign_001",
        role=AgentRole.CAMPAIGN_MANAGER,
    )

    # Create manager
    manager = CampaignManagerAgent(config=config)

    # Register management-layer agents
    manager.register_manager(AgentRole.SOCIAL_MEDIA_MANAGER, social_media_agent)
    manager.register_manager(AgentRole.CONTENT_MANAGER, content_agent)

    # Create campaign
    task = Task(
        task_id="campaign_001",
        task_type="create_campaign",
        parameters={
            "name": "Q1 Product Launch",
            "objective": "brand_awareness",
            "channels": ["social_media", "email"],
            "start_date": "2025-01-15",
            "end_date": "2025-02-15"
        }
    )

    result = await manager.execute(task)
"""

import uuid
from datetime import datetime
from typing import Any, Callable, Coroutine

from agents.base.base_agent import BaseAgent
from agents.base.agent_config import AgentConfig
from agents.base.agent_protocol import AgentRole, Task, TaskPriority, TaskStatus
from core.exceptions import AgentExecutionError, wrap_exception


class CampaignManagerAgent(BaseAgent):
    """
    Management-layer agent for orchestrating marketing campaigns.

    WHY: Provides unified campaign management across all marketing channels.
    HOW: Coordinates management agents, tracks campaign state, aggregates results.

    Attributes:
        _managers: Dictionary mapping roles to management-layer agents
        _campaigns: Dictionary storing campaign state by campaign_id
        _task_handlers: Dictionary mapping task types to handler methods (Strategy Pattern)
    """

    # Channel to manager role mapping
    # WHY: Maps campaign channels to management agent roles
    _CHANNEL_TO_ROLE: dict[str, AgentRole] = {
        "social_media": AgentRole.SOCIAL_MEDIA_MANAGER,
        "content": AgentRole.CONTENT_MANAGER,
        "email": AgentRole.EMAIL_SPECIALIST,
        "analytics": AgentRole.ANALYTICS_SPECIALIST,
    }

    def __init__(self, config: AgentConfig):
        """
        Initialize Campaign Manager Agent.

        WHY: Sets up campaign orchestration layer.
        HOW: Initializes base agent, creates registries, sets up task handlers.

        Args:
            config: Agent configuration
        """
        super().__init__(config)

        # Management agent registry
        # WHY: Store references to management agents for delegation
        self._managers: dict[AgentRole, BaseAgent] = {}

        # Campaign state storage
        # WHY: Track campaign lifecycle and metadata
        self._campaigns: dict[str, dict[str, Any]] = {}

        # Strategy Pattern: Dictionary dispatch for task routing
        # WHY: Eliminates if/elif chains, makes adding new tasks easier (Open/Closed Principle)
        # HOW: Map task types to handler methods
        self._task_handlers: dict[
            str, Callable[[Task], Coroutine[Any, Any, dict[str, Any]]]
        ] = {
            "create_campaign": self._create_campaign,
            "launch_campaign": self._launch_campaign,
            "pause_campaign": self._pause_campaign,
            "resume_campaign": self._resume_campaign,
            "get_campaign_status": self._get_campaign_status,
            "get_campaign_analytics": self._get_campaign_analytics,
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

    def register_manager(self, role: AgentRole, agent: BaseAgent) -> None:
        """
        Register a management-layer agent for delegation.

        WHY: Campaign manager coordinates management agents.
        HOW: Stores manager in registry by role.

        Args:
            role: Manager agent role (e.g., SOCIAL_MEDIA_MANAGER)
            agent: Manager agent instance
        """
        self._managers[role] = agent

    def has_manager(self, role: AgentRole) -> bool:
        """
        Check if manager is registered.

        WHY: Validation before delegating tasks.
        HOW: Checks if role exists in manager registry.

        Args:
            role: Manager agent role to check

        Returns:
            True if manager is registered, False otherwise
        """
        return role in self._managers

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
            "create_campaign": self._validate_create_campaign_params,
            "launch_campaign": self._validate_launch_campaign_params,
            "pause_campaign": lambda params: "campaign_id" in params,
            "resume_campaign": lambda params: "campaign_id" in params,
            "get_campaign_status": lambda params: "campaign_id" in params,
            "get_campaign_analytics": lambda params: "campaign_id" in params,
        }

        validator = validators.get(task.task_type)
        if validator is None:
            return True  # No specific validation required

        return validator(task.parameters)

    def _validate_create_campaign_params(self, params: dict[str, Any]) -> bool:
        """
        Validate create_campaign task parameters.

        WHY: Ensure all required campaign fields present.
        HOW: Checks for required fields.

        Args:
            params: Task parameters

        Returns:
            True if valid, False otherwise
        """
        required_fields = {"name", "objective", "channels", "start_date", "end_date"}
        return all(field in params for field in required_fields)

    def _validate_launch_campaign_params(self, params: dict[str, Any]) -> bool:
        """
        Validate launch_campaign task parameters.

        WHY: Ensure campaign can be launched.
        HOW: Checks for required fields.

        Args:
            params: Task parameters

        Returns:
            True if valid, False otherwise
        """
        required_fields = {"campaign_id"}
        return all(field in params for field in required_fields)

    async def _execute_task(self, task: Task) -> dict[str, Any]:
        """
        Execute campaign management task using Strategy Pattern.

        WHY: Core agent functionality - manages campaign lifecycle.
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
                message=f"Campaign Manager failed to execute task: {task.task_type}",
                context={
                    "agent_id": self.agent_id,
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                },
            ) from e

    async def _create_campaign(self, task: Task) -> dict[str, Any]:
        """
        Create new marketing campaign.

        WHY: Initialize campaign with metadata and objectives.
        HOW: Generates campaign ID, stores campaign state.

        Args:
            task: Task with campaign parameters

        Returns:
            Dict with campaign ID and metadata

        Raises:
            AgentExecutionError: If campaign creation fails
        """
        # Generate unique campaign ID
        campaign_id = f"campaign_{uuid.uuid4().hex[:8]}"

        # Extract campaign parameters
        campaign_data = {
            "campaign_id": campaign_id,
            "name": task.parameters["name"],
            "objective": task.parameters["objective"],
            "channels": task.parameters["channels"],
            "start_date": task.parameters["start_date"],
            "end_date": task.parameters["end_date"],
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "created_by": task.assigned_by.value,
        }

        # Store campaign state
        self._campaigns[campaign_id] = campaign_data

        return campaign_data

    async def _launch_campaign(self, task: Task) -> dict[str, Any]:
        """
        Launch campaign and coordinate execution.

        WHY: Activate campaign and delegate to management agents.
        HOW: Updates campaign status, delegates to channel managers.

        Args:
            task: Task with launch parameters

        Returns:
            Dict with launch confirmation and results

        Raises:
            AgentExecutionError: If campaign launch fails
        """
        campaign_id = task.parameters["campaign_id"]

        # Guard clause: Campaign must exist
        if campaign_id not in self._campaigns:
            raise AgentExecutionError(
                f"Campaign not found: {campaign_id}",
                context={"campaign_id": campaign_id},
            )

        campaign = self._campaigns[campaign_id]
        content = task.parameters.get("content", "Campaign launch content")

        # Update campaign status
        campaign["status"] = "launched"
        campaign["launched_at"] = datetime.now().isoformat()

        # Delegate to channel managers
        results = []

        for channel in campaign["channels"]:
            # Guard clause: Skip if manager not registered
            role = self._CHANNEL_TO_ROLE.get(channel)
            if role is None or not self.has_manager(role):
                continue

            manager = self._managers[role]

            # Create channel-specific task
            channel_task = self._create_manager_task(
                original_task=task,
                manager_role=role,
                task_type=(
                    "create_post"
                    if channel == "social_media"
                    else "generate_content" if channel == "content" else "send_email"
                ),
                parameters={
                    "content": content,
                    "campaign_id": campaign_id,
                    "platforms": (
                        ["linkedin", "twitter", "bluesky"]
                        if channel == "social_media"
                        else None
                    ),
                },
            )

            # Execute manager task
            result = await manager.execute(channel_task)

            # Guard clause: Only include successful results
            if result.status == TaskStatus.COMPLETED:
                results.append({"channel": channel, "result": result.result})

        # Store launch results
        campaign["launch_results"] = results

        return {
            "campaign_id": campaign_id,
            "status": "launched",
            "channels_activated": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_id,
        }

    async def _pause_campaign(self, task: Task) -> dict[str, Any]:
        """
        Pause active campaign.

        WHY: Temporarily stop campaign execution.
        HOW: Updates campaign status to paused.

        Args:
            task: Task with campaign ID

        Returns:
            Dict with pause confirmation

        Raises:
            AgentExecutionError: If campaign pause fails
        """
        campaign_id = task.parameters["campaign_id"]

        # Guard clause: Campaign must exist
        if campaign_id not in self._campaigns:
            raise AgentExecutionError(
                f"Campaign not found: {campaign_id}",
                context={"campaign_id": campaign_id},
            )

        campaign = self._campaigns[campaign_id]

        # Update campaign status
        campaign["status"] = "paused"
        campaign["paused_at"] = datetime.now().isoformat()

        return {
            "campaign_id": campaign_id,
            "status": "paused",
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_id,
        }

    async def _resume_campaign(self, task: Task) -> dict[str, Any]:
        """
        Resume paused campaign.

        WHY: Restart campaign execution after pause.
        HOW: Updates campaign status to active.

        Args:
            task: Task with campaign ID

        Returns:
            Dict with resume confirmation

        Raises:
            AgentExecutionError: If campaign resume fails
        """
        campaign_id = task.parameters["campaign_id"]

        # Guard clause: Campaign must exist
        if campaign_id not in self._campaigns:
            raise AgentExecutionError(
                f"Campaign not found: {campaign_id}",
                context={"campaign_id": campaign_id},
            )

        campaign = self._campaigns[campaign_id]

        # Update campaign status
        campaign["status"] = "active"
        campaign["resumed_at"] = datetime.now().isoformat()

        return {
            "campaign_id": campaign_id,
            "status": "active",
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_id,
        }

    async def _get_campaign_status(self, task: Task) -> dict[str, Any]:
        """
        Get current campaign status.

        WHY: Monitor campaign state and progress.
        HOW: Returns campaign metadata and status.

        Args:
            task: Task with campaign ID

        Returns:
            Dict with campaign status

        Raises:
            AgentExecutionError: If status retrieval fails
        """
        campaign_id = task.parameters["campaign_id"]

        # Guard clause: Campaign must exist
        if campaign_id not in self._campaigns:
            raise AgentExecutionError(
                f"Campaign not found: {campaign_id}",
                context={"campaign_id": campaign_id},
            )

        campaign = self._campaigns[campaign_id]

        return {
            **campaign,
            "fetched_at": datetime.now().isoformat(),
            "agent": self.agent_id,
        }

    async def _get_campaign_analytics(self, task: Task) -> dict[str, Any]:
        """
        Get campaign performance analytics.

        WHY: Track campaign effectiveness and ROI.
        HOW: Aggregates analytics from all channel managers.

        Args:
            task: Task with campaign ID

        Returns:
            Dict with aggregated analytics

        Raises:
            AgentExecutionError: If analytics retrieval fails
        """
        campaign_id = task.parameters["campaign_id"]

        # Guard clause: Campaign must exist
        if campaign_id not in self._campaigns:
            raise AgentExecutionError(
                f"Campaign not found: {campaign_id}",
                context={"campaign_id": campaign_id},
            )

        campaign = self._campaigns[campaign_id]
        analytics = []

        # Collect analytics from each channel
        for channel in campaign["channels"]:
            # Guard clause: Skip if manager not registered
            role = self._CHANNEL_TO_ROLE.get(channel)
            if role is None or not self.has_manager(role):
                continue

            manager = self._managers[role]

            # Create analytics task
            analytics_task = self._create_manager_task(
                original_task=task,
                manager_role=role,
                task_type="get_analytics",
                parameters={
                    "campaign_id": campaign_id,
                    "platforms": (
                        ["linkedin", "twitter", "bluesky"]
                        if channel == "social_media"
                        else None
                    ),
                },
            )

            # Execute manager task
            result = await manager.execute(analytics_task)

            # Guard clause: Only include successful results
            if result.status == TaskStatus.COMPLETED:
                analytics.append({"channel": channel, "data": result.result})

        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign["name"],
            "analytics": analytics,
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_id,
        }

    def _create_manager_task(
        self,
        original_task: Task,
        manager_role: AgentRole,
        task_type: str,
        parameters: dict[str, Any],
    ) -> Task:
        """
        Create task for manager agent (helper method).

        WHY: Centralize task creation logic for consistency.
        HOW: Creates new Task with manager-specific parameters.

        Args:
            original_task: Original task received by campaign manager
            manager_role: Role of manager to execute task
            task_type: Task type for manager
            parameters: Manager-specific parameters

        Returns:
            Task configured for manager
        """
        # Filter out None values from parameters
        filtered_params = {k: v for k, v in parameters.items() if v is not None}

        return Task(
            task_id=f"{original_task.task_id}_{manager_role.value}",
            task_type=task_type,
            priority=original_task.priority,
            parameters=filtered_params,
            assigned_to=manager_role,
            assigned_by=self.role,
            created_at=datetime.now(),
        )

    async def stop(self) -> None:
        """
        Gracefully stop the agent.

        WHY: Clean shutdown with resource cleanup.
        HOW: Stops all registered managers, clears state.
        """
        # Stop all registered managers
        for manager in self._managers.values():
            await manager.stop()

        # Clear registries
        self._managers.clear()
        self._campaigns.clear()

        # Call parent stop
        await super().stop()
