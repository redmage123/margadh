"""
Integration tests for Director of Communications Agent with cross-agent workflows.

WHY: Verify that Director of Communications Agent correctly integrates with CMO,
     VP Marketing, Content Manager, and other agents in complete workflows.

HOW: Uses real agent instance with mocked dependencies to test full brand governance,
     crisis communications, and messaging coordination workflows.

Following TDD methodology - these tests verify integrated behavior.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from agents.base.agent_protocol import AgentRole, Task, TaskPriority, TaskStatus
from agents.base.base_agent import AgentConfig
from agents.executive.director_communications import DirectorOfCommunicationsAgent


class TestDirectorOfCommunicationsIntegration:
    """Integration test suite for Director of Communications Agent."""

    @pytest.fixture
    def director_config(self):
        """Create Director of Communications Agent configuration."""
        return AgentConfig(
            agent_id="director_comms_001",
            role=AgentRole.DIRECTOR_COMMUNICATIONS,
        )

    @pytest.fixture
    def mock_cmo_agent(self):
        """Create comprehensive mocked CMO agent."""
        cmo = AsyncMock()
        cmo.agent_id = "cmo_001"
        cmo.execute = AsyncMock(
            return_value=Mock(
                status=TaskStatus.COMPLETED,
                result={
                    "escalation_handled": True,
                    "decision": "approve_with_conditions",
                    "strategic_direction": "Align with enterprise focus",
                },
            )
        )
        return cmo

    @pytest.fixture
    def mock_vp_marketing(self):
        """Create mocked VP Marketing agent."""
        vp = AsyncMock()
        vp.agent_id = "vp_marketing_001"
        vp.execute = AsyncMock(
            return_value=Mock(
                status=TaskStatus.COMPLETED,
                result={
                    "coordination_status": "acknowledged",
                    "teams_notified": ["content", "campaign", "social_media"],
                },
            )
        )
        return vp

    @pytest.fixture
    def mock_content_manager(self):
        """Create mocked Content Manager agent."""
        content_mgr = AsyncMock()
        content_mgr.agent_id = "content_manager_001"
        content_mgr.execute = AsyncMock(
            return_value=Mock(
                status=TaskStatus.COMPLETED,
                result={
                    "content_updated": True,
                    "revisions_applied": ["tone_adjustment", "brand_voice_fix"],
                },
            )
        )
        return content_mgr

    @pytest.fixture
    def mock_copywriter(self):
        """Create mocked Copywriter agent."""
        copywriter = AsyncMock()
        copywriter.agent_id = "copywriter_001"
        copywriter.execute = AsyncMock(
            return_value=Mock(
                status=TaskStatus.COMPLETED,
                result={
                    "training_completed": True,
                    "assessment_score": 92,
                    "feedback": "Strong understanding of brand voice",
                },
            )
        )
        return copywriter

    @pytest.fixture
    def mock_llm_client(self):
        """Create mocked LLM client for brand analysis."""
        client = AsyncMock()
        client.generate = AsyncMock(
            return_value=Mock(
                text="""
                BRAND VOICE ANALYSIS:
                - Tone consistency: 88/100
                - Voice characteristics: 92/100
                - Prohibited language: 100/100 (no violations)
                - Messaging alignment: 90/100
                - Audience fit: 87/100

                Overall Score: 91/100
                Status: Approved

                Feedback: Excellent brand voice alignment with strong professional tone.
                """
            )
        )
        return client

    @pytest.mark.asyncio
    async def test_full_brand_voice_review_workflow(
        self, director_config, mock_llm_client, mock_content_manager
    ):
        """Test complete brand voice review from submission to approval."""
        agent = DirectorOfCommunicationsAgent(config=director_config)
        agent._llm_client = mock_llm_client
        agent._content_manager = mock_content_manager

        task = Task(
            task_id="review_workflow_001",
            task_type="review_brand_voice",
            priority=TaskPriority.NORMAL,
            parameters={
                "content_id": "blog_enterprise_001",
                "content_type": "blog_post",
                "content_text": "Our AI-powered marketing platform helps enterprise teams achieve measurable results through intelligent automation.",
                "review_level": "comprehensive",
                "urgency": "normal",
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result["review_status"] in ["approved", "approved_with_notes"]
        assert result.result["brand_voice_score"] >= 85
        assert "feedback" in result.result

    @pytest.mark.asyncio
    async def test_crisis_management_with_cmo_escalation(
        self, director_config, mock_cmo_agent, mock_vp_marketing
    ):
        """Test crisis management workflow with CMO escalation."""
        agent = DirectorOfCommunicationsAgent(config=director_config)
        agent._cmo_agent = mock_cmo_agent
        agent._vp_marketing_agent = mock_vp_marketing

        task = Task(
            task_id="crisis_workflow_001",
            task_type="manage_crisis",
            priority=TaskPriority.URGENT,
            parameters={
                "crisis_id": "crisis_social_backlash_001",
                "crisis_type": "social_backlash",
                "severity": "high",
                "description": "Negative social media campaign about pricing changes",
                "affected_channels": ["twitter", "linkedin", "reddit"],
                "stakeholders": ["customers", "investors", "employees"],
                "time_discovered": "2025-11-03T14:00:00Z",
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result["response_status"] in [
            "activated",
            "in_progress",
            "escalated",
        ]
        assert "holding_statement" in result.result
        # High severity should escalate to CMO
        assert result.result.get("escalated_to_cmo") is True or result.result[
            "response_status"
        ] == "escalated"

    @pytest.mark.asyncio
    async def test_messaging_approval_with_vp_marketing_coordination(
        self, director_config, mock_vp_marketing, mock_llm_client
    ):
        """Test messaging approval workflow with VP Marketing coordination."""
        agent = DirectorOfCommunicationsAgent(config=director_config)
        agent._vp_marketing_agent = mock_vp_marketing
        agent._llm_client = mock_llm_client

        task = Task(
            task_id="messaging_workflow_001",
            task_type="approve_messaging",
            priority=TaskPriority.HIGH,
            parameters={
                "campaign_id": "campaign_q4_enterprise",
                "messaging_framework": {
                    "positioning": "Enterprise-grade AI marketing automation",
                    "value_proposition": "Drive measurable ROI with intelligent campaigns",
                    "differentiation": "Built for marketing teams, trusted by enterprises",
                },
                "target_audience": ["enterprise_cmos", "vp_marketing", "marketing_ops"],
                "channels": ["linkedin", "email", "content", "events"],
                "key_messages": [
                    "Enterprise-grade security and compliance",
                    "Proven ROI with AI-powered automation",
                    "Seamless integration with existing tools",
                ],
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result["approval_status"] in [
            "approved",
            "conditional",
            "revision_needed",
        ]
        assert "messaging_score" in result.result

    @pytest.mark.asyncio
    async def test_brand_guidelines_update_and_training_workflow(
        self, director_config, mock_copywriter, mock_content_manager
    ):
        """Test brand guidelines update followed by agent training."""
        agent = DirectorOfCommunicationsAgent(config=director_config)
        agent._copywriter = mock_copywriter
        agent._content_manager = mock_content_manager

        # Step 1: Update brand guidelines
        guidelines_task = Task(
            task_id="guidelines_workflow_001",
            task_type="define_brand_guidelines",
            priority=TaskPriority.HIGH,
            parameters={
                "guideline_type": "update",
                "brand_personality": [
                    "professional",
                    "innovative",
                    "trustworthy",
                    "results-driven",
                ],
                "tone_attributes": {
                    "professional_casual_scale": 8,
                    "serious_playful_scale": 7,
                },
                "voice_characteristics": {
                    "clarity": "Use precise, actionable language",
                    "expertise": "Demonstrate deep marketing knowledge",
                },
                "update_reason": "Shift to more enterprise-focused positioning",
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        guidelines_result = await agent.execute(guidelines_task)

        assert guidelines_result.status == TaskStatus.COMPLETED
        assert "guidelines_id" in guidelines_result.result
        assert "version" in guidelines_result.result
        # Training recommendation may be in distribution_list or other fields
        assert "distribution_list" in guidelines_result.result or "training_required" in guidelines_result.result

        # Step 2: Train agents on new guidelines
        training_task = Task(
            task_id="training_workflow_001",
            task_type="train_brand_voice",
            priority=TaskPriority.HIGH,
            parameters={
                "training_type": "guidelines_update",
                "target_agents": ["copywriter_001", "content_manager_001"],
                "focus_areas": ["tone", "voice_characteristics", "enterprise_positioning"],
                "assessment_required": True,
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.DIRECTOR_COMMUNICATIONS,
            created_at=datetime.now(),
        )

        training_result = await agent.execute(training_task)

        assert training_result.status == TaskStatus.COMPLETED
        assert "training_session_id" in training_result.result
        assert "agents_trained" in training_result.result
        assert len(training_result.result["agents_trained"]) == 2

    @pytest.mark.asyncio
    async def test_pr_materials_review_workflow(
        self, director_config, mock_llm_client, mock_cmo_agent
    ):
        """Test press release review and approval workflow."""
        agent = DirectorOfCommunicationsAgent(config=director_config)
        agent._llm_client = mock_llm_client
        agent._cmo_agent = mock_cmo_agent

        task = Task(
            task_id="pr_workflow_001",
            task_type="review_pr_materials",
            priority=TaskPriority.HIGH,
            parameters={
                "material_id": "press_release_funding_round",
                "material_type": "press_release",
                "material_content": """
                FOR IMMEDIATE RELEASE

                Company Announces $50M Series C Funding Round

                AI-powered marketing platform secures funding to accelerate enterprise expansion

                SAN FRANCISCO - Company today announced a $50M Series C funding round led by
                Enterprise Ventures. The funding will support product development, enterprise
                customer acquisition, and international expansion.

                "This investment validates our vision for AI-powered marketing automation,"
                said CEO. "We're committed to helping enterprise marketing teams achieve
                measurable results through intelligent automation."

                About Company:
                Company is the leading AI-powered marketing automation platform trusted by
                enterprise marketing teams worldwide.

                Contact: pr@company.com
                """,
                "distribution_plan": {
                    "channels": ["newswire", "website", "social_media", "email"],
                    "timing": "2025-11-15 09:00 AM EST",
                },
                "approval_urgency": "time_sensitive",
                "target_audience": ["media", "investors", "customers", "prospects"],
                "legal_approved": True,
                "executive_approved": True,
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result["approval_status"] in [
            "approved",
            "approved_with_edits",
            "revision_needed",
        ]
        assert "brand_voice_score" in result.result
        assert "risk_assessment" in result.result

    @pytest.mark.asyncio
    async def test_multi_campaign_messaging_coordination(
        self, director_config, mock_vp_marketing
    ):
        """Test messaging coordination across multiple simultaneous campaigns."""
        agent = DirectorOfCommunicationsAgent(config=director_config)
        agent._vp_marketing_agent = mock_vp_marketing

        task = Task(
            task_id="coordination_workflow_001",
            task_type="coordinate_messaging",
            priority=TaskPriority.HIGH,
            parameters={
                "coordination_scope": "product_launch",
                "campaigns": [
                    "campaign_product_launch_enterprise",
                    "campaign_product_launch_smb",
                    "campaign_product_launch_webinar",
                ],
                "timeframe": {"start_date": "2025-11-15", "end_date": "2025-12-15"},
                "channels": ["linkedin", "email", "content", "paid_ads", "events"],
                "primary_message": "Introducing AI-powered marketing automation for teams of all sizes",
                "stakeholders": ["marketing", "sales", "product", "customer_success"],
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.VP_MARKETING,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert "unified_messaging_framework" in result.result
        assert "coordination_plan" in result.result
        assert "conflicts_resolved" in result.result
        assert "primary_message" in result.result["unified_messaging_framework"]

    @pytest.mark.asyncio
    async def test_brand_sentiment_monitoring_with_alert(
        self, director_config, mock_vp_marketing
    ):
        """Test brand sentiment monitoring with negative sentiment alert."""
        agent = DirectorOfCommunicationsAgent(config=director_config)
        agent._vp_marketing_agent = mock_vp_marketing

        task = Task(
            task_id="sentiment_workflow_001",
            task_type="monitor_brand_sentiment",
            priority=TaskPriority.NORMAL,
            parameters={
                "monitoring_scope": "realtime",
                "channels": ["twitter", "linkedin", "reddit", "review_sites"],
                "timeframe": {"start_date": "2025-11-01", "end_date": "2025-11-03"},
                "keywords": [
                    "AI marketing",
                    "marketing automation",
                    "enterprise marketing",
                ],
                "competitors": ["Competitor A", "Competitor B"],
                "alert_threshold": -0.15,
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert "overall_sentiment" in result.result
        assert "channel_sentiment" in result.result
        assert "trending_topics" in result.result
        assert "recommendations" in result.result

    @pytest.mark.asyncio
    async def test_communications_audit_workflow(self, director_config):
        """Test communications audit across campaign."""
        agent = DirectorOfCommunicationsAgent(config=director_config)

        task = Task(
            task_id="audit_workflow_001",
            task_type="audit_communications",
            priority=TaskPriority.NORMAL,
            parameters={
                "audit_scope": "campaign",
                "audit_target": "campaign_q3_enterprise",
                "timeframe": {"start_date": "2025-07-01", "end_date": "2025-09-30"},
                "sample_size": 100,
                "focus_areas": ["tone", "voice_characteristics", "prohibited_language"],
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert "compliance_summary" in result.result
        assert "violations" in result.result
        assert "recommendations" in result.result

    @pytest.mark.asyncio
    async def test_brand_health_report_generation(self, director_config):
        """Test comprehensive brand health reporting for CMO."""
        agent = DirectorOfCommunicationsAgent(config=director_config)

        task = Task(
            task_id="report_workflow_001",
            task_type="report_brand_health",
            priority=TaskPriority.HIGH,
            parameters={
                "report_type": "quarterly",
                "timeframe": {"start_date": "2025-07-01", "end_date": "2025-09-30"},
                "include_sentiment": True,
                "include_compliance": True,
                "include_crisis": True,
                "comparison_period": {
                    "start_date": "2025-04-01",
                    "end_date": "2025-06-30",
                },
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        # Implementation may use "summary" or "executive_summary"
        assert "summary" in result.result or "executive_summary" in result.result
        assert "brand_metrics" in result.result
        assert "trends" in result.result or "key_highlights" in result.result
        assert "recommendations" in result.result

    @pytest.mark.asyncio
    async def test_crisis_to_resolution_complete_workflow(
        self, director_config, mock_cmo_agent, mock_vp_marketing
    ):
        """Test complete crisis workflow from detection to resolution."""
        agent = DirectorOfCommunicationsAgent(config=director_config)
        agent._cmo_agent = mock_cmo_agent
        agent._vp_marketing_agent = mock_vp_marketing

        # Step 1: Crisis activation
        crisis_task = Task(
            task_id="crisis_full_001",
            task_type="manage_crisis",
            priority=TaskPriority.URGENT,
            parameters={
                "crisis_id": "crisis_product_issue_001",
                "crisis_type": "product_issue",
                "severity": "medium",
                "description": "Product bug affecting email send functionality",
                "affected_channels": ["email", "website"],
                "stakeholders": ["customers", "support_team"],
                "time_discovered": "2025-11-03T16:00:00Z",
                "current_status": "investigating",
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.SOCIAL_MEDIA_MANAGER,
            created_at=datetime.now(),
        )

        crisis_result = await agent.execute(crisis_task)

        assert crisis_result.status == TaskStatus.COMPLETED
        assert crisis_result.result["response_status"] in ["activated", "in_progress"]
        assert "holding_statement" in crisis_result.result

        # Step 2: Monitor sentiment during crisis
        sentiment_task = Task(
            task_id="crisis_sentiment_001",
            task_type="monitor_brand_sentiment",
            priority=TaskPriority.URGENT,
            parameters={
                "monitoring_scope": "realtime",
                "channels": ["twitter", "linkedin", "email"],
                "timeframe": {"start_date": "2025-11-03", "end_date": "2025-11-03"},
                "keywords": ["email bug", "send failure", "email not working"],
                "alert_threshold": -0.20,
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.DIRECTOR_COMMUNICATIONS,
            created_at=datetime.now(),
        )

        sentiment_result = await agent.execute(sentiment_task)

        assert sentiment_result.status == TaskStatus.COMPLETED
        assert "overall_sentiment" in sentiment_result.result

    @pytest.mark.asyncio
    async def test_graceful_degradation_llm_unavailable(self, director_config):
        """Test graceful degradation when LLM client unavailable."""
        agent = DirectorOfCommunicationsAgent(config=director_config)
        # No LLM client configured

        task = Task(
            task_id="degradation_001",
            task_type="review_brand_voice",
            priority=TaskPriority.NORMAL,
            parameters={
                "content_id": "blog_test",
                "content_type": "blog_post",
                "content_text": "Test content for graceful degradation",
                "review_level": "standard",
            },
            assigned_to=AgentRole.DIRECTOR_COMMUNICATIONS,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Should complete with fallback analysis
        assert result.status == TaskStatus.COMPLETED
        assert "brand_voice_score" in result.result
        assert "review_status" in result.result

    @pytest.mark.asyncio
    async def test_agent_cleanup(self, director_config):
        """Test that agent stops cleanly."""
        agent = DirectorOfCommunicationsAgent(config=director_config)

        assert agent.is_available is True
        await agent.stop()
        assert agent.is_available is False
