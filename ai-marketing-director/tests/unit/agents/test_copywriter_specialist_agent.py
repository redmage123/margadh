"""
Unit tests for Copywriter Specialist Agent.

WHY: Ensures Copywriter Specialist correctly generates content across formats,
     maintains brand voice, and integrates with LLM.

HOW: Uses mocked LLM client to test content generation, brand voice validation,
     and quality checks.

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


class TestCopywriterSpecialistAgent:
    """Test suite for Copywriter Specialist Agent (Specialist Layer)."""

    @pytest.fixture
    def agent_config(self):
        """Create Copywriter Specialist agent configuration for testing."""
        return AgentConfig(
            agent_id="copywriter_001",
            role=AgentRole.COPYWRITER,
        )

    @pytest.fixture
    def mock_llm_client(self):
        """Create mocked LLM client."""
        client = AsyncMock()
        client.generate = AsyncMock(
            return_value=Mock(
                text="# Test Blog Post\n\nThis is a test blog post about AI in marketing..."
            )
        )
        return client

    @pytest.fixture
    def brand_voice_guidelines(self):
        """Create mock brand voice guidelines."""
        guidelines = Mock()
        guidelines.tone_attributes = ["professional", "friendly"]
        guidelines.personality_traits = ["helpful", "innovative"]
        guidelines.vocabulary_do = ["leverage", "optimize", "streamline"]
        guidelines.vocabulary_dont = ["cheap", "buy now", "limited time"]
        guidelines.sentence_structure = "clear and concise"
        guidelines.reading_level = "general"
        guidelines.to_prompt_context = Mock(return_value="Brand voice context...")
        return guidelines

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent_config):
        """Test that Copywriter Specialist Agent initializes correctly."""
        from agents.specialists.copywriter import CopywriterSpecialistAgent

        agent = CopywriterSpecialistAgent(config=agent_config)

        assert agent.agent_id == "copywriter_001"
        assert agent.role == AgentRole.COPYWRITER
        assert agent.is_available is True

    @pytest.mark.asyncio
    async def test_write_blog_post(self, agent_config, mock_llm_client):
        """Test writing blog post with LLM."""
        from agents.specialists.copywriter import CopywriterSpecialistAgent

        agent = CopywriterSpecialistAgent(config=agent_config)
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="task_001",
            task_type="write_blog_post",
            priority=TaskPriority.NORMAL,
            parameters={
                "topic": "AI in Marketing",
                "target_audience": "Marketing Directors",
                "word_count": 1000,
                "keywords": ["AI", "marketing", "automation"],
            },
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "content" in result.result
        assert "word_count" in result.result
        assert result.result["content_type"] == "blog_post"
        mock_llm_client.generate.assert_called()

    @pytest.mark.asyncio
    async def test_write_social_post(self, agent_config, mock_llm_client):
        """Test writing social media post."""
        from agents.specialists.copywriter import CopywriterSpecialistAgent

        mock_llm_client.generate = AsyncMock(
            return_value=Mock(text="Excited to announce our new product launch! 🚀")
        )

        agent = CopywriterSpecialistAgent(config=agent_config)
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="task_002",
            task_type="write_social_post",
            priority=TaskPriority.HIGH,
            parameters={
                "platform": "linkedin",
                "message_type": "announcement",
                "topic": "Product Launch",
                "call_to_action": "Learn more",
                "character_limit": 280,
            },
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "content" in result.result
        assert "platform" in result.result
        assert result.result["platform"] == "linkedin"

    @pytest.mark.asyncio
    async def test_write_email(self, agent_config, mock_llm_client):
        """Test writing email marketing copy."""
        from agents.specialists.copywriter import CopywriterSpecialistAgent

        agent = CopywriterSpecialistAgent(config=agent_config)
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="task_003",
            task_type="write_email",
            priority=TaskPriority.NORMAL,
            parameters={
                "email_type": "promotional",
                "subject_line_count": 3,
                "body_word_count": 200,
                "call_to_action": "Start Free Trial",
            },
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "subject_lines" in result.result
        assert isinstance(result.result["subject_lines"], list)

    @pytest.mark.asyncio
    async def test_write_case_study(self, agent_config, mock_llm_client):
        """Test writing customer case study."""
        from agents.specialists.copywriter import CopywriterSpecialistAgent

        agent = CopywriterSpecialistAgent(config=agent_config)
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="task_004",
            task_type="write_case_study",
            priority=TaskPriority.NORMAL,
            parameters={
                "customer_name": "Acme Corp",
                "industry": "Technology",
                "challenge": "Manual marketing processes",
                "solution": "Automated marketing platform",
                "results": {"roi_increase": 150, "time_saved": "20 hours/week"},
            },
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "content" in result.result
        assert "structure" in result.result

    @pytest.mark.asyncio
    async def test_write_product_description(self, agent_config, mock_llm_client):
        """Test writing product descriptions."""
        from agents.specialists.copywriter import CopywriterSpecialistAgent

        agent = CopywriterSpecialistAgent(config=agent_config)
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="task_005",
            task_type="write_product_description",
            priority=TaskPriority.NORMAL,
            parameters={
                "product_name": "Marketing Automation Platform",
                "features": ["Email automation", "Lead scoring", "Analytics"],
                "benefits": ["Save time", "Increase conversions", "Better insights"],
                "target_audience": "Marketing teams",
                "length": "medium",
            },
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert (
            "short_description" in result.result or "long_description" in result.result
        )

    @pytest.mark.asyncio
    async def test_generate_headlines(self, agent_config, mock_llm_client):
        """Test generating headline variations."""
        from agents.specialists.copywriter import CopywriterSpecialistAgent

        agent = CopywriterSpecialistAgent(config=agent_config)
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="task_006",
            task_type="generate_headlines",
            priority=TaskPriority.NORMAL,
            parameters={
                "topic": "AI Marketing Tools",
                "headline_type": "blog",
                "count": 5,
                "character_limit": 60,
            },
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "headlines" in result.result
        assert isinstance(result.result["headlines"], list)

    @pytest.mark.asyncio
    async def test_rewrite_content(self, agent_config, mock_llm_client):
        """Test rewriting content with new tone."""
        from agents.specialists.copywriter import CopywriterSpecialistAgent

        agent = CopywriterSpecialistAgent(config=agent_config)
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="task_007",
            task_type="rewrite_content",
            priority=TaskPriority.NORMAL,
            parameters={
                "original_content": "This is a test content.",
                "new_tone": "professional",
                "new_style": "shorter",
                "preserve_meaning": True,
            },
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "rewritten_content" in result.result

    @pytest.mark.asyncio
    async def test_validate_brand_voice(self, agent_config, brand_voice_guidelines):
        """Test validating content against brand voice."""
        from agents.specialists.copywriter import CopywriterSpecialistAgent

        agent = CopywriterSpecialistAgent(
            config=agent_config, brand_voice=brand_voice_guidelines
        )

        task = Task(
            task_id="task_008",
            task_type="validate_brand_voice",
            priority=TaskPriority.NORMAL,
            parameters={
                "content": "This is professional and helpful content.",
                "content_type": "blog_post",
            },
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "brand_voice_score" in result.result

    @pytest.mark.asyncio
    async def test_validate_task_write_blog_post(self, agent_config):
        """Test task validation for write_blog_post task type."""
        from agents.specialists.copywriter import CopywriterSpecialistAgent

        agent = CopywriterSpecialistAgent(config=agent_config)

        # Valid task
        valid_task = Task(
            task_id="task_009",
            task_type="write_blog_post",
            priority=TaskPriority.NORMAL,
            parameters={
                "topic": "Test Topic",
                "target_audience": "Test Audience",
                "word_count": 1000,
            },
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(valid_task)
        assert is_valid is True

        # Invalid task (missing required fields)
        invalid_task = Task(
            task_id="task_010",
            task_type="write_blog_post",
            priority=TaskPriority.NORMAL,
            parameters={"topic": "Test Topic"},  # Missing target_audience
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(invalid_task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_unsupported_task_type(self, agent_config):
        """Test that unsupported task types are rejected."""
        from agents.specialists.copywriter import CopywriterSpecialistAgent

        agent = CopywriterSpecialistAgent(config=agent_config)

        task = Task(
            task_id="task_011",
            task_type="unsupported_task",
            priority=TaskPriority.NORMAL,
            parameters={},
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_graceful_degradation_llm_failure(self, agent_config):
        """Test graceful degradation when LLM fails."""
        from agents.specialists.copywriter import CopywriterSpecialistAgent

        # Create agent with failing LLM client
        mock_llm_failing = AsyncMock()
        mock_llm_failing.generate = AsyncMock(
            side_effect=Exception("LLM service unavailable")
        )

        agent = CopywriterSpecialistAgent(config=agent_config)
        agent._llm_client = mock_llm_failing

        task = Task(
            task_id="task_012",
            task_type="write_blog_post",
            priority=TaskPriority.NORMAL,
            parameters={
                "topic": "Test",
                "target_audience": "Test",
                "word_count": 500,
            },
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        # Should raise AgentExecutionError with wrapped exception
        with pytest.raises(Exception):
            await agent.execute(task)

    @pytest.mark.asyncio
    async def test_agent_stops_cleanly(self, agent_config):
        """Test that agent stops cleanly."""
        from agents.specialists.copywriter import CopywriterSpecialistAgent

        agent = CopywriterSpecialistAgent(config=agent_config)

        # Should not raise exception
        await agent.stop()

        # Agent should no longer be available
        assert agent.is_available is False
