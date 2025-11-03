"""
Unit tests for Content Manager Agent.

WHY: Ensures Content Manager correctly coordinates content creation, manages
     editorial calendar, and ensures quality across specialist agents.

HOW: Uses mocked specialist agents (Copywriter, SEO, Designer) to test
     delegation, content workflows, and quality control.

Following TDD methodology (RED-GREEN-REFACTOR):
- Write tests FIRST (these tests will fail initially)
- Implement agent to make tests pass
- Refactor while keeping tests green
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from agents.base.agent_protocol import AgentRole, Task, TaskPriority, TaskStatus
from agents.base.base_agent import AgentConfig


class TestContentManagerAgent:
    """Test suite for Content Manager Agent (Management Layer)."""

    @pytest.fixture
    def agent_config(self):
        """Create Content Manager agent configuration for testing."""
        return AgentConfig(
            agent_id="content_001",
            role=AgentRole.CONTENT_MANAGER,
        )

    @pytest.fixture
    def mock_copywriter(self):
        """Create mocked Copywriter agent."""
        agent = AsyncMock()
        agent.agent_id = "copywriter_001"
        agent.role = AgentRole.COPYWRITER
        agent.is_available = True
        agent.validate_task = AsyncMock(return_value=True)
        agent.execute = AsyncMock(
            return_value=Mock(
                status=TaskStatus.COMPLETED,
                result={
                    "content": "# Test Blog Post\n\nThis is test content.",
                    "word_count": 500,
                    "content_type": "blog_post",
                },
            )
        )
        return agent

    @pytest.fixture
    def mock_seo_specialist(self):
        """Create mocked SEO Specialist agent."""
        agent = AsyncMock()
        agent.agent_id = "seo_001"
        agent.role = AgentRole.SEO_SPECIALIST
        agent.is_available = True
        agent.validate_task = AsyncMock(return_value=True)
        agent.execute = AsyncMock(
            return_value=Mock(
                status=TaskStatus.COMPLETED,
                result={
                    "optimized_content": "# Test Blog Post (Optimized)\n\nSEO content.",
                    "seo_score": 85,
                    "keywords": ["test", "content", "blog"],
                },
            )
        )
        return agent

    @pytest.fixture
    def mock_designer(self):
        """Create mocked Designer agent."""
        agent = AsyncMock()
        agent.agent_id = "designer_001"
        agent.role = AgentRole.DESIGNER
        agent.is_available = True
        agent.validate_task = AsyncMock(return_value=True)
        agent.execute = AsyncMock(
            return_value=Mock(
                status=TaskStatus.COMPLETED,
                result={
                    "image_url": "https://example.com/image.png",
                    "image_type": "featured_image",
                    "dimensions": "1200x630",
                },
            )
        )
        return agent

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent_config):
        """Test that Content Manager Agent initializes correctly."""
        from agents.management.content_manager import ContentManagerAgent

        agent = ContentManagerAgent(config=agent_config)

        assert agent.agent_id == "content_001"
        assert agent.role == AgentRole.CONTENT_MANAGER
        assert agent.is_available is True

    @pytest.mark.asyncio
    async def test_register_specialist_agents(
        self, agent_config, mock_copywriter, mock_seo_specialist, mock_designer
    ):
        """Test registering specialist agents."""
        from agents.management.content_manager import ContentManagerAgent

        agent = ContentManagerAgent(config=agent_config)

        # Register specialists
        agent.register_specialist(AgentRole.COPYWRITER, mock_copywriter)
        agent.register_specialist(AgentRole.SEO_SPECIALIST, mock_seo_specialist)
        agent.register_specialist(AgentRole.DESIGNER, mock_designer)

        # Verify specialists are registered
        assert agent.has_specialist(AgentRole.COPYWRITER) is True
        assert agent.has_specialist(AgentRole.SEO_SPECIALIST) is True
        assert agent.has_specialist(AgentRole.DESIGNER) is True

    @pytest.mark.asyncio
    async def test_create_content(
        self, agent_config, mock_copywriter, mock_seo_specialist, mock_designer
    ):
        """Test creating content with specialist coordination."""
        from agents.management.content_manager import ContentManagerAgent

        agent = ContentManagerAgent(config=agent_config)
        agent.register_specialist(AgentRole.COPYWRITER, mock_copywriter)
        agent.register_specialist(AgentRole.SEO_SPECIALIST, mock_seo_specialist)
        agent.register_specialist(AgentRole.DESIGNER, mock_designer)

        task = Task(
            task_id="task_001",
            task_type="create_content",
            priority=TaskPriority.NORMAL,
            parameters={
                "content_type": "blog_post",
                "topic": "AI in Marketing",
                "target_audience": "Marketing Directors",
                "keywords": ["AI", "marketing", "automation"],
                "word_count": 1000,
            },
            assigned_to=AgentRole.CONTENT_MANAGER,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "content_id" in result.result
        assert result.result["status"] in ["draft", "ready_for_review"]

        # Verify Copywriter was called
        mock_copywriter.execute.assert_called()

    @pytest.mark.asyncio
    async def test_review_content_approved(self, agent_config):
        """Test reviewing content with approval."""
        from agents.management.content_manager import ContentManagerAgent

        agent = ContentManagerAgent(config=agent_config)

        # First create content
        create_task = Task(
            task_id="task_001",
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

        create_result = await agent.execute(create_task)
        content_id = create_result.result["content_id"]

        # Now review it
        review_task = Task(
            task_id="task_002",
            task_type="review_content",
            priority=TaskPriority.HIGH,
            parameters={"content_id": content_id, "reviewer_notes": "Looks good!"},
            assigned_to=AgentRole.CONTENT_MANAGER,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(review_task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "content_id" in result.result
        assert "review_status" in result.result
        assert result.result["review_status"] in ["approved", "revision", "rejected"]

    @pytest.mark.asyncio
    async def test_schedule_content(self, agent_config):
        """Test scheduling content to editorial calendar."""
        from agents.management.content_manager import ContentManagerAgent

        agent = ContentManagerAgent(config=agent_config)

        # Create content first
        create_task = Task(
            task_id="task_001",
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

        create_result = await agent.execute(create_task)
        content_id = create_result.result["content_id"]

        # Schedule it
        publish_date = datetime.now() + timedelta(days=7)
        schedule_task = Task(
            task_id="task_002",
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

        result = await agent.execute(schedule_task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert result.result["content_id"] == content_id
        assert "scheduled_date" in result.result

    @pytest.mark.asyncio
    async def test_generate_content_ideas(self, agent_config):
        """Test generating content ideas."""
        from agents.management.content_manager import ContentManagerAgent

        agent = ContentManagerAgent(config=agent_config)

        task = Task(
            task_id="task_001",
            task_type="generate_content_ideas",
            priority=TaskPriority.NORMAL,
            parameters={
                "topic_areas": ["AI", "Marketing Automation", "Data Analytics"],
                "target_audience": "Marketing Directors",
                "count": 5,
            },
            assigned_to=AgentRole.CONTENT_MANAGER,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "ideas" in result.result
        assert isinstance(result.result["ideas"], list)

    @pytest.mark.asyncio
    async def test_optimize_content(self, agent_config, mock_seo_specialist):
        """Test optimizing existing content."""
        from agents.management.content_manager import ContentManagerAgent

        agent = ContentManagerAgent(config=agent_config)
        agent.register_specialist(AgentRole.SEO_SPECIALIST, mock_seo_specialist)

        # Create content first
        create_task = Task(
            task_id="task_001",
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

        create_result = await agent.execute(create_task)
        content_id = create_result.result["content_id"]

        # Optimize it
        optimize_task = Task(
            task_id="task_002",
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

        result = await agent.execute(optimize_task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "content_id" in result.result

    @pytest.mark.asyncio
    async def test_get_content_performance(self, agent_config):
        """Test getting content performance metrics."""
        from agents.management.content_manager import ContentManagerAgent

        agent = ContentManagerAgent(config=agent_config)

        task = Task(
            task_id="task_001",
            task_type="get_content_performance",
            priority=TaskPriority.NORMAL,
            parameters={"period": "last_30_days", "content_types": ["blog_post"]},
            assigned_to=AgentRole.CONTENT_MANAGER,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "performance_data" in result.result

    @pytest.mark.asyncio
    async def test_manage_content_calendar(self, agent_config):
        """Test managing editorial calendar."""
        from agents.management.content_manager import ContentManagerAgent

        agent = ContentManagerAgent(config=agent_config)

        task = Task(
            task_id="task_001",
            task_type="manage_content_calendar",
            priority=TaskPriority.NORMAL,
            parameters={
                "action": "get_upcoming",
                "date_range": "next_30_days",
            },
            assigned_to=AgentRole.CONTENT_MANAGER,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "calendar_items" in result.result

    @pytest.mark.asyncio
    async def test_brief_specialists(self, agent_config):
        """Test creating content briefs for specialists."""
        from agents.management.content_manager import ContentManagerAgent

        agent = ContentManagerAgent(config=agent_config)

        task = Task(
            task_id="task_001",
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

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "brief_id" in result.result

    @pytest.mark.asyncio
    async def test_validate_task_create_content(self, agent_config):
        """Test task validation for create_content task type."""
        from agents.management.content_manager import ContentManagerAgent

        agent = ContentManagerAgent(config=agent_config)

        # Valid task
        valid_task = Task(
            task_id="task_001",
            task_type="create_content",
            priority=TaskPriority.NORMAL,
            parameters={
                "content_type": "blog_post",
                "topic": "Test Topic",
                "target_audience": "Test Audience",
                "keywords": ["test"],
                "word_count": 1000,
            },
            assigned_to=AgentRole.CONTENT_MANAGER,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(valid_task)
        assert is_valid is True

        # Invalid task (missing required fields)
        invalid_task = Task(
            task_id="task_002",
            task_type="create_content",
            priority=TaskPriority.NORMAL,
            parameters={"content_type": "blog_post"},  # Missing required fields
            assigned_to=AgentRole.CONTENT_MANAGER,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(invalid_task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_unsupported_task_type(self, agent_config):
        """Test that unsupported task types are rejected."""
        from agents.management.content_manager import ContentManagerAgent

        agent = ContentManagerAgent(config=agent_config)

        task = Task(
            task_id="task_001",
            task_type="unsupported_task",
            priority=TaskPriority.NORMAL,
            parameters={},
            assigned_to=AgentRole.CONTENT_MANAGER,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_graceful_degradation_specialist_failure(
        self, agent_config, mock_copywriter, mock_seo_specialist
    ):
        """Test graceful degradation when specialist fails."""
        from agents.management.content_manager import ContentManagerAgent

        # Make SEO specialist fail
        mock_seo_specialist.execute = AsyncMock(
            side_effect=Exception("SEO service unavailable")
        )

        agent = ContentManagerAgent(config=agent_config)
        agent.register_specialist(AgentRole.COPYWRITER, mock_copywriter)
        agent.register_specialist(AgentRole.SEO_SPECIALIST, mock_seo_specialist)

        task = Task(
            task_id="task_001",
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

        result = await agent.execute(task)

        # Should complete with content from Copywriter, without SEO
        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        # Copywriter should have been called
        mock_copywriter.execute.assert_called()

    @pytest.mark.asyncio
    async def test_agent_stops_cleanly(
        self, agent_config, mock_copywriter, mock_seo_specialist
    ):
        """Test that agent stops cleanly."""
        from agents.management.content_manager import ContentManagerAgent

        agent = ContentManagerAgent(config=agent_config)
        agent.register_specialist(AgentRole.COPYWRITER, mock_copywriter)
        agent.register_specialist(AgentRole.SEO_SPECIALIST, mock_seo_specialist)

        # Should not raise exception
        await agent.stop()

        # Agent should no longer be available
        assert agent.is_available is False
