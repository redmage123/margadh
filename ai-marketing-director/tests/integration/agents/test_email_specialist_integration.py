"""
Integration tests for Email Specialist with external ESP clients.

WHY: Verify that Email Specialist correctly integrates with email service providers,
     handles campaign workflows, and provides reliable delivery tracking.

HOW: Uses real agent instance with mocked ESP clients (SendGrid) to test full
     email workflows including campaigns, A/B testing, and drip campaigns.

Following TDD methodology - these tests verify integrated behavior.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from agents.base.agent_protocol import AgentRole, Task, TaskPriority, TaskStatus
from agents.base.base_agent import AgentConfig
from agents.specialists.email_specialist import EmailSpecialistAgent


class TestEmailSpecialistIntegration:
    """Integration test suite for Email Specialist."""

    @pytest.fixture
    def email_config(self):
        """Create Email Specialist configuration."""
        return AgentConfig(
            agent_id="email_001",
            role=AgentRole.EMAIL_SPECIALIST,
        )

    @pytest.fixture
    def mock_esp_client(self):
        """Create comprehensive mocked ESP (SendGrid) client."""
        client = AsyncMock()

        # Mock campaign creation
        client.create_campaign = AsyncMock(
            return_value=Mock(
                id="campaign_12345",
                name="Test Campaign",
                recipient_count=5000,
                preview_url="https://esp.example.com/preview/campaign_12345",
                preview_html="<html><body>Test <a href='unsubscribe'>Unsubscribe</a></body></html>",
            )
        )

        # Mock get_campaign
        client.get_campaign = AsyncMock(
            return_value=Mock(
                id="campaign_12345",
                name="Test Campaign",
                recipient_count=5000,
            )
        )

        # Mock send_campaign
        client.send_campaign = AsyncMock(
            return_value=Mock(
                sent_count=5000,
                send_time=datetime.now(),
                estimated_delivery=datetime.now() + timedelta(minutes=5),
            )
        )

        # Mock schedule_campaign
        client.schedule_campaign = AsyncMock(
            return_value=Mock(scheduled_time=datetime.now() + timedelta(days=1))
        )

        # Mock campaign stats
        client.get_campaign_stats = AsyncMock(
            return_value=Mock(
                sent=5000,
                delivered=4950,
                opens=2475,
                unique_opens=2200,
                clicks=742,
                unique_clicks=650,
                bounces=50,
                spam_complaints=5,
                unsubscribes=15,
                revenue=15000.00,
            )
        )

        # Mock create_segment
        client.create_segment = AsyncMock(
            return_value=Mock(
                id="segment_456",
                name="Active US Subscribers",
                subscriber_count=1250,
                created_at=datetime.now(),
            )
        )

        # Mock get_list
        client.get_list = AsyncMock(return_value=Mock(id="list_123", name="Main List"))

        # Mock create_ab_test
        client.create_ab_test = AsyncMock(
            return_value=Mock(id="test_999", test_recipients=1000)
        )

        # Mock create_automation (drip campaign)
        client.create_automation = AsyncMock(
            return_value=Mock(id="drip_555", created_at=datetime.now())
        )

        # Mock create_template
        client.create_template = AsyncMock(
            return_value=Mock(id="template_789", name="Product Launch Template")
        )

        # Mock get_template
        client.get_template = AsyncMock(
            return_value=Mock(id="template_789", name="Product Launch Template")
        )

        return client

    @pytest.mark.asyncio
    async def test_full_email_campaign_workflow(self, email_config, mock_esp_client):
        """Test complete email campaign workflow from creation to sending."""
        agent = EmailSpecialistAgent(config=email_config)
        agent._esp_client = mock_esp_client

        # Create campaign
        create_task = Task(
            task_id="email_001",
            task_type="create_email_campaign",
            priority=TaskPriority.HIGH,
            parameters={
                "campaign_name": "Q4 Product Launch",
                "subject_line": "Introducing Our Revolutionary AI Platform",
                "recipient_list_id": "list_123",
                "template_id": "template_789",
            },
            assigned_to=AgentRole.EMAIL_SPECIALIST,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        create_result = await agent.execute(create_task)
        assert create_result.status == TaskStatus.COMPLETED
        assert "campaign_id" in create_result.result

        # Send campaign
        send_task = Task(
            task_id="email_002",
            task_type="send_email",
            priority=TaskPriority.HIGH,
            parameters={"campaign_id": create_result.result["campaign_id"]},
            assigned_to=AgentRole.EMAIL_SPECIALIST,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        send_result = await agent.execute(send_task)
        assert send_result.status == TaskStatus.COMPLETED
        assert send_result.result["status"] == "sending"

    @pytest.mark.asyncio
    async def test_ab_testing_workflow(self, email_config, mock_esp_client):
        """Test A/B testing campaign workflow."""
        agent = EmailSpecialistAgent(config=email_config)
        agent._esp_client = mock_esp_client

        # Create A/B test
        task = Task(
            task_id="email_003",
            task_type="ab_test_email",
            priority=TaskPriority.HIGH,
            parameters={
                "campaign_id": "campaign_12345",
                "test_type": "subject_line",
                "variant_a": "Transform Your Marketing Today",
                "variant_b": "Revolutionize Your Marketing Strategy",
                "test_size_percent": 20,
            },
            assigned_to=AgentRole.EMAIL_SPECIALIST,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)
        assert result.status == TaskStatus.COMPLETED
        assert "ab_test_id" in result.result
        assert result.result["test_type"] == "subject_line"

    @pytest.mark.asyncio
    async def test_drip_campaign_workflow(self, email_config, mock_esp_client):
        """Test automated drip campaign creation."""
        agent = EmailSpecialistAgent(config=email_config)
        agent._esp_client = mock_esp_client

        task = Task(
            task_id="email_004",
            task_type="create_drip_campaign",
            priority=TaskPriority.NORMAL,
            parameters={
                "campaign_name": "Customer Onboarding",
                "trigger_event": "subscription",
                "email_sequence": [
                    {"template_id": "welcome_email", "delay_days": 0, "subject_line": "Welcome!"},
                    {"template_id": "getting_started", "delay_days": 2, "subject_line": "Get Started"},
                    {"template_id": "advanced_features", "delay_days": 7, "subject_line": "Unlock Features"},
                ],
            },
            assigned_to=AgentRole.EMAIL_SPECIALIST,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)
        assert result.status == TaskStatus.COMPLETED
        assert "drip_campaign_id" in result.result
        assert result.result["email_count"] == 3

    @pytest.mark.asyncio
    async def test_list_segmentation_workflow(self, email_config, mock_esp_client):
        """Test email list segmentation."""
        agent = EmailSpecialistAgent(config=email_config)
        agent._esp_client = mock_esp_client

        task = Task(
            task_id="email_005",
            task_type="segment_email_list",
            priority=TaskPriority.NORMAL,
            parameters={
                "list_id": "list_123",
                "segment_name": "Active US Enterprise",
                "criteria": {"engagement": "active", "location": "US", "industry": "Technology"},
            },
            assigned_to=AgentRole.EMAIL_SPECIALIST,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)
        assert result.status == TaskStatus.COMPLETED
        assert "segment_id" in result.result
        assert result.result["subscriber_count"] > 0

    @pytest.mark.asyncio
    async def test_performance_tracking_with_caching(self, email_config, mock_esp_client):
        """Test email performance tracking with caching."""
        agent = EmailSpecialistAgent(config=email_config)
        agent._esp_client = mock_esp_client

        task = Task(
            task_id="email_006",
            task_type="track_email_performance",
            priority=TaskPriority.NORMAL,
            parameters={"campaign_id": "campaign_12345"},
            assigned_to=AgentRole.EMAIL_SPECIALIST,
            assigned_by=AgentRole.ANALYTICS_SPECIALIST,
            created_at=datetime.now(),
        )

        # First call - should fetch from ESP
        result1 = await agent.execute(task)
        assert result1.status == TaskStatus.COMPLETED
        assert result1.result.get("cached") is False
        assert result1.result["open_rate"] > 0

        # Second call - should use cache
        result2 = await agent.execute(task)
        assert result2.status == TaskStatus.COMPLETED
        assert result2.result.get("cached") is True

        # Verify ESP was only called once
        assert mock_esp_client.get_campaign_stats.call_count == 1

    @pytest.mark.asyncio
    async def test_graceful_degradation_esp_failure(self, email_config):
        """Test graceful degradation when ESP is unavailable."""
        agent = EmailSpecialistAgent(config=email_config)
        # No ESP client configured

        task = Task(
            task_id="email_007",
            task_type="create_email_campaign",
            priority=TaskPriority.NORMAL,
            parameters={
                "campaign_name": "Test Campaign",
                "subject_line": "Test Subject",
                "recipient_list_id": "list_123",
            },
            assigned_to=AgentRole.EMAIL_SPECIALIST,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)
        assert result.status == TaskStatus.COMPLETED
        assert "error" in result.result

    @pytest.mark.asyncio
    async def test_agent_cleanup(self, email_config):
        """Test that agent stops cleanly."""
        agent = EmailSpecialistAgent(config=email_config)

        assert agent.is_available is True
        await agent.stop()
        assert agent.is_available is False
