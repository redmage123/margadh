"""
Unit tests for VP Marketing Agent.

WHY: Ensures VP Marketing Agent correctly coordinates teams, approves campaigns,
     manages operations, and escalates appropriately to CMO.

HOW: Uses mocked management-layer agents and CMO to test coordination,
     approval workflows, sprint planning, and operational oversight.

Following TDD methodology (RED-GREEN-REFACTOR):
- Write tests FIRST (these tests will fail initially)
- Implement agent to make tests pass
- Refactor while keeping tests green
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from agents.base.agent_protocol import AgentRole, Task, TaskPriority, TaskStatus
from agents.base.base_agent import AgentConfig


class TestVPMarketingAgent:
    """Test suite for VP Marketing Agent (Executive Layer)."""

    @pytest.fixture
    def agent_config(self):
        """Create VP Marketing agent configuration for testing."""
        return AgentConfig(
            agent_id="vp_001",
            role=AgentRole.VP_MARKETING,
        )

    @pytest.fixture
    def mock_cmo_agent(self):
        """Create mocked CMO agent."""
        cmo = AsyncMock()
        cmo.agent_id = "cmo_001"
        cmo.role = AgentRole.CMO
        return cmo

    @pytest.fixture
    def mock_content_manager(self):
        """Create mocked Content Manager agent."""
        manager = AsyncMock()
        manager.agent_id = "content_001"
        manager.role = AgentRole.CONTENT_MANAGER
        manager.get_workload = AsyncMock(
            return_value={"current_projects": 5, "capacity": 8, "utilization": 0.625}
        )
        return manager

    @pytest.fixture
    def mock_campaign_manager(self):
        """Create mocked Campaign Manager agent."""
        manager = AsyncMock()
        manager.agent_id = "campaign_001"
        manager.role = AgentRole.CAMPAIGN_MANAGER
        manager.get_workload = AsyncMock(
            return_value={"current_projects": 3, "capacity": 5, "utilization": 0.6}
        )
        return manager

    @pytest.fixture
    def mock_social_media_manager(self):
        """Create mocked Social Media Manager agent."""
        manager = AsyncMock()
        manager.agent_id = "social_001"
        manager.role = AgentRole.SOCIAL_MEDIA_MANAGER
        manager.get_workload = AsyncMock(
            return_value={"current_projects": 7, "capacity": 10, "utilization": 0.7}
        )
        return manager

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent_config):
        """Test that VP Marketing Agent initializes correctly."""
        from agents.executive.vp_marketing import VPMarketingAgent

        agent = VPMarketingAgent(config=agent_config)

        assert agent.agent_id == "vp_001"
        assert agent.role == AgentRole.VP_MARKETING
        assert agent.is_available is True

    @pytest.mark.asyncio
    async def test_coordinate_teams(
        self,
        agent_config,
        mock_content_manager,
        mock_campaign_manager,
        mock_social_media_manager,
    ):
        """Test coordinating activities across management-layer teams."""
        from agents.executive.vp_marketing import VPMarketingAgent

        agent = VPMarketingAgent(config=agent_config)
        agent._content_manager = mock_content_manager
        agent._campaign_manager = mock_campaign_manager
        agent._social_media_manager = mock_social_media_manager

        task = Task(
            task_id="task_001",
            task_type="coordinate_teams",
            priority=TaskPriority.HIGH,
            parameters={
                "teams": [
                    "content_manager",
                    "campaign_manager",
                    "social_media_manager",
                ],
                "objectives": {
                    "goal": "Launch enterprise blog series",
                    "deadline": "2025-11-15",
                },
                "deadline": datetime.now() + timedelta(days=14),
            },
            assigned_to=AgentRole.VP_MARKETING,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "coordination_plan" in result.result
        assert "team_assignments" in result.result
        assert "dependencies" in result.result

    @pytest.mark.asyncio
    async def test_approve_campaign_success(self, agent_config, mock_campaign_manager):
        """Test successful campaign approval."""
        from agents.executive.vp_marketing import VPMarketingAgent

        agent = VPMarketingAgent(config=agent_config)
        agent._campaign_manager = mock_campaign_manager

        task = Task(
            task_id="task_002",
            task_type="approve_campaign",
            priority=TaskPriority.HIGH,
            parameters={
                "campaign_id": "campaign_123",
                "campaign_details": {
                    "name": "Enterprise LinkedIn Campaign",
                    "objective": "Generate 50 enterprise leads",
                    "channels": ["linkedin", "email"],
                },
                "budget": 5000,
                "resources": ["email_specialist", "linkedin_manager", "copywriter"],
            },
            assigned_to=AgentRole.VP_MARKETING,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "approval_status" in result.result
        assert result.result["approval_status"] in [
            "approved",
            "rejected",
            "conditional",
        ]
        assert "feedback" in result.result

    @pytest.mark.asyncio
    async def test_approve_campaign_rejection(self, agent_config):
        """Test campaign rejection for budget overrun."""
        from agents.executive.vp_marketing import VPMarketingAgent

        agent = VPMarketingAgent(config=agent_config)

        task = Task(
            task_id="task_003",
            task_type="approve_campaign",
            priority=TaskPriority.NORMAL,
            parameters={
                "campaign_id": "campaign_456",
                "campaign_details": {
                    "name": "Expensive Campaign",
                    "objective": "Brand awareness",
                },
                "budget": 50000,  # Excessive budget
                "resources": ["all"],
            },
            assigned_to=AgentRole.VP_MARKETING,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        # Could be rejected or escalated to CMO
        assert "approval_status" in result.result
        assert "feedback" in result.result

    @pytest.mark.asyncio
    async def test_assign_priorities(
        self, agent_config, mock_content_manager, mock_campaign_manager
    ):
        """Test assigning tactical priorities to management teams."""
        from agents.executive.vp_marketing import VPMarketingAgent

        agent = VPMarketingAgent(config=agent_config)
        agent._content_manager = mock_content_manager
        agent._campaign_manager = mock_campaign_manager

        task = Task(
            task_id="task_004",
            task_type="assign_priorities",
            priority=TaskPriority.HIGH,
            parameters={
                "priorities": [
                    {"task": "enterprise_blog", "importance": 1, "urgency": "high"},
                    {"task": "social_campaign", "importance": 2, "urgency": "medium"},
                    {"task": "email_newsletter", "importance": 3, "urgency": "low"},
                ],
                "team": "content_manager",
                "timeframe": "sprint_44",
            },
            assigned_to=AgentRole.VP_MARKETING,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "priority_queue" in result.result
        assert "assignments" in result.result
        assert isinstance(result.result["priority_queue"], list)

    @pytest.mark.asyncio
    async def test_review_content_approval(self, agent_config):
        """Test content review and approval."""
        from agents.executive.vp_marketing import VPMarketingAgent

        agent = VPMarketingAgent(config=agent_config)

        task = Task(
            task_id="task_005",
            task_type="review_content",
            priority=TaskPriority.NORMAL,
            parameters={
                "content_id": "blog_789",
                "content_type": "blog_post",
                "content_data": {
                    "title": "Top 5 AI Implementation Mistakes",
                    "word_count": 1500,
                    "seo_score": 85,
                    "brand_voice_score": 90,
                },
            },
            assigned_to=AgentRole.VP_MARKETING,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "review_status" in result.result
        assert result.result["review_status"] in [
            "approved",
            "revision_needed",
            "rejected",
        ]
        assert "quality_score" in result.result
        assert "feedback" in result.result

    @pytest.mark.asyncio
    async def test_monitor_operations(
        self,
        agent_config,
        mock_content_manager,
        mock_campaign_manager,
        mock_social_media_manager,
    ):
        """Test monitoring daily operational metrics."""
        from agents.executive.vp_marketing import VPMarketingAgent

        agent = VPMarketingAgent(config=agent_config)
        agent._content_manager = mock_content_manager
        agent._campaign_manager = mock_campaign_manager
        agent._social_media_manager = mock_social_media_manager

        task = Task(
            task_id="task_006",
            task_type="monitor_operations",
            priority=TaskPriority.NORMAL,
            parameters={
                "time_period": "last_24_hours",
                "teams": [
                    "content_manager",
                    "campaign_manager",
                    "social_media_manager",
                ],
                "metrics": ["workload", "productivity", "quality", "deadlines"],
            },
            assigned_to=AgentRole.VP_MARKETING,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "operational_health" in result.result
        assert "team_performance" in result.result
        assert "alerts" in result.result or "recommendations" in result.result

    @pytest.mark.asyncio
    async def test_resolve_conflicts(
        self, agent_config, mock_content_manager, mock_campaign_manager
    ):
        """Test resolving resource conflicts between teams."""
        from agents.executive.vp_marketing import VPMarketingAgent

        agent = VPMarketingAgent(config=agent_config)
        agent._content_manager = mock_content_manager
        agent._campaign_manager = mock_campaign_manager

        task = Task(
            task_id="task_007",
            task_type="resolve_conflicts",
            priority=TaskPriority.HIGH,
            parameters={
                "conflict_type": "resource_contention",
                "involved_agents": ["content_manager", "campaign_manager"],
                "context": {
                    "resource": "designer",
                    "content_deadline": "2025-11-10",
                    "campaign_deadline": "2025-11-12",
                },
            },
            assigned_to=AgentRole.VP_MARKETING,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "resolution" in result.result
        assert "compromises" in result.result or "reassignments" in result.result

    @pytest.mark.asyncio
    async def test_plan_sprint(
        self,
        agent_config,
        mock_content_manager,
        mock_campaign_manager,
        mock_social_media_manager,
    ):
        """Test sprint planning for marketing teams."""
        from agents.executive.vp_marketing import VPMarketingAgent

        agent = VPMarketingAgent(config=agent_config)
        agent._content_manager = mock_content_manager
        agent._campaign_manager = mock_campaign_manager
        agent._social_media_manager = mock_social_media_manager

        task = Task(
            task_id="task_008",
            task_type="plan_sprint",
            priority=TaskPriority.HIGH,
            parameters={
                "sprint_duration": 14,  # days
                "team_capacity": {
                    "content_manager": 8,
                    "campaign_manager": 5,
                    "social_media_manager": 10,
                },
                "objectives": [
                    "Launch enterprise blog series",
                    "Execute LinkedIn campaign",
                    "Increase social engagement 20%",
                ],
            },
            assigned_to=AgentRole.VP_MARKETING,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "sprint_plan" in result.result
        assert "deliverables" in result.result
        assert "resource_allocation" in result.result

    @pytest.mark.asyncio
    async def test_report_status(
        self,
        agent_config,
        mock_content_manager,
        mock_campaign_manager,
        mock_social_media_manager,
    ):
        """Test generating operational status report for CMO."""
        from agents.executive.vp_marketing import VPMarketingAgent

        agent = VPMarketingAgent(config=agent_config)
        agent._content_manager = mock_content_manager
        agent._campaign_manager = mock_campaign_manager
        agent._social_media_manager = mock_social_media_manager

        task = Task(
            task_id="task_009",
            task_type="report_status",
            priority=TaskPriority.NORMAL,
            parameters={
                "report_type": "weekly_operational",
                "time_period": "last_7_days",
                "metrics": [
                    "campaigns_launched",
                    "content_published",
                    "team_utilization",
                    "budget_spent",
                ],
            },
            assigned_to=AgentRole.VP_MARKETING,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "status_summary" in result.result
        assert "achievements" in result.result
        assert "issues" in result.result or "escalations" in result.result

    @pytest.mark.asyncio
    async def test_allocate_resources(
        self, agent_config, mock_content_manager, mock_campaign_manager
    ):
        """Test allocating shared resources across teams."""
        from agents.executive.vp_marketing import VPMarketingAgent

        agent = VPMarketingAgent(config=agent_config)
        agent._content_manager = mock_content_manager
        agent._campaign_manager = mock_campaign_manager

        task = Task(
            task_id="task_010",
            task_type="allocate_resources",
            priority=TaskPriority.HIGH,
            parameters={
                "resource_type": "designer",
                "requesting_teams": [
                    {"team": "content_manager", "urgency": "high", "hours_needed": 8},
                    {
                        "team": "campaign_manager",
                        "urgency": "medium",
                        "hours_needed": 4,
                    },
                ],
            },
            assigned_to=AgentRole.VP_MARKETING,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "allocation_schedule" in result.result
        assert "priorities" in result.result

    @pytest.mark.asyncio
    async def test_evaluate_team_performance(self, agent_config, mock_content_manager):
        """Test evaluating team productivity and effectiveness."""
        from agents.executive.vp_marketing import VPMarketingAgent

        agent = VPMarketingAgent(config=agent_config)
        agent._content_manager = mock_content_manager

        task = Task(
            task_id="task_011",
            task_type="evaluate_team_performance",
            priority=TaskPriority.NORMAL,
            parameters={
                "team": "content_manager",
                "time_period": "last_30_days",
                "kpis": [
                    "content_output",
                    "quality_score",
                    "deadline_adherence",
                    "collaboration_score",
                ],
            },
            assigned_to=AgentRole.VP_MARKETING,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "performance_score" in result.result
        assert "strengths" in result.result
        assert "improvements" in result.result or "actions" in result.result

    @pytest.mark.asyncio
    async def test_validate_task_coordinate_teams(self, agent_config):
        """Test task validation for coordinate_teams task type."""
        from agents.executive.vp_marketing import VPMarketingAgent

        agent = VPMarketingAgent(config=agent_config)

        # Valid task
        valid_task = Task(
            task_id="task_012",
            task_type="coordinate_teams",
            priority=TaskPriority.NORMAL,
            parameters={
                "teams": ["content_manager"],
                "objectives": {"goal": "test"},
                "deadline": datetime.now(),
            },
            assigned_to=AgentRole.VP_MARKETING,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(valid_task)
        assert is_valid is True

        # Invalid task (missing required field)
        invalid_task = Task(
            task_id="task_013",
            task_type="coordinate_teams",
            priority=TaskPriority.NORMAL,
            parameters={},  # Missing required fields
            assigned_to=AgentRole.VP_MARKETING,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(invalid_task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_unsupported_task_type(self, agent_config):
        """Test that unsupported task types are rejected."""
        from agents.executive.vp_marketing import VPMarketingAgent

        agent = VPMarketingAgent(config=agent_config)

        task = Task(
            task_id="task_014",
            task_type="unsupported_task",
            priority=TaskPriority.NORMAL,
            parameters={},
            assigned_to=AgentRole.VP_MARKETING,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_escalation_to_cmo(self, agent_config, mock_cmo_agent):
        """Test escalation to CMO for strategic decisions."""
        from agents.executive.vp_marketing import VPMarketingAgent

        agent = VPMarketingAgent(config=agent_config)
        agent._cmo_agent = mock_cmo_agent

        # Campaign with excessive budget should trigger escalation
        task = Task(
            task_id="task_015",
            task_type="approve_campaign",
            priority=TaskPriority.HIGH,
            parameters={
                "campaign_id": "campaign_999",
                "campaign_details": {"name": "Major Campaign"},
                "budget": 100000,  # Exceeds VP approval authority
                "resources": ["all"],
            },
            assigned_to=AgentRole.VP_MARKETING,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        # Should indicate escalation
        assert "approval_status" in result.result
        # Could be "escalated" or include escalation info

    @pytest.mark.asyncio
    async def test_agent_stops_cleanly(self, agent_config):
        """Test that agent stops cleanly."""
        from agents.executive.vp_marketing import VPMarketingAgent

        agent = VPMarketingAgent(config=agent_config)

        # Should not raise exception
        await agent.stop()

        # Agent should no longer be available
        assert agent.is_available is False
