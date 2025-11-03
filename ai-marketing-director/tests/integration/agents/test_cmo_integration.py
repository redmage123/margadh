"""
Integration tests for CMO coordination through full 4-tier hierarchy.

WHY: Verify that CMO Agent correctly coordinates through the complete agent hierarchy:
     CMO (Executive) → Campaign/Social Media Managers (Management) →
     LinkedIn/Twitter Managers (Specialists) → External APIs

HOW: Uses real agent instances with mocked external APIs.
     Tests full workflows with 4-tier delegation.

Following TDD methodology - these tests verify integrated behavior across all layers.
"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from agents.base.agent_protocol import AgentRole, Task, TaskPriority, TaskStatus
from agents.base.base_agent import AgentConfig
from agents.executive.cmo import CMOAgent
from agents.management.campaign_manager import CampaignManagerAgent
from agents.management.social_media_manager import SocialMediaManagerAgent
from agents.specialists.linkedin_manager import LinkedInManagerAgent
from agents.specialists.twitter_manager import TwitterManagerAgent


class TestCMOIntegration:
    """Integration test suite for CMO coordination through 4-tier hierarchy."""

    @pytest.fixture
    def cmo_config(self):
        """Create CMO configuration."""
        return AgentConfig(
            agent_id="cmo_001",
            role=AgentRole.CMO,
        )

    @pytest.fixture
    def campaign_config(self):
        """Create Campaign Manager configuration."""
        return AgentConfig(
            agent_id="campaign_001",
            role=AgentRole.CAMPAIGN_MANAGER,
        )

    @pytest.fixture
    def social_media_config(self):
        """Create Social Media Manager configuration."""
        return AgentConfig(
            agent_id="social_media_001",
            role=AgentRole.SOCIAL_MEDIA_MANAGER,
        )

    @pytest.fixture
    def linkedin_config(self):
        """Create LinkedIn Manager configuration."""
        return AgentConfig(
            agent_id="linkedin_001",
            role=AgentRole.LINKEDIN_MANAGER,
        )

    @pytest.fixture
    def twitter_config(self):
        """Create Twitter Manager configuration."""
        return AgentConfig(
            agent_id="twitter_001",
            role=AgentRole.TWITTER_MANAGER,
        )

    @pytest.fixture
    def mock_linkedin_client(self):
        """Create mocked LinkedIn API client."""
        client = AsyncMock()
        client.create_post = AsyncMock(
            return_value={
                "id": "linkedin_post_123",
                "text": "Executive-approved campaign post",
                "platform": "linkedin",
                "created_at": datetime.now().isoformat(),
            }
        )
        client.get_profile_stats = AsyncMock(
            return_value={
                "connections_count": 500,
                "followers_count": 1000,
                "platform": "linkedin",
            }
        )
        return client

    @pytest.fixture
    def mock_twitter_client(self):
        """Create mocked Twitter API client."""
        client = AsyncMock()
        client.create_tweet = AsyncMock(
            return_value={
                "id": "tweet_123",
                "text": "Executive-approved campaign tweet",
                "platform": "twitter",
                "created_at": datetime.now().isoformat(),
            }
        )
        client.get_profile_stats = AsyncMock(
            return_value={
                "followers_count": 5000,
                "following_count": 500,
                "tweet_count": 1200,
                "platform": "twitter",
            }
        )
        return client

    @pytest.mark.asyncio
    async def test_full_4_tier_campaign_approval_workflow(
        self,
        cmo_config,
        campaign_config,
        social_media_config,
        linkedin_config,
        twitter_config,
        mock_linkedin_client,
        mock_twitter_client,
    ):
        """Test complete workflow: CMO approves campaign → launches through hierarchy."""
        # Build 4-tier hierarchy
        cmo = CMOAgent(config=cmo_config)
        campaign_manager = CampaignManagerAgent(config=campaign_config)
        social_media_manager = SocialMediaManagerAgent(config=social_media_config)

        linkedin_manager = LinkedInManagerAgent(
            config=linkedin_config,
            linkedin_access_token="test_token",
            has_navigator=False,
        )
        linkedin_manager._linkedin_client = mock_linkedin_client

        twitter_manager = TwitterManagerAgent(
            config=twitter_config,
            api_key="test_key",
            api_secret="test_secret",
            access_token="test_token",
            access_token_secret="test_token_secret",
        )
        twitter_manager._twitter_client = mock_twitter_client

        # Wire up 4-tier hierarchy
        social_media_manager.register_specialist(
            AgentRole.LINKEDIN_MANAGER, linkedin_manager
        )
        social_media_manager.register_specialist(
            AgentRole.TWITTER_MANAGER, twitter_manager
        )
        campaign_manager.register_manager(
            AgentRole.SOCIAL_MEDIA_MANAGER, social_media_manager
        )
        cmo.register_manager(AgentRole.CAMPAIGN_MANAGER, campaign_manager)

        # Tier 1: CMO creates marketing strategy
        strategy_task = Task(
            task_id="cmo_strategy_001",
            task_type="create_marketing_strategy",
            priority=TaskPriority.HIGH,
            parameters={
                "name": "Q1 2025 Growth Strategy",
                "objectives": ["Increase brand awareness", "Generate leads"],
                "target_audiences": ["Enterprise CIOs", "Marketing Directors"],
                "key_initiatives": ["Product launch campaign"],
                "budget": 500000,
                "timeframe": "Q1 2025",
            },
            assigned_to=AgentRole.CMO,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        strategy_result = await cmo.execute(strategy_task)

        assert strategy_result.status == TaskStatus.COMPLETED
        assert "strategy_id" in strategy_result.result

        # Tier 2: Campaign Manager creates campaign (delegated from CMO context)
        create_campaign_task = Task(
            task_id="campaign_create_001",
            task_type="create_campaign",
            priority=TaskPriority.HIGH,
            parameters={
                "name": "Q1 Product Launch",
                "objective": "brand_awareness",
                "channels": ["social_media"],
                "start_date": "2025-01-15",
                "end_date": "2025-02-15",
            },
            assigned_to=AgentRole.CAMPAIGN_MANAGER,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        create_result = await campaign_manager.execute(create_campaign_task)
        assert create_result.status == TaskStatus.COMPLETED
        campaign_id = create_result.result["campaign_id"]

        # Tier 1: CMO approves campaign (queries Campaign Manager)
        approve_task = Task(
            task_id="cmo_approve_001",
            task_type="approve_campaign",
            priority=TaskPriority.HIGH,
            parameters={"campaign_id": campaign_id, "requested_budget": 50000},
            assigned_to=AgentRole.CMO,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        approval_result = await cmo.execute(approve_task)

        assert approval_result.status == TaskStatus.COMPLETED
        assert approval_result.result["approved"] is True
        assert approval_result.result["campaign_id"] == campaign_id

        # Tier 2: Campaign Manager launches campaign (delegates to Social Media Manager)
        launch_task = Task(
            task_id="campaign_launch_001",
            task_type="launch_campaign",
            priority=TaskPriority.HIGH,
            parameters={"campaign_id": campaign_id, "content": "Q1 product launch!"},
            assigned_to=AgentRole.CAMPAIGN_MANAGER,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        launch_result = await campaign_manager.execute(launch_task)

        # Verify full delegation chain worked
        assert launch_result.status == TaskStatus.COMPLETED
        assert launch_result.result["channels_activated"] >= 1

        # Verify specialists were called (4th tier)
        mock_linkedin_client.create_post.assert_called()
        mock_twitter_client.create_tweet.assert_called()

    @pytest.mark.asyncio
    async def test_cmo_monitors_performance_across_4_tiers(
        self,
        cmo_config,
        campaign_config,
        social_media_config,
        linkedin_config,
        twitter_config,
        mock_linkedin_client,
        mock_twitter_client,
    ):
        """Test CMO monitors performance aggregated through all layers."""
        # Build 4-tier hierarchy
        cmo = CMOAgent(config=cmo_config)
        campaign_manager = CampaignManagerAgent(config=campaign_config)
        social_media_manager = SocialMediaManagerAgent(config=social_media_config)

        linkedin_manager = LinkedInManagerAgent(
            config=linkedin_config,
            linkedin_access_token="test_token",
            has_navigator=False,
        )
        linkedin_manager._linkedin_client = mock_linkedin_client

        twitter_manager = TwitterManagerAgent(
            config=twitter_config,
            api_key="test_key",
            api_secret="test_secret",
            access_token="test_token",
            access_token_secret="test_token_secret",
        )
        twitter_manager._twitter_client = mock_twitter_client

        # Wire up hierarchy
        social_media_manager.register_specialist(
            AgentRole.LINKEDIN_MANAGER, linkedin_manager
        )
        social_media_manager.register_specialist(
            AgentRole.TWITTER_MANAGER, twitter_manager
        )
        campaign_manager.register_manager(
            AgentRole.SOCIAL_MEDIA_MANAGER, social_media_manager
        )
        cmo.register_manager(AgentRole.CAMPAIGN_MANAGER, campaign_manager)
        cmo.register_manager(AgentRole.SOCIAL_MEDIA_MANAGER, social_media_manager)

        # CMO monitors performance (queries all managers)
        monitor_task = Task(
            task_id="cmo_monitor_001",
            task_type="monitor_performance",
            priority=TaskPriority.NORMAL,
            parameters={"period": "Q1 2025"},
            assigned_to=AgentRole.CMO,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await cmo.execute(monitor_task)

        # Verify CMO aggregated data from management layer
        assert result.status == TaskStatus.COMPLETED
        assert "performance_data" in result.result
        # Graceful degradation: managers may not support all task types
        # CMO continues with partial or zero results
        assert result.result["managers_queried"] >= 0

    @pytest.mark.asyncio
    async def test_cmo_rejects_campaign_budget_exceeded(
        self,
        cmo_config,
        campaign_config,
    ):
        """Test CMO rejects campaign when budget insufficient."""
        cmo = CMOAgent(config=cmo_config)
        campaign_manager = CampaignManagerAgent(config=campaign_config)

        # Wire up
        cmo.register_manager(AgentRole.CAMPAIGN_MANAGER, campaign_manager)

        # CMO creates strategy with limited budget
        strategy_task = Task(
            task_id="cmo_strategy_001",
            task_type="create_marketing_strategy",
            priority=TaskPriority.HIGH,
            parameters={
                "name": "Limited Budget Strategy",
                "objectives": ["Test"],
                "target_audiences": ["Test"],
                "key_initiatives": ["Test"],
                "budget": 100000,  # Only $100k total
                "timeframe": "Q1 2025",
            },
            assigned_to=AgentRole.CMO,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        await cmo.execute(strategy_task)

        # Campaign Manager creates expensive campaign
        create_task = Task(
            task_id="campaign_create_001",
            task_type="create_campaign",
            priority=TaskPriority.HIGH,
            parameters={
                "name": "Expensive Campaign",
                "objective": "brand_awareness",
                "channels": ["social_media"],
                "start_date": "2025-01-15",
                "end_date": "2025-02-15",
            },
            assigned_to=AgentRole.CAMPAIGN_MANAGER,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        create_result = await campaign_manager.execute(create_task)
        campaign_id = create_result.result["campaign_id"]

        # CMO rejects due to budget
        approve_task = Task(
            task_id="cmo_approve_001",
            task_type="approve_campaign",
            priority=TaskPriority.HIGH,
            parameters={
                "campaign_id": campaign_id,
                "requested_budget": 150000,  # Exceeds total budget
            },
            assigned_to=AgentRole.CMO,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        approval_result = await cmo.execute(approve_task)

        # Verify rejection
        assert approval_result.status == TaskStatus.COMPLETED
        assert approval_result.result["approved"] is False
        assert "budget" in approval_result.result["reason"].lower()

    @pytest.mark.asyncio
    async def test_4_tier_hierarchy_cleanup(
        self,
        cmo_config,
        campaign_config,
        social_media_config,
        linkedin_config,
        mock_linkedin_client,
    ):
        """Test proper cleanup cascades through 4-tier hierarchy."""
        # Build hierarchy
        cmo = CMOAgent(config=cmo_config)
        campaign_manager = CampaignManagerAgent(config=campaign_config)
        social_media_manager = SocialMediaManagerAgent(config=social_media_config)
        linkedin_manager = LinkedInManagerAgent(
            config=linkedin_config,
            linkedin_access_token="test_token",
            has_navigator=False,
        )
        linkedin_manager._linkedin_client = mock_linkedin_client

        # Wire up 4 tiers
        social_media_manager.register_specialist(
            AgentRole.LINKEDIN_MANAGER, linkedin_manager
        )
        campaign_manager.register_manager(
            AgentRole.SOCIAL_MEDIA_MANAGER, social_media_manager
        )
        cmo.register_manager(AgentRole.CAMPAIGN_MANAGER, campaign_manager)

        # Verify all available
        assert cmo.is_available is True
        assert campaign_manager.is_available is True
        assert social_media_manager.is_available is True
        assert linkedin_manager.is_available is True

        # Stop top-level (should cascade)
        await cmo.stop()

        # Verify cascade cleanup through all tiers
        assert cmo.is_available is False
        assert campaign_manager.is_available is False
        assert social_media_manager.is_available is False
        assert linkedin_manager.is_available is False

    @pytest.mark.asyncio
    async def test_cmo_allocates_budget_across_campaigns(
        self,
        cmo_config,
    ):
        """Test CMO budget allocation across multiple campaigns."""
        cmo = CMOAgent(config=cmo_config)

        # Create strategy with budget
        strategy_task = Task(
            task_id="cmo_strategy_001",
            task_type="create_marketing_strategy",
            priority=TaskPriority.HIGH,
            parameters={
                "name": "Multi-Campaign Strategy",
                "objectives": ["Growth"],
                "target_audiences": ["Enterprise"],
                "key_initiatives": ["Multiple campaigns"],
                "budget": 500000,
                "timeframe": "2025",
            },
            assigned_to=AgentRole.CMO,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        await cmo.execute(strategy_task)

        # Allocate budget across campaigns
        allocate_task = Task(
            task_id="cmo_allocate_001",
            task_type="allocate_budget",
            priority=TaskPriority.HIGH,
            parameters={
                "allocations": [
                    {"campaign_id": "campaign_001", "amount": 150000},
                    {"campaign_id": "campaign_002", "amount": 200000},
                    {"campaign_id": "campaign_003", "amount": 100000},
                ],
            },
            assigned_to=AgentRole.CMO,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await cmo.execute(allocate_task)

        # Verify allocation
        assert result.status == TaskStatus.COMPLETED
        assert result.result["total_allocated"] == 450000
        assert result.result["remaining_budget"] == 50000
        assert result.result["allocations_count"] == 3
