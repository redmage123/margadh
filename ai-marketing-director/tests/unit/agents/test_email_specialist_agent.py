"""
Unit tests for Email Specialist Agent.

WHY: Ensures Email Specialist correctly creates campaigns, sends emails, performs
     A/B testing, segments lists, and tracks performance.

HOW: Uses mocked ESP clients (SendGrid) to test email operations, deliverability
     validation, and campaign workflows.

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


class TestEmailSpecialistAgent:
    """Test suite for Email Specialist Agent (Specialist Layer)."""

    @pytest.fixture
    def agent_config(self):
        """Create Email Specialist agent configuration for testing."""
        return AgentConfig(
            agent_id="email_001",
            role=AgentRole.EMAIL_SPECIALIST,
        )

    @pytest.fixture
    def mock_esp_client(self):
        """Create mocked email service provider (SendGrid) client."""
        client = AsyncMock()

        # Mock create_campaign
        client.create_campaign = AsyncMock(
            return_value=Mock(
                id="campaign_12345",
                name="Test Campaign",
                recipient_count=5000,
                preview_url="https://esp.example.com/preview/campaign_12345",
                preview_html="<html><body>Test email</body></html>",
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

        # Mock get_campaign_stats
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

        # Mock create_ab_test
        client.create_ab_test = AsyncMock(
            return_value=Mock(
                id="test_999",
                test_recipients=1000,
            )
        )

        return client

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent_config):
        """Test that Email Specialist Agent initializes correctly."""
        from agents.specialists.email_specialist import EmailSpecialistAgent

        agent = EmailSpecialistAgent(
            config=agent_config,
            sender_name="Test Company",
            sender_email="marketing@test.com",
            reply_to_email="reply@test.com",
        )

        assert agent.agent_id == "email_001"
        assert agent.role == AgentRole.EMAIL_SPECIALIST
        assert agent.is_available is True

    @pytest.mark.asyncio
    async def test_create_email_campaign(self, agent_config, mock_esp_client):
        """Test creating email campaign with template and recipient list."""
        from agents.specialists.email_specialist import EmailSpecialistAgent

        agent = EmailSpecialistAgent(config=agent_config)
        agent._esp_client = mock_esp_client

        task = Task(
            task_id="task_001",
            task_type="create_email_campaign",
            priority=TaskPriority.NORMAL,
            parameters={
                "campaign_name": "Product Launch",
                "subject_line": "Introducing Our New AI Platform",
                "recipient_list_id": "list_123",
                "template_id": "template_456",
            },
            assigned_to=AgentRole.EMAIL_SPECIALIST,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "campaign_id" in result.result
        assert result.result["campaign_id"] == "campaign_12345"
        assert "recipient_count" in result.result
        assert "deliverability_status" in result.result
        mock_esp_client.create_campaign.assert_called()

    @pytest.mark.asyncio
    async def test_send_email(self, agent_config, mock_esp_client):
        """Test sending email campaign to recipients."""
        from agents.specialists.email_specialist import EmailSpecialistAgent

        agent = EmailSpecialistAgent(config=agent_config)
        agent._esp_client = mock_esp_client

        task = Task(
            task_id="task_002",
            task_type="send_email",
            priority=TaskPriority.HIGH,
            parameters={"campaign_id": "campaign_12345", "test_mode": False},
            assigned_to=AgentRole.EMAIL_SPECIALIST,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "campaign_id" in result.result
        assert "status" in result.result
        assert result.result["status"] == "sending"
        assert "sent_count" in result.result
        mock_esp_client.send_campaign.assert_called()

    @pytest.mark.asyncio
    async def test_schedule_email(self, agent_config, mock_esp_client):
        """Test scheduling email campaign for future delivery."""
        from agents.specialists.email_specialist import EmailSpecialistAgent

        agent = EmailSpecialistAgent(config=agent_config)
        agent._esp_client = mock_esp_client

        send_time = (datetime.now() + timedelta(days=2)).isoformat()

        task = Task(
            task_id="task_003",
            task_type="schedule_email",
            priority=TaskPriority.NORMAL,
            parameters={"campaign_id": "campaign_12345", "send_time": send_time},
            assigned_to=AgentRole.EMAIL_SPECIALIST,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "campaign_id" in result.result
        assert "status" in result.result
        assert result.result["status"] == "scheduled"

    @pytest.mark.asyncio
    async def test_create_email_template(self, agent_config, mock_esp_client):
        """Test creating reusable email template."""
        from agents.specialists.email_specialist import EmailSpecialistAgent

        agent = EmailSpecialistAgent(config=agent_config)
        agent._esp_client = mock_esp_client

        task = Task(
            task_id="task_004",
            task_type="create_email_template",
            priority=TaskPriority.NORMAL,
            parameters={
                "template_name": "Product Launch Template",
                "subject_line": "New Product: {{product_name}}",
                "html_content": "<html><body>Hello {{first_name}}</body></html>",
                "text_content": "Hello {{first_name}}",
                "personalization_fields": ["first_name", "product_name"],
                "category": "promotional",
            },
            assigned_to=AgentRole.EMAIL_SPECIALIST,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "template_id" in result.result
        assert "template_name" in result.result

    @pytest.mark.asyncio
    async def test_segment_email_list(self, agent_config, mock_esp_client):
        """Test segmenting email list based on criteria."""
        from agents.specialists.email_specialist import EmailSpecialistAgent

        agent = EmailSpecialistAgent(config=agent_config)
        agent._esp_client = mock_esp_client

        task = Task(
            task_id="task_005",
            task_type="segment_email_list",
            priority=TaskPriority.NORMAL,
            parameters={
                "list_id": "list_123",
                "segment_name": "Active US Subscribers",
                "criteria": {"engagement": "active", "location": "US"},
            },
            assigned_to=AgentRole.EMAIL_SPECIALIST,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "segment_id" in result.result
        assert result.result["segment_id"] == "segment_456"
        assert "subscriber_count" in result.result
        mock_esp_client.create_segment.assert_called()

    @pytest.mark.asyncio
    async def test_ab_test_email(self, agent_config, mock_esp_client):
        """Test creating A/B test for email campaign."""
        from agents.specialists.email_specialist import EmailSpecialistAgent

        agent = EmailSpecialistAgent(config=agent_config)
        agent._esp_client = mock_esp_client

        task = Task(
            task_id="task_006",
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
        assert result.result is not None
        assert "ab_test_id" in result.result
        assert "test_type" in result.result
        assert result.result["test_type"] == "subject_line"
        mock_esp_client.create_ab_test.assert_called()

    @pytest.mark.asyncio
    async def test_track_email_performance(self, agent_config, mock_esp_client):
        """Test tracking email campaign performance metrics."""
        from agents.specialists.email_specialist import EmailSpecialistAgent

        agent = EmailSpecialistAgent(config=agent_config)
        agent._esp_client = mock_esp_client

        task = Task(
            task_id="task_007",
            task_type="track_email_performance",
            priority=TaskPriority.NORMAL,
            parameters={"campaign_id": "campaign_12345"},
            assigned_to=AgentRole.EMAIL_SPECIALIST,
            assigned_by=AgentRole.ANALYTICS_SPECIALIST,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "campaign_id" in result.result
        assert "open_rate" in result.result
        assert "click_rate" in result.result
        assert "bounce_rate" in result.result
        assert result.result["open_rate"] > 0
        mock_esp_client.get_campaign_stats.assert_called()

    @pytest.mark.asyncio
    async def test_create_drip_campaign(self, agent_config, mock_esp_client):
        """Test creating automated drip campaign workflow."""
        from agents.specialists.email_specialist import EmailSpecialistAgent

        agent = EmailSpecialistAgent(config=agent_config)
        agent._esp_client = mock_esp_client

        task = Task(
            task_id="task_008",
            task_type="create_drip_campaign",
            priority=TaskPriority.NORMAL,
            parameters={
                "campaign_name": "Welcome Series",
                "trigger_event": "subscription",
                "email_sequence": [
                    {
                        "template_id": "welcome_email",
                        "delay_days": 0,
                        "subject_line": "Welcome!",
                    },
                    {
                        "template_id": "getting_started",
                        "delay_days": 2,
                        "subject_line": "Get Started",
                    },
                    {
                        "template_id": "case_study",
                        "delay_days": 7,
                        "subject_line": "Success Stories",
                    },
                ],
            },
            assigned_to=AgentRole.EMAIL_SPECIALIST,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "drip_campaign_id" in result.result
        assert "email_count" in result.result
        assert result.result["email_count"] == 3

    @pytest.mark.asyncio
    async def test_performance_caching(self, agent_config, mock_esp_client):
        """Test that performance tracking uses caching."""
        from agents.specialists.email_specialist import EmailSpecialistAgent

        agent = EmailSpecialistAgent(config=agent_config)
        agent._esp_client = mock_esp_client

        task = Task(
            task_id="task_009",
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

        # Second call - should use cache
        result2 = await agent.execute(task)
        assert result2.status == TaskStatus.COMPLETED
        assert result2.result.get("cached") is True

        # Verify ESP was only called once
        assert mock_esp_client.get_campaign_stats.call_count == 1

    @pytest.mark.asyncio
    async def test_validate_task_create_email_campaign(self, agent_config):
        """Test task validation for create_email_campaign task type."""
        from agents.specialists.email_specialist import EmailSpecialistAgent

        agent = EmailSpecialistAgent(config=agent_config)

        # Valid task
        valid_task = Task(
            task_id="task_010",
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

        is_valid = await agent.validate_task(valid_task)
        assert is_valid is True

        # Invalid task (missing required field)
        invalid_task = Task(
            task_id="task_011",
            task_type="create_email_campaign",
            priority=TaskPriority.NORMAL,
            parameters={
                "campaign_name": "Test Campaign",
                # Missing subject_line and recipient_list_id
            },
            assigned_to=AgentRole.EMAIL_SPECIALIST,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(invalid_task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_unsupported_task_type(self, agent_config):
        """Test that unsupported task types are rejected."""
        from agents.specialists.email_specialist import EmailSpecialistAgent

        agent = EmailSpecialistAgent(config=agent_config)

        task = Task(
            task_id="task_012",
            task_type="unsupported_task",
            priority=TaskPriority.NORMAL,
            parameters={},
            assigned_to=AgentRole.EMAIL_SPECIALIST,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_graceful_degradation_no_esp_client(self, agent_config):
        """Test graceful degradation when ESP client is unavailable."""
        from agents.specialists.email_specialist import EmailSpecialistAgent

        agent = EmailSpecialistAgent(config=agent_config)
        # No ESP client configured

        task = Task(
            task_id="task_013",
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

        # Should complete with error message (graceful degradation)
        assert result.status == TaskStatus.COMPLETED
        assert "error" in result.result

    @pytest.mark.asyncio
    async def test_agent_stops_cleanly(self, agent_config):
        """Test that agent stops cleanly."""
        from agents.specialists.email_specialist import EmailSpecialistAgent

        agent = EmailSpecialistAgent(config=agent_config)

        # Should not raise exception
        await agent.stop()

        # Agent should no longer be available
        assert agent.is_available is False
