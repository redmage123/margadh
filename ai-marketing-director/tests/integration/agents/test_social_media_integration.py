"""
Integration tests for Social Media agent coordination.

WHY: Verify that Social Media Manager correctly coordinates specialist agents
     in real multi-agent workflows.

HOW: Uses real agent instances with mocked external APIs (LinkedIn, Twitter, Bluesky).
     Tests actual task delegation, result aggregation, and error handling.

Following TDD methodology - these tests verify integrated behavior.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from agents.base.agent_protocol import AgentRole, Task, TaskPriority, TaskStatus
from agents.base.base_agent import AgentConfig
from agents.management.social_media_manager import SocialMediaManagerAgent
from agents.specialists.linkedin_manager import LinkedInManagerAgent
from agents.specialists.twitter_manager import TwitterManagerAgent


class TestSocialMediaIntegration:
    """Integration test suite for Social Media coordination."""

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
                "text": "Test post",
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
                "text": "Test tweet",
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
    async def test_social_media_to_linkedin_integration(
        self,
        social_media_config,
        linkedin_config,
        mock_linkedin_client,
    ):
        """Test Social Media Manager delegates to LinkedIn Manager correctly."""
        # Create real agent instances
        social_media_manager = SocialMediaManagerAgent(config=social_media_config)
        linkedin_manager = LinkedInManagerAgent(
            config=linkedin_config,
            linkedin_access_token="test_token",
            has_navigator=False,
        )

        # Inject mocked LinkedIn client
        linkedin_manager._linkedin_client = mock_linkedin_client

        # Register LinkedIn manager with Social Media Manager
        social_media_manager.register_specialist(
            AgentRole.LINKEDIN_MANAGER, linkedin_manager
        )

        # Create task for Social Media Manager
        task = Task(
            task_id="integration_001",
            task_type="create_post",
            priority=TaskPriority.NORMAL,
            parameters={
                "content": "Integration test post",
                "platforms": ["linkedin"],
                "optimize": False,
            },
            assigned_to=AgentRole.SOCIAL_MEDIA_MANAGER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        # Execute through Social Media Manager
        result = await social_media_manager.execute(task)

        # Verify result
        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert result.result["platforms_posted"] == 1
        assert len(result.result["results"]) == 1
        assert result.result["results"][0]["platform"] == "linkedin"

        # Verify LinkedIn API was called
        mock_linkedin_client.create_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_social_media_multi_platform_integration(
        self,
        social_media_config,
        linkedin_config,
        twitter_config,
        mock_linkedin_client,
        mock_twitter_client,
    ):
        """Test Social Media Manager coordinates multiple specialists."""
        # Create real agent instances
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

        # Register specialists
        social_media_manager.register_specialist(
            AgentRole.LINKEDIN_MANAGER, linkedin_manager
        )
        social_media_manager.register_specialist(
            AgentRole.TWITTER_MANAGER, twitter_manager
        )

        # Create multi-platform task
        task = Task(
            task_id="integration_002",
            task_type="create_post",
            priority=TaskPriority.NORMAL,
            parameters={
                "content": "Multi-platform integration test",
                "platforms": ["linkedin", "twitter"],
                "optimize": False,
            },
            assigned_to=AgentRole.SOCIAL_MEDIA_MANAGER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        # Execute
        result = await social_media_manager.execute(task)

        # Verify coordination
        assert result.status == TaskStatus.COMPLETED
        assert result.result["platforms_posted"] == 2
        assert len(result.result["results"]) == 2

        # Verify both APIs were called
        mock_linkedin_client.create_post.assert_called_once()
        mock_twitter_client.create_tweet.assert_called_once()

    @pytest.mark.asyncio
    async def test_social_media_analytics_aggregation(
        self,
        social_media_config,
        linkedin_config,
        twitter_config,
        mock_linkedin_client,
        mock_twitter_client,
    ):
        """Test Social Media Manager aggregates analytics from specialists."""
        # Create real agent instances
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

        # Register specialists
        social_media_manager.register_specialist(
            AgentRole.LINKEDIN_MANAGER, linkedin_manager
        )
        social_media_manager.register_specialist(
            AgentRole.TWITTER_MANAGER, twitter_manager
        )

        # Create analytics task
        task = Task(
            task_id="integration_003",
            task_type="get_analytics",
            priority=TaskPriority.NORMAL,
            parameters={"platforms": ["linkedin", "twitter"]},
            assigned_to=AgentRole.SOCIAL_MEDIA_MANAGER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        # Execute
        result = await social_media_manager.execute(task)

        # Verify aggregation
        assert result.status == TaskStatus.COMPLETED
        assert result.result["platforms_count"] == 2
        assert result.result["total_followers"] == 6000  # 1000 + 5000

        # Verify both APIs were called
        mock_linkedin_client.get_profile_stats.assert_called_once()
        mock_twitter_client.get_profile_stats.assert_called_once()

    @pytest.mark.asyncio
    async def test_specialist_failure_handling(
        self,
        social_media_config,
        linkedin_config,
        twitter_config,
        mock_linkedin_client,
        mock_twitter_client,
    ):
        """Test Social Media Manager handles specialist failures gracefully."""
        # Create real agent instances
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

        # Make Twitter client fail
        mock_twitter_client.create_tweet = AsyncMock(
            side_effect=Exception("Twitter API error")
        )
        twitter_manager._twitter_client = mock_twitter_client

        # Register specialists
        social_media_manager.register_specialist(
            AgentRole.LINKEDIN_MANAGER, linkedin_manager
        )
        social_media_manager.register_specialist(
            AgentRole.TWITTER_MANAGER, twitter_manager
        )

        # Create task
        task = Task(
            task_id="integration_004",
            task_type="create_post",
            priority=TaskPriority.NORMAL,
            parameters={
                "content": "Failure handling test",
                "platforms": ["linkedin", "twitter"],
                "optimize": False,
            },
            assigned_to=AgentRole.SOCIAL_MEDIA_MANAGER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        # Execute - should complete with partial success
        result = await social_media_manager.execute(task)

        # Verify graceful degradation
        assert result.status == TaskStatus.COMPLETED
        assert result.result["platforms_posted"] == 1  # Only LinkedIn succeeded
        assert result.result["requested_platforms"] == 2

        # LinkedIn should have succeeded
        mock_linkedin_client.create_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_agent_lifecycle(
        self,
        social_media_config,
        linkedin_config,
        mock_linkedin_client,
    ):
        """Test proper agent lifecycle management."""
        # Create agents
        social_media_manager = SocialMediaManagerAgent(config=social_media_config)
        linkedin_manager = LinkedInManagerAgent(
            config=linkedin_config,
            linkedin_access_token="test_token",
            has_navigator=False,
        )
        linkedin_manager._linkedin_client = mock_linkedin_client

        # Register
        social_media_manager.register_specialist(
            AgentRole.LINKEDIN_MANAGER, linkedin_manager
        )

        # Verify availability
        assert social_media_manager.is_available is True
        assert linkedin_manager.is_available is True

        # Stop manager (should stop specialists)
        await social_media_manager.stop()

        # Verify cleanup
        assert social_media_manager.is_available is False
        assert linkedin_manager.is_available is False
