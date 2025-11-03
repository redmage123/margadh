"""
Unit tests for Twitter Manager Agent.

WHY: Ensures Twitter Manager Agent correctly handles Twitter-specific tasks.
HOW: Uses mocked Twitter client and LLM provider to test agent behavior.

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


class TestTwitterManagerAgent:
    """Test suite for Twitter Manager Agent."""

    @pytest.fixture
    def agent_config(self):
        """Create agent configuration for testing."""
        return AgentConfig(
            agent_id="twitter_001",
            role=AgentRole.TWITTER_MANAGER,
        )

    @pytest.fixture
    def mock_twitter_client(self):
        """Create mocked Twitter client."""
        client = AsyncMock()
        client.create_tweet = AsyncMock(
            return_value={
                "id": "tweet_123",
                "text": "Test tweet",
                "created_at": datetime.now().isoformat(),
                "platform": "twitter",
            }
        )
        client.create_thread = AsyncMock(
            return_value={
                "tweet_ids": ["tweet_1", "tweet_2", "tweet_3"],
                "thread_count": 3,
                "created_at": datetime.now().isoformat(),
                "platform": "twitter",
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
        client.search_tweets = AsyncMock(
            return_value=[
                {"id": "tweet_1", "text": "AI tweet 1", "created_at": None},
                {"id": "tweet_2", "text": "AI tweet 2", "created_at": None},
            ]
        )
        return client

    @pytest.fixture
    def mock_llm_provider(self):
        """Create mocked LLM provider."""
        provider = AsyncMock()
        # LLM provider returns string directly
        provider.complete = AsyncMock(return_value="Optimized Twitter post content")
        return provider

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent_config):
        """Test that Twitter Manager Agent initializes correctly."""
        from agents.specialists.twitter_manager import TwitterManagerAgent

        agent = TwitterManagerAgent(
            config=agent_config,
            api_key="test_api_key",
            api_secret="test_api_secret",
            access_token="test_access_token",
            access_token_secret="test_access_token_secret",
        )

        assert agent.agent_id == "twitter_001"
        assert agent.role == AgentRole.TWITTER_MANAGER
        assert agent.is_available is True

    @pytest.mark.asyncio
    async def test_validate_task_create_tweet(self, agent_config):
        """Test task validation for create_tweet task type."""
        from agents.specialists.twitter_manager import TwitterManagerAgent

        agent = TwitterManagerAgent(
            config=agent_config,
            api_key="test_api_key",
            api_secret="test_api_secret",
            access_token="test_access_token",
            access_token_secret="test_access_token_secret",
        )

        # Valid create_tweet task
        valid_task = Task(
            task_id="task_001",
            task_type="create_tweet",
            priority=TaskPriority.NORMAL,
            parameters={"text": "Test Twitter post"},
            assigned_to=AgentRole.TWITTER_MANAGER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(valid_task)
        assert is_valid is True

        # Invalid task (missing text)
        invalid_task = Task(
            task_id="task_002",
            task_type="create_tweet",
            priority=TaskPriority.NORMAL,
            parameters={},  # Missing text
            assigned_to=AgentRole.TWITTER_MANAGER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(invalid_task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_create_tweet_task(
        self, agent_config, mock_twitter_client, mock_llm_provider
    ):
        """Test creating a tweet."""
        from agents.specialists.twitter_manager import TwitterManagerAgent

        agent = TwitterManagerAgent(
            config=agent_config,
            api_key="test_api_key",
            api_secret="test_api_secret",
            access_token="test_access_token",
            access_token_secret="test_access_token_secret",
        )
        agent._twitter_client = mock_twitter_client
        agent._llm_provider = mock_llm_provider

        task = Task(
            task_id="task_001",
            task_type="create_tweet",
            priority=TaskPriority.NORMAL,
            parameters={
                "text": "Original tweet content",
                "optimize": False,
            },
            assigned_to=AgentRole.TWITTER_MANAGER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "tweet_id" in result.result
        assert result.result["tweet_id"] == "tweet_123"

        # Verify Twitter client was called
        mock_twitter_client.create_tweet.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_tweet_with_optimization(
        self, agent_config, mock_twitter_client, mock_llm_provider
    ):
        """Test creating a tweet with LLM optimization."""
        from agents.specialists.twitter_manager import TwitterManagerAgent

        agent = TwitterManagerAgent(
            config=agent_config,
            api_key="test_api_key",
            api_secret="test_api_secret",
            access_token="test_access_token",
            access_token_secret="test_access_token_secret",
        )
        agent._twitter_client = mock_twitter_client
        agent._llm_provider = mock_llm_provider

        task = Task(
            task_id="task_001",
            task_type="create_tweet",
            priority=TaskPriority.NORMAL,
            parameters={
                "text": "Original tweet content",
                "optimize": True,  # Request LLM optimization
            },
            assigned_to=AgentRole.TWITTER_MANAGER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED

        # Verify LLM was called for optimization
        mock_llm_provider.complete.assert_called_once()

        # Verify Twitter client was called
        mock_twitter_client.create_tweet.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_thread_task(
        self, agent_config, mock_twitter_client, mock_llm_provider
    ):
        """Test creating a Twitter thread."""
        from agents.specialists.twitter_manager import TwitterManagerAgent

        agent = TwitterManagerAgent(
            config=agent_config,
            api_key="test_api_key",
            api_secret="test_api_secret",
            access_token="test_access_token",
            access_token_secret="test_access_token_secret",
        )
        agent._twitter_client = mock_twitter_client
        agent._llm_provider = mock_llm_provider

        task = Task(
            task_id="task_001",
            task_type="create_thread",
            priority=TaskPriority.NORMAL,
            parameters={
                "tweets": ["First tweet", "Second tweet", "Third tweet"],
            },
            assigned_to=AgentRole.TWITTER_MANAGER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "tweet_ids" in result.result
        assert len(result.result["tweet_ids"]) == 3

        mock_twitter_client.create_thread.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_analytics_task(self, agent_config, mock_twitter_client):
        """Test getting Twitter profile analytics."""
        from agents.specialists.twitter_manager import TwitterManagerAgent

        agent = TwitterManagerAgent(
            config=agent_config,
            api_key="test_api_key",
            api_secret="test_api_secret",
            access_token="test_access_token",
            access_token_secret="test_access_token_secret",
        )
        # Pre-initialize clients to skip initialization logic
        agent._twitter_client = mock_twitter_client
        agent._llm_provider = None  # Not needed for this test

        task = Task(
            task_id="task_001",
            task_type="get_analytics",
            priority=TaskPriority.NORMAL,
            parameters={},
            assigned_to=AgentRole.TWITTER_MANAGER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "followers_count" in result.result
        assert result.result["followers_count"] == 5000

        mock_twitter_client.get_profile_stats.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_tweets_task(self, agent_config, mock_twitter_client):
        """Test searching for tweets."""
        from agents.specialists.twitter_manager import TwitterManagerAgent

        agent = TwitterManagerAgent(
            config=agent_config,
            api_key="test_api_key",
            api_secret="test_api_secret",
            access_token="test_access_token",
            access_token_secret="test_access_token_secret",
        )
        agent._twitter_client = mock_twitter_client
        agent._llm_provider = None

        task = Task(
            task_id="task_001",
            task_type="search_tweets",
            priority=TaskPriority.NORMAL,
            parameters={"query": "AI marketing", "limit": 10},
            assigned_to=AgentRole.TWITTER_MANAGER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "tweets" in result.result
        assert len(result.result["tweets"]) == 2

        mock_twitter_client.search_tweets.assert_called_once()

    @pytest.mark.asyncio
    async def test_optimize_tweet_task(
        self, agent_config, mock_llm_provider, mock_twitter_client
    ):
        """Test optimizing a tweet using LLM."""
        from agents.specialists.twitter_manager import TwitterManagerAgent

        agent = TwitterManagerAgent(
            config=agent_config,
            api_key="test_api_key",
            api_secret="test_api_secret",
            access_token="test_access_token",
            access_token_secret="test_access_token_secret",
        )
        # Pre-initialize clients to skip initialization logic
        agent._twitter_client = (
            mock_twitter_client  # Set mock to prevent initialization
        )
        agent._llm_provider = mock_llm_provider

        task = Task(
            task_id="task_001",
            task_type="optimize_tweet",
            priority=TaskPriority.NORMAL,
            parameters={
                "text": "Original tweet that needs optimization",
                "target_audience": "tech_enthusiasts",
            },
            assigned_to=AgentRole.TWITTER_MANAGER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "optimized_text" in result.result
        assert result.result["optimized_text"] == "Optimized Twitter post content"

        mock_llm_provider.complete.assert_called_once()

    @pytest.mark.asyncio
    async def test_unsupported_task_type(self, agent_config):
        """Test that unsupported task types are rejected."""
        from agents.specialists.twitter_manager import TwitterManagerAgent

        agent = TwitterManagerAgent(
            config=agent_config,
            api_key="test_api_key",
            api_secret="test_api_secret",
            access_token="test_access_token",
            access_token_secret="test_access_token_secret",
        )

        task = Task(
            task_id="task_001",
            task_type="unsupported_task",
            priority=TaskPriority.NORMAL,
            parameters={},
            assigned_to=AgentRole.TWITTER_MANAGER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_agent_stops_cleanly(self, agent_config):
        """Test that agent stops cleanly."""
        from agents.specialists.twitter_manager import TwitterManagerAgent

        agent = TwitterManagerAgent(
            config=agent_config,
            api_key="test_api_key",
            api_secret="test_api_secret",
            access_token="test_access_token",
            access_token_secret="test_access_token_secret",
        )

        # Should not raise exception
        await agent.stop()

        # Agent should no longer be available
        assert agent.is_available is False
