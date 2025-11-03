"""
Unit tests for SEO Specialist Agent.

WHY: Ensures SEO Specialist correctly performs keyword research, content optimization,
     SERP analysis, and tracking with external API integration.

HOW: Uses mocked SEO tool clients (SEMrush, Search Console) to test SEO operations,
     caching, and graceful degradation.

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


class TestSEOSpecialistAgent:
    """Test suite for SEO Specialist Agent (Specialist Layer)."""

    @pytest.fixture
    def agent_config(self):
        """Create SEO Specialist agent configuration for testing."""
        return AgentConfig(
            agent_id="seo_001",
            role=AgentRole.SEO_SPECIALIST,
        )

    @pytest.fixture
    def mock_semrush_client(self):
        """Create mocked SEMrush API client."""
        client = AsyncMock()
        client.keyword_research = AsyncMock(
            return_value={
                "primary": [
                    {
                        "keyword": "AI marketing tools",
                        "search_volume": 8100,
                        "difficulty": 65,
                        "cpc": 12.50,
                        "intent": "commercial",
                    }
                ],
                "secondary": [
                    {
                        "keyword": "marketing automation AI",
                        "search_volume": 3200,
                        "difficulty": 58,
                        "cpc": 10.20,
                        "intent": "commercial",
                    }
                ],
                "long_tail": [
                    {
                        "keyword": "best AI marketing tools for small business",
                        "search_volume": 480,
                        "difficulty": 42,
                        "cpc": 8.50,
                        "intent": "commercial",
                    }
                ],
                "volume": {"total": 12000, "average": 4000},
                "difficulty": {"average": 55.0},
            }
        )
        return client

    @pytest.fixture
    def mock_search_console_client(self):
        """Create mocked Google Search Console API client."""
        client = AsyncMock()
        client.get_rankings = AsyncMock(
            return_value={
                "rankings": [
                    {
                        "keyword": "AI marketing tools",
                        "position": 12,
                        "clicks": 450,
                        "impressions": 5200,
                        "ctr": 8.7,
                    }
                ]
            }
        )
        return client

    @pytest.fixture
    def mock_llm_client(self):
        """Create mocked LLM client for SEO analysis."""
        client = AsyncMock()
        client.generate = AsyncMock(
            return_value=Mock(
                text="Based on analysis, target 'AI marketing automation' as primary focus keyword. Include long-tail variations."
            )
        )
        return client

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent_config):
        """Test that SEO Specialist Agent initializes correctly."""
        from agents.specialists.seo_specialist import SEOSpecialistAgent

        agent = SEOSpecialistAgent(config=agent_config)

        assert agent.agent_id == "seo_001"
        assert agent.role == AgentRole.SEO_SPECIALIST
        assert agent.is_available is True

    @pytest.mark.asyncio
    async def test_keyword_research(self, agent_config, mock_semrush_client):
        """Test keyword research with SEO tools."""
        from agents.specialists.seo_specialist import SEOSpecialistAgent

        agent = SEOSpecialistAgent(config=agent_config)
        agent._semrush_client = mock_semrush_client

        task = Task(
            task_id="task_001",
            task_type="keyword_research",
            priority=TaskPriority.NORMAL,
            parameters={
                "topic": "AI Marketing Tools",
                "target_audience": "Marketing Directors",
                "language": "en",
                "count": 20,
            },
            assigned_to=AgentRole.SEO_SPECIALIST,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "primary_keywords" in result.result
        assert "secondary_keywords" in result.result
        assert "long_tail_keywords" in result.result
        assert "recommendations" in result.result
        mock_semrush_client.keyword_research.assert_called()

    @pytest.mark.asyncio
    async def test_optimize_content(
        self, agent_config, mock_semrush_client, mock_llm_client
    ):
        """Test content SEO optimization."""
        from agents.specialists.seo_specialist import SEOSpecialistAgent

        agent = SEOSpecialistAgent(config=agent_config)
        agent._semrush_client = mock_semrush_client
        agent._llm_client = mock_llm_client

        content = """# AI Marketing Tools

        Marketing teams need powerful tools to succeed. This article covers various options available."""

        task = Task(
            task_id="task_002",
            task_type="optimize_content",
            priority=TaskPriority.HIGH,
            parameters={
                "content": content,
                "target_keywords": ["AI marketing tools", "marketing automation"],
            },
            assigned_to=AgentRole.SEO_SPECIALIST,
            assigned_by=AgentRole.COPYWRITER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "current_score" in result.result
        assert "suggestions" in result.result
        assert isinstance(result.result["suggestions"], list)

    @pytest.mark.asyncio
    async def test_analyze_serp(self, agent_config, mock_semrush_client):
        """Test SERP analysis for target keyword."""
        from agents.specialists.seo_specialist import SEOSpecialistAgent

        # Mock SERP data
        mock_semrush_client.analyze_serp = AsyncMock(
            return_value={
                "results": [
                    {
                        "position": 1,
                        "url": "https://example.com/ai-marketing-tools",
                        "title": "15 Best AI Marketing Tools",
                        "domain_authority": 72,
                        "word_count": 3500,
                    }
                ],
                "competition_level": "high",
            }
        )

        agent = SEOSpecialistAgent(config=agent_config)
        agent._semrush_client = mock_semrush_client

        task = Task(
            task_id="task_003",
            task_type="analyze_serp",
            priority=TaskPriority.NORMAL,
            parameters={"keyword": "AI marketing tools", "location": "US"},
            assigned_to=AgentRole.SEO_SPECIALIST,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "top_results" in result.result or "competition_level" in result.result

    @pytest.mark.asyncio
    async def test_generate_meta_descriptions(self, agent_config, mock_llm_client):
        """Test meta description generation."""
        from agents.specialists.seo_specialist import SEOSpecialistAgent

        mock_llm_client.generate = AsyncMock(
            return_value=Mock(
                text="Discover 15 powerful AI marketing tools that streamline campaigns, boost ROI, and automate content creation."
            )
        )

        agent = SEOSpecialistAgent(config=agent_config)
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="task_004",
            task_type="generate_meta_descriptions",
            priority=TaskPriority.NORMAL,
            parameters={
                "content": "Article about AI marketing tools...",
                "target_keywords": ["AI marketing tools"],
                "variations": 3,
            },
            assigned_to=AgentRole.SEO_SPECIALIST,
            assigned_by=AgentRole.COPYWRITER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "meta_descriptions" in result.result
        assert isinstance(result.result["meta_descriptions"], list)

    @pytest.mark.asyncio
    async def test_suggest_internal_links(self, agent_config):
        """Test internal linking suggestions."""
        from agents.specialists.seo_specialist import SEOSpecialistAgent

        agent = SEOSpecialistAgent(config=agent_config)

        task = Task(
            task_id="task_005",
            task_type="suggest_internal_links",
            priority=TaskPriority.NORMAL,
            parameters={
                "content_id": "blog_001",
                "content": "Article about marketing automation and AI tools...",
                "max_suggestions": 5,
            },
            assigned_to=AgentRole.SEO_SPECIALIST,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "suggestions" in result.result

    @pytest.mark.asyncio
    async def test_audit_seo(self, agent_config):
        """Test SEO audit functionality."""
        from agents.specialists.seo_specialist import SEOSpecialistAgent

        agent = SEOSpecialistAgent(config=agent_config)

        task = Task(
            task_id="task_006",
            task_type="audit_seo",
            priority=TaskPriority.HIGH,
            parameters={"content_id": "blog_001", "scope": "on_page"},
            assigned_to=AgentRole.SEO_SPECIALIST,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "overall_score" in result.result or "issues" in result.result

    @pytest.mark.asyncio
    async def test_track_rankings(self, agent_config, mock_search_console_client):
        """Test keyword ranking tracking."""
        from agents.specialists.seo_specialist import SEOSpecialistAgent

        agent = SEOSpecialistAgent(config=agent_config)
        agent._search_console_client = mock_search_console_client

        task = Task(
            task_id="task_007",
            task_type="track_rankings",
            priority=TaskPriority.NORMAL,
            parameters={
                "keywords": ["AI marketing tools", "marketing automation"],
                "location": "US",
            },
            assigned_to=AgentRole.SEO_SPECIALIST,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "rankings" in result.result

    @pytest.mark.asyncio
    async def test_generate_seo_report(self, agent_config):
        """Test SEO performance report generation."""
        from agents.specialists.seo_specialist import SEOSpecialistAgent

        agent = SEOSpecialistAgent(config=agent_config)

        task = Task(
            task_id="task_008",
            task_type="generate_seo_report",
            priority=TaskPriority.HIGH,
            parameters={
                "date_range": "last_30_days",
                "include_charts": True,
                "report_type": "summary",
            },
            assigned_to=AgentRole.SEO_SPECIALIST,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "report_id" in result.result or "recommendations" in result.result

    @pytest.mark.asyncio
    async def test_keyword_caching(self, agent_config, mock_semrush_client):
        """Test that keyword research results are cached."""
        from agents.specialists.seo_specialist import SEOSpecialistAgent

        agent = SEOSpecialistAgent(config=agent_config)
        agent._semrush_client = mock_semrush_client

        task = Task(
            task_id="task_009",
            task_type="keyword_research",
            priority=TaskPriority.NORMAL,
            parameters={"topic": "AI Marketing", "language": "en"},
            assigned_to=AgentRole.SEO_SPECIALIST,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        # First call - should fetch from API
        result1 = await agent.execute(task)
        assert result1.status == TaskStatus.COMPLETED

        # Second call - should use cache (same topic)
        result2 = await agent.execute(task)
        assert result2.status == TaskStatus.COMPLETED

        # API should only be called once due to caching
        assert mock_semrush_client.keyword_research.call_count == 1

    @pytest.mark.asyncio
    async def test_validate_task_keyword_research(self, agent_config):
        """Test task validation for keyword_research task type."""
        from agents.specialists.seo_specialist import SEOSpecialistAgent

        agent = SEOSpecialistAgent(config=agent_config)

        # Valid task
        valid_task = Task(
            task_id="task_010",
            task_type="keyword_research",
            priority=TaskPriority.NORMAL,
            parameters={"topic": "AI Marketing", "language": "en"},
            assigned_to=AgentRole.SEO_SPECIALIST,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(valid_task)
        assert is_valid is True

        # Invalid task (missing required field)
        invalid_task = Task(
            task_id="task_011",
            task_type="keyword_research",
            priority=TaskPriority.NORMAL,
            parameters={},  # Missing topic
            assigned_to=AgentRole.SEO_SPECIALIST,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(invalid_task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_unsupported_task_type(self, agent_config):
        """Test that unsupported task types are rejected."""
        from agents.specialists.seo_specialist import SEOSpecialistAgent

        agent = SEOSpecialistAgent(config=agent_config)

        task = Task(
            task_id="task_012",
            task_type="unsupported_task",
            priority=TaskPriority.NORMAL,
            parameters={},
            assigned_to=AgentRole.SEO_SPECIALIST,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_graceful_degradation_api_failure(self, agent_config):
        """Test graceful degradation when SEO tools API fails."""
        from agents.specialists.seo_specialist import SEOSpecialistAgent

        # Create agent with failing SEMrush client
        mock_semrush_failing = AsyncMock()
        mock_semrush_failing.keyword_research = AsyncMock(
            side_effect=Exception("SEMrush API unavailable")
        )

        agent = SEOSpecialistAgent(config=agent_config)
        agent._semrush_client = mock_semrush_failing

        task = Task(
            task_id="task_013",
            task_type="keyword_research",
            priority=TaskPriority.NORMAL,
            parameters={"topic": "AI Marketing", "language": "en"},
            assigned_to=AgentRole.SEO_SPECIALIST,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        # Should raise AgentExecutionError with wrapped exception
        with pytest.raises(Exception):
            await agent.execute(task)

    @pytest.mark.asyncio
    async def test_seo_score_calculation(self, agent_config):
        """Test SEO score calculation for content."""
        from agents.specialists.seo_specialist import SEOSpecialistAgent

        agent = SEOSpecialistAgent(config=agent_config)

        # Content with good SEO
        good_content = """# AI Marketing Tools for 2025

AI marketing tools are revolutionizing how businesses approach marketing automation.

## Benefits of AI Marketing Tools

Marketing teams using AI marketing tools see improved efficiency and better ROI.

## Top AI Marketing Tools

Here are the best AI marketing tools available today:
1. Tool A
2. Tool B
3. Tool C

In conclusion, AI marketing tools provide significant advantages for modern marketing teams."""

        # Calculate score
        score = agent._calculate_seo_score(
            good_content, ["AI marketing tools", "marketing automation"]
        )

        # Score should be positive
        assert score > 0
        assert score <= 100

    @pytest.mark.asyncio
    async def test_agent_stops_cleanly(self, agent_config):
        """Test that agent stops cleanly."""
        from agents.specialists.seo_specialist import SEOSpecialistAgent

        agent = SEOSpecialistAgent(config=agent_config)

        # Should not raise exception
        await agent.stop()

        # Agent should no longer be available
        assert agent.is_available is False
