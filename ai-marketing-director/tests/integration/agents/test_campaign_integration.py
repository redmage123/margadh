"""
Integration tests for Campaign Manager coordination.

WHY: Verify that Campaign Manager correctly orchestrates multi-channel campaigns
     through management and specialist agents.

HOW: Uses real agent instances with mocked external APIs.
     Tests full campaign lifecycle with multi-layer delegation.

Following TDD methodology - these tests verify integrated behavior.
"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from agents.base.agent_protocol import AgentRole, Task, TaskPriority, TaskStatus
from agents.base.base_agent import AgentConfig
from agents.management.campaign_manager import CampaignManagerAgent
from agents.management.social_media_manager import SocialMediaManagerAgent
from agents.specialists.linkedin_manager import LinkedInManagerAgent
from agents.specialists.twitter_manager import TwitterManagerAgent


class TestCampaignIntegration:
    """Integration test suite for Campaign coordination."""

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
                "text": "Campaign post",
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
                "text": "Campaign tweet",
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
    async def test_full_campaign_lifecycle(
        self,
        campaign_config,
        social_media_config,
        linkedin_config,
        twitter_config,
        mock_linkedin_client,
        mock_twitter_client,
    ):
        """Test complete campaign lifecycle: create → launch → get status."""
        # Build agent hierarchy
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

        # Step 1: Create campaign
        create_task = Task(
            task_id="campaign_create_001",
            task_type="create_campaign",
            priority=TaskPriority.HIGH,
            parameters={
                "name": "Q1 Integration Test Campaign",
                "objective": "brand_awareness",
                "channels": ["social_media"],
                "start_date": "2025-01-15",
                "end_date": "2025-02-15",
            },
            assigned_to=AgentRole.CAMPAIGN_MANAGER,
            assigned_by=AgentRole.VP_MARKETING,
            created_at=datetime.now(),
        )

        create_result = await campaign_manager.execute(create_task)

        assert create_result.status == TaskStatus.COMPLETED
        assert "campaign_id" in create_result.result
        campaign_id = create_result.result["campaign_id"]

        # Step 2: Launch campaign
        launch_task = Task(
            task_id="campaign_launch_001",
            task_type="launch_campaign",
            priority=TaskPriority.HIGH,
            parameters={
                "campaign_id": campaign_id,
                "content": "Exciting Q1 campaign launch!",
            },
            assigned_to=AgentRole.CAMPAIGN_MANAGER,
            assigned_by=AgentRole.VP_MARKETING,
            created_at=datetime.now(),
        )

        launch_result = await campaign_manager.execute(launch_task)

        assert launch_result.status == TaskStatus.COMPLETED
        assert launch_result.result["campaign_id"] == campaign_id
        assert launch_result.result["status"] == "launched"
        assert launch_result.result["channels_activated"] >= 1

        # Verify delegation occurred
        mock_linkedin_client.create_post.assert_called()
        mock_twitter_client.create_tweet.assert_called()

        # Step 3: Get campaign status
        status_task = Task(
            task_id="campaign_status_001",
            task_type="get_campaign_status",
            priority=TaskPriority.NORMAL,
            parameters={"campaign_id": campaign_id},
            assigned_to=AgentRole.CAMPAIGN_MANAGER,
            assigned_by=AgentRole.VP_MARKETING,
            created_at=datetime.now(),
        )

        status_result = await campaign_manager.execute(status_task)

        assert status_result.status == TaskStatus.COMPLETED
        assert status_result.result["campaign_id"] == campaign_id
        assert status_result.result["status"] == "launched"

    @pytest.mark.asyncio
    async def test_campaign_analytics_integration(
        self,
        campaign_config,
        social_media_config,
        linkedin_config,
        twitter_config,
        mock_linkedin_client,
        mock_twitter_client,
    ):
        """Test campaign analytics aggregation through agent hierarchy."""
        # Build agent hierarchy
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

        # Create campaign
        create_task = Task(
            task_id="campaign_analytics_001",
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

        create_result = await campaign_manager.execute(create_task)
        campaign_id = create_result.result["campaign_id"]

        # Get analytics
        analytics_task = Task(
            task_id="campaign_analytics_002",
            task_type="get_campaign_analytics",
            priority=TaskPriority.NORMAL,
            parameters={"campaign_id": campaign_id},
            assigned_to=AgentRole.CAMPAIGN_MANAGER,
            assigned_by=AgentRole.VP_MARKETING,
            created_at=datetime.now(),
        )

        analytics_result = await campaign_manager.execute(analytics_task)

        # Verify analytics aggregation through hierarchy
        assert analytics_result.status == TaskStatus.COMPLETED
        assert "analytics" in analytics_result.result
        assert len(analytics_result.result["analytics"]) >= 1

        # Verify API calls propagated through hierarchy
        mock_linkedin_client.get_profile_stats.assert_called()
        mock_twitter_client.get_profile_stats.assert_called()

    @pytest.mark.asyncio
    async def test_campaign_pause_resume(
        self,
        campaign_config,
    ):
        """Test campaign pause and resume lifecycle."""
        campaign_manager = CampaignManagerAgent(config=campaign_config)

        # Create campaign
        create_task = Task(
            task_id="pause_test_001",
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

        create_result = await campaign_manager.execute(create_task)
        campaign_id = create_result.result["campaign_id"]

        # Pause campaign
        pause_task = Task(
            task_id="pause_test_002",
            task_type="pause_campaign",
            priority=TaskPriority.HIGH,
            parameters={"campaign_id": campaign_id},
            assigned_to=AgentRole.CAMPAIGN_MANAGER,
            assigned_by=AgentRole.VP_MARKETING,
            created_at=datetime.now(),
        )

        pause_result = await campaign_manager.execute(pause_task)

        assert pause_result.status == TaskStatus.COMPLETED
        assert pause_result.result["status"] == "paused"

        # Resume campaign
        resume_task = Task(
            task_id="pause_test_003",
            task_type="resume_campaign",
            priority=TaskPriority.NORMAL,
            parameters={"campaign_id": campaign_id},
            assigned_to=AgentRole.CAMPAIGN_MANAGER,
            assigned_by=AgentRole.VP_MARKETING,
            created_at=datetime.now(),
        )

        resume_result = await campaign_manager.execute(resume_task)

        assert resume_result.status == TaskStatus.COMPLETED
        assert resume_result.result["status"] == "active"

    @pytest.mark.asyncio
    async def test_agent_hierarchy_cleanup(
        self,
        campaign_config,
        social_media_config,
        linkedin_config,
        mock_linkedin_client,
    ):
        """Test proper cleanup through agent hierarchy."""
        # Build hierarchy
        campaign_manager = CampaignManagerAgent(config=campaign_config)
        social_media_manager = SocialMediaManagerAgent(config=social_media_config)
        linkedin_manager = LinkedInManagerAgent(
            config=linkedin_config,
            linkedin_access_token="test_token",
            has_navigator=False,
        )
        linkedin_manager._linkedin_client = mock_linkedin_client

        # Wire up
        social_media_manager.register_specialist(
            AgentRole.LINKEDIN_MANAGER, linkedin_manager
        )
        campaign_manager.register_manager(
            AgentRole.SOCIAL_MEDIA_MANAGER, social_media_manager
        )

        # Verify all available
        assert campaign_manager.is_available is True
        assert social_media_manager.is_available is True
        assert linkedin_manager.is_available is True

        # Stop top-level (should cascade)
        await campaign_manager.stop()

        # Verify cascade cleanup
        assert campaign_manager.is_available is False
        assert social_media_manager.is_available is False
        assert linkedin_manager.is_available is False
