"""
Integration tests for Analytics Specialist with external API clients.

WHY: Verify that Analytics Specialist correctly integrates with external APIs,
     handles caching, and provides graceful degradation.

HOW: Uses real agent instance with mocked external API clients (Google Analytics,
     social media APIs) to test full analytics workflows.

Following TDD methodology - these tests verify integrated behavior.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from agents.base.agent_protocol import AgentRole, Task, TaskPriority, TaskStatus
from agents.base.base_agent import AgentConfig
from agents.specialists.analytics_specialist import AnalyticsSpecialistAgent


class TestAnalyticsSpecialistIntegration:
    """Integration test suite for Analytics Specialist."""

    @pytest.fixture
    def analytics_config(self):
        """Create Analytics Specialist configuration."""
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
                "bounce_rate": 35.5,
                "avg_session_duration": 180.5,
            }
        )
        return client

    @pytest.fixture
    def mock_social_clients(self):
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
    async def test_campaign_performance_tracking_with_multiple_sources(
        self, analytics_config, mock_google_analytics_client, mock_social_clients
    ):
        """Test tracking campaign performance from multiple data sources."""
        agent = AnalyticsSpecialistAgent(config=analytics_config)
        agent._google_analytics_client = mock_google_analytics_client
        agent._social_media_clients = mock_social_clients

        task = Task(
            task_id="analytics_001",
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

        # Verify result
        assert result.status == TaskStatus.COMPLETED
        assert "metrics" in result.result
        assert result.result["campaign_id"] == "campaign_001"

    @pytest.mark.asyncio
    async def test_executive_report_generation(self, analytics_config):
        """Test generating executive dashboard report."""
        agent = AnalyticsSpecialistAgent(config=analytics_config)

        task = Task(
            task_id="analytics_002",
            task_type="generate_report",
            priority=TaskPriority.HIGH,
            parameters={
                "report_type": "executive_dashboard",
                "date_range": "Q1_2025",
                "include_charts": True,
            },
            assigned_to=AgentRole.ANALYTICS_SPECIALIST,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Verify report structure
        assert result.status == TaskStatus.COMPLETED
        assert "report_id" in result.result
        assert "summary" in result.result
        assert "recommendations" in result.result

    @pytest.mark.asyncio
    async def test_graceful_degradation_api_failures(
        self, analytics_config, mock_social_clients
    ):
        """Test graceful degradation when Google Analytics fails."""
        # Create agent with failing GA client
        mock_ga_failing = AsyncMock()
        mock_ga_failing.get_analytics = AsyncMock(
            side_effect=Exception("Google Analytics API unavailable")
        )

        agent = AnalyticsSpecialistAgent(config=analytics_config)
        agent._google_analytics_client = mock_ga_failing
        agent._social_media_clients = mock_social_clients

        task = Task(
            task_id="analytics_003",
            task_type="track_campaign_performance",
            priority=TaskPriority.NORMAL,
            parameters={
                "campaign_id": "campaign_002",
                "metrics": ["impressions", "engagement"],
                "date_range": "last_7_days",
            },
            assigned_to=AgentRole.ANALYTICS_SPECIALIST,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Should complete with partial data from social media
        assert result.status == TaskStatus.COMPLETED
        assert "metrics" in result.result

    @pytest.mark.asyncio
    async def test_social_analytics_aggregation(
        self, analytics_config, mock_social_clients
    ):
        """Test aggregating social media analytics across platforms."""
        agent = AnalyticsSpecialistAgent(config=analytics_config)
        agent._social_media_clients = mock_social_clients

        task = Task(
            task_id="analytics_004",
            task_type="get_social_analytics",
            priority=TaskPriority.NORMAL,
            parameters={
                "platforms": ["linkedin", "twitter"],
                "metrics": ["engagement", "reach", "followers"],
                "date_range": "last_30_days",
            },
            assigned_to=AgentRole.ANALYTICS_SPECIALIST,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Verify aggregation
        assert result.status == TaskStatus.COMPLETED
        assert "platforms" in result.result or "aggregated" in result.result

    @pytest.mark.asyncio
    async def test_kpi_monitoring_with_alerts(self, analytics_config):
        """Test KPI monitoring with alert generation."""
        agent = AnalyticsSpecialistAgent(config=analytics_config)

        task = Task(
            task_id="analytics_005",
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

        # Verify KPI monitoring
        assert result.status == TaskStatus.COMPLETED
        assert "kpis" in result.result
        assert isinstance(result.result["kpis"], dict)

    @pytest.mark.asyncio
    async def test_agent_cleanup(self, analytics_config):
        """Test that agent stops cleanly."""
        agent = AnalyticsSpecialistAgent(config=analytics_config)

        # Verify available
        assert agent.is_available is True

        # Stop cleanly
        await agent.stop()

        # Verify stopped
        assert agent.is_available is False
