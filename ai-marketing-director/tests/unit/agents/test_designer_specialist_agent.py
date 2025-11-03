"""
Unit tests for Designer Specialist Agent.

WHY: Ensures Designer Specialist correctly generates visual assets, maintains
     brand consistency, and integrates with AI image generation tools.

HOW: Uses mocked image generation clients (DALL-E, etc.) to test design operations,
     brand compliance validation, and platform optimization.

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


class TestDesignerSpecialistAgent:
    """Test suite for Designer Specialist Agent (Specialist Layer)."""

    @pytest.fixture
    def agent_config(self):
        """Create Designer Specialist agent configuration for testing."""
        return AgentConfig(
            agent_id="designer_001",
            role=AgentRole.DESIGNER,
        )

    @pytest.fixture
    def mock_dalle_client(self):
        """Create mocked DALL-E API client."""
        client = AsyncMock()
        client.generate = AsyncMock(
            return_value=Mock(
                url="https://cdn.example.com/generated_image.webp",
                path="/var/assets/generated_image.webp",
                width=1200,
                height=627,
                format="webp",
                size_kb=145,
            )
        )
        return client

    @pytest.fixture
    def brand_guidelines(self):
        """Create mock brand guidelines."""
        guidelines = Mock()
        guidelines.primary_colors = ["#1E40AF", "#3B82F6", "#60A5FA"]
        guidelines.secondary_colors = ["#F59E0B", "#10B981"]
        guidelines.visual_style = "modern"
        guidelines.imagery_style = "professional"
        guidelines.to_prompt_context = Mock(
            return_value="Brand colors: blue, orange. Style: modern, professional."
        )
        return guidelines

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent_config):
        """Test that Designer Specialist Agent initializes correctly."""
        from agents.specialists.designer import DesignerSpecialistAgent

        agent = DesignerSpecialistAgent(config=agent_config)

        assert agent.agent_id == "designer_001"
        assert agent.role == AgentRole.DESIGNER
        assert agent.is_available is True

    @pytest.mark.asyncio
    async def test_generate_social_graphic(self, agent_config, mock_dalle_client):
        """Test generating platform-specific social media graphic."""
        from agents.specialists.designer import DesignerSpecialistAgent

        agent = DesignerSpecialistAgent(config=agent_config)
        agent._dalle_client = mock_dalle_client

        task = Task(
            task_id="task_001",
            task_type="generate_social_graphic",
            priority=TaskPriority.NORMAL,
            parameters={
                "platform": "linkedin",
                "content_topic": "AI Marketing Automation",
                "graphic_type": "post",
                "style": "professional",
                "include_text": True,
                "text_content": "Transform Your Marketing with AI",
            },
            assigned_to=AgentRole.DESIGNER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "image_url" in result.result
        assert "platform" in result.result
        assert result.result["platform"] == "linkedin"
        assert "dimensions" in result.result
        mock_dalle_client.generate.assert_called()

    @pytest.mark.asyncio
    async def test_generate_blog_image(self, agent_config, mock_dalle_client):
        """Test generating featured image for blog post."""
        from agents.specialists.designer import DesignerSpecialistAgent

        agent = DesignerSpecialistAgent(config=agent_config)
        agent._dalle_client = mock_dalle_client

        task = Task(
            task_id="task_002",
            task_type="generate_blog_image",
            priority=TaskPriority.NORMAL,
            parameters={
                "blog_title": "AI Marketing Trends 2025",
                "blog_summary": "Comprehensive guide to emerging AI trends",
                "keywords": ["AI", "marketing", "automation"],
                "style": "professional",
                "image_type": "featured",
            },
            assigned_to=AgentRole.DESIGNER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "image_url" in result.result
        assert "image_type" in result.result
        assert result.result["image_type"] == "featured"

    @pytest.mark.asyncio
    async def test_create_infographic(self, agent_config, mock_dalle_client):
        """Test creating data-driven infographic."""
        from agents.specialists.designer import DesignerSpecialistAgent

        agent = DesignerSpecialistAgent(config=agent_config)
        agent._dalle_client = mock_dalle_client

        task = Task(
            task_id="task_003",
            task_type="create_infographic",
            priority=TaskPriority.NORMAL,
            parameters={
                "title": "Marketing Automation ROI",
                "data": {"ROI": 150, "Time Saved": 40, "Efficiency": 200},
                "chart_type": "bar",
                "color_scheme": "brand",
                "layout": "vertical",
            },
            assigned_to=AgentRole.DESIGNER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "infographic_url" in result.result
        assert "chart_type" in result.result
        assert result.result["chart_type"] == "bar"

    @pytest.mark.asyncio
    async def test_generate_ad_creative(self, agent_config, mock_dalle_client):
        """Test generating advertising creative."""
        from agents.specialists.designer import DesignerSpecialistAgent

        agent = DesignerSpecialistAgent(config=agent_config)
        agent._dalle_client = mock_dalle_client

        task = Task(
            task_id="task_004",
            task_type="generate_ad_creative",
            priority=TaskPriority.HIGH,
            parameters={
                "ad_type": "banner",
                "size": "leaderboard",
                "message": "Transform Your Marketing",
                "call_to_action": "Start Free Trial",
                "brand_elements": True,
            },
            assigned_to=AgentRole.DESIGNER,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "ad_creative_url" in result.result
        assert "ad_type" in result.result
        assert result.result["ad_type"] == "banner"

    @pytest.mark.asyncio
    async def test_design_email_header(self, agent_config, mock_dalle_client):
        """Test designing email marketing header."""
        from agents.specialists.designer import DesignerSpecialistAgent

        agent = DesignerSpecialistAgent(config=agent_config)
        agent._dalle_client = mock_dalle_client

        task = Task(
            task_id="task_005",
            task_type="design_email_header",
            priority=TaskPriority.NORMAL,
            parameters={
                "email_type": "newsletter",
                "subject": "Monthly Marketing Insights",
                "theme": "brand",
                "include_logo": True,
            },
            assigned_to=AgentRole.DESIGNER,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "header_url" in result.result
        assert "email_type" in result.result

    @pytest.mark.asyncio
    async def test_create_thumbnail(self, agent_config, mock_dalle_client):
        """Test creating video/content thumbnail."""
        from agents.specialists.designer import DesignerSpecialistAgent

        agent = DesignerSpecialistAgent(config=agent_config)
        agent._dalle_client = mock_dalle_client

        task = Task(
            task_id="task_006",
            task_type="create_thumbnail",
            priority=TaskPriority.NORMAL,
            parameters={
                "content_type": "webinar",
                "title": "AI Marketing Masterclass",
                "duration": "60 min",
                "style": "engaging",
                "include_play_button": True,
            },
            assigned_to=AgentRole.DESIGNER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "thumbnail_url" in result.result
        assert "content_type" in result.result

    @pytest.mark.asyncio
    async def test_generate_design_variations(self, agent_config, mock_dalle_client):
        """Test generating design variations for A/B testing."""
        from agents.specialists.designer import DesignerSpecialistAgent

        agent = DesignerSpecialistAgent(config=agent_config)
        agent._dalle_client = mock_dalle_client

        task = Task(
            task_id="task_007",
            task_type="generate_design_variations",
            priority=TaskPriority.NORMAL,
            parameters={
                "base_design_id": "design_001",
                "variation_count": 3,
                "variation_types": ["color", "layout", "style"],
            },
            assigned_to=AgentRole.DESIGNER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "variations" in result.result
        assert isinstance(result.result["variations"], list)
        assert len(result.result["variations"]) == 3

    @pytest.mark.asyncio
    async def test_optimize_image(self, agent_config):
        """Test image optimization for web performance."""
        from agents.specialists.designer import DesignerSpecialistAgent

        agent = DesignerSpecialistAgent(config=agent_config)

        task = Task(
            task_id="task_008",
            task_type="optimize_image",
            priority=TaskPriority.NORMAL,
            parameters={
                "image_url": "https://example.com/large_image.png",
                "target_format": "webp",
                "quality": 85,
                "max_width": 1200,
                "max_height": 630,
            },
            assigned_to=AgentRole.DESIGNER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "optimized_url" in result.result
        assert (
            "compression_ratio" in result.result or "optimized_size_kb" in result.result
        )

    @pytest.mark.asyncio
    async def test_brand_compliance_validation(
        self, agent_config, brand_guidelines, mock_dalle_client
    ):
        """Test brand compliance validation for generated images."""
        from agents.specialists.designer import DesignerSpecialistAgent

        agent = DesignerSpecialistAgent(
            config=agent_config, brand_guidelines=brand_guidelines
        )
        agent._dalle_client = mock_dalle_client

        task = Task(
            task_id="task_009",
            task_type="generate_social_graphic",
            priority=TaskPriority.NORMAL,
            parameters={
                "platform": "linkedin",
                "content_topic": "Brand Consistency Test",
                "style": "professional",
            },
            assigned_to=AgentRole.DESIGNER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert "brand_compliance_score" in result.result

    @pytest.mark.asyncio
    async def test_platform_dimensions(self, agent_config, mock_dalle_client):
        """Test that correct dimensions are used for each platform."""
        from agents.specialists.designer import DesignerSpecialistAgent

        agent = DesignerSpecialistAgent(config=agent_config)
        agent._dalle_client = mock_dalle_client

        # Test LinkedIn dimensions
        task = Task(
            task_id="task_010",
            task_type="generate_social_graphic",
            priority=TaskPriority.NORMAL,
            parameters={
                "platform": "linkedin",
                "content_topic": "Test Topic",
                "graphic_type": "post",
            },
            assigned_to=AgentRole.DESIGNER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert "dimensions" in result.result
        # LinkedIn post should be 1200x627
        assert result.result["dimensions"]["width"] == 1200
        assert result.result["dimensions"]["height"] == 627

    @pytest.mark.asyncio
    async def test_validate_task_generate_social_graphic(self, agent_config):
        """Test task validation for generate_social_graphic task type."""
        from agents.specialists.designer import DesignerSpecialistAgent

        agent = DesignerSpecialistAgent(config=agent_config)

        # Valid task
        valid_task = Task(
            task_id="task_011",
            task_type="generate_social_graphic",
            priority=TaskPriority.NORMAL,
            parameters={"platform": "linkedin", "content_topic": "Test Topic"},
            assigned_to=AgentRole.DESIGNER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(valid_task)
        assert is_valid is True

        # Invalid task (missing required field)
        invalid_task = Task(
            task_id="task_012",
            task_type="generate_social_graphic",
            priority=TaskPriority.NORMAL,
            parameters={"platform": "linkedin"},  # Missing content_topic
            assigned_to=AgentRole.DESIGNER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(invalid_task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_unsupported_task_type(self, agent_config):
        """Test that unsupported task types are rejected."""
        from agents.specialists.designer import DesignerSpecialistAgent

        agent = DesignerSpecialistAgent(config=agent_config)

        task = Task(
            task_id="task_013",
            task_type="unsupported_task",
            priority=TaskPriority.NORMAL,
            parameters={},
            assigned_to=AgentRole.DESIGNER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_graceful_degradation_no_image_generator(self, agent_config):
        """Test graceful degradation when image generator is unavailable."""
        from agents.specialists.designer import DesignerSpecialistAgent

        agent = DesignerSpecialistAgent(config=agent_config)
        # No image generator configured

        task = Task(
            task_id="task_014",
            task_type="generate_social_graphic",
            priority=TaskPriority.NORMAL,
            parameters={"platform": "linkedin", "content_topic": "Test Topic"},
            assigned_to=AgentRole.DESIGNER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Should complete with error message (graceful degradation)
        assert result.status == TaskStatus.COMPLETED
        assert "error" in result.result or "image_url" in result.result

    @pytest.mark.asyncio
    async def test_agent_stops_cleanly(self, agent_config):
        """Test that agent stops cleanly."""
        from agents.specialists.designer import DesignerSpecialistAgent

        agent = DesignerSpecialistAgent(config=agent_config)

        # Should not raise exception
        await agent.stop()

        # Agent should no longer be available
        assert agent.is_available is False
