"""
Unit tests for Campaign Manager Agent.

WHY: Ensures Campaign Manager correctly orchestrates multi-channel campaigns.
HOW: Uses mocked management-layer agents to test coordination and campaign execution.

Following TDD methodology (RED-GREEN-REFACTOR):
- Write tests FIRST (these tests will fail initially)
- Implement agent to make tests pass
- Refactor while keeping tests green
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from agents.base.agent_protocol import AgentRole, Task, TaskPriority, TaskStatus
from agents.base.base_agent import AgentConfig


class TestCampaignManagerAgent:
    """Test suite for Campaign Manager Agent."""

    @pytest.fixture
    def agent_config(self):
        """Create agent configuration for testing."""
        return AgentConfig(
            agent_id="campaign_001",
            role=AgentRole.CAMPAIGN_MANAGER,
        )

    @pytest.fixture
    def mock_social_media_manager(self):
        """Create mocked Social Media Manager agent."""
        agent = AsyncMock()
        agent.agent_id = "social_media_001"
        agent.role = AgentRole.SOCIAL_MEDIA_MANAGER
        agent.is_available = True
        agent.validate_task = AsyncMock(return_value=True)
        agent.execute = AsyncMock(
            return_value=Mock(
                status=TaskStatus.COMPLETED,
                result={
                    "results": [
                        {"platform": "linkedin", "post_id": "post_123"},
                        {"platform": "twitter", "tweet_id": "tweet_123"},
                    ],
                    "platforms_posted": 2,
                },
            )
        )
        return agent

    @pytest.fixture
    def mock_content_manager(self):
        """Create mocked Content Manager agent."""
        agent = AsyncMock()
        agent.agent_id = "content_001"
        agent.role = AgentRole.CONTENT_MANAGER
        agent.is_available = True
        agent.validate_task = AsyncMock(return_value=True)
        agent.execute = AsyncMock(
            return_value=Mock(
                status=TaskStatus.COMPLETED,
                result={
                    "content": "Generated campaign content",
                    "content_type": "blog_post",
                },
            )
        )
        return agent

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent_config):
        """Test that Campaign Manager Agent initializes correctly."""
        from agents.management.campaign_manager import CampaignManagerAgent

        agent = CampaignManagerAgent(config=agent_config)

        assert agent.agent_id == "campaign_001"
        assert agent.role == AgentRole.CAMPAIGN_MANAGER
        assert agent.is_available is True

    @pytest.mark.asyncio
    async def test_register_manager_agents(
        self, agent_config, mock_social_media_manager, mock_content_manager
    ):
        """Test registering management-layer agents."""
        from agents.management.campaign_manager import CampaignManagerAgent

        agent = CampaignManagerAgent(config=agent_config)

        # Register manager agents
        agent.register_manager(
            AgentRole.SOCIAL_MEDIA_MANAGER, mock_social_media_manager
        )
        agent.register_manager(AgentRole.CONTENT_MANAGER, mock_content_manager)

        # Verify managers are registered
        assert agent.has_manager(AgentRole.SOCIAL_MEDIA_MANAGER) is True
        assert agent.has_manager(AgentRole.CONTENT_MANAGER) is True

    @pytest.mark.asyncio
    async def test_create_campaign(self, agent_config):
        """Test creating a new campaign."""
        from agents.management.campaign_manager import CampaignManagerAgent

        agent = CampaignManagerAgent(config=agent_config)

        task = Task(
            task_id="task_001",
            task_type="create_campaign",
            priority=TaskPriority.HIGH,
            parameters={
                "name": "Q1 Product Launch",
                "objective": "brand_awareness",
                "channels": ["social_media", "email"],
                "start_date": "2025-01-15",
                "end_date": "2025-02-15",
            },
            assigned_to=AgentRole.CAMPAIGN_MANAGER,
            assigned_by=AgentRole.VP_MARKETING,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "campaign_id" in result.result
        assert result.result["name"] == "Q1 Product Launch"
        assert result.result["status"] == "created"

    @pytest.mark.asyncio
    async def test_launch_campaign(
        self, agent_config, mock_social_media_manager, mock_content_manager
    ):
        """Test launching a campaign."""
        from agents.management.campaign_manager import CampaignManagerAgent

        agent = CampaignManagerAgent(config=agent_config)
        agent.register_manager(
            AgentRole.SOCIAL_MEDIA_MANAGER, mock_social_media_manager
        )
        agent.register_manager(AgentRole.CONTENT_MANAGER, mock_content_manager)

        # First create campaign
        create_task = Task(
            task_id="task_001",
            task_type="create_campaign",
            priority=TaskPriority.HIGH,
            parameters={
                "name": "Test Campaign",
                "objective": "lead_generation",
                "channels": ["social_media"],
                "start_date": "2025-01-15",
                "end_date": "2025-02-15",
            },
            assigned_to=AgentRole.CAMPAIGN_MANAGER,
            assigned_by=AgentRole.VP_MARKETING,
            created_at=datetime.now(),
        )

        create_result = await agent.execute(create_task)
        campaign_id = create_result.result["campaign_id"]

        # Now launch campaign
        launch_task = Task(
            task_id="task_002",
            task_type="launch_campaign",
            priority=TaskPriority.HIGH,
            parameters={
                "campaign_id": campaign_id,
                "content": "Campaign launch content",
            },
            assigned_to=AgentRole.CAMPAIGN_MANAGER,
            assigned_by=AgentRole.VP_MARKETING,
            created_at=datetime.now(),
        )

        result = await agent.execute(launch_task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert result.result["campaign_id"] == campaign_id
        assert result.result["status"] == "launched"

        # Verify social media manager was called
        mock_social_media_manager.execute.assert_called()

    @pytest.mark.asyncio
    async def test_get_campaign_status(self, agent_config):
        """Test getting campaign status."""
        from agents.management.campaign_manager import CampaignManagerAgent

        agent = CampaignManagerAgent(config=agent_config)

        # Create campaign first
        create_task = Task(
            task_id="task_001",
            task_type="create_campaign",
            priority=TaskPriority.HIGH,
            parameters={
                "name": "Status Test Campaign",
                "objective": "engagement",
                "channels": ["social_media"],
                "start_date": "2025-01-15",
                "end_date": "2025-02-15",
            },
            assigned_to=AgentRole.CAMPAIGN_MANAGER,
            assigned_by=AgentRole.VP_MARKETING,
            created_at=datetime.now(),
        )

        create_result = await agent.execute(create_task)
        campaign_id = create_result.result["campaign_id"]

        # Get campaign status
        status_task = Task(
            task_id="task_002",
            task_type="get_campaign_status",
            priority=TaskPriority.NORMAL,
            parameters={"campaign_id": campaign_id},
            assigned_to=AgentRole.CAMPAIGN_MANAGER,
            assigned_by=AgentRole.VP_MARKETING,
            created_at=datetime.now(),
        )

        result = await agent.execute(status_task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert result.result["campaign_id"] == campaign_id
        assert "status" in result.result
        assert "name" in result.result

    @pytest.mark.asyncio
    async def test_get_campaign_analytics(
        self, agent_config, mock_social_media_manager
    ):
        """Test getting campaign analytics."""
        from agents.management.campaign_manager import CampaignManagerAgent

        # Update mock to return analytics
        mock_social_media_manager.execute = AsyncMock(
            return_value=Mock(
                status=TaskStatus.COMPLETED,
                result={
                    "analytics": [
                        {
                            "platform": "linkedin",
                            "impressions": 5000,
                            "engagement": 250,
                        },
                        {
                            "platform": "twitter",
                            "impressions": 10000,
                            "engagement": 500,
                        },
                    ],
                    "total_followers": 15000,
                },
            )
        )

        agent = CampaignManagerAgent(config=agent_config)
        agent.register_manager(
            AgentRole.SOCIAL_MEDIA_MANAGER, mock_social_media_manager
        )

        # Create and launch campaign first
        create_task = Task(
            task_id="task_001",
            task_type="create_campaign",
            priority=TaskPriority.HIGH,
            parameters={
                "name": "Analytics Test Campaign",
                "objective": "engagement",
                "channels": ["social_media"],
                "start_date": "2025-01-15",
                "end_date": "2025-02-15",
            },
            assigned_to=AgentRole.CAMPAIGN_MANAGER,
            assigned_by=AgentRole.VP_MARKETING,
            created_at=datetime.now(),
        )

        create_result = await agent.execute(create_task)
        campaign_id = create_result.result["campaign_id"]

        # Get analytics
        analytics_task = Task(
            task_id="task_002",
            task_type="get_campaign_analytics",
            priority=TaskPriority.NORMAL,
            parameters={"campaign_id": campaign_id},
            assigned_to=AgentRole.CAMPAIGN_MANAGER,
            assigned_by=AgentRole.VP_MARKETING,
            created_at=datetime.now(),
        )

        result = await agent.execute(analytics_task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "campaign_id" in result.result
        assert "analytics" in result.result

    @pytest.mark.asyncio
    async def test_pause_campaign(self, agent_config):
        """Test pausing a campaign."""
        from agents.management.campaign_manager import CampaignManagerAgent

        agent = CampaignManagerAgent(config=agent_config)

        # Create campaign first
        create_task = Task(
            task_id="task_001",
            task_type="create_campaign",
            priority=TaskPriority.HIGH,
            parameters={
                "name": "Pause Test Campaign",
                "objective": "engagement",
                "channels": ["social_media"],
                "start_date": "2025-01-15",
                "end_date": "2025-02-15",
            },
            assigned_to=AgentRole.CAMPAIGN_MANAGER,
            assigned_by=AgentRole.VP_MARKETING,
            created_at=datetime.now(),
        )

        create_result = await agent.execute(create_task)
        campaign_id = create_result.result["campaign_id"]

        # Pause campaign
        pause_task = Task(
            task_id="task_002",
            task_type="pause_campaign",
            priority=TaskPriority.HIGH,
            parameters={"campaign_id": campaign_id},
            assigned_to=AgentRole.CAMPAIGN_MANAGER,
            assigned_by=AgentRole.VP_MARKETING,
            created_at=datetime.now(),
        )

        result = await agent.execute(pause_task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert result.result["campaign_id"] == campaign_id
        assert result.result["status"] == "paused"

    @pytest.mark.asyncio
    async def test_validate_task_create_campaign(self, agent_config):
        """Test task validation for create_campaign task type."""
        from agents.management.campaign_manager import CampaignManagerAgent

        agent = CampaignManagerAgent(config=agent_config)

        # Valid create_campaign task
        valid_task = Task(
            task_id="task_001",
            task_type="create_campaign",
            priority=TaskPriority.HIGH,
            parameters={
                "name": "Valid Campaign",
                "objective": "awareness",
                "channels": ["social_media"],
                "start_date": "2025-01-15",
                "end_date": "2025-02-15",
            },
            assigned_to=AgentRole.CAMPAIGN_MANAGER,
            assigned_by=AgentRole.VP_MARKETING,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(valid_task)
        assert is_valid is True

        # Invalid task (missing required fields)
        invalid_task = Task(
            task_id="task_002",
            task_type="create_campaign",
            priority=TaskPriority.HIGH,
            parameters={"name": "Invalid Campaign"},  # Missing required fields
            assigned_to=AgentRole.CAMPAIGN_MANAGER,
            assigned_by=AgentRole.VP_MARKETING,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(invalid_task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_unsupported_task_type(self, agent_config):
        """Test that unsupported task types are rejected."""
        from agents.management.campaign_manager import CampaignManagerAgent

        agent = CampaignManagerAgent(config=agent_config)

        task = Task(
            task_id="task_001",
            task_type="unsupported_task",
            priority=TaskPriority.NORMAL,
            parameters={},
            assigned_to=AgentRole.CAMPAIGN_MANAGER,
            assigned_by=AgentRole.VP_MARKETING,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_agent_stops_cleanly(self, agent_config):
        """Test that agent stops cleanly."""
        from agents.management.campaign_manager import CampaignManagerAgent

        agent = CampaignManagerAgent(config=agent_config)

        # Should not raise exception
        await agent.stop()

        # Agent should no longer be available
        assert agent.is_available is False
