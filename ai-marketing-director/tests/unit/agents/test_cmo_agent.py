"""
Unit tests for CMO Agent (Chief Marketing Officer).

WHY: Ensures CMO Agent correctly provides strategic oversight and manages
     coordination across all management-layer agents.

HOW: Uses mocked management-layer agents to test delegation, approval workflows,
     budget allocation, and performance monitoring.

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


class TestCMOAgent:
    """Test suite for CMO Agent (Executive Layer)."""

    @pytest.fixture
    def agent_config(self):
        """Create CMO agent configuration for testing."""
        return AgentConfig(
            agent_id="cmo_001",
            role=AgentRole.CMO,
        )

    @pytest.fixture
    def mock_campaign_manager(self):
        """Create mocked Campaign Manager agent."""
        agent = AsyncMock()
        agent.agent_id = "campaign_001"
        agent.role = AgentRole.CAMPAIGN_MANAGER
        agent.is_available = True
        agent.validate_task = AsyncMock(return_value=True)
        agent.execute = AsyncMock(
            return_value=Mock(
                status=TaskStatus.COMPLETED,
                result={
                    "campaign_id": "campaign_test_001",
                    "name": "Q1 Product Launch",
                    "status": "created",
                    "budget_requested": 50000,
                    "expected_roi": 3.5,
                },
            )
        )
        return agent

    @pytest.fixture
    def mock_social_media_manager(self):
        """Create mocked Social Media Manager agent."""
        agent = AsyncMock()
        agent.agent_id = "social_media_001"
        agent.role = AgentRole.SOCIAL_MEDIA_MANAGER
        agent.is_available = True
        agent.validate_task = AsyncMock(return_value=True)
        agent.execute = AsyncMock(
            return_value=Mock(
                status=TaskStatus.COMPLETED,
                result={
                    "analytics": [
                        {"platform": "linkedin", "followers": 10000, "engagement": 500},
                        {"platform": "twitter", "followers": 25000, "engagement": 800},
                    ],
                    "total_followers": 35000,
                },
            )
        )
        return agent

    @pytest.fixture
    def mock_content_manager(self):
        """Create mocked Content Manager agent."""
        agent = AsyncMock()
        agent.agent_id = "content_001"
        agent.role = AgentRole.CONTENT_MANAGER
        agent.is_available = True
        agent.validate_task = AsyncMock(return_value=True)
        agent.execute = AsyncMock(
            return_value=Mock(
                status=TaskStatus.COMPLETED,
                result={"content_produced": 15, "content_published": 12},
            )
        )
        return agent

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent_config):
        """Test that CMO Agent initializes correctly."""
        from agents.executive.cmo import CMOAgent

        agent = CMOAgent(config=agent_config)

        assert agent.agent_id == "cmo_001"
        assert agent.role == AgentRole.CMO
        assert agent.is_available is True

    @pytest.mark.asyncio
    async def test_register_manager_agents(
        self,
        agent_config,
        mock_campaign_manager,
        mock_social_media_manager,
        mock_content_manager,
    ):
        """Test registering management-layer agents."""
        from agents.executive.cmo import CMOAgent

        agent = CMOAgent(config=agent_config)

        # Register management agents
        agent.register_manager(AgentRole.CAMPAIGN_MANAGER, mock_campaign_manager)
        agent.register_manager(
            AgentRole.SOCIAL_MEDIA_MANAGER, mock_social_media_manager
        )
        agent.register_manager(AgentRole.CONTENT_MANAGER, mock_content_manager)

        # Verify managers are registered
        assert agent.has_manager(AgentRole.CAMPAIGN_MANAGER) is True
        assert agent.has_manager(AgentRole.SOCIAL_MEDIA_MANAGER) is True
        assert agent.has_manager(AgentRole.CONTENT_MANAGER) is True

    @pytest.mark.asyncio
    async def test_create_marketing_strategy(self, agent_config):
        """Test creating a new marketing strategy."""
        from agents.executive.cmo import CMOAgent

        agent = CMOAgent(config=agent_config)

        task = Task(
            task_id="task_001",
            task_type="create_marketing_strategy",
            priority=TaskPriority.HIGH,
            parameters={
                "name": "2025 Growth Strategy",
                "objectives": [
                    "Increase brand awareness by 40%",
                    "Generate 10,000 qualified leads",
                    "Achieve 3.5x ROAS",
                ],
                "target_audiences": ["Enterprise CIOs", "Marketing Directors"],
                "key_initiatives": [
                    "Thought leadership campaign",
                    "Product launch series",
                ],
                "budget": 500000,
                "timeframe": "Q1-Q4 2025",
            },
            assigned_to=AgentRole.CMO,
            assigned_by=AgentRole.CMO,  # Self-directed for executive
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "strategy_id" in result.result
        assert result.result["name"] == "2025 Growth Strategy"
        assert result.result["status"] == "active"
        assert "objectives" in result.result

    @pytest.mark.asyncio
    async def test_approve_campaign(self, agent_config, mock_campaign_manager):
        """Test approving a campaign proposal."""
        from agents.executive.cmo import CMOAgent

        agent = CMOAgent(config=agent_config)
        agent.register_manager(AgentRole.CAMPAIGN_MANAGER, mock_campaign_manager)

        # First create a strategy so campaigns can be evaluated against it
        strategy_task = Task(
            task_id="task_001",
            task_type="create_marketing_strategy",
            priority=TaskPriority.HIGH,
            parameters={
                "name": "2025 Strategy",
                "objectives": ["Brand awareness"],
                "target_audiences": ["Enterprise"],
                "key_initiatives": ["Product launches"],
                "budget": 500000,
                "timeframe": "2025",
            },
            assigned_to=AgentRole.CMO,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )
        await agent.execute(strategy_task)

        # Now approve a campaign
        approve_task = Task(
            task_id="task_002",
            task_type="approve_campaign",
            priority=TaskPriority.HIGH,
            parameters={
                "campaign_id": "campaign_test_001",
                "requested_budget": 50000,
            },
            assigned_to=AgentRole.CMO,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(approve_task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "approved" in result.result
        assert "campaign_id" in result.result
        assert result.result["campaign_id"] == "campaign_test_001"

        # Verify Campaign Manager was called to get campaign details
        mock_campaign_manager.execute.assert_called()

    @pytest.mark.asyncio
    async def test_reject_campaign_insufficient_budget(
        self, agent_config, mock_campaign_manager
    ):
        """Test rejecting a campaign when budget insufficient."""
        from agents.executive.cmo import CMOAgent

        # Mock campaign with excessive budget request
        mock_campaign_manager.execute = AsyncMock(
            return_value=Mock(
                status=TaskStatus.COMPLETED,
                result={
                    "campaign_id": "campaign_expensive",
                    "name": "Expensive Campaign",
                    "status": "created",
                    "budget_requested": 600000,  # Exceeds total budget
                    "expected_roi": 2.0,
                },
            )
        )

        agent = CMOAgent(config=agent_config)
        agent.register_manager(AgentRole.CAMPAIGN_MANAGER, mock_campaign_manager)

        # Create strategy with limited budget
        strategy_task = Task(
            task_id="task_001",
            task_type="create_marketing_strategy",
            priority=TaskPriority.HIGH,
            parameters={
                "name": "Limited Budget Strategy",
                "objectives": ["Test"],
                "target_audiences": ["Test"],
                "key_initiatives": ["Test"],
                "budget": 500000,  # Total budget
                "timeframe": "2025",
            },
            assigned_to=AgentRole.CMO,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )
        await agent.execute(strategy_task)

        # Try to approve expensive campaign
        approve_task = Task(
            task_id="task_002",
            task_type="approve_campaign",
            priority=TaskPriority.HIGH,
            parameters={
                "campaign_id": "campaign_expensive",
                "requested_budget": 600000,
            },
            assigned_to=AgentRole.CMO,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(approve_task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result["approved"] is False
        assert "reason" in result.result
        assert "budget" in result.result["reason"].lower()

    @pytest.mark.asyncio
    async def test_allocate_budget(self, agent_config):
        """Test allocating budget across campaigns."""
        from agents.executive.cmo import CMOAgent

        agent = CMOAgent(config=agent_config)

        # First create strategy with budget
        strategy_task = Task(
            task_id="task_001",
            task_type="create_marketing_strategy",
            priority=TaskPriority.HIGH,
            parameters={
                "name": "Budget Test Strategy",
                "objectives": ["Test"],
                "target_audiences": ["Test"],
                "key_initiatives": ["Test"],
                "budget": 500000,
                "timeframe": "2025",
            },
            assigned_to=AgentRole.CMO,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )
        await agent.execute(strategy_task)

        # Allocate budget
        allocate_task = Task(
            task_id="task_002",
            task_type="allocate_budget",
            priority=TaskPriority.NORMAL,
            parameters={
                "allocations": [
                    {"campaign_id": "campaign_001", "amount": 100000},
                    {"campaign_id": "campaign_002", "amount": 150000},
                    {"campaign_id": "campaign_003", "amount": 75000},
                ],
            },
            assigned_to=AgentRole.CMO,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(allocate_task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "total_allocated" in result.result
        assert result.result["total_allocated"] == 325000
        assert "remaining_budget" in result.result
        assert result.result["remaining_budget"] == 175000

    @pytest.mark.asyncio
    async def test_monitor_performance(
        self,
        agent_config,
        mock_campaign_manager,
        mock_social_media_manager,
        mock_content_manager,
    ):
        """Test monitoring performance across all management agents."""
        from agents.executive.cmo import CMOAgent

        agent = CMOAgent(config=agent_config)

        # Register all managers
        agent.register_manager(AgentRole.CAMPAIGN_MANAGER, mock_campaign_manager)
        agent.register_manager(
            AgentRole.SOCIAL_MEDIA_MANAGER, mock_social_media_manager
        )
        agent.register_manager(AgentRole.CONTENT_MANAGER, mock_content_manager)

        task = Task(
            task_id="task_001",
            task_type="monitor_performance",
            priority=TaskPriority.NORMAL,
            parameters={"period": "Q1 2025"},
            assigned_to=AgentRole.CMO,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "performance_data" in result.result
        assert len(result.result["performance_data"]) >= 1

        # Verify all managers were queried
        mock_campaign_manager.execute.assert_called()
        mock_social_media_manager.execute.assert_called()
        mock_content_manager.execute.assert_called()

    @pytest.mark.asyncio
    async def test_coordinate_initiative(
        self, agent_config, mock_campaign_manager, mock_social_media_manager
    ):
        """Test coordinating multi-campaign initiative."""
        from agents.executive.cmo import CMOAgent

        agent = CMOAgent(config=agent_config)
        agent.register_manager(AgentRole.CAMPAIGN_MANAGER, mock_campaign_manager)
        agent.register_manager(
            AgentRole.SOCIAL_MEDIA_MANAGER, mock_social_media_manager
        )

        task = Task(
            task_id="task_001",
            task_type="coordinate_initiative",
            priority=TaskPriority.HIGH,
            parameters={
                "initiative_name": "Q1 Product Launch",
                "involved_managers": ["campaign_manager", "social_media_manager"],
                "objectives": ["Launch product", "Generate awareness"],
                "timeline": "2025-Q1",
            },
            assigned_to=AgentRole.CMO,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "initiative_id" in result.result
        assert "status" in result.result

    @pytest.mark.asyncio
    async def test_generate_executive_report(
        self, agent_config, mock_campaign_manager, mock_social_media_manager
    ):
        """Test generating executive-level report."""
        from agents.executive.cmo import CMOAgent

        agent = CMOAgent(config=agent_config)
        agent.register_manager(AgentRole.CAMPAIGN_MANAGER, mock_campaign_manager)
        agent.register_manager(
            AgentRole.SOCIAL_MEDIA_MANAGER, mock_social_media_manager
        )

        task = Task(
            task_id="task_001",
            task_type="generate_executive_report",
            priority=TaskPriority.NORMAL,
            parameters={
                "report_type": "quarterly",
                "period": "Q1 2025",
                "include_sections": [
                    "performance_summary",
                    "budget_utilization",
                    "key_achievements",
                ],
            },
            assigned_to=AgentRole.CMO,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "report_id" in result.result
        assert "sections" in result.result

    @pytest.mark.asyncio
    async def test_set_priorities(self, agent_config):
        """Test setting campaign priorities."""
        from agents.executive.cmo import CMOAgent

        agent = CMOAgent(config=agent_config)

        task = Task(
            task_id="task_001",
            task_type="set_priorities",
            priority=TaskPriority.HIGH,
            parameters={
                "priorities": [
                    {"campaign_id": "campaign_001", "priority": 1},
                    {"campaign_id": "campaign_002", "priority": 2},
                    {"campaign_id": "campaign_003", "priority": 3},
                ],
            },
            assigned_to=AgentRole.CMO,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert "priorities_set" in result.result
        assert result.result["priorities_set"] == 3

    @pytest.mark.asyncio
    async def test_validate_task_create_strategy(self, agent_config):
        """Test task validation for create_marketing_strategy task type."""
        from agents.executive.cmo import CMOAgent

        agent = CMOAgent(config=agent_config)

        # Valid task
        valid_task = Task(
            task_id="task_001",
            task_type="create_marketing_strategy",
            priority=TaskPriority.HIGH,
            parameters={
                "name": "Valid Strategy",
                "objectives": ["Test"],
                "target_audiences": ["Test"],
                "key_initiatives": ["Test"],
                "budget": 100000,
                "timeframe": "2025",
            },
            assigned_to=AgentRole.CMO,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(valid_task)
        assert is_valid is True

        # Invalid task (missing required fields)
        invalid_task = Task(
            task_id="task_002",
            task_type="create_marketing_strategy",
            priority=TaskPriority.HIGH,
            parameters={"name": "Incomplete Strategy"},  # Missing required fields
            assigned_to=AgentRole.CMO,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(invalid_task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_validate_task_approve_campaign(self, agent_config):
        """Test task validation for approve_campaign task type."""
        from agents.executive.cmo import CMOAgent

        agent = CMOAgent(config=agent_config)

        # Valid task
        valid_task = Task(
            task_id="task_001",
            task_type="approve_campaign",
            priority=TaskPriority.HIGH,
            parameters={"campaign_id": "campaign_001", "requested_budget": 50000},
            assigned_to=AgentRole.CMO,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(valid_task)
        assert is_valid is True

        # Invalid task (missing campaign_id)
        invalid_task = Task(
            task_id="task_002",
            task_type="approve_campaign",
            priority=TaskPriority.HIGH,
            parameters={"requested_budget": 50000},  # Missing campaign_id
            assigned_to=AgentRole.CMO,
            assigned_by=AgentRole.CAMPAIGN_MANAGER,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(invalid_task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_unsupported_task_type(self, agent_config):
        """Test that unsupported task types are rejected."""
        from agents.executive.cmo import CMOAgent

        agent = CMOAgent(config=agent_config)

        task = Task(
            task_id="task_001",
            task_type="unsupported_task",
            priority=TaskPriority.NORMAL,
            parameters={},
            assigned_to=AgentRole.CMO,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        is_valid = await agent.validate_task(task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_graceful_degradation_manager_failure(
        self, agent_config, mock_campaign_manager, mock_social_media_manager
    ):
        """Test graceful degradation when one manager fails."""
        from agents.executive.cmo import CMOAgent

        # Make social media manager fail
        mock_social_media_manager.execute = AsyncMock(
            side_effect=Exception("Social media API error")
        )

        agent = CMOAgent(config=agent_config)
        agent.register_manager(AgentRole.CAMPAIGN_MANAGER, mock_campaign_manager)
        agent.register_manager(
            AgentRole.SOCIAL_MEDIA_MANAGER, mock_social_media_manager
        )

        # Monitor performance should continue with partial results
        task = Task(
            task_id="task_001",
            task_type="monitor_performance",
            priority=TaskPriority.NORMAL,
            parameters={"period": "Q1 2025"},
            assigned_to=AgentRole.CMO,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # Should still complete with data from Campaign Manager
        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        # Should have fewer results due to failed manager
        assert len(result.result["performance_data"]) >= 1

    @pytest.mark.asyncio
    async def test_agent_stops_cleanly(
        self, agent_config, mock_campaign_manager, mock_social_media_manager
    ):
        """Test that agent stops cleanly."""
        from agents.executive.cmo import CMOAgent

        agent = CMOAgent(config=agent_config)
        agent.register_manager(AgentRole.CAMPAIGN_MANAGER, mock_campaign_manager)
        agent.register_manager(
            AgentRole.SOCIAL_MEDIA_MANAGER, mock_social_media_manager
        )

        # Should not raise exception
        await agent.stop()

        # Agent should no longer be available
        assert agent.is_available is False
