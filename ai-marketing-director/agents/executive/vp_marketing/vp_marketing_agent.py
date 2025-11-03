"""
VP Marketing Agent - Executive-layer operational leadership and coordination.

WHY: Bridges CMO strategy and management-layer execution by coordinating teams,
     approving campaigns, managing resources, and overseeing daily operations.

HOW: Coordinates management teams (Content, Campaign, Social Media), approves
     campaigns within authority, monitors operational health, and escalates
     strategic decisions to CMO.

Responsibilities:
- Coordinate activities across management-layer teams
- Approve campaigns within budget authority ($10K)
- Assign priorities and manage workload
- Review content and deliverables
- Monitor operational metrics
- Resolve resource conflicts
- Plan sprints and allocate resources
- Report status to CMO
- Evaluate team performance

Escalation Path: CMO
Reports To: CMO
Manages: Content Manager, Campaign Manager, Social Media Manager
"""

from datetime import datetime
from typing import Any, Callable, Coroutine, Optional

from agents.base.agent_protocol import Task
from agents.base.base_agent import AgentConfig, BaseAgent
from core.exceptions import AgentExecutionError


class VPMarketingAgent(BaseAgent):
    """
    Executive-layer agent for marketing operations and team coordination.

    WHY: Bridges strategy (CMO) and execution (management layer) with
         day-to-day operational leadership and campaign approval.
    HOW: Coordinates management teams, approves campaigns, monitors operations,
         manages resources, and escalates strategic decisions to CMO.
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize VP Marketing Agent.

        WHY: Sets up operational management capabilities, team references,
             and approval workflows.
        HOW: Initializes task handlers, approval thresholds, and operational state.

        Args:
            config: Agent configuration
        """
        super().__init__(config)

        # Management team references (Optional[Any] for now)
        self._content_manager: Optional[Any] = None
        self._campaign_manager: Optional[Any] = None
        self._social_media_manager: Optional[Any] = None

        # CMO reference for escalation
        self._cmo_agent: Optional[Any] = None

        # Operational state
        self._pending_approvals: list[dict[str, Any]] = []
        self._team_workload: dict[str, dict[str, Any]] = {}
        self._active_sprints: list[dict[str, Any]] = []
        self._escalation_log: list[dict[str, Any]] = []

        # Approval thresholds
        self._max_campaign_budget: float = 10000.0  # VP can approve up to $10K
        self._max_approval_time: int = 6  # hours

        # Strategy Pattern: Task type -> handler method mapping
        self._task_handlers: dict[
            str, Callable[[Task], Coroutine[Any, Any, dict[str, Any]]]
        ] = {
            "coordinate_teams": self._coordinate_teams,
            "approve_campaign": self._approve_campaign,
            "assign_priorities": self._assign_priorities,
            "review_content": self._review_content,
            "monitor_operations": self._monitor_operations,
            "resolve_conflicts": self._resolve_conflicts,
            "plan_sprint": self._plan_sprint,
            "report_status": self._report_status,
            "allocate_resources": self._allocate_resources,
            "evaluate_team_performance": self._evaluate_team_performance,
        }

    # ========================================================================
    # Task Validation
    # ========================================================================

    async def validate_task(self, task: Task) -> bool:
        """
        Validate task can be executed by VP Marketing Agent.

        WHY: Ensures task type is supported and required parameters are present.
        HOW: Checks task type in handlers and validates required parameters.

        Args:
            task: Task to validate

        Returns:
            True if task is valid and can be executed, False otherwise
        """
        # Guard clause: Check if task type is supported
        if task.task_type not in self._task_handlers:
            return False

        # Guard clause: Validate required parameters for each task type
        required_params: dict[str, list[str]] = {
            "coordinate_teams": ["teams", "objectives", "deadline"],
            "approve_campaign": ["campaign_id", "campaign_details", "budget"],
            "assign_priorities": ["priorities", "team", "timeframe"],
            "review_content": ["content_id", "content_type", "content_data"],
            "monitor_operations": ["time_period", "teams", "metrics"],
            "resolve_conflicts": ["conflict_type", "involved_agents", "context"],
            "plan_sprint": ["sprint_duration", "team_capacity", "objectives"],
            "report_status": ["report_type", "time_period", "metrics"],
            "allocate_resources": ["resource_type", "requesting_teams"],
            "evaluate_team_performance": ["team", "time_period", "kpis"],
        }

        if task.task_type in required_params:
            for param in required_params[task.task_type]:
                if param not in task.parameters:
                    return False

        return True

    # ========================================================================
    # Task Execution (Strategy Pattern)
    # ========================================================================

    async def _execute_task(self, task: Task) -> dict[str, Any]:
        """
        Execute VP Marketing task using strategy pattern.

        WHY: Routes tasks to appropriate handlers based on task type.
        HOW: Looks up handler in dispatch table and delegates execution.

        Args:
            task: Task to execute

        Returns:
            Task execution result

        Raises:
            AgentExecutionError: If task type unsupported or execution fails
        """
        # Guard clause: Check if handler exists
        if task.task_type not in self._task_handlers:
            raise AgentExecutionError(
                message=f"Unsupported task type: {task.task_type}",
                context={
                    "agent_id": self.agent_id,
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                },
            )

        try:
            # Delegate to appropriate handler
            handler = self._task_handlers[task.task_type]
            return await handler(task)

        except AgentExecutionError:
            # Re-raise our own errors
            raise
        except Exception as e:
            # Wrap unexpected errors
            raise AgentExecutionError(
                message=f"Task execution failed: {task.task_type}",
                original_exception=e,
                context={
                    "agent_id": self.agent_id,
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                },
            ) from e

    # ========================================================================
    # Task Type Implementations
    # ========================================================================

    async def _coordinate_teams(self, task: Task) -> dict[str, Any]:
        """
        Coordinate activities across management-layer teams.

        WHY: Ensures teams work together effectively toward common goals.
        HOW: Creates coordination plan with assignments, dependencies, and timelines.

        Args:
            task: Coordination task with teams, objectives, and deadline

        Returns:
            dict with coordination_plan, team_assignments, dependencies
        """
        try:
            teams = task.parameters["teams"]
            objectives = task.parameters["objectives"]
            deadline = task.parameters["deadline"]

            # Create coordination plan
            coordination_plan = {
                "goal": objectives.get("goal", "Coordinate team activities"),
                "deadline": (
                    deadline.isoformat()
                    if isinstance(deadline, datetime)
                    else str(deadline)
                ),
                "teams_involved": teams,
                "coordination_strategy": "parallel_execution_with_checkpoints",
            }

            # Assign tasks to teams based on their roles
            team_assignments = {}
            dependencies = []

            for team in teams:
                if "content" in team.lower():
                    team_assignments[team] = {
                        "role": "Content creation and quality assurance",
                        "deliverables": ["blog_posts", "whitepapers", "case_studies"],
                        "priority": "high",
                    }
                    dependencies.append(
                        {
                            "team": team,
                            "blocks": ["social_media_manager"],
                            "reason": "Content needed before social promotion",
                        }
                    )
                elif "campaign" in team.lower():
                    team_assignments[team] = {
                        "role": "Campaign strategy and execution",
                        "deliverables": ["campaign_plan", "metrics_tracking"],
                        "priority": "high",
                    }
                elif "social" in team.lower():
                    team_assignments[team] = {
                        "role": "Social media distribution and engagement",
                        "deliverables": ["social_posts", "engagement_metrics"],
                        "priority": "medium",
                    }

            return {
                "coordination_plan": coordination_plan,
                "team_assignments": team_assignments,
                "dependencies": dependencies,
            }

        except KeyError as e:
            raise AgentExecutionError(
                message="Missing required parameter for team coordination",
                original_exception=e,
                context={
                    "agent_id": self.agent_id,
                    "task_id": task.task_id,
                    "missing_param": str(e),
                },
            ) from e

    async def _approve_campaign(self, task: Task) -> dict[str, Any]:
        """
        Approve or reject campaign based on budget authority and strategic fit.

        WHY: VP has limited budget authority; higher budgets escalate to CMO.
        HOW: Evaluates budget, strategy alignment, resources; approves or escalates.

        Args:
            task: Campaign approval request with budget and details

        Returns:
            dict with approval_status, feedback, conditions, approved_budget
        """
        try:
            campaign_id = task.parameters["campaign_id"]
            campaign_details = task.parameters["campaign_details"]
            budget = task.parameters["budget"]

            # Guard clause: Budget exceeds VP authority - escalate to CMO
            if budget > self._max_campaign_budget:
                self._escalation_log.append(
                    {
                        "campaign_id": campaign_id,
                        "budget": budget,
                        "reason": "Budget exceeds VP approval authority",
                        "escalated_at": datetime.now().isoformat(),
                    }
                )

                return {
                    "approval_status": "escalated",
                    "feedback": f"Campaign budget ${budget:,.2f} exceeds VP authority (${self._max_campaign_budget:,.2f}). Escalated to CMO for approval.",
                    "approved_budget": 0,
                    "escalation_reason": "budget_exceeded",
                }

            # Evaluate campaign strategic alignment
            has_clear_objective = "objective" in campaign_details
            has_channels = "channels" in campaign_details
            has_resources = "resources" in task.parameters

            # Guard clause: Missing critical information - reject
            if not has_clear_objective:
                return {
                    "approval_status": "rejected",
                    "feedback": "Campaign lacks clear objective. Please define measurable goals.",
                    "approved_budget": 0,
                }

            # Guard clause: Missing channels - request revision
            if not has_channels:
                return {
                    "approval_status": "conditional",
                    "feedback": "Approve campaign pending channel strategy definition.",
                    "conditions": [
                        "Define marketing channels and distribution strategy"
                    ],
                    "approved_budget": budget,
                }

            # Guard clause: Resource concerns - conditional approval
            if not has_resources or not task.parameters["resources"]:
                return {
                    "approval_status": "conditional",
                    "feedback": "Campaign approved with resource allocation plan required.",
                    "conditions": ["Submit detailed resource allocation plan"],
                    "approved_budget": budget,
                }

            # Approve campaign
            self._pending_approvals.append(
                {
                    "campaign_id": campaign_id,
                    "budget": budget,
                    "approved_at": datetime.now().isoformat(),
                    "approved_by": self.agent_id,
                }
            )

            return {
                "approval_status": "approved",
                "feedback": f"Campaign '{campaign_details.get('name', campaign_id)}' approved. Budget: ${budget:,.2f}. Proceed with execution.",
                "approved_budget": budget,
            }

        except KeyError as e:
            raise AgentExecutionError(
                message="Missing required parameter for campaign approval",
                original_exception=e,
                context={
                    "agent_id": self.agent_id,
                    "task_id": task.task_id,
                    "missing_param": str(e),
                },
            ) from e

    async def _assign_priorities(self, task: Task) -> dict[str, Any]:
        """
        Assign tactical priorities to management teams.

        WHY: Ensures teams focus on most important and urgent work first.
        HOW: Sorts priorities by importance/urgency and creates priority queue.

        Args:
            task: Priority assignment with priorities, team, and timeframe

        Returns:
            dict with priority_queue, assignments, deadlines
        """
        try:
            priorities = task.parameters["priorities"]
            team = task.parameters["team"]
            timeframe = task.parameters["timeframe"]

            # Sort priorities by importance (lower number = higher priority)
            # Then by urgency
            urgency_order = {"high": 1, "medium": 2, "low": 3}

            sorted_priorities = sorted(
                priorities,
                key=lambda p: (
                    p.get("importance", 999),
                    urgency_order.get(p.get("urgency", "low"), 3),
                ),
            )

            # Create priority queue
            priority_queue = []
            assignments = {}
            deadlines = {}

            for idx, priority in enumerate(sorted_priorities):
                task_name = priority.get("task", f"task_{idx}")
                priority_queue.append(
                    {
                        "position": idx + 1,
                        "task": task_name,
                        "importance": priority.get("importance", 0),
                        "urgency": priority.get("urgency", "medium"),
                    }
                )

                assignments[task_name] = {
                    "assigned_to": team,
                    "priority_level": idx + 1,
                    "timeframe": timeframe,
                }

                # Calculate deadline based on urgency
                deadline_days = {"high": 3, "medium": 7, "low": 14}
                days = deadline_days.get(priority.get("urgency", "medium"), 7)
                deadline_date = datetime.now()
                deadlines[task_name] = (
                    f"{timeframe}_day_{(idx + 1) * days}"  # Sprint-relative deadline
                )

            return {
                "priority_queue": priority_queue,
                "assignments": assignments,
                "deadlines": deadlines,
            }

        except KeyError as e:
            raise AgentExecutionError(
                message="Missing required parameter for priority assignment",
                original_exception=e,
                context={
                    "agent_id": self.agent_id,
                    "task_id": task.task_id,
                    "missing_param": str(e),
                },
            ) from e

    async def _review_content(self, task: Task) -> dict[str, Any]:
        """
        Review content for quality, brand alignment, and strategic fit.

        WHY: VP reviews high-value content before publication.
        HOW: Evaluates SEO, brand voice, and quality metrics.

        Args:
            task: Content review request with content_id, type, and data

        Returns:
            dict with review_status, quality_score, feedback
        """
        try:
            content_id = task.parameters["content_id"]
            content_type = task.parameters["content_type"]
            content_data = task.parameters["content_data"]

            # Extract quality metrics
            seo_score = content_data.get("seo_score", 0)
            brand_voice_score = content_data.get("brand_voice_score", 0)

            # Calculate overall quality score
            quality_score = (seo_score + brand_voice_score) / 2

            # Guard clause: High quality - approve
            if seo_score > 80 and brand_voice_score > 80:
                return {
                    "review_status": "approved",
                    "quality_score": quality_score,
                    "feedback": f"Content '{content_data.get('title', content_id)}' approved. Excellent SEO ({seo_score}) and brand alignment ({brand_voice_score}).",
                }

            # Guard clause: Low quality - reject
            if quality_score < 60:
                return {
                    "review_status": "rejected",
                    "quality_score": quality_score,
                    "feedback": f"Content quality below acceptable threshold. SEO: {seo_score}, Brand Voice: {brand_voice_score}. Major revision needed.",
                }

            # Needs revision
            feedback_items = []
            if seo_score < 80:
                feedback_items.append(
                    f"Improve SEO optimization (current: {seo_score})"
                )
            if brand_voice_score < 80:
                feedback_items.append(
                    f"Strengthen brand voice alignment (current: {brand_voice_score})"
                )

            return {
                "review_status": "revision_needed",
                "quality_score": quality_score,
                "feedback": f"Content requires revision: {'; '.join(feedback_items)}",
            }

        except KeyError as e:
            raise AgentExecutionError(
                message="Missing required parameter for content review",
                original_exception=e,
                context={
                    "agent_id": self.agent_id,
                    "task_id": task.task_id,
                    "missing_param": str(e),
                },
            ) from e

    async def _monitor_operations(self, task: Task) -> dict[str, Any]:
        """
        Monitor daily operational metrics across management teams.

        WHY: VP oversees operational health and identifies issues early.
        HOW: Gathers workload data, calculates health metrics, identifies alerts.

        Args:
            task: Monitoring request with time_period, teams, and metrics

        Returns:
            dict with operational_health, team_performance, alerts, recommendations
        """
        try:
            time_period = task.parameters["time_period"]
            teams = task.parameters["teams"]
            metrics = task.parameters["metrics"]

            # Gather team workload (from management agents if available)
            team_performance = {}
            total_utilization = 0
            team_count = 0

            for team in teams:
                # Try to get workload from actual management agent
                workload = await self._get_team_workload(team)

                if workload:
                    utilization = workload.get("utilization", 0)
                    team_performance[team] = {
                        "current_projects": workload.get("current_projects", 0),
                        "capacity": workload.get("capacity", 0),
                        "utilization": utilization,
                        "status": self._calculate_team_status(utilization),
                    }
                    total_utilization += utilization
                    team_count += 1
                else:
                    # Default data if agent not available
                    team_performance[team] = {
                        "current_projects": 0,
                        "capacity": 0,
                        "utilization": 0.0,
                        "status": "unknown",
                    }

            # Calculate operational health
            avg_utilization = total_utilization / team_count if team_count > 0 else 0.0
            operational_health = {
                "overall_status": self._calculate_operational_status(avg_utilization),
                "average_utilization": avg_utilization,
                "time_period": time_period,
                "teams_monitored": len(teams),
            }

            # Identify alerts
            alerts = []
            recommendations = []

            for team, perf in team_performance.items():
                utilization = perf["utilization"]

                # Alert: Overutilization
                if utilization > 0.9:
                    alerts.append(
                        {
                            "severity": "high",
                            "team": team,
                            "issue": "overutilization",
                            "utilization": utilization,
                        }
                    )
                    recommendations.append(
                        f"Reduce workload for {team} or add resources"
                    )

                # Alert: Underutilization
                if utilization < 0.3:
                    alerts.append(
                        {
                            "severity": "low",
                            "team": team,
                            "issue": "underutilization",
                            "utilization": utilization,
                        }
                    )
                    recommendations.append(f"Consider additional projects for {team}")

            return {
                "operational_health": operational_health,
                "team_performance": team_performance,
                "alerts": alerts,
                "recommendations": recommendations,
            }

        except KeyError as e:
            raise AgentExecutionError(
                message="Missing required parameter for operations monitoring",
                original_exception=e,
                context={
                    "agent_id": self.agent_id,
                    "task_id": task.task_id,
                    "missing_param": str(e),
                },
            ) from e

    async def _resolve_conflicts(self, task: Task) -> dict[str, Any]:
        """
        Resolve resource conflicts between teams.

        WHY: VP mediates disputes and makes resource allocation decisions.
        HOW: Analyzes conflict context, prioritizes based on deadlines/urgency.

        Args:
            task: Conflict resolution request with type, agents, and context

        Returns:
            dict with resolution, compromises, reassignments
        """
        try:
            conflict_type = task.parameters["conflict_type"]
            involved_agents = task.parameters["involved_agents"]
            context = task.parameters["context"]

            # Handle resource contention
            if conflict_type == "resource_contention":
                resource = context.get("resource", "unknown")

                # Compare deadlines to prioritize
                deadlines = {}
                for agent in involved_agents:
                    deadline_key = f"{agent}_deadline"
                    if deadline_key in context:
                        deadlines[agent] = context[deadline_key]

                # Sort by deadline (earliest first)
                sorted_agents = sorted(
                    deadlines.items(),
                    key=lambda x: (
                        datetime.fromisoformat(x[1]) if isinstance(x[1], str) else x[1]
                    ),
                )

                # Primary team gets priority, secondary team gets reassignment
                if sorted_agents:
                    priority_team = sorted_agents[0][0]
                    other_teams = [a for a in involved_agents if a != priority_team]

                    resolution = f"Resource '{resource}' allocated to {priority_team} due to earlier deadline."
                    reassignments = {}

                    for team in other_teams:
                        reassignments[team] = {
                            "alternative": f"{resource}_backup",
                            "delay": "2_days",
                        }

                    return {
                        "resolution": resolution,
                        "priority_allocation": {
                            "team": priority_team,
                            "resource": resource,
                        },
                        "reassignments": reassignments,
                        "compromises": [
                            f"{team} receives alternative resource"
                            for team in other_teams
                        ],
                    }

            # Default conflict resolution
            return {
                "resolution": f"Conflict of type '{conflict_type}' resolved through direct negotiation.",
                "compromises": [
                    f"All teams ({', '.join(involved_agents)}) agreed to share resources"
                ],
                "reassignments": {},
            }

        except KeyError as e:
            raise AgentExecutionError(
                message="Missing required parameter for conflict resolution",
                original_exception=e,
                context={
                    "agent_id": self.agent_id,
                    "task_id": task.task_id,
                    "missing_param": str(e),
                },
            ) from e

    async def _plan_sprint(self, task: Task) -> dict[str, Any]:
        """
        Plan sprint for marketing teams.

        WHY: VP coordinates sprint planning across management teams.
        HOW: Distributes objectives based on team capacity and creates sprint plan.

        Args:
            task: Sprint planning request with duration, capacity, objectives

        Returns:
            dict with sprint_plan, deliverables, resource_allocation
        """
        try:
            sprint_duration = task.parameters["sprint_duration"]
            team_capacity = task.parameters["team_capacity"]
            objectives = task.parameters["objectives"]

            # Create sprint plan
            sprint_plan = {
                "duration_days": sprint_duration,
                "start_date": datetime.now().isoformat(),
                "teams": list(team_capacity.keys()),
                "objectives_count": len(objectives),
            }

            # Distribute objectives across teams
            deliverables = []
            resource_allocation = {}

            for idx, objective in enumerate(objectives):
                # Assign to team with most capacity
                assigned_team = max(team_capacity.items(), key=lambda x: x[1])[0]

                deliverables.append(
                    {
                        "objective": objective,
                        "assigned_to": assigned_team,
                        "priority": idx + 1,
                        "estimated_effort": team_capacity[assigned_team]
                        // len(objectives),
                    }
                )

                # Track resource allocation
                if assigned_team not in resource_allocation:
                    resource_allocation[assigned_team] = {
                        "capacity": team_capacity[assigned_team],
                        "allocated": 0,
                        "objectives": [],
                    }

                allocation = team_capacity[assigned_team] // len(objectives)
                resource_allocation[assigned_team]["allocated"] += allocation
                resource_allocation[assigned_team]["objectives"].append(objective)

            # Store sprint for tracking
            self._active_sprints.append(
                {
                    "sprint_plan": sprint_plan,
                    "deliverables": deliverables,
                    "created_at": datetime.now().isoformat(),
                }
            )

            return {
                "sprint_plan": sprint_plan,
                "deliverables": deliverables,
                "resource_allocation": resource_allocation,
            }

        except KeyError as e:
            raise AgentExecutionError(
                message="Missing required parameter for sprint planning",
                original_exception=e,
                context={
                    "agent_id": self.agent_id,
                    "task_id": task.task_id,
                    "missing_param": str(e),
                },
            ) from e

    async def _report_status(self, task: Task) -> dict[str, Any]:
        """
        Generate operational status report for CMO.

        WHY: CMO needs regular updates on operational performance.
        HOW: Aggregates metrics, achievements, issues, and escalations.

        Args:
            task: Status report request with report_type, time_period, metrics

        Returns:
            dict with status_summary, achievements, issues, escalations
        """
        try:
            report_type = task.parameters["report_type"]
            time_period = task.parameters["time_period"]
            metrics = task.parameters["metrics"]

            # Create status summary
            status_summary = {
                "report_type": report_type,
                "time_period": time_period,
                "generated_at": datetime.now().isoformat(),
                "generated_by": self.agent_id,
            }

            # Track achievements
            achievements = []

            if "campaigns_launched" in metrics:
                campaigns_launched = len(
                    [a for a in self._pending_approvals if "approved" in a]
                )
                achievements.append(
                    f"{campaigns_launched} campaigns approved and launched"
                )

            if "content_published" in metrics:
                achievements.append("Content review process streamlined")

            if "team_utilization" in metrics:
                achievements.append("Team utilization optimized across all departments")

            # Track issues and escalations
            issues = []
            escalations = []

            if len(self._escalation_log) > 0:
                escalations = [
                    {
                        "campaign_id": esc.get("campaign_id"),
                        "reason": esc.get("reason"),
                        "budget": esc.get("budget"),
                    }
                    for esc in self._escalation_log
                ]
                issues.append(
                    f"{len(escalations)} campaigns require CMO approval due to budget"
                )

            if not achievements:
                achievements.append(
                    "Operational monitoring and team coordination ongoing"
                )

            if not issues:
                issues.append("No critical issues to report")

            return {
                "status_summary": status_summary,
                "achievements": achievements,
                "issues": issues,
                "escalations": escalations,
            }

        except KeyError as e:
            raise AgentExecutionError(
                message="Missing required parameter for status reporting",
                original_exception=e,
                context={
                    "agent_id": self.agent_id,
                    "task_id": task.task_id,
                    "missing_param": str(e),
                },
            ) from e

    async def _allocate_resources(self, task: Task) -> dict[str, Any]:
        """
        Allocate shared resources across teams.

        WHY: VP manages scarce resources to maximize team productivity.
        HOW: Prioritizes by urgency and creates allocation schedule.

        Args:
            task: Resource allocation request with resource_type and requesting teams

        Returns:
            dict with allocation_schedule, priorities, justification
        """
        try:
            resource_type = task.parameters["resource_type"]
            requesting_teams = task.parameters["requesting_teams"]

            # Sort teams by urgency and hours needed
            urgency_order = {"high": 1, "medium": 2, "low": 3}

            sorted_teams = sorted(
                requesting_teams,
                key=lambda t: (
                    urgency_order.get(t.get("urgency", "low"), 3),
                    -t.get("hours_needed", 0),
                ),
            )

            # Create allocation schedule
            allocation_schedule = []
            priorities = []
            current_day = 1

            for idx, team_request in enumerate(sorted_teams):
                team = team_request.get("team")
                hours = team_request.get("hours_needed", 0)
                urgency = team_request.get("urgency", "medium")

                allocation_schedule.append(
                    {
                        "team": team,
                        "resource": resource_type,
                        "hours_allocated": hours,
                        "start_day": current_day,
                        "priority": idx + 1,
                    }
                )

                priorities.append(
                    {"team": team, "priority_level": idx + 1, "urgency": urgency}
                )

                # Update day counter (assuming 8-hour workdays)
                current_day += (hours // 8) + (1 if hours % 8 > 0 else 0)

            justification = f"Resource '{resource_type}' allocated based on urgency and business impact. High-urgency teams receive priority access."

            return {
                "allocation_schedule": allocation_schedule,
                "priorities": priorities,
                "justification": justification,
            }

        except KeyError as e:
            raise AgentExecutionError(
                message="Missing required parameter for resource allocation",
                original_exception=e,
                context={
                    "agent_id": self.agent_id,
                    "task_id": task.task_id,
                    "missing_param": str(e),
                },
            ) from e

    async def _evaluate_team_performance(self, task: Task) -> dict[str, Any]:
        """
        Evaluate team productivity and effectiveness.

        WHY: VP assesses team performance to identify improvement opportunities.
        HOW: Analyzes KPIs, calculates performance score, identifies actions.

        Args:
            task: Performance evaluation request with team, time_period, kpis

        Returns:
            dict with performance_score, strengths, improvements, actions
        """
        try:
            team = task.parameters["team"]
            time_period = task.parameters["time_period"]
            kpis = task.parameters["kpis"]

            # Get team workload data
            workload = await self._get_team_workload(team)

            # Calculate performance score (0-100)
            performance_score = 75.0  # Default baseline

            if workload:
                utilization = workload.get("utilization", 0.5)

                # Optimal utilization is 0.7-0.8 (70-80%)
                if 0.7 <= utilization <= 0.8:
                    performance_score = 90.0
                elif 0.6 <= utilization < 0.7 or 0.8 < utilization <= 0.85:
                    performance_score = 80.0
                elif utilization < 0.5:
                    performance_score = 65.0  # Underutilized
                elif utilization > 0.9:
                    performance_score = 70.0  # Overutilized (risk of burnout)

            # Identify strengths
            strengths = []
            if "content_output" in kpis:
                strengths.append("Consistent content production")
            if "quality_score" in kpis:
                strengths.append("High quality standards maintained")
            if "collaboration_score" in kpis:
                strengths.append("Strong cross-team collaboration")

            # Identify improvement areas
            improvements = []
            actions = []

            if performance_score < 70:
                improvements.append("Productivity below target")
                actions.append("Review workload and resource allocation")

            if workload and workload.get("utilization", 0) > 0.9:
                improvements.append("Team overutilization risk")
                actions.append("Reduce workload or add team capacity")

            if "deadline_adherence" in kpis:
                improvements.append("Deadline adherence monitoring")
                actions.append("Implement better project tracking")

            if not improvements:
                improvements.append("Minor optimization opportunities exist")
                actions.append("Maintain current performance standards")

            if not strengths:
                strengths.append("Team operational and meeting basic expectations")

            return {
                "performance_score": performance_score,
                "strengths": strengths,
                "improvements": improvements,
                "actions": actions,
            }

        except KeyError as e:
            raise AgentExecutionError(
                message="Missing required parameter for performance evaluation",
                original_exception=e,
                context={
                    "agent_id": self.agent_id,
                    "task_id": task.task_id,
                    "missing_param": str(e),
                },
            ) from e

    # ========================================================================
    # Helper Methods
    # ========================================================================

    async def _get_team_workload(self, team: str) -> dict[str, Any] | None:
        """
        Get workload data from management agent.

        WHY: Needs current workload data to make informed decisions.
        HOW: Calls get_workload() method on management agent if available.

        Args:
            team: Team identifier

        Returns:
            Workload data dict or None if agent not available
        """
        try:
            if "content" in team.lower() and self._content_manager:
                if hasattr(self._content_manager, "get_workload"):
                    return await self._content_manager.get_workload()
            elif "campaign" in team.lower() and self._campaign_manager:
                if hasattr(self._campaign_manager, "get_workload"):
                    return await self._campaign_manager.get_workload()
            elif "social" in team.lower() and self._social_media_manager:
                if hasattr(self._social_media_manager, "get_workload"):
                    return await self._social_media_manager.get_workload()

            return None

        except Exception:
            # Gracefully handle agent communication errors
            return None

    def _calculate_team_status(self, utilization: float) -> str:
        """
        Calculate team status based on utilization.

        WHY: Provides human-readable status for operational dashboards.
        HOW: Maps utilization percentage to status categories.

        Args:
            utilization: Team utilization (0.0 - 1.0)

        Returns:
            Status string: optimal, busy, overloaded, underutilized
        """
        if utilization > 0.9:
            return "overloaded"
        if utilization > 0.8:
            return "busy"
        if utilization > 0.5:
            return "optimal"
        return "underutilized"

    def _calculate_operational_status(self, avg_utilization: float) -> str:
        """
        Calculate overall operational status.

        WHY: Provides high-level health indicator for CMO reporting.
        HOW: Maps average utilization to operational health categories.

        Args:
            avg_utilization: Average utilization across teams (0.0 - 1.0)

        Returns:
            Status string: healthy, attention_needed, critical
        """
        if 0.6 <= avg_utilization <= 0.85:
            return "healthy"
        if avg_utilization < 0.4 or avg_utilization > 0.95:
            return "critical"
        return "attention_needed"
