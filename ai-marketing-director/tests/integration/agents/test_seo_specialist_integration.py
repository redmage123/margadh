"""
Integration tests for SEO Specialist with external API clients.

WHY: Verify that SEO Specialist correctly integrates with external SEO tools,
     handles caching, and provides accurate analysis.

HOW: Uses real agent instance with mocked external API clients (SEMrush,
     Search Console, LLM) to test full SEO workflows.

Following TDD methodology - these tests verify integrated behavior.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from agents.base.agent_protocol import AgentRole, Task, TaskPriority, TaskStatus
from agents.base.base_agent import AgentConfig
from agents.specialists.seo_specialist import SEOSpecialistAgent


class TestSEOSpecialistIntegration:
    """Integration test suite for SEO Specialist."""

    @pytest.fixture
    def seo_config(self):
        """Create SEO Specialist configuration."""
        return AgentConfig(
            agent_id="seo_001",
            role=AgentRole.SEO_SPECIALIST,
        )

    @pytest.fixture
    def mock_semrush_client(self):
        """Create mocked SEMrush API client with comprehensive data."""
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
                    },
                    {
                        "keyword": "marketing automation software",
                        "search_volume": 6200,
                        "difficulty": 62,
                        "cpc": 15.30,
                        "intent": "commercial",
                    },
                ],
                "secondary": [
                    {
                        "keyword": "AI marketing platform",
                        "search_volume": 3200,
                        "difficulty": 58,
                        "cpc": 11.20,
                        "intent": "commercial",
                    }
                ],
                "long_tail": [
                    {
                        "keyword": "best AI marketing tools 2025",
                        "search_volume": 720,
                        "difficulty": 48,
                        "cpc": 9.80,
                        "intent": "commercial",
                    }
                ],
                "volume": {"total": 18220, "average": 6073},
                "difficulty": {"average": 58.3},
            }
        )
        client.analyze_serp = AsyncMock(
            return_value={
                "results": [
                    {
                        "position": 1,
                        "url": "https://example.com/ai-marketing-tools",
                        "title": "15 Best AI Marketing Tools for 2025",
                        "domain_authority": 72,
                        "word_count": 3500,
                        "content_type": "listicle",
                    }
                ],
                "competition_level": "high",
            }
        )
        return client

    @pytest.fixture
    def mock_llm_client(self):
        """Create mocked LLM client for AI-powered analysis."""
        client = AsyncMock()
        client.generate = AsyncMock(
            return_value=Mock(
                text="Target 'AI marketing tools' as primary focus keyword. Include long-tail variations for content sections. Balance difficulty with search volume for optimal results."
            )
        )
        return client

    @pytest.mark.asyncio
    async def test_full_keyword_research_workflow(
        self, seo_config, mock_semrush_client, mock_llm_client
    ):
        """Test complete keyword research workflow with AI analysis."""
        agent = SEOSpecialistAgent(config=seo_config)
        agent._semrush_client = mock_semrush_client
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="seo_001",
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

        # Verify result structure
        assert result.status == TaskStatus.COMPLETED
        assert "primary_keywords" in result.result
        assert "secondary_keywords" in result.result
        assert "long_tail_keywords" in result.result
        assert "recommendations" in result.result

        # Verify API calls
        mock_semrush_client.keyword_research.assert_called_once()
        mock_llm_client.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_content_optimization_with_scoring(
        self, seo_config, mock_llm_client
    ):
        """Test content optimization with SEO score calculation."""
        agent = SEOSpecialistAgent(config=seo_config)
        agent._llm_client = mock_llm_client

        content = """# AI Marketing Tools for 2025

Marketing teams are leveraging AI marketing tools to improve efficiency.

## Benefits of AI Marketing Tools

These tools help with automation and data analysis."""

        task = Task(
            task_id="seo_002",
            task_type="optimize_content",
            priority=TaskPriority.HIGH,
            parameters={
                "content": content,
                "target_keywords": ["AI marketing tools", "marketing automation"],
                "content_type": "blog_post",
            },
            assigned_to=AgentRole.SEO_SPECIALIST,
            assigned_by=AgentRole.COPYWRITER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Verify optimization result
        assert result.status == TaskStatus.COMPLETED
        assert "current_score" in result.result
        assert "suggestions" in result.result
        assert result.result["current_score"] > 0
        assert isinstance(result.result["suggestions"], list)

    @pytest.mark.asyncio
    async def test_serp_analysis_with_competitive_insights(
        self, seo_config, mock_semrush_client
    ):
        """Test SERP analysis with competitive intelligence."""
        agent = SEOSpecialistAgent(config=seo_config)
        agent._semrush_client = mock_semrush_client

        task = Task(
            task_id="seo_003",
            task_type="analyze_serp",
            priority=TaskPriority.NORMAL,
            parameters={"keyword": "AI marketing tools", "location": "US"},
            assigned_to=AgentRole.SEO_SPECIALIST,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Verify SERP analysis
        assert result.status == TaskStatus.COMPLETED
        assert "top_results" in result.result or "competition_level" in result.result
        assert "opportunity_score" in result.result
        assert "recommendations" in result.result

        # Verify API call
        mock_semrush_client.analyze_serp.assert_called_once()

    @pytest.mark.asyncio
    async def test_keyword_caching_effectiveness(
        self, seo_config, mock_semrush_client, mock_llm_client
    ):
        """Test that keyword caching reduces API calls."""
        agent = SEOSpecialistAgent(config=seo_config)
        agent._semrush_client = mock_semrush_client
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="seo_004",
            task_type="keyword_research",
            priority=TaskPriority.NORMAL,
            parameters={"topic": "Marketing Automation", "language": "en"},
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

        # Verify caching worked (only one API call)
        assert mock_semrush_client.keyword_research.call_count == 1

        # Verify cache indicator
        assert result2.result.get("cached") is True

    @pytest.mark.asyncio
    async def test_meta_description_generation(self, seo_config, mock_llm_client):
        """Test meta description generation with AI."""
        agent = SEOSpecialistAgent(config=seo_config)
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="seo_005",
            task_type="generate_meta_descriptions",
            priority=TaskPriority.NORMAL,
            parameters={
                "content": "Comprehensive guide about AI marketing tools...",
                "target_keywords": ["AI marketing tools"],
                "variations": 3,
            },
            assigned_to=AgentRole.SEO_SPECIALIST,
            assigned_by=AgentRole.COPYWRITER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Verify meta descriptions
        assert result.status == TaskStatus.COMPLETED
        assert "meta_descriptions" in result.result
        assert isinstance(result.result["meta_descriptions"], list)
        assert "title_tags" in result.result

    @pytest.mark.asyncio
    async def test_graceful_degradation_no_semrush(self, seo_config):
        """Test graceful degradation when SEMrush is unavailable."""
        agent = SEOSpecialistAgent(config=seo_config)
        # No SEMrush client configured

        task = Task(
            task_id="seo_006",
            task_type="keyword_research",
            priority=TaskPriority.NORMAL,
            parameters={"topic": "Marketing Tools", "language": "en"},
            assigned_to=AgentRole.SEO_SPECIALIST,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Should complete with fallback data
        assert result.status == TaskStatus.COMPLETED
        assert "primary_keywords" in result.result

    @pytest.mark.asyncio
    async def test_seo_audit_workflow(self, seo_config):
        """Test SEO audit workflow."""
        agent = SEOSpecialistAgent(config=seo_config)

        task = Task(
            task_id="seo_007",
            task_type="audit_seo",
            priority=TaskPriority.HIGH,
            parameters={"content_id": "blog_001", "scope": "on_page"},
            assigned_to=AgentRole.SEO_SPECIALIST,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Verify audit result
        assert result.status == TaskStatus.COMPLETED
        assert "overall_score" in result.result
        assert "issues" in result.result
        assert "recommendations" in result.result

    @pytest.mark.asyncio
    async def test_agent_cleanup(self, seo_config):
        """Test that agent stops cleanly."""
        agent = SEOSpecialistAgent(config=seo_config)

        # Verify available
        assert agent.is_available is True

        # Stop cleanly
        await agent.stop()

        # Verify stopped
        assert agent.is_available is False
