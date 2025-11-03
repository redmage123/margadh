"""
Integration tests for VP Marketing Agent with management-layer teams.

WHY: Verify that VP Marketing correctly coordinates teams, manages approval workflows,
     and integrates with CMO for escalations.

HOW: Uses real agent instance with mocked management-layer agents (Content, Campaign,
     Social Media managers) and CMO to test full operational workflows including
     team coordination, campaign approval, and CMO escalation.

Following TDD methodology - these tests verify integrated behavior.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from agents.base.agent_protocol import AgentRole, Task, TaskPriority, TaskStatus
from agents.base.base_agent import AgentConfig
from agents.executive.vp_marketing import VPMarketingAgent


class TestVPMarketingIntegration:
    """Integration test suite for VP Marketing Agent."""

    @pytest.fixture
    def vp_config(self):
        """Create VP Marketing Agent configuration."""
        return AgentConfig(
            agent_id="vp_001",
            role=AgentRole.VP_MARKETING,
        )

    @pytest.fixture
    def mock_cmo_agent(self):
        """Create comprehensive mocked CMO agent."""
        cmo = AsyncMock()
        cmo.agent_id = "cmo_001"
        cmo.role = AgentRole.CMO
        cmo.delegate_decision = AsyncMock(
            return_value={"decision": "approved", "budget_adjustment": 2000}
        )
        return cmo

    @pytest.fixture
    def mock_content_manager(self):
        """Create comprehensive mocked Content Manager."""
        manager = AsyncMock()
        manager.agent_id = "content_001"
        manager.role = AgentRole.CONTENT_MANAGER
        manager.get_workload = AsyncMock(
            return_value={
                "current_projects": 5,
                "capacity": 8,
                "utilization": 0.625,
                "deadlines": ["2025-11-05", "2025-11-08"],
            }
        )
        manager.get_status = AsyncMock(
            return_value={
                "active_content": 5,
                "pending_reviews": 2,
                "published_this_week": 3,
            }
        )
        return manager

    @pytest.fixture
    def mock_campaign_manager(self):
        """Create comprehensive mocked Campaign Manager."""
        manager = AsyncMock()
        manager.agent_id = "campaign_001"
        manager.role = AgentRole.CAMPAIGN_MANAGER
        manager.get_workload = AsyncMock(
            return_value={
                "current_projects": 3,
                "capacity": 5,
                "utilization": 0.6,
                "deadlines": ["2025-11-07"],
            }
        )
        manager.get_status = AsyncMock(
            return_value={"active_campaigns": 3, "campaigns_this_month": 8}
        )
        return manager

    @pytest.fixture
    def mock_social_media_manager(self):
        """Create comprehensive mocked Social Media Manager."""
        manager = AsyncMock()
        manager.agent_id = "social_001"
        manager.role = AgentRole.SOCIAL_MEDIA_MANAGER
        manager.get_workload = AsyncMock(
            return_value={
                "current_projects": 7,
                "capacity": 10,
                "utilization": 0.7,
                "deadlines": ["2025-11-04", "2025-11-06"],
            }
        )
        manager.get_status = AsyncMock(
            return_value={
                "posts_this_week": 15,
                "engagement_rate": 0.052,
                "pending_posts": 5,
            }
        )
        return manager

    @pytest.mark.asyncio
    async def test_full_campaign_approval_workflow(
        self, vp_config, mock_campaign_manager
    ):
        """Test complete campaign approval workflow from submission to approval."""
        agent = VPMarketingAgent(config=vp_config)
        agent._campaign_manager = mock_campaign_manager

        # Campaign submission
        task = Task(
            task_id="integration_001",
            task_type="approve_campaign",
            priority=TaskPriority.HIGH,
            parameters={
                "campaign_id": "campaign_enterprise_001",
                "campaign_details": {
                    "name": "Enterprise Q4 Campaign",
                    "objective": "Generate 100 enterprise leads",
                    "channels": ["linkedin", "email", "content"],
                    "duration": "30_days",
                },
                "budget": 8000,  # Within VP approval authority
                "resources": ["email_specialist", "linkedin_manager", "copywriter"],
            },
            assigned_to=AgentRole.VP_MARKETING,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Verify approval workflow completed
        assert result.status == TaskStatus.COMPLETED
        assert "approval_status" in result.result
        assert result.result["approval_status"] in ["approved", "conditional"]
        assert "feedback" in result.result
        assert "approved_budget" in result.result or "conditions" in result.result

    @pytest.mark.asyncio
    async def test_cmo_escalation_workflow(self, vp_config, mock_cmo_agent):
        """Test escalation to CMO for high-budget campaign approval."""
        agent = VPMarketingAgent(config=vp_config)
        agent._cmo_agent = mock_cmo_agent

        # High-budget campaign requiring CMO approval
        task = Task(
            task_id="integration_002",
            task_type="approve_campaign",
            priority=TaskPriority.HIGH,
            parameters={
                "campaign_id": "campaign_major_001",
                "campaign_details": {
                    "name": "Major Product Launch",
                    "objective": "Launch new product",
                },
                "budget": 50000,  # Exceeds VP approval authority ($10K)
                "resources": ["all"],
            },
            assigned_to=AgentRole.VP_MARKETING,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Verify escalation occurred
        assert result.status == TaskStatus.COMPLETED
        assert "approval_status" in result.result
        # Should be escalated or include escalation info
        assert (
            result.result["approval_status"] == "escalated"
            or "escalation" in result.result
            or "cmo_approval_required" in result.result
        )

    @pytest.mark.asyncio
    async def test_team_coordination_workflow(
        self,
        vp_config,
        mock_content_manager,
        mock_campaign_manager,
        mock_social_media_manager,
    ):
        """Test coordinating activities across all management-layer teams."""
        agent = VPMarketingAgent(config=vp_config)
        agent._content_manager = mock_content_manager
        agent._campaign_manager = mock_campaign_manager
        agent._social_media_manager = mock_social_media_manager

        # Coordinate enterprise blog series across teams
        task = Task(
            task_id="integration_003",
            task_type="coordinate_teams",
            priority=TaskPriority.HIGH,
            parameters={
                "teams": ["content_manager", "campaign_manager", "social_media_manager"],
                "objectives": {
                    "goal": "Launch enterprise blog series with promotion",
                    "content": "5 blog posts on enterprise topics",
                    "campaign": "LinkedIn promotion campaign",
                    "social": "Social media amplification",
                },
                "deadline": datetime.now() + timedelta(days=14),
            },
            assigned_to=AgentRole.VP_MARKETING,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Verify coordination plan created
        assert result.status == TaskStatus.COMPLETED
        assert "coordination_plan" in result.result
        assert "team_assignments" in result.result
        assert len(result.result["team_assignments"]) == 3

    @pytest.mark.asyncio
    async def test_sprint_planning_workflow(
        self,
        vp_config,
        mock_content_manager,
        mock_campaign_manager,
        mock_social_media_manager,
    ):
        """Test sprint planning with resource allocation across teams."""
        agent = VPMarketingAgent(config=vp_config)
        agent._content_manager = mock_content_manager
        agent._campaign_manager = mock_campaign_manager
        agent._social_media_manager = mock_social_media_manager

        task = Task(
            task_id="integration_004",
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
                    "Launch 3 enterprise blog posts",
                    "Execute LinkedIn lead generation campaign",
                    "Increase social engagement 25%",
                    "Publish weekly newsletter",
                ],
            },
            assigned_to=AgentRole.VP_MARKETING,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Verify sprint plan created
        assert result.status == TaskStatus.COMPLETED
        assert "sprint_plan" in result.result
        assert "deliverables" in result.result
        assert "resource_allocation" in result.result
        assert isinstance(result.result["deliverables"], list)

    @pytest.mark.asyncio
    async def test_resource_conflict_resolution_workflow(
        self, vp_config, mock_content_manager, mock_campaign_manager
    ):
        """Test resolving resource conflicts between competing teams."""
        agent = VPMarketingAgent(config=vp_config)
        agent._content_manager = mock_content_manager
        agent._campaign_manager = mock_campaign_manager

        # Both teams need designer at same time
        task = Task(
            task_id="integration_005",
            task_type="resolve_conflicts",
            priority=TaskPriority.HIGH,
            parameters={
                "conflict_type": "resource_contention",
                "involved_agents": ["content_manager", "campaign_manager"],
                "context": {
                    "resource": "designer",
                    "content_request": {
                        "task": "blog header images",
                        "deadline": "2025-11-10",
                        "priority": "high",
                    },
                    "campaign_request": {
                        "task": "LinkedIn ad creatives",
                        "deadline": "2025-11-12",
                        "priority": "medium",
                    },
                },
            },
            assigned_to=AgentRole.VP_MARKETING,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Verify conflict resolved
        assert result.status == TaskStatus.COMPLETED
        assert "resolution" in result.result
        assert (
            "compromises" in result.result
            or "reassignments" in result.result
            or "allocation_schedule" in result.result
        )

    @pytest.mark.asyncio
    async def test_operational_monitoring_workflow(
        self,
        vp_config,
        mock_content_manager,
        mock_campaign_manager,
        mock_social_media_manager,
    ):
        """Test monitoring operational health across all teams."""
        agent = VPMarketingAgent(config=vp_config)
        agent._content_manager = mock_content_manager
        agent._campaign_manager = mock_campaign_manager
        agent._social_media_manager = mock_social_media_manager

        task = Task(
            task_id="integration_006",
            task_type="monitor_operations",
            priority=TaskPriority.NORMAL,
            parameters={
                "time_period": "last_24_hours",
                "teams": ["content_manager", "campaign_manager", "social_media_manager"],
                "metrics": ["workload", "productivity", "quality", "deadlines"],
            },
            assigned_to=AgentRole.VP_MARKETING,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Verify monitoring results
        assert result.status == TaskStatus.COMPLETED
        assert "operational_health" in result.result
        assert "team_performance" in result.result
        # Should include all three teams
        assert len(result.result["team_performance"]) == 3

    @pytest.mark.asyncio
    async def test_content_review_and_approval_workflow(self, vp_config):
        """Test content review workflow before publication."""
        agent = VPMarketingAgent(config=vp_config)

        # High-quality content for review
        task = Task(
            task_id="integration_007",
            task_type="review_content",
            priority=TaskPriority.NORMAL,
            parameters={
                "content_id": "blog_enterprise_ai",
                "content_type": "blog_post",
                "content_data": {
                    "title": "Top 5 AI Implementation Mistakes Enterprises Make",
                    "word_count": 1800,
                    "seo_score": 92,
                    "brand_voice_score": 95,
                    "readability": 85,
                    "author": "copywriter_001",
                },
            },
            assigned_to=AgentRole.VP_MARKETING,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Verify review completed
        assert result.status == TaskStatus.COMPLETED
        assert "review_status" in result.result
        assert "quality_score" in result.result
        assert "feedback" in result.result
        # High scores should result in approval
        assert result.result["review_status"] in ["approved", "conditional"]

    @pytest.mark.asyncio
    async def test_priority_assignment_workflow(
        self, vp_config, mock_content_manager, mock_campaign_manager
    ):
        """Test assigning tactical priorities based on CMO strategy."""
        agent = VPMarketingAgent(config=vp_config)
        agent._content_manager = mock_content_manager
        agent._campaign_manager = mock_campaign_manager

        # Assign priorities for Q4 enterprise focus
        task = Task(
            task_id="integration_008",
            task_type="assign_priorities",
            priority=TaskPriority.HIGH,
            parameters={
                "priorities": [
                    {
                        "task": "enterprise_blog_series",
                        "importance": 1,
                        "urgency": "high",
                        "team": "content_manager",
                    },
                    {
                        "task": "linkedin_enterprise_campaign",
                        "importance": 1,
                        "urgency": "high",
                        "team": "campaign_manager",
                    },
                    {
                        "task": "smb_social_campaign",
                        "importance": 2,
                        "urgency": "medium",
                        "team": "campaign_manager",
                    },
                    {
                        "task": "weekly_newsletter",
                        "importance": 3,
                        "urgency": "low",
                        "team": "content_manager",
                    },
                ],
                "team": "all",
                "timeframe": "sprint_45",
            },
            assigned_to=AgentRole.VP_MARKETING,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Verify priorities assigned
        assert result.status == TaskStatus.COMPLETED
        assert "priority_queue" in result.result
        assert isinstance(result.result["priority_queue"], list)
        # Highest priority items should be first
        assert len(result.result["priority_queue"]) >= 2

    @pytest.mark.asyncio
    async def test_status_reporting_workflow(
        self,
        vp_config,
        mock_content_manager,
        mock_campaign_manager,
        mock_social_media_manager,
    ):
        """Test generating operational status report for CMO."""
        agent = VPMarketingAgent(config=vp_config)
        agent._content_manager = mock_content_manager
        agent._campaign_manager = mock_campaign_manager
        agent._social_media_manager = mock_social_media_manager

        task = Task(
            task_id="integration_009",
            task_type="report_status",
            priority=TaskPriority.NORMAL,
            parameters={
                "report_type": "weekly_operational",
                "time_period": "last_7_days",
                "metrics": [
                    "campaigns_launched",
                    "content_published",
                    "team_utilization",
                    "approvals_processed",
                ],
            },
            assigned_to=AgentRole.VP_MARKETING,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Verify status report generated
        assert result.status == TaskStatus.COMPLETED
        assert "status_summary" in result.result
        assert "achievements" in result.result or "metrics" in result.result
        # Should include information about all teams

    @pytest.mark.asyncio
    async def test_resource_allocation_workflow(
        self, vp_config, mock_content_manager, mock_campaign_manager
    ):
        """Test allocating shared resources across multiple teams."""
        agent = VPMarketingAgent(config=vp_config)
        agent._content_manager = mock_content_manager
        agent._campaign_manager = mock_campaign_manager

        task = Task(
            task_id="integration_010",
            task_type="allocate_resources",
            priority=TaskPriority.HIGH,
            parameters={
                "resource_type": "copywriter",
                "requesting_teams": [
                    {
                        "team": "content_manager",
                        "urgency": "high",
                        "hours_needed": 12,
                        "task": "enterprise blog series",
                    },
                    {
                        "team": "campaign_manager",
                        "urgency": "medium",
                        "hours_needed": 6,
                        "task": "email campaign copy",
                    },
                ],
            },
            assigned_to=AgentRole.VP_MARKETING,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Verify resources allocated
        assert result.status == TaskStatus.COMPLETED
        assert "allocation_schedule" in result.result
        assert "priorities" in result.result
        # Should allocate to both teams

    @pytest.mark.asyncio
    async def test_team_performance_evaluation_workflow(
        self, vp_config, mock_content_manager
    ):
        """Test evaluating team performance for CMO review."""
        agent = VPMarketingAgent(config=vp_config)
        agent._content_manager = mock_content_manager

        task = Task(
            task_id="integration_011",
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

        # Verify performance evaluation completed
        assert result.status == TaskStatus.COMPLETED
        assert "performance_score" in result.result
        assert "strengths" in result.result or "improvements" in result.result

    @pytest.mark.asyncio
    async def test_agent_cleanup(self, vp_config):
        """Test that agent stops cleanly."""
        agent = VPMarketingAgent(config=vp_config)

        assert agent.is_available is True
        await agent.stop()
        assert agent.is_available is False
