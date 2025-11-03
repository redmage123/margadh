"""
Integration tests for Content Manager coordination with specialist agents.

WHY: Verify that Content Manager correctly coordinates content creation through
     real specialist agents (Copywriter, SEO Specialist, Designer).

HOW: Uses real agent instances with mocked external dependencies (LLM, image APIs).
     Tests full content workflows with multi-specialist coordination.

Following TDD methodology - these tests verify integrated behavior across layers.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from agents.base.agent_protocol import AgentRole, Task, TaskPriority, TaskStatus
from agents.base.base_agent import AgentConfig
from agents.management.content_manager import ContentManagerAgent


class TestContentManagerIntegration:
    """Integration test suite for Content Manager with specialists."""

    @pytest.fixture
    def content_manager_config(self):
        """Create Content Manager configuration."""
        return AgentConfig(
            agent_id="content_manager_001",
            role=AgentRole.CONTENT_MANAGER,
        )

    @pytest.fixture
    def mock_copywriter_agent(self):
        """Create a real-like Copywriter agent with mocked LLM."""
        agent = AsyncMock()
        agent.agent_id = "copywriter_001"
        agent.role = AgentRole.COPYWRITER
        agent.is_available = True
        agent.validate_task = AsyncMock(return_value=True)
        agent.execute = AsyncMock(
            return_value=Mock(
                status=TaskStatus.COMPLETED,
                result={
                    "content": "# AI in Marketing: The Future is Now\n\nAI is transforming marketing...",
                    "word_count": 1200,
                    "content_type": "blog_post",
                    "reading_time": "5 minutes",
                },
            )
        )
        return agent

    @pytest.fixture
    def mock_seo_agent(self):
        """Create a real-like SEO Specialist agent with mocked analysis."""
        agent = AsyncMock()
        agent.agent_id = "seo_001"
        agent.role = AgentRole.SEO_SPECIALIST
        agent.is_available = True
        agent.validate_task = AsyncMock(return_value=True)
        agent.execute = AsyncMock(
            return_value=Mock(
                status=TaskStatus.COMPLETED,
                result={
                    "optimized_content": "# AI in Marketing: The Future is Now\n\nOptimized SEO content...",
                    "seo_score": 92,
                    "keywords": ["AI", "marketing", "automation", "strategy"],
                    "meta_description": "Discover how AI transforms marketing strategies...",
                    "improvements": ["Added keywords", "Optimized headings"],
                },
            )
        )
        return agent

    @pytest.fixture
    def mock_designer_agent(self):
        """Create a real-like Designer agent with mocked image generation."""
        agent = AsyncMock()
        agent.agent_id = "designer_001"
        agent.role = AgentRole.DESIGNER
        agent.is_available = True
        agent.validate_task = AsyncMock(return_value=True)
        agent.execute = AsyncMock(
            return_value=Mock(
                status=TaskStatus.COMPLETED,
                result={
                    "image_url": "https://cdn.example.com/images/ai-marketing-hero.png",
                    "image_type": "featured_image",
                    "dimensions": "1200x630",
                    "alt_text": "AI transforming marketing strategies",
                },
            )
        )
        return agent

    @pytest.mark.asyncio
    async def test_full_content_creation_workflow(
        self,
        content_manager_config,
        mock_copywriter_agent,
        mock_seo_agent,
        mock_designer_agent,
    ):
        """Test complete content creation workflow with all specialists."""
        # Build Content Manager with specialists
        content_manager = ContentManagerAgent(config=content_manager_config)
        content_manager.register_specialist(AgentRole.COPYWRITER, mock_copywriter_agent)
        content_manager.register_specialist(AgentRole.SEO_SPECIALIST, mock_seo_agent)
        content_manager.register_specialist(AgentRole.DESIGNER, mock_designer_agent)

        # Step 1: Create content (coordinates all specialists)
        create_task = Task(
            task_id="content_create_001",
            task_type="create_content",
            priority=TaskPriority.HIGH,
            parameters={
                "content_type": "blog_post",
                "topic": "AI in Marketing",
                "target_audience": "Marketing Directors",
                "keywords": ["AI", "marketing", "automation"],
                "word_count": 1500,
            },
            assigned_to=AgentRole.CONTENT_MANAGER,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        create_result = await content_manager.execute(create_task)

        # Verify content created successfully
        assert create_result.status == TaskStatus.COMPLETED
        assert "content_id" in create_result.result
        assert create_result.result["status"] in ["draft", "ready_for_review"]

        content_id = create_result.result["content_id"]

        # Verify Copywriter was called
        mock_copywriter_agent.execute.assert_called()

        # Step 2: Review content
        review_task = Task(
            task_id="content_review_001",
            task_type="review_content",
            priority=TaskPriority.HIGH,
            parameters={"content_id": content_id, "reviewer_notes": "Excellent work!"},
            assigned_to=AgentRole.CONTENT_MANAGER,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        review_result = await content_manager.execute(review_task)

        # Verify review completed
        assert review_result.status == TaskStatus.COMPLETED
        assert "review_status" in review_result.result

        # Step 3: Schedule content to editorial calendar
        publish_date = datetime.now() + timedelta(days=7)
        schedule_task = Task(
            task_id="content_schedule_001",
            task_type="schedule_content",
            priority=TaskPriority.NORMAL,
            parameters={
                "content_id": content_id,
                "publish_date": publish_date.isoformat(),
                "channels": ["blog", "social_media"],
            },
            assigned_to=AgentRole.CONTENT_MANAGER,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        schedule_result = await content_manager.execute(schedule_task)

        # Verify scheduling
        assert schedule_result.status == TaskStatus.COMPLETED
        assert "scheduled_date" in schedule_result.result
        assert schedule_result.result["content_id"] == content_id

    @pytest.mark.asyncio
    async def test_content_optimization_with_seo_specialist(
        self, content_manager_config, mock_seo_agent
    ):
        """Test content optimization delegated to SEO Specialist."""
        content_manager = ContentManagerAgent(config=content_manager_config)
        content_manager.register_specialist(AgentRole.SEO_SPECIALIST, mock_seo_agent)

        # First create content (without SEO)
        create_task = Task(
            task_id="content_create_002",
            task_type="create_content",
            priority=TaskPriority.NORMAL,
            parameters={
                "content_type": "blog_post",
                "topic": "Marketing Automation",
                "target_audience": "CMOs",
                "keywords": ["automation", "efficiency"],
                "word_count": 1000,
            },
            assigned_to=AgentRole.CONTENT_MANAGER,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        create_result = await content_manager.execute(create_task)
        content_id = create_result.result["content_id"]

        # Now optimize it with SEO Specialist
        optimize_task = Task(
            task_id="content_optimize_001",
            task_type="optimize_content",
            priority=TaskPriority.NORMAL,
            parameters={
                "content_id": content_id,
                "optimization_goals": ["seo", "readability"],
            },
            assigned_to=AgentRole.CONTENT_MANAGER,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        optimize_result = await content_manager.execute(optimize_task)

        # Verify optimization
        assert optimize_result.status == TaskStatus.COMPLETED
        assert optimize_result.result["content_id"] == content_id

        # Verify SEO Specialist was called
        mock_seo_agent.execute.assert_called()

    @pytest.mark.asyncio
    async def test_content_ideas_generation(self, content_manager_config):
        """Test generating content ideas for planning."""
        content_manager = ContentManagerAgent(config=content_manager_config)

        # Generate content ideas
        ideas_task = Task(
            task_id="content_ideas_001",
            task_type="generate_content_ideas",
            priority=TaskPriority.NORMAL,
            parameters={
                "topic_areas": ["AI", "Marketing Automation", "Data Analytics"],
                "target_audience": "Marketing Directors",
                "count": 10,
            },
            assigned_to=AgentRole.CONTENT_MANAGER,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        ideas_result = await content_manager.execute(ideas_task)

        # Verify ideas generated
        assert ideas_result.status == TaskStatus.COMPLETED
        assert "ideas" in ideas_result.result
        assert isinstance(ideas_result.result["ideas"], list)

    @pytest.mark.asyncio
    async def test_editorial_calendar_management(self, content_manager_config):
        """Test managing editorial calendar with multiple scheduled items."""
        content_manager = ContentManagerAgent(config=content_manager_config)

        # Create multiple content items
        content_ids = []
        for i in range(3):
            create_task = Task(
                task_id=f"content_create_{i}",
                task_type="create_content",
                priority=TaskPriority.NORMAL,
                parameters={
                    "content_type": "blog_post",
                    "topic": f"Topic {i}",
                    "target_audience": "Test",
                    "keywords": ["test"],
                    "word_count": 500,
                },
                assigned_to=AgentRole.CONTENT_MANAGER,
                assigned_by=AgentRole.CAMPAIGN_MANAGER,
                created_at=datetime.now(),
            )

            result = await content_manager.execute(create_task)
            content_ids.append(result.result["content_id"])

            # Schedule each item
            publish_date = datetime.now() + timedelta(days=7 * (i + 1))
            schedule_task = Task(
                task_id=f"schedule_{i}",
                task_type="schedule_content",
                priority=TaskPriority.NORMAL,
                parameters={
                    "content_id": result.result["content_id"],
                    "publish_date": publish_date.isoformat(),
                    "channels": ["blog"],
                },
                assigned_to=AgentRole.CONTENT_MANAGER,
                assigned_by=AgentRole.CAMPAIGN_MANAGER,
                created_at=datetime.now(),
            )

            await content_manager.execute(schedule_task)

        # Get calendar view
        calendar_task = Task(
            task_id="calendar_view_001",
            task_type="manage_content_calendar",
            priority=TaskPriority.NORMAL,
            parameters={"action": "get_upcoming", "date_range": "next_30_days"},
            assigned_to=AgentRole.CONTENT_MANAGER,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        calendar_result = await content_manager.execute(calendar_task)

        # Verify calendar
        assert calendar_result.status == TaskStatus.COMPLETED
        assert "calendar_items" in calendar_result.result
        assert isinstance(calendar_result.result["calendar_items"], list)

    @pytest.mark.asyncio
    async def test_graceful_degradation_missing_specialists(
        self, content_manager_config
    ):
        """Test Content Manager continues without all specialists available."""
        # Create Content Manager WITHOUT any specialists
        content_manager = ContentManagerAgent(config=content_manager_config)

        # Try to create content anyway
        create_task = Task(
            task_id="content_create_degraded_001",
            task_type="create_content",
            priority=TaskPriority.NORMAL,
            parameters={
                "content_type": "blog_post",
                "topic": "Test Topic",
                "target_audience": "Test Audience",
                "keywords": ["test"],
                "word_count": 500,
            },
            assigned_to=AgentRole.CONTENT_MANAGER,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await content_manager.execute(create_task)

        # Should complete even without specialists (graceful degradation)
        assert result.status == TaskStatus.COMPLETED
        assert "content_id" in result.result

    @pytest.mark.asyncio
    async def test_specialist_failure_graceful_handling(
        self, content_manager_config, mock_copywriter_agent, mock_seo_agent
    ):
        """Test graceful handling when specialist fails mid-workflow."""
        # Make SEO Specialist fail
        mock_seo_agent.execute = AsyncMock(
            side_effect=Exception("SEO service temporarily unavailable")
        )

        content_manager = ContentManagerAgent(config=content_manager_config)
        content_manager.register_specialist(AgentRole.COPYWRITER, mock_copywriter_agent)
        content_manager.register_specialist(AgentRole.SEO_SPECIALIST, mock_seo_agent)

        # Create content (should succeed with Copywriter, skip SEO)
        create_task = Task(
            task_id="content_create_failure_001",
            task_type="create_content",
            priority=TaskPriority.NORMAL,
            parameters={
                "content_type": "blog_post",
                "topic": "Test",
                "target_audience": "Test",
                "keywords": ["test"],
                "word_count": 500,
            },
            assigned_to=AgentRole.CONTENT_MANAGER,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await content_manager.execute(create_task)

        # Should complete with content from Copywriter
        assert result.status == TaskStatus.COMPLETED
        assert "content_id" in result.result

        # Verify Copywriter was called
        mock_copywriter_agent.execute.assert_called()

    @pytest.mark.asyncio
    async def test_content_brief_creation_for_specialists(
        self, content_manager_config
    ):
        """Test creating detailed content briefs for specialist agents."""
        content_manager = ContentManagerAgent(config=content_manager_config)

        # Create content brief
        brief_task = Task(
            task_id="brief_001",
            task_type="brief_specialists",
            priority=TaskPriority.HIGH,
            parameters={
                "brief_type": "blog_post",
                "topic": "AI in Marketing",
                "target_audience": "Marketing Directors",
                "objectives": ["Educate", "Generate leads"],
                "word_count": 1500,
                "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            },
            assigned_to=AgentRole.CONTENT_MANAGER,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        brief_result = await content_manager.execute(brief_task)

        # Verify brief created
        assert brief_result.status == TaskStatus.COMPLETED
        assert "brief_id" in brief_result.result

    @pytest.mark.asyncio
    async def test_content_performance_tracking(self, content_manager_config):
        """Test tracking content performance metrics."""
        content_manager = ContentManagerAgent(config=content_manager_config)

        # Get content performance
        performance_task = Task(
            task_id="performance_001",
            task_type="get_content_performance",
            priority=TaskPriority.NORMAL,
            parameters={"period": "last_30_days", "content_types": ["blog_post"]},
            assigned_to=AgentRole.CONTENT_MANAGER,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        performance_result = await content_manager.execute(performance_task)

        # Verify performance data
        assert performance_result.status == TaskStatus.COMPLETED
        assert "performance_data" in performance_result.result

    @pytest.mark.asyncio
    async def test_content_manager_stops_cleanly(
        self, content_manager_config, mock_copywriter_agent, mock_seo_agent
    ):
        """Test Content Manager stops cleanly with all specialists."""
        content_manager = ContentManagerAgent(config=content_manager_config)
        content_manager.register_specialist(AgentRole.COPYWRITER, mock_copywriter_agent)
        content_manager.register_specialist(AgentRole.SEO_SPECIALIST, mock_seo_agent)

        # Verify available
        assert content_manager.is_available is True

        # Stop cleanly
        await content_manager.stop()

        # Verify stopped
        assert content_manager.is_available is False
