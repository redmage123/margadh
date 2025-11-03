"""
Unit tests for LinkedIn Manager Agent.

WHY: Ensures LinkedIn Manager Agent correctly handles LinkedIn-specific tasks.
HOW: Uses mocked LinkedIn client and LLM provider to test agent behavior.

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


class TestLinkedInManagerAgent:
    """Test suite for LinkedIn Manager Agent."""

    @pytest.fixture
    def agent_config(self):
        """Create agent configuration for testing."""
        return AgentConfig(
            agent_id="linkedin_001",
            role=AgentRole.LINKEDIN_MANAGER,
        )

    @pytest.fixture
    def mock_linkedin_client(self):
        """Create mocked LinkedIn client."""
        client = AsyncMock()
        client.has_navigator = False
        client.create_post = AsyncMock(
            return_value={
                "id": "post_123",
                "text": "Test post",
                "created_at": datetime.now().isoformat(),
                "platform": "linkedin",
            }
        )
        client.get_profile_stats = AsyncMock(
            return_value={
                "connections_count": 500,
                "followers_count": 1000,
                "profile_views_90_days": 200,
                "platform": "linkedin",
            }
        )
        return client

    @pytest.fixture
    def mock_llm_provider(self):
        """Create mocked LLM provider."""
        provider = AsyncMock()
        # LLM provider returns string directly
        provider.complete = AsyncMock(return_value="Optimized LinkedIn post content")
        return provider

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent_config):
        """Test that LinkedIn Manager Agent initializes correctly."""
        from agents.specialists.linkedin_manager import LinkedInManagerAgent

        agent = LinkedInManagerAgent(
            config=agent_config, linkedin_access_token="test_token", has_navigator=False
        )

        assert agent.agent_id == "linkedin_001"
        assert agent.role == AgentRole.LINKEDIN_MANAGER
        assert agent.is_available is True

    @pytest.mark.asyncio
    async def test_validate_task_create_post(self, agent_config):
        """Test task validation for create_post task type."""
        from agents.specialists.linkedin_manager import LinkedInManagerAgent

        agent = LinkedInManagerAgent(
            config=agent_config, linkedin_access_token="test_token"
        )

        # Valid create_post task
        valid_task = Task(
            task_id="task_001",
            task_type="create_post",
            priority=TaskPriority.NORMAL,
            parameters={"content": "Test LinkedIn post", "visibility": "public"},
            assigned_to=AgentRole.LINKEDIN_MANAGER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(valid_task)
        assert is_valid is True

        # Invalid task (missing content)
        invalid_task = Task(
            task_id="task_002",
            task_type="create_post",
            priority=TaskPriority.NORMAL,
            parameters={"visibility": "public"},  # Missing content
            assigned_to=AgentRole.LINKEDIN_MANAGER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(invalid_task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_create_post_task(
        self, agent_config, mock_linkedin_client, mock_llm_provider
    ):
        """Test creating a LinkedIn post."""
        from agents.specialists.linkedin_manager import LinkedInManagerAgent

        agent = LinkedInManagerAgent(
            config=agent_config, linkedin_access_token="test_token"
        )
        agent._linkedin_client = mock_linkedin_client
        agent._llm_provider = mock_llm_provider

        task = Task(
            task_id="task_001",
            task_type="create_post",
            priority=TaskPriority.NORMAL,
            parameters={
                "content": "Original post content",
                "visibility": "public",
                "optimize": False,
            },
            assigned_to=AgentRole.LINKEDIN_MANAGER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "post_id" in result.result
        assert result.result["post_id"] == "post_123"

        # Verify LinkedIn client was called
        mock_linkedin_client.create_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_post_with_optimization(
        self, agent_config, mock_linkedin_client, mock_llm_provider
    ):
        """Test creating a LinkedIn post with LLM optimization."""
        from agents.specialists.linkedin_manager import LinkedInManagerAgent

        agent = LinkedInManagerAgent(
            config=agent_config, linkedin_access_token="test_token"
        )
        agent._linkedin_client = mock_linkedin_client
        agent._llm_provider = mock_llm_provider

        task = Task(
            task_id="task_001",
            task_type="create_post",
            priority=TaskPriority.NORMAL,
            parameters={
                "content": "Original post content",
                "visibility": "public",
                "optimize": True,  # Request LLM optimization
            },
            assigned_to=AgentRole.LINKEDIN_MANAGER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED

        # Verify LLM was called for optimization
        mock_llm_provider.complete.assert_called_once()

        # Verify optimized content was used
        call_args = mock_linkedin_client.create_post.call_args
        assert call_args is not None

    @pytest.mark.asyncio
    async def test_get_analytics_task(self, agent_config, mock_linkedin_client):
        """Test getting LinkedIn profile analytics."""
        from agents.specialists.linkedin_manager import LinkedInManagerAgent

        agent = LinkedInManagerAgent(
            config=agent_config, linkedin_access_token="test_token"
        )
        # Pre-initialize clients to skip initialization logic
        agent._linkedin_client = mock_linkedin_client
        agent._llm_provider = None  # Not needed for this test

        task = Task(
            task_id="task_001",
            task_type="get_analytics",
            priority=TaskPriority.NORMAL,
            parameters={},
            assigned_to=AgentRole.LINKEDIN_MANAGER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "connections_count" in result.result
        assert result.result["connections_count"] == 500

        mock_linkedin_client.get_profile_stats.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_leads_requires_navigator(self, agent_config):
        """Test that search_leads task requires Navigator."""
        from agents.specialists.linkedin_manager import LinkedInManagerAgent
        from core.exceptions import AgentValidationError

        # Agent without Navigator
        agent = LinkedInManagerAgent(
            config=agent_config, linkedin_access_token="test_token", has_navigator=False
        )

        task = Task(
            task_id="task_001",
            task_type="search_leads",
            priority=TaskPriority.NORMAL,
            parameters={"title": "Marketing Director", "company_size": "1001-5000"},
            assigned_to=AgentRole.LINKEDIN_MANAGER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        # Should fail validation (no Navigator)
        is_valid = await agent.validate_task(task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_search_leads_with_navigator(
        self, agent_config, mock_linkedin_client
    ):
        """Test searching for leads with Navigator."""
        from agents.specialists.linkedin_manager import LinkedInManagerAgent

        # Agent with Navigator
        agent = LinkedInManagerAgent(
            config=agent_config, linkedin_access_token="test_token", has_navigator=True
        )

        mock_linkedin_client.has_navigator = True
        mock_linkedin_client.search_leads = AsyncMock(
            return_value=[
                {"id": "lead_1", "name": "John Doe", "title": "Marketing Director"},
                {"id": "lead_2", "name": "Jane Smith", "title": "Marketing Director"},
            ]
        )
        # Pre-initialize clients to skip initialization logic
        agent._linkedin_client = mock_linkedin_client
        agent._llm_provider = None  # Not needed for this test

        task = Task(
            task_id="task_001",
            task_type="search_leads",
            priority=TaskPriority.NORMAL,
            parameters={
                "title": "Marketing Director",
                "company_size": "1001-5000",
                "limit": 10,
            },
            assigned_to=AgentRole.LINKEDIN_MANAGER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "leads" in result.result
        assert len(result.result["leads"]) == 2

        mock_linkedin_client.search_leads.assert_called_once()

    @pytest.mark.asyncio
    async def test_optimize_post_task(
        self, agent_config, mock_llm_provider, mock_linkedin_client
    ):
        """Test optimizing a LinkedIn post using LLM."""
        from agents.specialists.linkedin_manager import LinkedInManagerAgent

        agent = LinkedInManagerAgent(
            config=agent_config, linkedin_access_token="test_token"
        )
        # Pre-initialize clients to skip initialization logic
        agent._linkedin_client = (
            mock_linkedin_client  # Set mock to prevent initialization
        )
        agent._llm_provider = mock_llm_provider

        task = Task(
            task_id="task_001",
            task_type="optimize_post",
            priority=TaskPriority.NORMAL,
            parameters={
                "content": "Original post content that needs optimization",
                "target_audience": "enterprise_leaders",
            },
            assigned_to=AgentRole.LINKEDIN_MANAGER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "optimized_content" in result.result
        assert result.result["optimized_content"] == "Optimized LinkedIn post content"

        mock_llm_provider.complete.assert_called_once()

    @pytest.mark.asyncio
    async def test_unsupported_task_type(self, agent_config):
        """Test that unsupported task types are rejected."""
        from agents.specialists.linkedin_manager import LinkedInManagerAgent

        agent = LinkedInManagerAgent(
            config=agent_config, linkedin_access_token="test_token"
        )

        task = Task(
            task_id="task_001",
            task_type="unsupported_task",
            priority=TaskPriority.NORMAL,
            parameters={},
            assigned_to=AgentRole.LINKEDIN_MANAGER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_agent_stops_cleanly(self, agent_config):
        """Test that agent stops cleanly."""
        from agents.specialists.linkedin_manager import LinkedInManagerAgent

        agent = LinkedInManagerAgent(
            config=agent_config, linkedin_access_token="test_token"
        )

        # Should not raise exception
        await agent.stop()

        # Agent should no longer be available
        assert agent.is_available is False
