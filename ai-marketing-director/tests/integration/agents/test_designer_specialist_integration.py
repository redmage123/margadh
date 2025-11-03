"""
Integration tests for Designer Specialist with external API clients.

WHY: Verify that Designer Specialist correctly integrates with AI image generation
     tools, handles brand compliance, and provides quality visual assets.

HOW: Uses real agent instance with mocked external image generation clients (DALL-E)
     to test full design workflows.

Following TDD methodology - these tests verify integrated behavior.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from agents.base.agent_protocol import AgentRole, Task, TaskPriority, TaskStatus
from agents.base.base_agent import AgentConfig
from agents.specialists.designer import BrandGuidelines, DesignerSpecialistAgent


class TestDesignerSpecialistIntegration:
    """Integration test suite for Designer Specialist."""

    @pytest.fixture
    def designer_config(self):
        """Create Designer Specialist configuration."""
        return AgentConfig(
            agent_id="designer_001",
            role=AgentRole.DESIGNER,
        )

    @pytest.fixture
    def brand_guidelines(self):
        """Create comprehensive brand guidelines for testing."""
        return BrandGuidelines(
            primary_colors=["#1E40AF", "#3B82F6", "#60A5FA"],
            secondary_colors=["#F59E0B", "#10B981"],
            fonts={"heading": "Montserrat", "body": "Open Sans"},
            logo_usage={
                "min_size": "100px",
                "clearspace": "20px",
                "placement": "top-left",
            },
            visual_style="modern",
            imagery_style="professional",
        )

    @pytest.fixture
    def mock_dalle_client(self):
        """Create mocked DALL-E API client with comprehensive responses."""
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

    @pytest.mark.asyncio
    async def test_full_social_media_workflow(
        self, designer_config, brand_guidelines, mock_dalle_client
    ):
        """Test complete social media graphic workflow with brand compliance."""
        agent = DesignerSpecialistAgent(
            config=designer_config, brand_guidelines=brand_guidelines
        )
        agent._dalle_client = mock_dalle_client

        task = Task(
            task_id="design_001",
            task_type="generate_social_graphic",
            priority=TaskPriority.NORMAL,
            parameters={
                "platform": "linkedin",
                "content_topic": "AI Marketing Transformation",
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

        # Verify complete workflow
        assert result.status == TaskStatus.COMPLETED
        assert "image_url" in result.result
        assert "platform" in result.result
        assert "dimensions" in result.result
        assert "brand_compliance_score" in result.result

        # Verify brand compliance validation ran
        assert result.result["brand_compliance_score"] >= 0

        # Verify DALL-E API was called
        mock_dalle_client.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_multi_platform_campaign_workflow(
        self, designer_config, brand_guidelines, mock_dalle_client
    ):
        """Test creating graphics for multiple platforms in one campaign."""
        agent = DesignerSpecialistAgent(
            config=designer_config, brand_guidelines=brand_guidelines
        )
        agent._dalle_client = mock_dalle_client

        platforms = ["linkedin", "twitter", "instagram"]
        results = []

        for platform in platforms:
            task = Task(
                task_id=f"design_{platform}",
                task_type="generate_social_graphic",
                priority=TaskPriority.HIGH,
                parameters={
                    "platform": platform,
                    "content_topic": "Product Launch Campaign",
                    "graphic_type": "post",
                    "style": "bold",
                },
                assigned_to=AgentRole.DESIGNER,
                assigned_by=AgentRole.CAMPAIGN_MANAGER,
                created_at=datetime.now(),
            )

            result = await agent.execute(task)
            results.append(result)

        # Verify all platforms completed successfully
        assert all(r.status == TaskStatus.COMPLETED for r in results)

        # Verify each platform has correct dimensions
        assert results[0].result["platform"] == "linkedin"
        assert results[1].result["platform"] == "twitter"
        assert results[2].result["platform"] == "instagram"

        # Verify API was called for each platform
        assert mock_dalle_client.generate.call_count == 3

    @pytest.mark.asyncio
    async def test_blog_content_design_workflow(
        self, designer_config, brand_guidelines, mock_dalle_client
    ):
        """Test complete blog content design workflow."""
        agent = DesignerSpecialistAgent(
            config=designer_config, brand_guidelines=brand_guidelines
        )
        agent._dalle_client = mock_dalle_client

        # Create featured image
        featured_task = Task(
            task_id="design_002",
            task_type="generate_blog_image",
            priority=TaskPriority.NORMAL,
            parameters={
                "blog_title": "The Future of AI Marketing in 2025",
                "blog_summary": "Comprehensive guide to emerging AI marketing trends",
                "keywords": ["AI", "marketing", "automation", "trends"],
                "style": "professional",
                "image_type": "featured",
            },
            assigned_to=AgentRole.DESIGNER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        featured_result = await agent.execute(featured_task)

        # Create infographic
        infographic_task = Task(
            task_id="design_003",
            task_type="create_infographic",
            priority=TaskPriority.NORMAL,
            parameters={
                "title": "Marketing Automation ROI",
                "data": {"ROI Increase": 150, "Time Saved": 40, "Efficiency Gain": 200},
                "chart_type": "bar",
                "color_scheme": "brand",
                "layout": "vertical",
            },
            assigned_to=AgentRole.DESIGNER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        infographic_result = await agent.execute(infographic_task)

        # Verify both completed successfully
        assert featured_result.status == TaskStatus.COMPLETED
        assert infographic_result.status == TaskStatus.COMPLETED

        # Verify correct content types
        assert featured_result.result["image_type"] == "featured"
        assert infographic_result.result["chart_type"] == "bar"

        # Verify API calls
        assert mock_dalle_client.generate.call_count == 2

    @pytest.mark.asyncio
    async def test_ab_testing_variation_workflow(
        self, designer_config, brand_guidelines, mock_dalle_client
    ):
        """Test A/B testing design variation generation workflow."""
        agent = DesignerSpecialistAgent(
            config=designer_config, brand_guidelines=brand_guidelines
        )
        agent._dalle_client = mock_dalle_client

        task = Task(
            task_id="design_004",
            task_type="generate_design_variations",
            priority=TaskPriority.HIGH,
            parameters={
                "base_design_id": "design_001",
                "variation_count": 3,
                "variation_types": ["color", "layout", "style"],
            },
            assigned_to=AgentRole.DESIGNER,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Verify variations created
        assert result.status == TaskStatus.COMPLETED
        assert "variations" in result.result
        assert len(result.result["variations"]) == 3

        # Verify variation types
        variation_types = [v["type"] for v in result.result["variations"]]
        assert "color" in variation_types
        assert "layout" in variation_types
        assert "style" in variation_types

    @pytest.mark.asyncio
    async def test_campaign_asset_bundle_workflow(
        self, designer_config, brand_guidelines, mock_dalle_client
    ):
        """Test creating complete campaign asset bundle."""
        agent = DesignerSpecialistAgent(
            config=designer_config, brand_guidelines=brand_guidelines
        )
        agent._dalle_client = mock_dalle_client

        # Social graphic
        social_task = Task(
            task_id="design_005",
            task_type="generate_social_graphic",
            priority=TaskPriority.HIGH,
            parameters={
                "platform": "linkedin",
                "content_topic": "New Product Launch",
                "style": "bold",
            },
            assigned_to=AgentRole.DESIGNER,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        # Email header
        email_task = Task(
            task_id="design_006",
            task_type="design_email_header",
            priority=TaskPriority.HIGH,
            parameters={
                "email_type": "campaign",
                "subject": "Introducing Our New Product",
                "theme": "brand",
                "include_logo": True,
            },
            assigned_to=AgentRole.DESIGNER,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        # Ad creative
        ad_task = Task(
            task_id="design_007",
            task_type="generate_ad_creative",
            priority=TaskPriority.HIGH,
            parameters={
                "ad_type": "banner",
                "size": "leaderboard",
                "message": "Transform Your Marketing Today",
                "call_to_action": "Start Free Trial",
                "brand_elements": True,
            },
            assigned_to=AgentRole.DESIGNER,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        # Execute all tasks
        social_result = await agent.execute(social_task)
        email_result = await agent.execute(email_task)
        ad_result = await agent.execute(ad_task)

        # Verify all completed
        assert social_result.status == TaskStatus.COMPLETED
        assert email_result.status == TaskStatus.COMPLETED
        assert ad_result.status == TaskStatus.COMPLETED

        # Verify correct asset types
        assert "image_url" in social_result.result
        assert "header_url" in email_result.result
        assert "ad_creative_url" in ad_result.result

        # Verify multiple API calls
        assert mock_dalle_client.generate.call_count == 3

    @pytest.mark.asyncio
    async def test_graceful_degradation_api_failure(
        self, designer_config, brand_guidelines
    ):
        """Test graceful degradation when image generation API fails."""
        agent = DesignerSpecialistAgent(
            config=designer_config, brand_guidelines=brand_guidelines
        )

        # Mock DALL-E client with failure
        failing_client = AsyncMock()
        failing_client.generate = AsyncMock(
            side_effect=Exception("API rate limit exceeded")
        )
        agent._dalle_client = failing_client

        task = Task(
            task_id="design_008",
            task_type="generate_social_graphic",
            priority=TaskPriority.NORMAL,
            parameters={"platform": "linkedin", "content_topic": "Test Topic"},
            assigned_to=AgentRole.DESIGNER,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        # Should handle error gracefully (wrapped in AgentExecutionError)
        with pytest.raises(Exception):  # AgentExecutionError
            await agent.execute(task)

    @pytest.mark.asyncio
    async def test_image_optimization_workflow(self, designer_config):
        """Test image optimization workflow."""
        agent = DesignerSpecialistAgent(config=designer_config)

        task = Task(
            task_id="design_009",
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

        # Verify optimization completed
        assert result.status == TaskStatus.COMPLETED
        assert "optimized_url" in result.result
        assert (
            "compression_ratio" in result.result or "optimized_size_kb" in result.result
        )

    @pytest.mark.asyncio
    async def test_brand_compliance_across_multiple_designs(
        self, designer_config, brand_guidelines, mock_dalle_client
    ):
        """Test that brand compliance is enforced across multiple designs."""
        agent = DesignerSpecialistAgent(
            config=designer_config, brand_guidelines=brand_guidelines
        )
        agent._dalle_client = mock_dalle_client

        designs = []
        for i in range(3):
            task = Task(
                task_id=f"design_brand_{i}",
                task_type="generate_social_graphic",
                priority=TaskPriority.NORMAL,
                parameters={
                    "platform": "linkedin",
                    "content_topic": f"Brand Test {i}",
                    "style": "professional",
                },
                assigned_to=AgentRole.DESIGNER,
                assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
                created_at=datetime.now(),
            )

            result = await agent.execute(task)
            designs.append(result)

        # Verify all have brand compliance scores
        assert all(
            "brand_compliance_score" in d.result
            for d in designs
            if d.status == TaskStatus.COMPLETED
        )

        # Verify all scores are reasonable
        assert all(
            0 <= d.result["brand_compliance_score"] <= 100
            for d in designs
            if d.status == TaskStatus.COMPLETED
        )

    @pytest.mark.asyncio
    async def test_agent_cleanup(self, designer_config):
        """Test that agent stops cleanly."""
        agent = DesignerSpecialistAgent(config=designer_config)

        # Verify available
        assert agent.is_available is True

        # Stop cleanly
        await agent.stop()

        # Verify stopped
        assert agent.is_available is False
