"""
Unit tests for Director of Communications Agent (Executive Layer).

WHY: Verify that Director of Communications Agent correctly handles brand voice review,
     messaging approval, crisis management, and PR oversight tasks independently.

HOW: Uses mocked dependencies to test each task type handler in isolation, following
     TDD methodology - these tests are written FIRST before implementation.

Following TDD methodology - RED phase (tests written before implementation).
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from agents.base.agent_protocol import AgentRole, Task, TaskPriority, TaskStatus
from agents.base.base_agent import AgentConfig
from agents.executive.director_communications import DirectorOfCommunicationsAgent


class TestDirectorOfCommunicationsAgent:
    """Test suite for Director of Communications Agent."""

    @pytest.fixture
    def agent_config(self):
        """Create Director of Communications Agent configuration."""
        return AgentConfig(
            agent_id="director_comms_001",
            role=AgentRole.DIRECTOR_COMMUNICATIONS,
        )

    @pytest.fixture
    def director_agent(self, agent_config):
        """Create Director of Communications Agent instance."""
        return DirectorOfCommunicationsAgent(config=agent_config)

    @pytest.fixture
    def mock_llm_client(self):
        """Create mocked LLM client for brand analysis."""
        client = AsyncMock()
        client.generate = AsyncMock(
            return_value=Mock(
                text="""
                BRAND VOICE ANALYSIS:
                - Tone consistency: 85/100
                - Voice characteristics: 90/100
                - Prohibited language: 100/100 (no violations)
                - Messaging alignment: 88/100
                - Audience fit: 87/100

                Overall Score: 90/100
                Status: Approved

                Feedback: Content demonstrates strong brand voice alignment with professional
                tone and clear messaging. Minor improvements suggested for audience engagement.
                """
            )
        )
        return client

    @pytest.fixture
    def mock_cmo_agent(self):
        """Create mocked CMO agent for escalation."""
        cmo = AsyncMock()
        cmo.agent_id = "cmo_001"
        cmo.execute = AsyncMock(
            return_value=Mock(
                status=TaskStatus.COMPLETED,
                result={
                    "escalation_handled": True,
                    "decision": "approve_with_conditions",
                },
            )
        )
        return cmo

    @pytest.fixture
    def mock_copywriter(self):
        """Create mocked Copywriter agent."""
        copywriter = AsyncMock()
        copywriter.agent_id = "copywriter_001"
        return copywriter

    @pytest.mark.asyncio
    async def test_review_brand_voice_approved(self, director_agent, mock_llm_client):
        """Test brand voice review with approved content."""
        director_agent._llm_client = mock_llm_client

        task = Task(
            task_id="review_001",
            task_type="review_brand_voice",
            priority=TaskPriority.NORMAL,
            parameters={
                "content_id": "blog_123",
                "content_type": "blog_post",
                "content_text": "Our AI-powered marketing platform helps you achieve measurable results.",
                "review_level": "standard",
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await director_agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert "content_id" in result.result
        assert "review_status" in result.result
        assert "brand_voice_score" in result.result
        assert result.result["review_status"] in ["approved", "approved_with_notes"]
        assert result.result["brand_voice_score"] >= 70

    @pytest.mark.asyncio
    async def test_review_brand_voice_revision_needed(
        self, director_agent, mock_llm_client
    ):
        """Test brand voice review with content needing revision."""
        # Mock poor brand voice score
        mock_llm_client.generate = AsyncMock(
            return_value=Mock(
                text="""
                BRAND VOICE ANALYSIS:
                Overall Score: 65/100
                Status: Revision Needed
                """
            )
        )
        director_agent._llm_client = mock_llm_client

        task = Task(
            task_id="review_002",
            task_type="review_brand_voice",
            priority=TaskPriority.HIGH,
            parameters={
                "content_id": "blog_456",
                "content_type": "blog_post",
                "content_text": "Revolutionary game-changing synergy!",  # Prohibited terms
                "review_level": "comprehensive",
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.COPYWRITER,
            created_at=datetime.now(),
        )

        result = await director_agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result["review_status"] in ["revision_needed", "rejected"]
        assert result.result["brand_voice_score"] < 70

    @pytest.mark.asyncio
    async def test_approve_messaging_success(self, director_agent, mock_llm_client):
        """Test campaign messaging approval."""
        director_agent._llm_client = mock_llm_client

        task = Task(
            task_id="messaging_001",
            task_type="approve_messaging",
            priority=TaskPriority.HIGH,
            parameters={
                "campaign_id": "campaign_enterprise_001",
                "messaging_framework": {
                    "positioning": "AI-powered marketing automation",
                    "value_proposition": "Measurable ROI through intelligent automation",
                },
                "target_audience": ["enterprise_cmos", "marketing_directors"],
                "channels": ["linkedin", "email", "content"],
                "key_messages": [
                    "AI-powered marketing automation",
                    "Measurable ROI",
                    "Enterprise-grade security",
                ],
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await director_agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert "approval_status" in result.result
        assert "messaging_score" in result.result
        assert result.result["approval_status"] in [
            "approved",
            "conditional",
            "revision_needed",
        ]

    @pytest.mark.asyncio
    async def test_approve_messaging_escalation(
        self, director_agent, mock_cmo_agent, mock_llm_client
    ):
        """Test messaging approval escalation to CMO for strategic campaigns."""
        director_agent._cmo_agent = mock_cmo_agent
        director_agent._llm_client = mock_llm_client

        task = Task(
            task_id="messaging_002",
            task_type="approve_messaging",
            priority=TaskPriority.URGENT,
            parameters={
                "campaign_id": "campaign_strategic_rebrand",
                "messaging_framework": {
                    "positioning": "Complete brand repositioning",  # Strategic change
                },
                "target_audience": ["all_customers"],
                "channels": ["all"],
                "key_messages": ["New brand identity"],
                "approval_urgency": "urgent",
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.VP_MARKETING,
            created_at=datetime.now(),
        )

        result = await director_agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        # Should escalate major brand repositioning to CMO
        assert result.result["approval_status"] in ["escalated", "conditional"]

    @pytest.mark.asyncio
    async def test_manage_crisis_high_severity(self, director_agent, mock_cmo_agent):
        """Test crisis management with high severity."""
        director_agent._cmo_agent = mock_cmo_agent

        task = Task(
            task_id="crisis_001",
            task_type="manage_crisis",
            priority=TaskPriority.URGENT,
            parameters={
                "crisis_id": "crisis_databreach_001",
                "crisis_type": "data_breach",
                "severity": "high",
                "description": "Potential customer data exposure",
                "affected_channels": ["email", "website", "social_media"],
                "stakeholders": ["customers", "investors", "media"],
                "time_discovered": "2025-11-03T14:30:00Z",
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        result = await director_agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert "response_status" in result.result
        assert "holding_statement" in result.result
        assert result.result["response_status"] in [
            "activated",
            "in_progress",
            "escalated",
        ]
        # High severity should escalate to CMO
        assert (
            result.result.get("escalated_to_cmo") is True
            or "escalated" in result.result["response_status"]
        )

    @pytest.mark.asyncio
    async def test_manage_crisis_critical_immediate_escalation(
        self, director_agent, mock_cmo_agent
    ):
        """Test critical crisis immediately escalates to CMO."""
        director_agent._cmo_agent = mock_cmo_agent

        task = Task(
            task_id="crisis_002",
            task_type="manage_crisis",
            priority=TaskPriority.URGENT,
            parameters={
                "crisis_id": "crisis_executive_001",
                "crisis_type": "executive_statement",
                "severity": "critical",
                "description": "CEO statement controversy",
                "affected_channels": ["all"],
                "stakeholders": ["all"],
                "time_discovered": "2025-11-03T15:00:00Z",
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.VP_MARKETING,
            created_at=datetime.now(),
        )

        result = await director_agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result["escalated_to_cmo"] is True
        assert result.result["response_status"] == "escalated"

    @pytest.mark.asyncio
    async def test_define_brand_guidelines(self, director_agent):
        """Test brand guidelines creation."""
        task = Task(
            task_id="guidelines_001",
            task_type="define_brand_guidelines",
            priority=TaskPriority.HIGH,
            parameters={
                "guideline_type": "update",
                "brand_personality": [
                    "professional",
                    "innovative",
                    "trustworthy",
                    "helpful",
                ],
                "tone_attributes": {
                    "professional_casual_scale": 7,
                    "serious_playful_scale": 6,
                },
                "voice_characteristics": {
                    "clarity": "Use simple, clear language",
                    "empathy": "Show understanding",
                },
                "target_audiences": [
                    {"segment": "enterprise", "tone_adjustment": "more_formal"}
                ],
                "prohibited_terms": ["revolutionary", "game-changing"],
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await director_agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert "guidelines_id" in result.result
        assert "version" in result.result
        assert "brand_guidelines" in result.result
        assert "personality" in result.result["brand_guidelines"]

    @pytest.mark.asyncio
    async def test_review_pr_materials_approved(self, director_agent, mock_llm_client):
        """Test PR materials review with approval."""
        director_agent._llm_client = mock_llm_client

        task = Task(
            task_id="pr_001",
            task_type="review_pr_materials",
            priority=TaskPriority.HIGH,
            parameters={
                "material_id": "press_release_q4",
                "material_type": "press_release",
                "material_content": "Company announces Q4 results with 25% revenue growth",
                "distribution_plan": {"channels": ["newswire", "website", "email"]},
                "approval_urgency": "time_sensitive",
                "target_audience": ["investors", "media", "customers"],
                "legal_approved": True,
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await director_agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert "approval_status" in result.result
        assert "brand_voice_score" in result.result
        assert "pr_standards_score" in result.result
        assert "risk_assessment" in result.result

    @pytest.mark.asyncio
    async def test_coordinate_messaging(self, director_agent):
        """Test messaging coordination across campaigns."""
        task = Task(
            task_id="coordinate_001",
            task_type="coordinate_messaging",
            priority=TaskPriority.NORMAL,
            parameters={
                "coordination_scope": "quarter",
                "campaigns": [
                    "campaign_enterprise",
                    "campaign_smb",
                    "campaign_product_launch",
                ],
                "timeframe": {"start_date": "2025-11-01", "end_date": "2025-12-31"},
                "channels": ["linkedin", "email", "content", "social_media"],
                "primary_message": "AI-powered marketing excellence",
                "stakeholders": ["sales", "marketing", "product"],
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.VP_MARKETING,
            created_at=datetime.now(),
        )

        result = await director_agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert "coordination_id" in result.result
        assert "unified_messaging_framework" in result.result
        assert "coordination_plan" in result.result

    @pytest.mark.asyncio
    async def test_monitor_brand_sentiment(self, director_agent):
        """Test brand sentiment monitoring."""
        task = Task(
            task_id="sentiment_001",
            task_type="monitor_brand_sentiment",
            priority=TaskPriority.NORMAL,
            parameters={
                "monitoring_scope": "daily",
                "channels": ["linkedin", "twitter", "email", "blog"],
                "timeframe": {"start_date": "2025-11-01", "end_date": "2025-11-03"},
                "keywords": ["AI marketing", "marketing automation"],
                "alert_threshold": -0.10,
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await director_agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert "overall_sentiment" in result.result
        assert "channel_sentiment" in result.result
        assert "trending_topics" in result.result

    @pytest.mark.asyncio
    async def test_train_brand_voice(self, director_agent, mock_copywriter):
        """Test agent brand voice training."""
        director_agent._copywriter = mock_copywriter

        task = Task(
            task_id="training_001",
            task_type="train_brand_voice",
            priority=TaskPriority.NORMAL,
            parameters={
                "training_type": "guidelines_update",
                "target_agents": ["copywriter_001", "content_manager_001"],
                "focus_areas": ["tone", "voice_characteristics"],
                "assessment_required": True,
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await director_agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert "training_session_id" in result.result
        assert "agents_trained" in result.result
        assert "training_materials" in result.result

    @pytest.mark.asyncio
    async def test_audit_communications(self, director_agent):
        """Test communications compliance audit."""
        task = Task(
            task_id="audit_001",
            task_type="audit_communications",
            priority=TaskPriority.NORMAL,
            parameters={
                "audit_scope": "campaign",
                "audit_target": "campaign_enterprise_q3",
                "timeframe": {"start_date": "2025-09-01", "end_date": "2025-09-30"},
                "sample_size": 50,
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await director_agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert "audit_id" in result.result
        assert "compliance_summary" in result.result
        assert "violations" in result.result
        assert "recommendations" in result.result

    @pytest.mark.asyncio
    async def test_report_brand_health(self, director_agent):
        """Test brand health reporting."""
        task = Task(
            task_id="report_001",
            task_type="report_brand_health",
            priority=TaskPriority.HIGH,
            parameters={
                "report_type": "quarterly",
                "timeframe": {"start_date": "2025-09-01", "end_date": "2025-11-30"},
                "include_sentiment": True,
                "include_compliance": True,
                "include_crisis": True,
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await director_agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert "report_id" in result.result
        assert "executive_summary" in result.result
        assert "brand_metrics" in result.result
        assert "recommendations" in result.result

    @pytest.mark.asyncio
    async def test_unknown_task_type(self, director_agent):
        """Test handling of unknown task type."""
        task = Task(
            task_id="unknown_001",
            task_type="unknown_task_type",
            priority=TaskPriority.NORMAL,
            parameters={},
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await director_agent.execute(task)

        assert result.status == TaskStatus.FAILED
        assert (
            "error" in result.result
            or "unknown" in result.result.get("message", "").lower()
        )

    @pytest.mark.asyncio
    async def test_missing_required_parameters(self, director_agent):
        """Test validation of required parameters."""
        task = Task(
            task_id="validation_001",
            task_type="review_brand_voice",
            priority=TaskPriority.NORMAL,
            parameters={
                "content_id": "blog_123",
                # Missing required "content_text"
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await director_agent.execute(task)

        # Should complete with error message (graceful degradation)
        assert result.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
        if result.status == TaskStatus.COMPLETED:
            assert "error" in result.result

    @pytest.mark.asyncio
    async def test_agent_lifecycle(self, director_agent):
        """Test agent start and stop lifecycle."""
        assert director_agent.is_available is True

        await director_agent.stop()

        assert director_agent.is_available is False
