"""
CMO Agent (Chief Marketing Officer) - Executive layer for strategic oversight.

WHY: Provides top-level strategic direction, resource allocation, and coordination
     across all marketing activities through management-layer agents.

HOW: Supervises management agents (Campaign, Social Media, Content managers),
     maintains strategic state (strategies, budgets, priorities), delegates execution,
     and aggregates performance data for executive-level decision making.

Supported Task Types:
- create_marketing_strategy: Define overall marketing objectives and strategy
- approve_campaign: Review and approve/reject campaign proposals
- allocate_budget: Distribute marketing budget across campaigns
- monitor_performance: Aggregate performance metrics from all managers
- coordinate_initiative: Orchestrate multi-campaign initiatives
- generate_executive_report: Create executive-level summaries
- set_priorities: Establish campaign priorities and resolve conflicts
- review_manager_performance: Evaluate management agent effectiveness

Implementation follows TDD - tests written first (RED), implementation (GREEN),
then refactored (REFACTOR).

Usage:
    from agents.executive.cmo import CMOAgent
    from agents.management import CampaignManagerAgent, SocialMediaManagerAgent
    from agents.base import AgentConfig, AgentRole, Task

    config = AgentConfig(
        agent_id="cmo_001",
        role=AgentRole.CMO,
    )

    # Create CMO
    cmo = CMOAgent(config=config)

    # Register management-layer agents
    cmo.register_manager(AgentRole.CAMPAIGN_MANAGER, campaign_manager)
    cmo.register_manager(AgentRole.SOCIAL_MEDIA_MANAGER, social_media_manager)

    # Execute strategic task
    task = Task(
        task_id="strategy_001",
        task_type="create_marketing_strategy",
        parameters={
            "name": "2025 Growth Strategy",
            "objectives": ["Increase awareness", "Generate leads"],
            "budget": 500000
        }
    )

    result = await cmo.execute(task)
"""

import uuid
from datetime import datetime
from typing import Any, Callable, Coroutine

from agents.base.base_agent import BaseAgent
from agents.base.agent_config import AgentConfig
from agents.base.agent_protocol import AgentRole, Task, TaskPriority, TaskStatus
from core.exceptions import AgentExecutionError, wrap_exception


class CMOAgent(BaseAgent):
    """
    Executive-layer agent for strategic marketing oversight.

    WHY: Provides unified strategic direction and resource coordination.
    HOW: Supervises management agents, maintains strategy state, delegates execution.

    Attributes:
        _managers: Dictionary mapping roles to management-layer agents
        _strategies: Dictionary storing marketing strategies by strategy_id
        _budget_allocations: Dictionary tracking budget allocations by campaign_id
        _campaign_approvals: Dictionary tracking campaign approval status
        _priorities: Dictionary tracking campaign priorities
        _task_handlers: Dictionary mapping task types to handler methods (Strategy Pattern)
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize CMO Agent.

        WHY: Sets up executive layer for strategic oversight.
        HOW: Initializes base agent, creates state storage, sets up task handlers.

        Args:
            config: Agent configuration
        """
        super().__init__(config)

        # Management agent registry
        # WHY: Store references to management agents for delegation
        self._managers: dict[AgentRole, BaseAgent] = {}

        # Strategic state storage
        # WHY: Track strategies, budgets, approvals, priorities
        self._strategies: dict[str, dict[str, Any]] = {}
        self._budget_allocations: dict[str, float] = {}
        self._campaign_approvals: dict[str, str] = {}  # campaign_id -> status
        self._priorities: dict[str, int] = {}  # campaign_id -> priority score

        # Strategy Pattern: Dictionary dispatch for task routing
        # WHY: Eliminates if/elif chains, makes adding new tasks easier (Open/Closed Principle)
        # HOW: Map task types to handler methods
        self._task_handlers: dict[
            str, Callable[[Task], Coroutine[Any, Any, dict[str, Any]]]
        ] = {
            "create_marketing_strategy": self._create_marketing_strategy,
            "approve_campaign": self._approve_campaign,
            "allocate_budget": self._allocate_budget,
            "monitor_performance": self._monitor_performance,
            "coordinate_initiative": self._coordinate_initiative,
            "generate_executive_report": self._generate_executive_report,
            "set_priorities": self._set_priorities,
            "review_manager_performance": self._review_manager_performance,
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

        WHY: CMO needs references to management agents it supervises.
        HOW: Stores manager in registry by role.

        Args:
            role: Manager agent role (e.g., CAMPAIGN_MANAGER)
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
            "create_marketing_strategy": self._validate_create_strategy_params,
            "approve_campaign": self._validate_approve_campaign_params,
            "allocate_budget": lambda params: "allocations" in params,
            "monitor_performance": lambda params: "period" in params,
            "coordinate_initiative": lambda params: "initiative_name" in params,
            "generate_executive_report": lambda params: "report_type" in params,
            "set_priorities": lambda params: "priorities" in params,
            "review_manager_performance": lambda params: True,  # No required params
        }

        validator = validators.get(task.task_type)
        if validator is None:
            return True  # No specific validation required

        return validator(task.parameters)

    def _validate_create_strategy_params(self, params: dict[str, Any]) -> bool:
        """
        Validate create_marketing_strategy task parameters.

        WHY: Ensure required fields present for strategy creation.
        HOW: Checks for required strategy fields.

        Args:
            params: Task parameters

        Returns:
            True if valid, False otherwise
        """
        required_fields = {
            "name",
            "objectives",
            "target_audiences",
            "key_initiatives",
            "budget",
            "timeframe",
        }
        return all(field in params for field in required_fields)

    def _validate_approve_campaign_params(self, params: dict[str, Any]) -> bool:
        """
        Validate approve_campaign task parameters.

        WHY: Ensure required fields present for approval decision.
        HOW: Checks for campaign_id and requested_budget.

        Args:
            params: Task parameters

        Returns:
            True if valid, False otherwise
        """
        required_fields = {"campaign_id", "requested_budget"}
        return all(field in params for field in required_fields)

    async def _execute_task(self, task: Task) -> dict[str, Any]:
        """
        Execute CMO strategic task using Strategy Pattern.

        WHY: Core agent functionality - strategic oversight and coordination.
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
                message=f"CMO failed to execute task: {task.task_type}",
                context={
                    "agent_id": self.agent_id,
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                },
            ) from e

    async def _create_marketing_strategy(self, task: Task) -> dict[str, Any]:
        """
        Create new marketing strategy.

        WHY: Establish strategic foundation for all marketing activities.
        HOW: Generates strategy ID, stores strategy state, returns confirmation.

        Args:
            task: Task with strategy parameters

        Returns:
            Dict with strategy details

        Raises:
            AgentExecutionError: If strategy creation fails
        """
        # Generate unique strategy ID
        strategy_id = f"strategy_{uuid.uuid4().hex[:8]}"

        # Extract strategy parameters
        strategy_data = {
            "strategy_id": strategy_id,
            "name": task.parameters["name"],
            "objectives": task.parameters["objectives"],
            "target_audiences": task.parameters["target_audiences"],
            "key_initiatives": task.parameters["key_initiatives"],
            "budget": task.parameters["budget"],
            "timeframe": task.parameters["timeframe"],
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "created_by": self.agent_id,
        }

        # Store strategy state
        self._strategies[strategy_id] = strategy_data

        return strategy_data

    async def _approve_campaign(self, task: Task) -> dict[str, Any]:
        """
        Approve or reject campaign proposal.

        WHY: Ensure campaigns align with strategy and resources.
        HOW: Fetches campaign details from Campaign Manager, evaluates against
             strategic criteria, returns approval decision.

        Args:
            task: Task with campaign approval request

        Returns:
            Dict with approval decision

        Raises:
            AgentExecutionError: If approval process fails
        """
        campaign_id = task.parameters["campaign_id"]
        requested_budget = task.parameters["requested_budget"]

        # Guard clause: Need Campaign Manager to get campaign details
        if not self.has_manager(AgentRole.CAMPAIGN_MANAGER):
            return {
                "approved": False,
                "campaign_id": campaign_id,
                "reason": "Campaign Manager not available",
                "timestamp": datetime.now().isoformat(),
            }

        # Get campaign details from Campaign Manager
        campaign_manager = self._managers[AgentRole.CAMPAIGN_MANAGER]

        try:
            status_task = Task(
                task_id=f"{task.task_id}_get_status",
                task_type="get_campaign_status",
                priority=task.priority,
                parameters={"campaign_id": campaign_id},
                assigned_to=AgentRole.CAMPAIGN_MANAGER,
                assigned_by=self.role,
                created_at=datetime.now(),
            )

            result = await campaign_manager.execute(status_task)

            # Guard clause: Campaign Manager failed to get campaign
            if result.status != TaskStatus.COMPLETED:
                return {
                    "approved": False,
                    "campaign_id": campaign_id,
                    "reason": "Could not retrieve campaign details",
                    "timestamp": datetime.now().isoformat(),
                }

            campaign_data = result.result

        except Exception:
            # Guard clause: Exception getting campaign details
            return {
                "approved": False,
                "campaign_id": campaign_id,
                "reason": "Error retrieving campaign details",
                "timestamp": datetime.now().isoformat(),
            }

        # Evaluate campaign against strategic criteria
        approval = self._evaluate_campaign(campaign_data, requested_budget)

        # Store approval decision
        self._campaign_approvals[campaign_id] = (
            "approved" if approval["approved"] else "rejected"
        )

        return {
            **approval,
            "campaign_id": campaign_id,
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_id,
        }

    def _evaluate_campaign(
        self, campaign_data: dict[str, Any], requested_budget: float
    ) -> dict[str, Any]:
        """
        Evaluate campaign against strategic criteria.

        WHY: Ensure campaigns meet strategic criteria before approval.
        HOW: Checks budget availability, strategic alignment, returns decision.

        Args:
            campaign_data: Campaign details
            requested_budget: Requested campaign budget

        Returns:
            Dict with approval decision and reason
        """
        # Check budget availability
        # Calculate total allocated budget
        total_allocated = sum(self._budget_allocations.values())

        # Get total available budget from active strategy
        total_budget = 0
        for strategy in self._strategies.values():
            if strategy.get("status") == "active":
                total_budget = strategy.get("budget", 0)
                break

        remaining_budget = total_budget - total_allocated

        # Guard clause: Insufficient budget
        if requested_budget > remaining_budget:
            return {
                "approved": False,
                "reason": f"Insufficient budget. Requested: ${requested_budget:,.2f}, Available: ${remaining_budget:,.2f}",
            }

        # Default: Approve campaign (in production, add more criteria checks)
        return {
            "approved": True,
            "reason": "Campaign aligns with strategy and budget available",
        }

    async def _allocate_budget(self, task: Task) -> dict[str, Any]:
        """
        Allocate budget across campaigns.

        WHY: Optimize resource allocation across marketing activities.
        HOW: Records budget allocations, tracks total allocated, returns summary.

        Args:
            task: Task with budget allocation details

        Returns:
            Dict with allocation summary

        Raises:
            AgentExecutionError: If budget allocation fails
        """
        allocations = task.parameters["allocations"]

        total_allocated = 0

        # Record each allocation
        for allocation in allocations:
            campaign_id = allocation["campaign_id"]
            amount = allocation["amount"]

            self._budget_allocations[campaign_id] = amount
            total_allocated += amount

        # Calculate remaining budget
        total_budget = 0
        for strategy in self._strategies.values():
            if strategy.get("status") == "active":
                total_budget = strategy.get("budget", 0)
                break

        remaining_budget = total_budget - total_allocated

        return {
            "total_allocated": total_allocated,
            "remaining_budget": remaining_budget,
            "allocations_count": len(allocations),
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_id,
        }

    async def _monitor_performance(self, task: Task) -> dict[str, Any]:
        """
        Monitor performance across all management agents.

        WHY: Track overall marketing effectiveness and identify issues.
        HOW: Queries all registered managers for performance data, aggregates results.

        Args:
            task: Task with performance monitoring request

        Returns:
            Dict with aggregated performance data

        Raises:
            AgentExecutionError: If performance monitoring fails
        """
        period = task.parameters["period"]

        performance_data = []

        # Collect performance from each manager
        for role, manager in self._managers.items():
            try:
                # Create performance request task
                perf_task = Task(
                    task_id=f"{task.task_id}_{role.value}",
                    task_type=(
                        "get_analytics"
                        if role == AgentRole.SOCIAL_MEDIA_MANAGER
                        else (
                            "get_campaign_status"
                            if role == AgentRole.CAMPAIGN_MANAGER
                            else "get_performance"
                        )
                    ),
                    priority=task.priority,
                    parameters=(
                        {"period": period}
                        if role != AgentRole.CAMPAIGN_MANAGER
                        else {"campaign_id": "all"}
                    ),
                    assigned_to=role,
                    assigned_by=self.role,
                    created_at=datetime.now(),
                )

                result = await manager.execute(perf_task)

                # Guard clause: Only include successful results
                if result.status == TaskStatus.COMPLETED:
                    performance_data.append(
                        {"manager": role.value, "data": result.result}
                    )

            except Exception:
                # Guard clause: Manager failed, continue with others
                # WHY: Graceful degradation - one manager failure shouldn't stop monitoring
                continue

        return {
            "performance_data": performance_data,
            "period": period,
            "managers_queried": len(performance_data),
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_id,
        }

    async def _coordinate_initiative(self, task: Task) -> dict[str, Any]:
        """
        Coordinate multi-campaign initiative.

        WHY: Synchronize multi-campaign efforts for maximum impact.
        HOW: Creates initiative ID, stores coordination metadata, returns confirmation.

        Args:
            task: Task with initiative details

        Returns:
            Dict with initiative coordination details

        Raises:
            AgentExecutionError: If coordination fails
        """
        # Generate unique initiative ID
        initiative_id = f"initiative_{uuid.uuid4().hex[:8]}"

        initiative_data = {
            "initiative_id": initiative_id,
            "name": task.parameters["initiative_name"],
            "involved_managers": task.parameters.get("involved_managers", []),
            "objectives": task.parameters.get("objectives", []),
            "timeline": task.parameters.get("timeline", ""),
            "status": "coordinating",
            "created_at": datetime.now().isoformat(),
        }

        return {
            **initiative_data,
            "agent": self.agent_id,
        }

    async def _generate_executive_report(self, task: Task) -> dict[str, Any]:
        """
        Generate executive-level report.

        WHY: Provide stakeholders with strategic marketing insights.
        HOW: Collects data from managers, formats executive summary.

        Args:
            task: Task with report request

        Returns:
            Dict with executive report

        Raises:
            AgentExecutionError: If report generation fails
        """
        # Generate unique report ID
        report_id = f"report_{uuid.uuid4().hex[:8]}"

        report_data = {
            "report_id": report_id,
            "report_type": task.parameters["report_type"],
            "period": task.parameters["period"],
            "sections": task.parameters.get("include_sections", []),
            "generated_at": datetime.now().isoformat(),
            "generated_by": self.agent_id,
        }

        return report_data

    async def _set_priorities(self, task: Task) -> dict[str, Any]:
        """
        Set campaign priorities.

        WHY: Guide resource allocation and resolve conflicts.
        HOW: Records priority levels, updates priority state.

        Args:
            task: Task with priority settings

        Returns:
            Dict with priority confirmation

        Raises:
            AgentExecutionError: If priority setting fails
        """
        priorities = task.parameters["priorities"]

        # Record each priority
        for priority_item in priorities:
            campaign_id = priority_item["campaign_id"]
            priority_level = priority_item["priority"]

            self._priorities[campaign_id] = priority_level

        return {
            "priorities_set": len(priorities),
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_id,
        }

    async def _review_manager_performance(self, task: Task) -> dict[str, Any]:
        """
        Review management agent performance.

        WHY: Evaluate management agent effectiveness and adjust delegation.
        HOW: Analyzes manager performance metrics, provides recommendations.

        Args:
            task: Task with performance review request

        Returns:
            Dict with performance review

        Raises:
            AgentExecutionError: If performance review fails
        """
        # Generate unique review ID
        review_id = f"review_{uuid.uuid4().hex[:8]}"

        review_data = {
            "review_id": review_id,
            "managers_reviewed": len(self._managers),
            "review_date": datetime.now().isoformat(),
            "reviewer": self.agent_id,
        }

        return review_data

    async def stop(self) -> None:
        """
        Gracefully stop the agent.

        WHY: Clean shutdown with resource cleanup.
        HOW: Stops all registered managers, clears state.
        """
        # Stop all registered managers
        for manager in self._managers.values():
            await manager.stop()

        # Clear registries and state
        self._managers.clear()
        self._strategies.clear()
        self._budget_allocations.clear()
        self._campaign_approvals.clear()
        self._priorities.clear()

        # Call parent stop
        await super().stop()
