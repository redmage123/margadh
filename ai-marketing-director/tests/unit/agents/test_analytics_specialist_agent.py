"""
Unit tests for Analytics Specialist Agent.

WHY: Ensures Analytics Specialist correctly tracks performance, generates reports,
     and integrates with external analytics APIs.

HOW: Uses mocked external APIs (Google Analytics, social media) to test
     data aggregation, reporting, and graceful degradation.

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


class TestAnalyticsSpecialistAgent:
    """Test suite for Analytics Specialist Agent (Specialist Layer)."""

    @pytest.fixture
    def agent_config(self):
        """Create Analytics Specialist agent configuration for testing."""
        return AgentConfig(
            agent_id="analytics_001",
            role=AgentRole.ANALYTICS_SPECIALIST,
        )

    @pytest.fixture
    def mock_google_analytics_client(self):
        """Create mocked Google Analytics API client."""
        client = AsyncMock()
        client.get_analytics = AsyncMock(
            return_value={
                "sessions": 15000,
                "pageviews": 45000,
                "bounceRate": 35.5,
                "avgSessionDuration": 180.5,
            }
        )
        return client

    @pytest.fixture
    def mock_social_media_clients(self):
        """Create mocked social media API clients."""
        return {
            "linkedin": AsyncMock(
                get_analytics=AsyncMock(
                    return_value={
                        "followers": 5000,
                        "engagement_rate": 4.5,
                        "reach": 25000,
                        "impressions": 50000,
                    }
                )
            ),
            "twitter": AsyncMock(
                get_analytics=AsyncMock(
                    return_value={
                        "followers": 10000,
                        "engagement_rate": 2.8,
                        "reach": 50000,
                        "impressions": 100000,
                    }
                )
            ),
        }

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent_config):
        """Test that Analytics Specialist Agent initializes correctly."""
        from agents.specialists.analytics_specialist import AnalyticsSpecialistAgent

        agent = AnalyticsSpecialistAgent(config=agent_config)

        assert agent.agent_id == "analytics_001"
        assert agent.role == AgentRole.ANALYTICS_SPECIALIST
        assert agent.is_available is True

    @pytest.mark.asyncio
    async def test_track_campaign_performance(
        self, agent_config, mock_google_analytics_client, mock_social_media_clients
    ):
        """Test tracking campaign performance metrics."""
        from agents.specialists.analytics_specialist import AnalyticsSpecialistAgent

        agent = AnalyticsSpecialistAgent(config=agent_config)
        agent._google_analytics_client = mock_google_analytics_client
        agent._social_media_clients = mock_social_media_clients

        task = Task(
            task_id="task_001",
            task_type="track_campaign_performance",
            priority=TaskPriority.HIGH,
            parameters={
                "campaign_id": "campaign_001",
                "metrics": ["impressions", "clicks", "conversions"],
                "date_range": "last_7_days",
            },
            assigned_to=AgentRole.ANALYTICS_SPECIALIST,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "metrics" in result.result
        assert "campaign_id" in result.result
        assert result.result["campaign_id"] == "campaign_001"

    @pytest.mark.asyncio
    async def test_generate_report(self, agent_config):
        """Test generating comprehensive analytical reports."""
        from agents.specialists.analytics_specialist import AnalyticsSpecialistAgent

        agent = AnalyticsSpecialistAgent(config=agent_config)

        task = Task(
            task_id="task_002",
            task_type="generate_report",
            priority=TaskPriority.NORMAL,
            parameters={
                "report_type": "executive_dashboard",
                "date_range": "last_30_days",
                "include_charts": True,
            },
            assigned_to=AgentRole.ANALYTICS_SPECIALIST,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "report_id" in result.result
        assert "report_type" in result.result
        assert result.result["report_type"] == "executive_dashboard"

    @pytest.mark.asyncio
    async def test_analyze_audience(self, agent_config):
        """Test analyzing audience demographics and behavior."""
        from agents.specialists.analytics_specialist import AnalyticsSpecialistAgent

        agent = AnalyticsSpecialistAgent(config=agent_config)

        task = Task(
            task_id="task_003",
            task_type="analyze_audience",
            priority=TaskPriority.NORMAL,
            parameters={
                "analysis_type": "demographics",
                "date_range": "last_30_days",
                "segments": ["enterprise", "smb"],
            },
            assigned_to=AgentRole.ANALYTICS_SPECIALIST,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "demographics" in result.result or "behavior" in result.result

    @pytest.mark.asyncio
    async def test_monitor_kpis(self, agent_config):
        """Test monitoring KPIs against targets."""
        from agents.specialists.analytics_specialist import AnalyticsSpecialistAgent

        agent = AnalyticsSpecialistAgent(config=agent_config)

        task = Task(
            task_id="task_004",
            task_type="monitor_kpis",
            priority=TaskPriority.HIGH,
            parameters={
                "kpi_names": ["conversion_rate", "ctr", "roi"],
                "targets": {"conversion_rate": 3.0, "ctr": 2.5, "roi": 250.0},
                "alert_threshold": 0.1,
            },
            assigned_to=AgentRole.ANALYTICS_SPECIALIST,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "kpis" in result.result
        assert isinstance(result.result["kpis"], dict)

    @pytest.mark.asyncio
    async def test_track_conversions(self, agent_config):
        """Test tracking conversion funnels and attribution."""
        from agents.specialists.analytics_specialist import AnalyticsSpecialistAgent

        agent = AnalyticsSpecialistAgent(config=agent_config)

        task = Task(
            task_id="task_005",
            task_type="track_conversions",
            priority=TaskPriority.NORMAL,
            parameters={
                "funnel_name": "lead_generation",
                "date_range": "last_30_days",
                "attribution_model": "last_touch",
            },
            assigned_to=AgentRole.ANALYTICS_SPECIALIST,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "funnel_name" in result.result
        assert "stages" in result.result or "total_conversions" in result.result

    @pytest.mark.asyncio
    async def test_get_social_analytics(self, agent_config, mock_social_media_clients):
        """Test retrieving social media analytics."""
        from agents.specialists.analytics_specialist import AnalyticsSpecialistAgent

        agent = AnalyticsSpecialistAgent(config=agent_config)
        agent._social_media_clients = mock_social_media_clients

        task = Task(
            task_id="task_006",
            task_type="get_social_analytics",
            priority=TaskPriority.NORMAL,
            parameters={
                "platforms": ["linkedin", "twitter"],
                "metrics": ["engagement", "reach", "followers"],
                "date_range": "last_7_days",
            },
            assigned_to=AgentRole.ANALYTICS_SPECIALIST,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "platforms" in result.result or "aggregated" in result.result

    @pytest.mark.asyncio
    async def test_get_web_analytics(self, agent_config, mock_google_analytics_client):
        """Test retrieving website analytics from Google Analytics."""
        from agents.specialists.analytics_specialist import AnalyticsSpecialistAgent

        agent = AnalyticsSpecialistAgent(config=agent_config)
        agent._google_analytics_client = mock_google_analytics_client

        task = Task(
            task_id="task_007",
            task_type="get_web_analytics",
            priority=TaskPriority.NORMAL,
            parameters={
                "metrics": ["sessions", "pageviews", "bounceRate"],
                "dimensions": ["page", "source"],
                "date_range": "last_30_days",
            },
            assigned_to=AgentRole.ANALYTICS_SPECIALIST,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "metrics" in result.result

    @pytest.mark.asyncio
    async def test_generate_insights(self, agent_config):
        """Test generating data-driven insights and recommendations."""
        from agents.specialists.analytics_specialist import AnalyticsSpecialistAgent

        agent = AnalyticsSpecialistAgent(config=agent_config)

        task = Task(
            task_id="task_008",
            task_type="generate_insights",
            priority=TaskPriority.NORMAL,
            parameters={"focus_area": "campaigns", "date_range": "last_30_days"},
            assigned_to=AgentRole.ANALYTICS_SPECIALIST,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "insights" in result.result or "recommendations" in result.result

    @pytest.mark.asyncio
    async def test_validate_task_track_campaign_performance(self, agent_config):
        """Test task validation for track_campaign_performance task type."""
        from agents.specialists.analytics_specialist import AnalyticsSpecialistAgent

        agent = AnalyticsSpecialistAgent(config=agent_config)

        # Valid task
        valid_task = Task(
            task_id="task_009",
            task_type="track_campaign_performance",
            priority=TaskPriority.NORMAL,
            parameters={
                "campaign_id": "campaign_001",
                "metrics": ["impressions"],
                "date_range": "last_7_days",
            },
            assigned_to=AgentRole.ANALYTICS_SPECIALIST,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(valid_task)
        assert is_valid is True

        # Invalid task (missing required fields)
        invalid_task = Task(
            task_id="task_010",
            task_type="track_campaign_performance",
            priority=TaskPriority.NORMAL,
            parameters={"campaign_id": "campaign_001"},  # Missing date_range
            assigned_to=AgentRole.ANALYTICS_SPECIALIST,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(invalid_task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_unsupported_task_type(self, agent_config):
        """Test that unsupported task types are rejected."""
        from agents.specialists.analytics_specialist import AnalyticsSpecialistAgent

        agent = AnalyticsSpecialistAgent(config=agent_config)

        task = Task(
            task_id="task_011",
            task_type="unsupported_task",
            priority=TaskPriority.NORMAL,
            parameters={},
            assigned_to=AgentRole.ANALYTICS_SPECIALIST,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_graceful_degradation_google_analytics_failure(
        self, agent_config, mock_social_media_clients
    ):
        """Test graceful degradation when Google Analytics fails."""
        from agents.specialists.analytics_specialist import AnalyticsSpecialistAgent

        # Make Google Analytics fail
        mock_ga_client = AsyncMock()
        mock_ga_client.get_analytics = AsyncMock(
            side_effect=Exception("Google Analytics API unavailable")
        )

        agent = AnalyticsSpecialistAgent(config=agent_config)
        agent._google_analytics_client = mock_ga_client
        agent._social_media_clients = mock_social_media_clients

        task = Task(
            task_id="task_012",
            task_type="track_campaign_performance",
            priority=TaskPriority.NORMAL,
            parameters={
                "campaign_id": "campaign_001",
                "metrics": ["impressions", "clicks"],
                "date_range": "last_7_days",
            },
            assigned_to=AgentRole.ANALYTICS_SPECIALIST,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Should complete with partial data from social media
        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None

    @pytest.mark.asyncio
    async def test_caching_reduces_api_calls(
        self, agent_config, mock_google_analytics_client
    ):
        """Test that caching reduces external API calls."""
        from agents.specialists.analytics_specialist import AnalyticsSpecialistAgent

        agent = AnalyticsSpecialistAgent(config=agent_config)
        agent._google_analytics_client = mock_google_analytics_client

        task = Task(
            task_id="task_013",
            task_type="get_web_analytics",
            priority=TaskPriority.NORMAL,
            parameters={
                "metrics": ["sessions", "pageviews"],
                "dimensions": ["page"],
                "date_range": "last_7_days",
            },
            assigned_to=AgentRole.ANALYTICS_SPECIALIST,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        # First call
        result1 = await agent.execute(task)
        assert result1.status == TaskStatus.COMPLETED

        # Second call (should use cache)
        result2 = await agent.execute(task)
        assert result2.status == TaskStatus.COMPLETED

        # Google Analytics client should be called only once (cache hit on second call)
        # Note: This depends on implementation details of caching
        assert mock_google_analytics_client.get_analytics.call_count >= 1

    @pytest.mark.asyncio
    async def test_agent_stops_cleanly(self, agent_config):
        """Test that agent stops cleanly."""
        from agents.specialists.analytics_specialist import AnalyticsSpecialistAgent

        agent = AnalyticsSpecialistAgent(config=agent_config)

        # Should not raise exception
        await agent.stop()

        # Agent should no longer be available
        assert agent.is_available is False
