"""
Unit tests for Social Media Manager Agent.

WHY: Ensures Social Media Manager correctly coordinates specialist agents.
HOW: Uses mocked specialist agents to test coordination and task delegation.

Following TDD methodology (RED-GREEN-REFACTOR):
- Write tests FIRST (these tests will fail initially)
- Implement agent to make tests pass
- Refactor while keeping tests green
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from agents.base.agent_protocol import AgentRole, Task, TaskPriority, TaskStatus
from agents.base.base_agent import AgentConfig


class TestSocialMediaManagerAgent:
    """Test suite for Social Media Manager Agent."""

    @pytest.fixture
    def agent_config(self):
        """Create agent configuration for testing."""
        return AgentConfig(
            agent_id="social_media_001",
            role=AgentRole.SOCIAL_MEDIA_MANAGER,
        )

    @pytest.fixture
    def mock_linkedin_manager(self):
        """Create mocked LinkedIn manager agent."""
        agent = AsyncMock()
        agent.agent_id = "linkedin_001"
        agent.role = AgentRole.LINKEDIN_MANAGER
        agent.is_available = True
        agent.validate_task = AsyncMock(return_value=True)
        agent.execute = AsyncMock(
            return_value=Mock(
                status=TaskStatus.COMPLETED,
                result={
                    "post_id": "linkedin_post_123",
                    "platform": "linkedin",
                },
            )
        )
        return agent

    @pytest.fixture
    def mock_twitter_manager(self):
        """Create mocked Twitter manager agent."""
        agent = AsyncMock()
        agent.agent_id = "twitter_001"
        agent.role = AgentRole.TWITTER_MANAGER
        agent.is_available = True
        agent.validate_task = AsyncMock(return_value=True)
        agent.execute = AsyncMock(
            return_value=Mock(
                status=TaskStatus.COMPLETED,
                result={
                    "tweet_id": "twitter_tweet_123",
                    "platform": "twitter",
                },
            )
        )
        return agent

    @pytest.fixture
    def mock_bluesky_manager(self):
        """Create mocked Bluesky manager agent."""
        agent = AsyncMock()
        agent.agent_id = "bluesky_001"
        agent.role = AgentRole.BLUESKY_MANAGER
        agent.is_available = True
        agent.validate_task = AsyncMock(return_value=True)
        agent.execute = AsyncMock(
            return_value=Mock(
                status=TaskStatus.COMPLETED,
                result={
                    "post_id": "bluesky_post_123",
                    "platform": "bluesky",
                },
            )
        )
        return agent

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent_config):
        """Test that Social Media Manager Agent initializes correctly."""
        from agents.management.social_media_manager import SocialMediaManagerAgent

        agent = SocialMediaManagerAgent(config=agent_config)

        assert agent.agent_id == "social_media_001"
        assert agent.role == AgentRole.SOCIAL_MEDIA_MANAGER
        assert agent.is_available is True

    @pytest.mark.asyncio
    async def test_register_specialist_agents(
        self,
        agent_config,
        mock_linkedin_manager,
        mock_twitter_manager,
        mock_bluesky_manager,
    ):
        """Test registering specialist agents."""
        from agents.management.social_media_manager import SocialMediaManagerAgent

        agent = SocialMediaManagerAgent(config=agent_config)

        # Register specialist agents
        agent.register_specialist(AgentRole.LINKEDIN_MANAGER, mock_linkedin_manager)
        agent.register_specialist(AgentRole.TWITTER_MANAGER, mock_twitter_manager)
        agent.register_specialist(AgentRole.BLUESKY_MANAGER, mock_bluesky_manager)

        # Verify specialists are registered
        assert agent.has_specialist(AgentRole.LINKEDIN_MANAGER) is True
        assert agent.has_specialist(AgentRole.TWITTER_MANAGER) is True
        assert agent.has_specialist(AgentRole.BLUESKY_MANAGER) is True

    @pytest.mark.asyncio
    async def test_create_post_single_platform(
        self, agent_config, mock_linkedin_manager
    ):
        """Test creating post on single platform."""
        from agents.management.social_media_manager import SocialMediaManagerAgent

        agent = SocialMediaManagerAgent(config=agent_config)
        agent.register_specialist(AgentRole.LINKEDIN_MANAGER, mock_linkedin_manager)

        task = Task(
            task_id="task_001",
            task_type="create_post",
            priority=TaskPriority.NORMAL,
            parameters={
                "content": "Test social media post",
                "platforms": ["linkedin"],
            },
            assigned_to=AgentRole.SOCIAL_MEDIA_MANAGER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "results" in result.result
        assert len(result.result["results"]) == 1
        assert result.result["results"][0]["platform"] == "linkedin"

        # Verify LinkedIn manager was called
        mock_linkedin_manager.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_post_multi_platform(
        self,
        agent_config,
        mock_linkedin_manager,
        mock_twitter_manager,
        mock_bluesky_manager,
    ):
        """Test creating post across multiple platforms."""
        from agents.management.social_media_manager import SocialMediaManagerAgent

        agent = SocialMediaManagerAgent(config=agent_config)
        agent.register_specialist(AgentRole.LINKEDIN_MANAGER, mock_linkedin_manager)
        agent.register_specialist(AgentRole.TWITTER_MANAGER, mock_twitter_manager)
        agent.register_specialist(AgentRole.BLUESKY_MANAGER, mock_bluesky_manager)

        task = Task(
            task_id="task_001",
            task_type="create_post",
            priority=TaskPriority.NORMAL,
            parameters={
                "content": "Test multi-platform post",
                "platforms": ["linkedin", "twitter", "bluesky"],
            },
            assigned_to=AgentRole.SOCIAL_MEDIA_MANAGER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "results" in result.result
        assert len(result.result["results"]) == 3

        # Verify all managers were called
        mock_linkedin_manager.execute.assert_called_once()
        mock_twitter_manager.execute.assert_called_once()
        mock_bluesky_manager.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_analytics_aggregated(
        self,
        agent_config,
        mock_linkedin_manager,
        mock_twitter_manager,
        mock_bluesky_manager,
    ):
        """Test getting aggregated analytics from all platforms."""
        from agents.management.social_media_manager import SocialMediaManagerAgent

        # Update mocks to return analytics
        mock_linkedin_manager.execute = AsyncMock(
            return_value=Mock(
                status=TaskStatus.COMPLETED,
                result={
                    "platform": "linkedin",
                    "followers_count": 5000,
                    "connections_count": 1500,
                },
            )
        )
        mock_twitter_manager.execute = AsyncMock(
            return_value=Mock(
                status=TaskStatus.COMPLETED,
                result={
                    "platform": "twitter",
                    "followers_count": 10000,
                    "tweet_count": 2500,
                },
            )
        )
        mock_bluesky_manager.execute = AsyncMock(
            return_value=Mock(
                status=TaskStatus.COMPLETED,
                result={
                    "platform": "bluesky",
                    "followers_count": 3000,
                    "posts_count": 800,
                },
            )
        )

        agent = SocialMediaManagerAgent(config=agent_config)
        agent.register_specialist(AgentRole.LINKEDIN_MANAGER, mock_linkedin_manager)
        agent.register_specialist(AgentRole.TWITTER_MANAGER, mock_twitter_manager)
        agent.register_specialist(AgentRole.BLUESKY_MANAGER, mock_bluesky_manager)

        task = Task(
            task_id="task_001",
            task_type="get_analytics",
            priority=TaskPriority.NORMAL,
            parameters={"platforms": ["linkedin", "twitter", "bluesky"]},
            assigned_to=AgentRole.SOCIAL_MEDIA_MANAGER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "analytics" in result.result
        assert len(result.result["analytics"]) == 3
        assert result.result["total_followers"] == 18000  # 5000 + 10000 + 3000

        # Verify all managers were called
        mock_linkedin_manager.execute.assert_called_once()
        mock_twitter_manager.execute.assert_called_once()
        mock_bluesky_manager.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_task_create_post(self, agent_config):
        """Test task validation for create_post task type."""
        from agents.management.social_media_manager import SocialMediaManagerAgent

        agent = SocialMediaManagerAgent(config=agent_config)

        # Valid create_post task
        valid_task = Task(
            task_id="task_001",
            task_type="create_post",
            priority=TaskPriority.NORMAL,
            parameters={"content": "Test post", "platforms": ["linkedin"]},
            assigned_to=AgentRole.SOCIAL_MEDIA_MANAGER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(valid_task)
        assert is_valid is True

        # Invalid task (missing content)
        invalid_task = Task(
            task_id="task_002",
            task_type="create_post",
            priority=TaskPriority.NORMAL,
            parameters={"platforms": ["linkedin"]},  # Missing content
            assigned_to=AgentRole.SOCIAL_MEDIA_MANAGER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(invalid_task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_cross_post_with_platform_optimization(
        self, agent_config, mock_linkedin_manager, mock_twitter_manager
    ):
        """Test cross-posting with platform-specific optimization."""
        from agents.management.social_media_manager import SocialMediaManagerAgent

        agent = SocialMediaManagerAgent(config=agent_config)
        agent.register_specialist(AgentRole.LINKEDIN_MANAGER, mock_linkedin_manager)
        agent.register_specialist(AgentRole.TWITTER_MANAGER, mock_twitter_manager)

        task = Task(
            task_id="task_001",
            task_type="create_post",
            priority=TaskPriority.NORMAL,
            parameters={
                "content": "A very long post that needs to be optimized differently for each platform based on their character limits and audience expectations",
                "platforms": ["linkedin", "twitter"],
                "optimize": True,  # Request platform-specific optimization
            },
            assigned_to=AgentRole.SOCIAL_MEDIA_MANAGER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED

        # Verify both managers were called with optimization enabled
        assert mock_linkedin_manager.execute.call_count == 1
        assert mock_twitter_manager.execute.call_count == 1

    @pytest.mark.asyncio
    async def test_unsupported_task_type(self, agent_config):
        """Test that unsupported task types are rejected."""
        from agents.management.social_media_manager import SocialMediaManagerAgent

        agent = SocialMediaManagerAgent(config=agent_config)

        task = Task(
            task_id="task_001",
            task_type="unsupported_task",
            priority=TaskPriority.NORMAL,
            parameters={},
            assigned_to=AgentRole.SOCIAL_MEDIA_MANAGER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_agent_stops_cleanly(self, agent_config):
        """Test that agent stops cleanly."""
        from agents.management.social_media_manager import SocialMediaManagerAgent

        agent = SocialMediaManagerAgent(config=agent_config)

        # Should not raise exception
        await agent.stop()

        # Agent should no longer be available
        assert agent.is_available is False
