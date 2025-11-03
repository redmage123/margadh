"""
Unit tests for Market Research Agent.

WHY: Ensures Market Research Agent correctly analyzes competitors, identifies trends,
     performs sentiment analysis, and generates market insights.

HOW: Uses mocked research API clients (Crunchbase, SimilarWeb, Google Trends) to test
     research operations, caching, and intelligence generation.

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


class TestMarketResearchAgent:
    """Test suite for Market Research Agent (Specialist Layer)."""

    @pytest.fixture
    def agent_config(self):
        """Create Market Research agent configuration for testing."""
        return AgentConfig(
            agent_id="research_001",
            role=AgentRole.MARKET_RESEARCH,
        )

    @pytest.fixture
    def mock_crunchbase_client(self):
        """Create mocked Crunchbase API client."""
        client = AsyncMock()
        client.get_company = AsyncMock(
            return_value={
                "name": "Competitor Inc",
                "short_description": "Leading marketing automation platform",
                "founded_year": 2015,
                "funding_total": 50000000,
                "employee_count": 175,
                "headquarters": "San Francisco, CA",
                "industry": "Marketing Technology",
                "website": "https://competitor.example.com",
                "investors": ["VC Fund A", "VC Fund B"],
                "funding_rounds": 3,
                "last_funding_date": "2024-01-15",
            }
        )
        return client

    @pytest.fixture
    def mock_similarweb_client(self):
        """Create mocked SimilarWeb API client."""
        client = AsyncMock()
        client.get_website_stats = AsyncMock(
            return_value={
                "monthly_visits": 1500000,
                "traffic_sources": {
                    "direct": 30,
                    "search": 40,
                    "social": 20,
                    "referral": 10,
                },
                "top_countries": ["US", "UK", "CA"],
                "bounce_rate": 45.2,
                "pages_per_visit": 3.8,
                "avg_visit_duration": 180,
                "global_rank": 15000,
                "category_rank": 150,
                "device_distribution": {"desktop": 60, "mobile": 40},
            }
        )
        return client

    @pytest.fixture
    def mock_google_trends_client(self):
        """Create mocked Google Trends API client."""
        client = AsyncMock()
        client.get_trend_data = AsyncMock(
            return_value={
                "direction": "rising",
                "data": [70, 75, 80, 85, 90],
                "related_queries": {
                    "rising": [
                        "AI marketing tools",
                        "marketing automation",
                        "email marketing",
                    ],
                    "top": ["marketing software", "CRM", "analytics"],
                },
            }
        )
        return client

    @pytest.fixture
    def mock_llm_client(self):
        """Create mocked LLM client for insights generation."""
        client = AsyncMock()
        client.generate = AsyncMock(
            return_value=Mock(
                text="Strategic analysis: Competitor shows strong market position with significant funding. Key differentiators needed in AI/ML capabilities."
            )
        )
        return client

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent_config):
        """Test that Market Research Agent initializes correctly."""
        from agents.specialists.market_research import MarketResearchAgent

        agent = MarketResearchAgent(config=agent_config)

        assert agent.agent_id == "research_001"
        assert agent.role == AgentRole.MARKET_RESEARCH
        assert agent.is_available is True

    @pytest.mark.asyncio
    async def test_analyze_competitor(
        self,
        agent_config,
        mock_crunchbase_client,
        mock_similarweb_client,
        mock_llm_client,
    ):
        """Test analyzing specific competitor."""
        from agents.specialists.market_research import MarketResearchAgent

        agent = MarketResearchAgent(config=agent_config)
        agent._crunchbase_client = mock_crunchbase_client
        agent._similarweb_client = mock_similarweb_client
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="task_001",
            task_type="analyze_competitor",
            priority=TaskPriority.HIGH,
            parameters={
                "competitor_name": "Competitor Inc",
                "depth": "standard",
            },
            assigned_to=AgentRole.MARKET_RESEARCH,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "competitor_name" in result.result
        assert "profile" in result.result
        assert "raw_data" in result.result
        mock_crunchbase_client.get_company.assert_called()
        mock_similarweb_client.get_website_stats.assert_called()

    @pytest.mark.asyncio
    async def test_identify_market_trends(
        self, agent_config, mock_google_trends_client, mock_llm_client
    ):
        """Test identifying market trends."""
        from agents.specialists.market_research import MarketResearchAgent

        agent = MarketResearchAgent(config=agent_config)
        agent._google_trends_client = mock_google_trends_client
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="task_002",
            task_type="identify_market_trends",
            priority=TaskPriority.NORMAL,
            parameters={
                "industry": "marketing automation",
                "timeframe": "30_days",
            },
            assigned_to=AgentRole.MARKET_RESEARCH,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "industry" in result.result
        assert "trends" in result.result
        assert isinstance(result.result["trends"], list)
        mock_google_trends_client.get_trend_data.assert_called()

    @pytest.mark.asyncio
    async def test_analyze_sentiment(self, agent_config, mock_llm_client):
        """Test customer sentiment analysis."""
        from agents.specialists.market_research import MarketResearchAgent

        agent = MarketResearchAgent(config=agent_config)
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="task_003",
            task_type="analyze_sentiment",
            priority=TaskPriority.NORMAL,
            parameters={
                "data_sources": ["reviews", "social_media"],
                "target": "Our Product",
            },
            assigned_to=AgentRole.MARKET_RESEARCH,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "target" in result.result
        assert "sentiment_scores" in result.result
        assert "overall_sentiment" in result.result

    @pytest.mark.asyncio
    async def test_research_industry(
        self, agent_config, mock_crunchbase_client, mock_llm_client
    ):
        """Test industry research."""
        from agents.specialists.market_research import MarketResearchAgent

        agent = MarketResearchAgent(config=agent_config)
        agent._crunchbase_client = mock_crunchbase_client
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="task_004",
            task_type="research_industry",
            priority=TaskPriority.NORMAL,
            parameters={
                "industry": "Marketing Technology",
                "focus_areas": ["market_size", "growth_rate", "key_players"],
            },
            assigned_to=AgentRole.MARKET_RESEARCH,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "industry" in result.result
        assert "industry_research" in result.result

    @pytest.mark.asyncio
    async def test_perform_swot_analysis(self, agent_config, mock_llm_client):
        """Test SWOT analysis."""
        from agents.specialists.market_research import MarketResearchAgent

        agent = MarketResearchAgent(config=agent_config)
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="task_005",
            task_type="perform_swot_analysis",
            priority=TaskPriority.HIGH,
            parameters={
                "company_name": "Our Company",
                "include_market_context": True,
            },
            assigned_to=AgentRole.MARKET_RESEARCH,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "swot" in result.result
        assert "strengths" in result.result["swot"]
        assert "weaknesses" in result.result["swot"]
        assert "opportunities" in result.result["swot"]
        assert "threats" in result.result["swot"]

    @pytest.mark.asyncio
    async def test_track_competitor_activity(
        self, agent_config, mock_crunchbase_client
    ):
        """Test tracking competitor activity."""
        from agents.specialists.market_research import MarketResearchAgent

        agent = MarketResearchAgent(config=agent_config)
        agent._crunchbase_client = mock_crunchbase_client

        task = Task(
            task_id="task_006",
            task_type="track_competitor_activity",
            priority=TaskPriority.NORMAL,
            parameters={
                "competitor_name": "Competitor Inc",
                "activity_types": ["product_launches", "funding", "news"],
            },
            assigned_to=AgentRole.MARKET_RESEARCH,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "competitor_name" in result.result
        assert "activities" in result.result

    @pytest.mark.asyncio
    async def test_identify_opportunities(self, agent_config, mock_llm_client):
        """Test market opportunity identification."""
        from agents.specialists.market_research import MarketResearchAgent

        agent = MarketResearchAgent(config=agent_config)
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="task_007",
            task_type="identify_opportunities",
            priority=TaskPriority.HIGH,
            parameters={
                "industry": "SMB Marketing",
                "context": "Looking for whitespace opportunities in marketing automation for small businesses",
            },
            assigned_to=AgentRole.MARKET_RESEARCH,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "industry" in result.result
        assert "opportunities" in result.result

    @pytest.mark.asyncio
    async def test_generate_market_insights(self, agent_config, mock_llm_client):
        """Test generating AI-powered market insights."""
        from agents.specialists.market_research import MarketResearchAgent

        agent = MarketResearchAgent(config=agent_config)
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="task_008",
            task_type="generate_market_insights",
            priority=TaskPriority.NORMAL,
            parameters={
                "industry": "Marketing Technology",
                "focus_areas": [
                    "competitive_landscape",
                    "market_trends",
                    "strategic_recommendations",
                ],
            },
            assigned_to=AgentRole.MARKET_RESEARCH,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "industry" in result.result
        assert "insights" in result.result or "analysis" in result.result

    @pytest.mark.asyncio
    async def test_research_caching(
        self,
        agent_config,
        mock_crunchbase_client,
        mock_similarweb_client,
        mock_llm_client,
    ):
        """Test that research results use 24-hour caching."""
        from agents.specialists.market_research import MarketResearchAgent

        agent = MarketResearchAgent(config=agent_config)
        agent._crunchbase_client = mock_crunchbase_client
        agent._similarweb_client = mock_similarweb_client
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="task_009",
            task_type="analyze_competitor",
            priority=TaskPriority.NORMAL,
            parameters={"competitor_name": "Competitor Inc"},
            assigned_to=AgentRole.MARKET_RESEARCH,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        # First call - should fetch from APIs
        result1 = await agent.execute(task)
        assert result1.status == TaskStatus.COMPLETED
        assert result1.result.get("cached") is False

        # Second call - should use cache
        result2 = await agent.execute(task)
        assert result2.status == TaskStatus.COMPLETED
        assert result2.result.get("cached") is True

        # Verify APIs only called once
        assert mock_crunchbase_client.get_company.call_count == 1

    @pytest.mark.asyncio
    async def test_validate_task_analyze_competitor(self, agent_config):
        """Test task validation for analyze_competitor task type."""
        from agents.specialists.market_research import MarketResearchAgent

        agent = MarketResearchAgent(config=agent_config)

        # Valid task
        valid_task = Task(
            task_id="task_010",
            task_type="analyze_competitor",
            priority=TaskPriority.NORMAL,
            parameters={"competitor_name": "Competitor Inc"},
            assigned_to=AgentRole.MARKET_RESEARCH,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(valid_task)
        assert is_valid is True

        # Invalid task (missing required field)
        invalid_task = Task(
            task_id="task_011",
            task_type="analyze_competitor",
            priority=TaskPriority.NORMAL,
            parameters={},  # Missing competitor_name
            assigned_to=AgentRole.MARKET_RESEARCH,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(invalid_task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_unsupported_task_type(self, agent_config):
        """Test that unsupported task types are rejected."""
        from agents.specialists.market_research import MarketResearchAgent

        agent = MarketResearchAgent(config=agent_config)

        task = Task(
            task_id="task_012",
            task_type="unsupported_task",
            priority=TaskPriority.NORMAL,
            parameters={},
            assigned_to=AgentRole.MARKET_RESEARCH,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_graceful_degradation_no_apis(self, agent_config):
        """Test graceful degradation when research APIs are unavailable."""
        from agents.specialists.market_research import MarketResearchAgent

        agent = MarketResearchAgent(config=agent_config)
        # No API clients configured

        task = Task(
            task_id="task_013",
            task_type="analyze_competitor",
            priority=TaskPriority.NORMAL,
            parameters={"competitor_name": "Competitor Inc"},
            assigned_to=AgentRole.MARKET_RESEARCH,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Should complete with error message (graceful degradation)
        assert result.status == TaskStatus.COMPLETED
        assert "error" in result.result

    @pytest.mark.asyncio
    async def test_agent_stops_cleanly(self, agent_config):
        """Test that agent stops cleanly."""
        from agents.specialists.market_research import MarketResearchAgent

        agent = MarketResearchAgent(config=agent_config)

        # Should not raise exception
        await agent.stop()

        # Agent should no longer be available
        assert agent.is_available is False
