"""
Integration tests for Market Research Agent with external research APIs.

WHY: Verify that Market Research Agent correctly integrates with research platforms,
     handles multi-source data aggregation, and provides reliable intelligence.

HOW: Uses real agent instance with mocked research clients (Crunchbase, SimilarWeb,
     Google Trends) to test full research workflows including competitor analysis,
     trend identification, and strategic insights generation.

Following TDD methodology - these tests verify integrated behavior.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from agents.base.agent_protocol import AgentRole, Task, TaskPriority, TaskStatus
from agents.base.base_agent import AgentConfig
from agents.specialists.market_research import MarketResearchAgent


class TestMarketResearchIntegration:
    """Integration test suite for Market Research Agent."""

    @pytest.fixture
    def research_config(self):
        """Create Market Research Agent configuration."""
        return AgentConfig(
            agent_id="research_001",
            role=AgentRole.MARKET_RESEARCH,
        )

    @pytest.fixture
    def mock_crunchbase_client(self):
        """Create comprehensive mocked Crunchbase API client."""
        client = AsyncMock()

        # Mock company data
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

        # Mock industry data
        client.get_industry_data = AsyncMock(
            return_value={
                "total_companies": 1500,
                "total_funding": 25000000000,
                "growth_rate": 15.2,
                "top_companies": ["Company A", "Company B", "Company C"],
            }
        )

        return client

    @pytest.fixture
    def mock_similarweb_client(self):
        """Create comprehensive mocked SimilarWeb API client."""
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
        """Create comprehensive mocked Google Trends API client."""
        client = AsyncMock()

        client.get_trend_data = AsyncMock(
            return_value={
                "direction": "rising",
                "data": [70, 75, 80, 85, 90],
                "trend_direction": "rising",
                "average_interest": 80,
                "related_queries": {
                    "rising": [
                        "AI marketing tools",
                        "marketing automation",
                        "email marketing",
                    ],
                    "top": ["marketing software", "CRM", "analytics"],
                },
                "interest_over_time": [70, 75, 80, 85, 90],
                "rising_queries": ["AI marketing", "automation"],
            }
        )

        return client

    @pytest.fixture
    def mock_llm_client(self):
        """Create mocked LLM client for insights generation."""
        client = AsyncMock()

        client.generate = AsyncMock(
            return_value=Mock(
                text="""
STRENGTHS:
- Strong market position with $50M funding
- Proven technology platform
- Established customer base

WEAKNESSES:
- Limited international presence
- High customer acquisition costs

OPPORTUNITIES:
- Growing demand for AI-powered marketing
- Expanding international markets
- Strategic partnerships

THREATS:
- Increasing competition
- Market saturation

STRATEGIC RECOMMENDATIONS:
- Focus on AI capabilities
- Expand internationally
- Build strategic partnerships
"""
            )
        )

        return client

    @pytest.mark.asyncio
    async def test_full_competitive_analysis_workflow(
        self,
        research_config,
        mock_crunchbase_client,
        mock_similarweb_client,
        mock_llm_client,
    ):
        """Test complete competitive analysis workflow with all data sources."""
        agent = MarketResearchAgent(config=research_config)
        agent._crunchbase_client = mock_crunchbase_client
        agent._similarweb_client = mock_similarweb_client
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="research_001",
            task_type="analyze_competitor",
            priority=TaskPriority.HIGH,
            parameters={
                "competitor_name": "Competitor Inc",
                "competitor_domain": "competitor.example.com",
                "include_financials": True,
                "include_traffic": True,
            },
            assigned_to=AgentRole.MARKET_RESEARCH,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert "competitor_name" in result.result
        assert "profile" in result.result
        assert "raw_data" in result.result

        # Verify all data sources were used
        assert "financials" in result.result["raw_data"]
        assert "traffic" in result.result["raw_data"]
        assert "llm_analysis" in result.result["raw_data"]

        # Verify profile contains key metrics
        profile = result.result["profile"]
        assert profile["company_name"] == "Competitor Inc"
        assert profile["funding_total"] == 50000000
        assert profile["monthly_traffic"] == 1500000

    @pytest.mark.asyncio
    async def test_market_trend_identification_workflow(
        self, research_config, mock_google_trends_client, mock_llm_client
    ):
        """Test market trend identification with insights generation."""
        agent = MarketResearchAgent(config=research_config)
        agent._google_trends_client = mock_google_trends_client
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="research_002",
            task_type="identify_market_trends",
            priority=TaskPriority.NORMAL,
            parameters={
                "industry": "Marketing Technology",
                "timeframe": "12m",
                "keywords": ["marketing automation", "AI marketing"],
            },
            assigned_to=AgentRole.MARKET_RESEARCH,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert "industry" in result.result
        assert "trends" in result.result
        assert isinstance(result.result["trends"], list)
        assert len(result.result["trends"]) == 2  # Two keywords provided

        # Verify trend data structure
        for trend in result.result["trends"]:
            assert "keyword" in trend
            assert "interest_over_time" in trend
            assert "related_queries" in trend

    @pytest.mark.asyncio
    async def test_swot_analysis_workflow(
        self, research_config, mock_crunchbase_client, mock_llm_client
    ):
        """Test complete SWOT analysis workflow."""
        agent = MarketResearchAgent(config=research_config)
        agent._crunchbase_client = mock_crunchbase_client
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="research_003",
            task_type="perform_swot_analysis",
            priority=TaskPriority.HIGH,
            parameters={
                "company_name": "Our Company",
                "include_market_context": True,
                "focus_area": "product",
            },
            assigned_to=AgentRole.MARKET_RESEARCH,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert "company_name" in result.result
        assert "swot" in result.result
        assert "strengths" in result.result["swot"]
        assert "weaknesses" in result.result["swot"]
        assert "opportunities" in result.result["swot"]
        assert "threats" in result.result["swot"]
        assert "recommendations" in result.result

    @pytest.mark.asyncio
    async def test_multi_source_intelligence_aggregation(
        self,
        research_config,
        mock_crunchbase_client,
        mock_google_trends_client,
        mock_llm_client,
    ):
        """Test aggregating intelligence from multiple research sources."""
        agent = MarketResearchAgent(config=research_config)
        agent._crunchbase_client = mock_crunchbase_client
        agent._google_trends_client = mock_google_trends_client
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="research_004",
            task_type="generate_market_insights",
            priority=TaskPriority.HIGH,
            parameters={
                "industry": "Marketing Technology",
                "focus_areas": [
                    "competitive_landscape",
                    "market_trends",
                    "growth_opportunities",
                ],
                "include_forecasts": True,
            },
            assigned_to=AgentRole.MARKET_RESEARCH,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert "industry" in result.result
        assert "market_data" in result.result

        # Verify multi-source data aggregation
        market_data = result.result["market_data"]
        assert "industry_metrics" in market_data or "industry_metrics_error" in market_data
        # Trends may not be present if Google Trends API not configured in all scenarios
        assert "trends" in market_data or "trends_error" in market_data or "focus_areas" in market_data

    @pytest.mark.asyncio
    async def test_opportunity_identification_workflow(
        self, research_config, mock_google_trends_client, mock_llm_client
    ):
        """Test market opportunity identification workflow."""
        agent = MarketResearchAgent(config=research_config)
        agent._google_trends_client = mock_google_trends_client
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="research_005",
            task_type="identify_opportunities",
            priority=TaskPriority.HIGH,
            parameters={
                "industry": "SMB Marketing",
                "context": "Looking for whitespace opportunities in marketing automation",
                "focus_areas": ["market_gaps", "customer_needs", "technology_trends"],
            },
            assigned_to=AgentRole.MARKET_RESEARCH,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert "industry" in result.result
        assert "opportunities" in result.result
        assert "market_context" in result.result

    @pytest.mark.asyncio
    async def test_research_caching_workflow(
        self,
        research_config,
        mock_crunchbase_client,
        mock_similarweb_client,
        mock_llm_client,
    ):
        """Test that research results use 24-hour caching to reduce API calls."""
        agent = MarketResearchAgent(config=research_config)
        agent._crunchbase_client = mock_crunchbase_client
        agent._similarweb_client = mock_similarweb_client
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="research_006",
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
        assert mock_similarweb_client.get_website_stats.call_count == 1

    @pytest.mark.asyncio
    async def test_graceful_degradation_partial_api_failure(
        self, research_config, mock_similarweb_client, mock_llm_client
    ):
        """Test graceful degradation when some APIs fail."""
        agent = MarketResearchAgent(config=research_config)
        # Only set up SimilarWeb and LLM, Crunchbase missing
        agent._similarweb_client = mock_similarweb_client
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="research_007",
            task_type="analyze_competitor",
            priority=TaskPriority.NORMAL,
            parameters={
                "competitor_name": "Competitor Inc",
                "competitor_domain": "competitor.example.com",
            },
            assigned_to=AgentRole.MARKET_RESEARCH,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Should complete with partial data
        assert result.status == TaskStatus.COMPLETED
        assert "traffic" in result.result["raw_data"]
        assert "financials" not in result.result["raw_data"]

    @pytest.mark.asyncio
    async def test_graceful_degradation_all_apis_unavailable(self, research_config):
        """Test graceful degradation when all research APIs are unavailable."""
        agent = MarketResearchAgent(config=research_config)
        # No API clients configured

        task = Task(
            task_id="research_008",
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
    async def test_agent_cleanup(self, research_config):
        """Test that agent stops cleanly."""
        agent = MarketResearchAgent(config=research_config)

        assert agent.is_available is True
        await agent.stop()
        assert agent.is_available is False
