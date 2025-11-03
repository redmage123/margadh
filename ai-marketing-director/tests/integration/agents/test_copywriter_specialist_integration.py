"""
Integration tests for Copywriter Specialist with LLM integration.

WHY: Verify that Copywriter Specialist correctly integrates with LLM,
     maintains brand voice consistency, and generates quality content.

HOW: Uses real agent instance with mocked LLM client to test full
     content generation workflows.

Following TDD methodology - these tests verify integrated behavior.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from agents.base.agent_protocol import AgentRole, Task, TaskPriority, TaskStatus
from agents.base.base_agent import AgentConfig
from agents.specialists.copywriter import (
    BrandVoiceGuidelines,
    CopywriterSpecialistAgent,
)


class TestCopywriterSpecialistIntegration:
    """Integration test suite for Copywriter Specialist."""

    @pytest.fixture
    def copywriter_config(self):
        """Create Copywriter Specialist configuration."""
        return AgentConfig(
            agent_id="copywriter_001",
            role=AgentRole.COPYWRITER,
        )

    @pytest.fixture
    def brand_voice_guidelines(self):
        """Create comprehensive brand voice guidelines."""
        return BrandVoiceGuidelines(
            tone_attributes=["professional", "friendly", "authoritative"],
            personality_traits=["helpful", "innovative", "trustworthy"],
            vocabulary_do=["leverage", "optimize", "streamline", "enhance", "empower"],
            vocabulary_dont=["cheap", "buy now", "limited time", "click here"],
            sentence_structure="Clear and concise with active voice",
            reading_level="general professional",
        )

    @pytest.fixture
    def mock_llm_client(self):
        """Create mocked LLM client with realistic responses."""
        client = AsyncMock()

        # Default blog post response
        client.generate = AsyncMock(
            return_value=Mock(
                text="""# AI in Marketing: Transform Your Strategy

Artificial intelligence is revolutionizing how marketing teams operate. From automated content creation to predictive analytics, AI tools empower marketers to work smarter and achieve better results.

## Key Benefits

1. **Increased Efficiency**: Automate repetitive tasks
2. **Better Insights**: Leverage data for strategic decisions
3. **Personalization**: Optimize customer experiences

## Getting Started

Marketing directors can streamline their operations by implementing AI gradually. Start with one area, measure results, and expand from there.

Ready to enhance your marketing with AI? Let's explore the possibilities together."""
            )
        )
        return client

    @pytest.mark.asyncio
    async def test_multi_format_content_generation(
        self, copywriter_config, brand_voice_guidelines, mock_llm_client
    ):
        """Test generating content across multiple formats."""
        agent = CopywriterSpecialistAgent(
            config=copywriter_config, brand_voice=brand_voice_guidelines
        )
        agent._llm_client = mock_llm_client

        # Test blog post
        blog_task = Task(
            task_id="copy_001",
            task_type="write_blog_post",
            priority=TaskPriority.NORMAL,
            parameters={
                "topic": "AI in Marketing",
                "target_audience": "Marketing Directors",
                "word_count": 1000,
            },
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        blog_result = await agent.execute(blog_task)

        assert blog_result.status == TaskStatus.COMPLETED
        assert "content" in blog_result.result
        assert blog_result.result["content_type"] == "blog_post"

        # Test social post
        mock_llm_client.generate = AsyncMock(
            return_value=Mock(
                text="🚀 Excited to announce our new AI-powered marketing platform! Transform your strategy and empower your team. Learn more: [link]"
            )
        )

        social_task = Task(
            task_id="copy_002",
            task_type="write_social_post",
            priority=TaskPriority.HIGH,
            parameters={
                "platform": "linkedin",
                "message_type": "announcement",
                "topic": "Product Launch",
                "character_limit": 280,
            },
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        social_result = await agent.execute(social_task)

        assert social_result.status == TaskStatus.COMPLETED
        assert "content" in social_result.result

    @pytest.mark.asyncio
    async def test_brand_voice_consistency(
        self, copywriter_config, brand_voice_guidelines, mock_llm_client
    ):
        """Test that brand voice is maintained across content."""
        agent = CopywriterSpecialistAgent(
            config=copywriter_config, brand_voice=brand_voice_guidelines
        )
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="copy_003",
            task_type="write_blog_post",
            priority=TaskPriority.NORMAL,
            parameters={
                "topic": "Marketing Automation",
                "target_audience": "Small Business Owners",
                "word_count": 800,
            },
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Verify brand voice score is included
        assert result.status == TaskStatus.COMPLETED
        assert "brand_voice_score" in result.result

    @pytest.mark.asyncio
    async def test_content_quality_validation(
        self, copywriter_config, brand_voice_guidelines, mock_llm_client
    ):
        """Test content quality validation workflow."""
        agent = CopywriterSpecialistAgent(
            config=copywriter_config, brand_voice=brand_voice_guidelines
        )
        agent._llm_client = mock_llm_client

        # Create content
        create_task = Task(
            task_id="copy_004",
            task_type="write_blog_post",
            priority=TaskPriority.NORMAL,
            parameters={
                "topic": "SEO Best Practices",
                "target_audience": "Content Marketers",
                "word_count": 1200,
            },
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        create_result = await agent.execute(create_task)
        content = create_result.result["content"]

        # Validate brand voice
        validate_task = Task(
            task_id="copy_005",
            task_type="validate_brand_voice",
            priority=TaskPriority.NORMAL,
            parameters={"content": content, "content_type": "blog_post"},
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        validate_result = await agent.execute(validate_task)

        assert validate_result.status == TaskStatus.COMPLETED
        assert "brand_voice_score" in validate_result.result
        assert isinstance(validate_result.result["brand_voice_score"], float)

    @pytest.mark.asyncio
    async def test_content_revision_workflow(
        self, copywriter_config, brand_voice_guidelines, mock_llm_client
    ):
        """Test full content creation and revision workflow."""
        agent = CopywriterSpecialistAgent(
            config=copywriter_config, brand_voice=brand_voice_guidelines
        )
        agent._llm_client = mock_llm_client

        # Create original content
        original_content = "This is basic content about marketing."

        # Rewrite with new tone
        mock_llm_client.generate = AsyncMock(
            return_value=Mock(
                text="Marketing strategies empower businesses to optimize their reach and streamline customer engagement."
            )
        )

        rewrite_task = Task(
            task_id="copy_006",
            task_type="rewrite_content",
            priority=TaskPriority.NORMAL,
            parameters={
                "original_content": original_content,
                "new_tone": "professional",
                "new_style": "more engaging",
                "preserve_meaning": True,
            },
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        rewrite_result = await agent.execute(rewrite_task)

        assert rewrite_result.status == TaskStatus.COMPLETED
        assert "rewritten_content" in rewrite_result.result
        assert (
            rewrite_result.result["rewritten_content"] != original_content
        )  # Should be different

    @pytest.mark.asyncio
    async def test_graceful_degradation_llm_unavailable(
        self, copywriter_config, brand_voice_guidelines
    ):
        """Test graceful degradation when LLM is unavailable."""
        # Create agent with failing LLM
        mock_llm_failing = AsyncMock()
        mock_llm_failing.generate = AsyncMock(
            side_effect=Exception("LLM service temporarily unavailable")
        )

        agent = CopywriterSpecialistAgent(
            config=copywriter_config, brand_voice=brand_voice_guidelines
        )
        agent._llm_client = mock_llm_failing

        task = Task(
            task_id="copy_007",
            task_type="write_blog_post",
            priority=TaskPriority.NORMAL,
            parameters={
                "topic": "Test Topic",
                "target_audience": "Test Audience",
                "word_count": 500,
            },
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        # Should raise exception (no fallback content generation)
        with pytest.raises(Exception):
            await agent.execute(task)

    @pytest.mark.asyncio
    async def test_headline_generation_variations(
        self, copywriter_config, brand_voice_guidelines, mock_llm_client
    ):
        """Test generating multiple headline variations."""
        # Mock multiple headline responses
        mock_llm_client.generate = AsyncMock(
            return_value=Mock(
                text="""1. Transform Your Marketing with AI-Powered Tools
2. AI Marketing: The Future is Now
3. Boost ROI with Intelligent Marketing Automation
4. Marketing Directors: Leverage AI for Better Results
5. Revolutionize Your Strategy with AI Technology"""
            )
        )

        agent = CopywriterSpecialistAgent(
            config=copywriter_config, brand_voice=brand_voice_guidelines
        )
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="copy_008",
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
        assert "headlines" in result.result
        assert isinstance(result.result["headlines"], list)

    @pytest.mark.asyncio
    async def test_email_campaign_content(
        self, copywriter_config, brand_voice_guidelines, mock_llm_client
    ):
        """Test email marketing content generation."""
        mock_llm_client.generate = AsyncMock(
            return_value=Mock(
                text="""Subject Lines:
1. Transform Your Marketing Strategy Today
2. Exclusive Insights: AI for Marketing Directors
3. Unlock Your Team's Potential with AI

Body:
Dear [Name],

We're excited to share how AI can empower your marketing team to achieve exceptional results.

Our platform helps you:
- Streamline content creation
- Optimize campaign performance
- Enhance customer engagement

Ready to transform your marketing? Start your free trial today.

Best regards,
The Marketing Team"""
            )
        )

        agent = CopywriterSpecialistAgent(
            config=copywriter_config, brand_voice=brand_voice_guidelines
        )
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="copy_009",
            task_type="write_email",
            priority=TaskPriority.HIGH,
            parameters={
                "email_type": "promotional",
                "subject_line_count": 3,
                "body_word_count": 150,
                "call_to_action": "Start Free Trial",
            },
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert "subject_lines" in result.result
        assert isinstance(result.result["subject_lines"], list)

    @pytest.mark.asyncio
    async def test_agent_cleanup(self, copywriter_config):
        """Test that agent stops cleanly."""
        agent = CopywriterSpecialistAgent(config=copywriter_config)

        # Verify available
        assert agent.is_available is True

        # Stop cleanly
        await agent.stop()

        # Verify stopped
        assert agent.is_available is False
