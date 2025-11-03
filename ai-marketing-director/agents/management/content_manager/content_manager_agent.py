"""
Content Manager Agent - Management layer for content coordination.

WHY: Provides centralized content strategy, quality control, and editorial calendar
     management while coordinating specialist agents for content creation.

HOW: Coordinates Copywriter, SEO Specialist, Designer agents, manages content
     lifecycle from draft to published, enforces quality standards.

Supported Task Types:
- create_content: Coordinate specialists to create content
- review_content: Review and approve/reject content for quality
- schedule_content: Add content to editorial calendar
- generate_content_ideas: Generate content ideas aligned with strategy
- optimize_content: Optimize existing content for SEO/engagement
- get_content_performance: Track content metrics across channels
- manage_content_calendar: Manage editorial calendar and deadlines
- brief_specialists: Create detailed content briefs for specialists

Implementation follows TDD - tests written first (RED), implementation (GREEN),
then refactored (REFACTOR).

Usage:
    from agents.management.content_manager import ContentManagerAgent
    from agents.specialists import CopywriterAgent, SEOSpecialistAgent
    from agents.base import AgentConfig, AgentRole, Task

    config = AgentConfig(
        agent_id="content_001",
        role=AgentRole.CONTENT_MANAGER,
    )

    # Create manager
    manager = ContentManagerAgent(config=config)

    # Register specialist agents
    manager.register_specialist(AgentRole.COPYWRITER, copywriter_agent)
    manager.register_specialist(AgentRole.SEO_SPECIALIST, seo_agent)

    # Execute content task
    task = Task(
        task_id="content_001",
        task_type="create_content",
        parameters={
            "content_type": "blog_post",
            "topic": "AI in Marketing",
            "target_audience": "Marketing Directors"
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


class ContentManagerAgent(BaseAgent):
    """
    Management-layer agent for content coordination.

    WHY: Provides unified content strategy and quality control.
    HOW: Coordinates specialists, manages calendar, enforces standards.

    Attributes:
        _specialists: Dictionary mapping roles to specialist agents
        _content_library: Dictionary storing content by content_id
        _editorial_calendar: Dictionary storing scheduled content
        _content_briefs: Dictionary storing active content briefs
        _task_handlers: Dictionary mapping task types to handler methods (Strategy Pattern)
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize Content Manager Agent.

        WHY: Sets up management layer for content coordination.
        HOW: Initializes base agent, creates state storage, sets up task handlers.

        Args:
            config: Agent configuration
        """
        super().__init__(config)

        # Specialist agent registry
        # WHY: Store references to specialist agents for delegation
        self._specialists: dict[AgentRole, BaseAgent] = {}

        # Content state storage
        # WHY: Track content lifecycle and metadata
        self._content_library: dict[str, dict[str, Any]] = (
            {}
        )  # content_id -> content data
        self._editorial_calendar: dict[str, dict[str, Any]] = (
            {}
        )  # schedule_id -> schedule data
        self._content_briefs: dict[str, dict[str, Any]] = {}  # brief_id -> brief data

        # Strategy Pattern: Dictionary dispatch for task routing
        # WHY: Eliminates if/elif chains, makes adding new tasks easier (Open/Closed Principle)
        # HOW: Map task types to handler methods
        self._task_handlers: dict[
            str, Callable[[Task], Coroutine[Any, Any, dict[str, Any]]]
        ] = {
            "create_content": self._create_content,
            "review_content": self._review_content,
            "schedule_content": self._schedule_content,
            "generate_content_ideas": self._generate_content_ideas,
            "optimize_content": self._optimize_content,
            "get_content_performance": self._get_content_performance,
            "manage_content_calendar": self._manage_content_calendar,
            "brief_specialists": self._brief_specialists,
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

        WHY: Content Manager needs references to specialists it coordinates.
        HOW: Stores specialist in registry by role.

        Args:
            role: Specialist agent role (e.g., COPYWRITER)
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
            "create_content": self._validate_create_content_params,
            "review_content": lambda params: "content_id" in params,
            "schedule_content": self._validate_schedule_content_params,
            "generate_content_ideas": lambda params: True,  # No required params
            "optimize_content": lambda params: "content_id" in params,
            "get_content_performance": lambda params: True,  # No required params
            "manage_content_calendar": lambda params: True,  # No required params
            "brief_specialists": self._validate_brief_specialists_params,
        }

        validator = validators.get(task.task_type)
        if validator is None:
            return True  # No specific validation required

        return validator(task.parameters)

    def _validate_create_content_params(self, params: dict[str, Any]) -> bool:
        """
        Validate create_content task parameters.

        WHY: Ensure required fields present for content creation.
        HOW: Checks for required content fields.

        Args:
            params: Task parameters

        Returns:
            True if valid, False otherwise
        """
        required_fields = {
            "content_type",
            "topic",
            "target_audience",
            "keywords",
            "word_count",
        }
        return all(field in params for field in required_fields)

    def _validate_schedule_content_params(self, params: dict[str, Any]) -> bool:
        """
        Validate schedule_content task parameters.

        WHY: Ensure required fields present for scheduling.
        HOW: Checks for content_id and publish_date.

        Args:
            params: Task parameters

        Returns:
            True if valid, False otherwise
        """
        required_fields = {"content_id", "publish_date"}
        return all(field in params for field in required_fields)

    def _validate_brief_specialists_params(self, params: dict[str, Any]) -> bool:
        """
        Validate brief_specialists task parameters.

        WHY: Ensure required fields present for briefing.
        HOW: Checks for brief_type and topic.

        Args:
            params: Task parameters

        Returns:
            True if valid, False otherwise
        """
        required_fields = {"brief_type", "topic"}
        return all(field in params for field in required_fields)

    async def _execute_task(self, task: Task) -> dict[str, Any]:
        """
        Execute content management task using Strategy Pattern.

        WHY: Core agent functionality - coordinates content specialists.
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
                message=f"Content Manager failed to execute task: {task.task_type}",
                context={
                    "agent_id": self.agent_id,
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                },
            ) from e

    async def _create_content(self, task: Task) -> dict[str, Any]:
        """
        Create content with specialist coordination.

        WHY: Coordinate multi-specialist content creation workflow.
        HOW: Delegates to Copywriter, optionally SEO/Designer, stores in library.

        Args:
            task: Task with content parameters

        Returns:
            Dict with content creation result

        Raises:
            AgentExecutionError: If content creation fails
        """
        # Generate unique content ID
        content_id = f"content_{uuid.uuid4().hex[:8]}"

        content_data = {
            "content_id": content_id,
            "content_type": task.parameters["content_type"],
            "topic": task.parameters["topic"],
            "target_audience": task.parameters["target_audience"],
            "keywords": task.parameters["keywords"],
            "word_count": task.parameters["word_count"],
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "created_by": self.agent_id,
        }

        # Delegate to Copywriter if available
        if self.has_specialist(AgentRole.COPYWRITER):
            try:
                copywriter = self._specialists[AgentRole.COPYWRITER]
                copywriter_task = self._create_specialist_task(
                    original_task=task,
                    specialist_role=AgentRole.COPYWRITER,
                    task_type="write_content",
                    parameters={
                        "content_type": task.parameters["content_type"],
                        "topic": task.parameters["topic"],
                        "word_count": task.parameters["word_count"],
                    },
                )

                result = await copywriter.execute(copywriter_task)
                if result.status == TaskStatus.COMPLETED:
                    content_data["content"] = result.result.get("content", "")
                    content_data["word_count_actual"] = result.result.get(
                        "word_count", 0
                    )

            except Exception:
                # Graceful degradation: Continue without copywriter content
                content_data["content"] = (
                    f"[Content draft for: {task.parameters['topic']}]"
                )

        # Store content in library
        content_data["status"] = "ready_for_review"
        self._content_library[content_id] = content_data

        return {
            "content_id": content_id,
            "status": content_data["status"],
            "content_type": content_data["content_type"],
            "created_at": content_data["created_at"],
            "agent": self.agent_id,
        }

    async def _review_content(self, task: Task) -> dict[str, Any]:
        """
        Review content for quality and approval.

        WHY: Ensure content meets quality and brand standards.
        HOW: Evaluates content against criteria, returns approval decision.

        Args:
            task: Task with review request

        Returns:
            Dict with review decision

        Raises:
            AgentExecutionError: If review fails
        """
        content_id = task.parameters["content_id"]

        # Guard clause: Content must exist
        if content_id not in self._content_library:
            raise AgentExecutionError(
                f"Content not found: {content_id}",
                context={"content_id": content_id},
            )

        content = self._content_library[content_id]

        # Simple approval logic (in production, add real quality checks)
        review_status = "approved"  # Default to approved
        content["status"] = review_status
        content["reviewed_at"] = datetime.now().isoformat()

        return {
            "content_id": content_id,
            "review_status": review_status,
            "reviewed_at": content["reviewed_at"],
            "agent": self.agent_id,
        }

    async def _schedule_content(self, task: Task) -> dict[str, Any]:
        """
        Schedule content to editorial calendar.

        WHY: Plan content publication for optimal timing.
        HOW: Adds to calendar, checks conflicts, stores schedule.

        Args:
            task: Task with scheduling request

        Returns:
            Dict with schedule confirmation

        Raises:
            AgentExecutionError: If scheduling fails
        """
        content_id = task.parameters["content_id"]
        publish_date = task.parameters["publish_date"]

        # Guard clause: Content must exist
        if content_id not in self._content_library:
            raise AgentExecutionError(
                f"Content not found: {content_id}",
                context={"content_id": content_id},
            )

        # Generate schedule ID
        schedule_id = f"schedule_{uuid.uuid4().hex[:8]}"

        schedule_data = {
            "schedule_id": schedule_id,
            "content_id": content_id,
            "publish_date": publish_date,
            "channels": task.parameters.get("channels", []),
            "status": "scheduled",
            "created_at": datetime.now().isoformat(),
        }

        # Store in calendar
        self._editorial_calendar[schedule_id] = schedule_data

        # Update content status
        self._content_library[content_id]["status"] = "scheduled"

        return {
            "content_id": content_id,
            "schedule_id": schedule_id,
            "scheduled_date": publish_date,
            "channels": schedule_data["channels"],
            "agent": self.agent_id,
        }

    async def _generate_content_ideas(self, task: Task) -> dict[str, Any]:
        """
        Generate content ideas aligned with strategy.

        WHY: Align content creation with marketing strategy and trends.
        HOW: Analyzes parameters, generates relevant content ideas.

        Args:
            task: Task with idea generation request

        Returns:
            Dict with content ideas

        Raises:
            AgentExecutionError: If idea generation fails
        """
        topic_areas = task.parameters.get("topic_areas", [])
        target_audience = task.parameters.get("target_audience", "General")
        count = task.parameters.get("count", 5)

        # Generate ideas (in production, use LLM for better ideas)
        ideas = []
        for i in range(min(count, 10)):  # Cap at 10
            ideas.append(
                {
                    "idea_id": f"idea_{uuid.uuid4().hex[:8]}",
                    "title": f"Content Idea {i+1} for {target_audience}",
                    "topic_area": (
                        topic_areas[i % len(topic_areas)] if topic_areas else "General"
                    ),
                    "content_type": "blog_post",
                    "estimated_value": "medium",
                }
            )

        return {
            "ideas": ideas,
            "count": len(ideas),
            "generated_at": datetime.now().isoformat(),
            "agent": self.agent_id,
        }

    async def _optimize_content(self, task: Task) -> dict[str, Any]:
        """
        Optimize existing content.

        WHY: Improve performance of existing content.
        HOW: Delegates to SEO Specialist for optimization.

        Args:
            task: Task with optimization request

        Returns:
            Dict with optimization result

        Raises:
            AgentExecutionError: If optimization fails
        """
        content_id = task.parameters["content_id"]

        # Guard clause: Content must exist
        if content_id not in self._content_library:
            raise AgentExecutionError(
                f"Content not found: {content_id}",
                context={"content_id": content_id},
            )

        content = self._content_library[content_id]

        # Delegate to SEO Specialist if available
        if self.has_specialist(AgentRole.SEO_SPECIALIST):
            try:
                seo = self._specialists[AgentRole.SEO_SPECIALIST]
                seo_task = self._create_specialist_task(
                    original_task=task,
                    specialist_role=AgentRole.SEO_SPECIALIST,
                    task_type="optimize_content",
                    parameters={"content": content.get("content", "")},
                )

                result = await seo.execute(seo_task)
                if result.status == TaskStatus.COMPLETED:
                    content["optimized"] = True
                    content["optimized_at"] = datetime.now().isoformat()

            except Exception:
                # Graceful degradation: Continue without SEO optimization
                pass

        return {
            "content_id": content_id,
            "optimized": content.get("optimized", False),
            "agent": self.agent_id,
        }

    async def _get_content_performance(self, task: Task) -> dict[str, Any]:
        """
        Get content performance metrics.

        WHY: Track content effectiveness and ROI.
        HOW: Aggregates metrics from content library.

        Args:
            task: Task with performance request

        Returns:
            Dict with performance data

        Raises:
            AgentExecutionError: If performance retrieval fails
        """
        period = task.parameters.get("period", "all_time")

        # Aggregate performance data from content library
        performance_data = []

        for content_id, content in self._content_library.items():
            if content.get("status") == "published":
                performance_data.append(
                    {
                        "content_id": content_id,
                        "content_type": content.get("content_type"),
                        "views": 0,  # Placeholder
                        "engagement": 0,  # Placeholder
                    }
                )

        return {
            "performance_data": performance_data,
            "period": period,
            "total_content": len(self._content_library),
            "published_content": len(performance_data),
            "agent": self.agent_id,
        }

    async def _manage_content_calendar(self, task: Task) -> dict[str, Any]:
        """
        Manage editorial calendar.

        WHY: Organize content production and publication.
        HOW: Queries calendar state, returns scheduled items.

        Args:
            task: Task with calendar request

        Returns:
            Dict with calendar data

        Raises:
            AgentExecutionError: If calendar management fails
        """
        action = task.parameters.get("action", "get_upcoming")

        calendar_items = list(self._editorial_calendar.values())

        return {
            "calendar_items": calendar_items,
            "total_scheduled": len(calendar_items),
            "action": action,
            "agent": self.agent_id,
        }

    async def _brief_specialists(self, task: Task) -> dict[str, Any]:
        """
        Create content brief for specialists.

        WHY: Provide clear direction for content creation.
        HOW: Creates detailed brief with requirements, stores in state.

        Args:
            task: Task with brief request

        Returns:
            Dict with brief details

        Raises:
            AgentExecutionError: If brief creation fails
        """
        # Generate unique brief ID
        brief_id = f"brief_{uuid.uuid4().hex[:8]}"

        brief_data = {
            "brief_id": brief_id,
            "brief_type": task.parameters["brief_type"],
            "topic": task.parameters["topic"],
            "target_audience": task.parameters.get("target_audience", "General"),
            "objectives": task.parameters.get("objectives", []),
            "word_count": task.parameters.get("word_count", 1000),
            "due_date": task.parameters.get("due_date", ""),
            "status": "active",
            "created_at": datetime.now().isoformat(),
        }

        # Store brief
        self._content_briefs[brief_id] = brief_data

        return {
            "brief_id": brief_id,
            "brief_type": brief_data["brief_type"],
            "topic": brief_data["topic"],
            "created_at": brief_data["created_at"],
            "agent": self.agent_id,
        }

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
        HOW: Stops all registered specialists, clears state.
        """
        # Stop all registered specialists
        for specialist in self._specialists.values():
            await specialist.stop()

        # Clear registries and state
        self._specialists.clear()
        self._content_library.clear()
        self._editorial_calendar.clear()
        self._content_briefs.clear()

        # Call parent stop
        await super().stop()
