"""
Regression Tests - Base Agent Behavior.

WHY: Ensures that known good behavior doesn't change unintentionally.
     Captures baseline behavior and detects regressions.

HOW: Tests specific behaviors with exact expected outputs.
     Uses snapshots of known good states.

Test Coverage:
- Task validation behavior
- Error message formats
- Result structure
- Configuration validation
- Exception context preservation
"""

import asyncio
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.base import (
    AgentConfig,
    AgentMessage,
    AgentResult,
    AgentRole,
    BaseAgent,
    Task,
    TaskPriority,
    TaskStatus,
)
from core.exceptions import (
    AgentCommunicationError,
    AgentExecutionError,
    AgentValidationError,
)


# Test agent implementation
class RegressionTestAgent(BaseAgent):
    """Concrete agent for regression testing."""

    async def _execute_task(self, task: Task) -> dict[str, Any]:
        """Execute task with predictable output."""
        return {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "result": "success",
        }


@pytest.mark.regression
class TestTaskValidationRegression:
    """Regression tests for task validation behavior."""

    @pytest.fixture
    def agent(self):
        """Create test agent."""
        config = AgentConfig(
            agent_id="regression_test_agent_001",
            role=AgentRole.COPYWRITER,
        )
        return RegressionTestAgent(config=config)

    def test_task_validation_with_wrong_role_returns_false(self, agent):
        """
        Regression: Task validation returns False for wrong role.

        WHY: Ensures validation behavior remains consistent.
        BASELINE: Established 2025-11-03
        """
        task = Task(
            task_id="reg_task_001",
            task_type="analyze_data",
            priority=TaskPriority.NORMAL,
            parameters={"data": "test"},
            assigned_to=AgentRole.ANALYTICS_SPECIALIST,  # Wrong role
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        result = asyncio.run(agent.validate_task(task))

        # BASELINE: Wrong role should return False
        assert result is False

    def test_task_validation_with_correct_role_returns_true(self, agent):
        """
        Regression: Task validation returns True for correct role.

        WHY: Ensures validation behavior remains consistent.
        BASELINE: Established 2025-11-03
        """
        task = Task(
            task_id="reg_task_002",
            task_type="create_blog",
            priority=TaskPriority.NORMAL,
            parameters={"topic": "AI"},
            assigned_to=AgentRole.COPYWRITER,  # Correct role
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = asyncio.run(agent.validate_task(task))

        # BASELINE: Correct role should return True
        assert result is True

    def test_task_validation_when_agent_unavailable_returns_false(self):
        """
        Regression: Task validation returns False when agent unavailable.

        WHY: Ensures availability checking remains consistent.
        BASELINE: Established 2025-11-03
        """
        config = AgentConfig(
            agent_id="regression_test_agent_002",
            role=AgentRole.COPYWRITER,
            max_concurrent_tasks=1,
        )
        agent = RegressionTestAgent(config=config)

        task = Task(
            task_id="reg_task_003",
            task_type="create_blog",
            priority=TaskPriority.NORMAL,
            parameters={"topic": "AI"},
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        # Make agent busy
        agent._current_tasks.add("other_task")

        result = asyncio.run(agent.validate_task(task))

        # BASELINE: Busy agent should return False
        assert result is False


@pytest.mark.regression
class TestErrorMessageRegression:
    """Regression tests for error message formats."""

    @pytest.fixture
    def agent(self):
        """Create test agent."""
        config = AgentConfig(
            agent_id="regression_test_agent_003",
            role=AgentRole.COPYWRITER,
        )
        return RegressionTestAgent(config=config)

    @pytest.mark.asyncio
    async def test_validation_error_message_format(self, agent):
        """
        Regression: Validation error has consistent message format.

        WHY: Ensures error messages remain parseable and informative.
        BASELINE: Established 2025-11-03
        """
        task = Task(
            task_id="reg_task_004",
            task_type="analyze_data",
            priority=TaskPriority.NORMAL,
            parameters={},
            assigned_to=AgentRole.ANALYTICS_SPECIALIST,  # Wrong role
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        with pytest.raises(AgentValidationError) as exc_info:
            await agent.execute(task)

        error = exc_info.value

        # BASELINE: Error message structure
        assert "validation failed" in error.message.lower()
        assert error.context is not None
        assert "agent_id" in error.context
        assert "task_id" in error.context
        assert error.context["agent_id"] == "regression_test_agent_003"
        assert error.context["task_id"] == "reg_task_004"

    @pytest.mark.asyncio
    async def test_execution_error_preserves_context(self, agent):
        """
        Regression: Execution errors preserve full context.

        WHY: Ensures debugging information is consistently available.
        BASELINE: Established 2025-11-03
        """
        task = Task(
            task_id="reg_task_005",
            task_type="create_blog",
            priority=TaskPriority.NORMAL,
            parameters={"topic": "AI"},
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        with patch.object(
            agent, "_execute_task", new_callable=AsyncMock
        ) as mock_execute:
            original_error = ValueError("Test error")
            mock_execute.side_effect = original_error

            with pytest.raises(AgentExecutionError) as exc_info:
                await agent.execute(task)

            error = exc_info.value

            # BASELINE: Context preservation
            assert error.context["agent_id"] == "regression_test_agent_003"
            assert error.context["task_id"] == "reg_task_005"
            assert error.context["task_type"] == "create_blog"
            assert error.original_exception == original_error


@pytest.mark.regression
class TestResultStructureRegression:
    """Regression tests for result structure."""

    @pytest.fixture
    def agent(self):
        """Create test agent."""
        config = AgentConfig(
            agent_id="regression_test_agent_004",
            role=AgentRole.COPYWRITER,
        )
        return RegressionTestAgent(config=config)

    @pytest.mark.asyncio
    async def test_success_result_structure(self, agent):
        """
        Regression: Success results have consistent structure.

        WHY: Ensures result structure remains stable for consumers.
        BASELINE: Established 2025-11-03
        """
        task = Task(
            task_id="reg_task_006",
            task_type="create_blog",
            priority=TaskPriority.NORMAL,
            parameters={"topic": "AI", "word_count": 1500},
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        result = await agent.execute(task)

        # BASELINE: Result structure
        assert isinstance(result, AgentResult)
        assert result.task_id == "reg_task_006"
        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert result.error is None
        assert result.metadata is not None

        # BASELINE: Metadata structure
        assert "agent_id" in result.metadata
        assert "execution_time" in result.metadata
        assert "completed_at" in result.metadata
        assert result.metadata["agent_id"] == "regression_test_agent_004"
        assert isinstance(result.metadata["execution_time"], float)
        assert result.metadata["execution_time"] >= 0


@pytest.mark.regression
class TestConfigurationValidationRegression:
    """Regression tests for configuration validation."""

    def test_empty_agent_id_raises_validation_error(self):
        """
        Regression: Empty agent_id raises ValueError.

        WHY: Ensures validation remains strict.
        BASELINE: Established 2025-11-03
        """
        with pytest.raises(ValueError) as exc_info:
            AgentConfig(
                agent_id="",  # Empty
                role=AgentRole.COPYWRITER,
            )

        # BASELINE: Error message
        assert "agent_id" in str(exc_info.value).lower()

    def test_invalid_agent_id_characters_raises_error(self):
        """
        Regression: Invalid characters in agent_id raises ValueError.

        WHY: Ensures agent_id format validation remains consistent.
        BASELINE: Established 2025-11-03
        """
        with pytest.raises(ValueError) as exc_info:
            AgentConfig(
                agent_id="invalid-agent@123",  # Special chars
                role=AgentRole.COPYWRITER,
            )

        # BASELINE: Error mentions invalid characters
        assert "invalid characters" in str(exc_info.value).lower()

    def test_temperature_range_validation(self):
        """
        Regression: Temperature must be 0.0-1.0.

        WHY: Ensures LLM config validation remains strict.
        BASELINE: Established 2025-11-03
        """
        from agents.base.agent_config import LLMConfig

        # Too low
        with pytest.raises(ValueError):
            LLMConfig(temperature=-0.1)

        # Too high
        with pytest.raises(ValueError):
            LLMConfig(temperature=1.1)

        # Valid boundaries
        LLMConfig(temperature=0.0)  # Should not raise
        LLMConfig(temperature=1.0)  # Should not raise

    def test_model_provider_mismatch_raises_error(self):
        """
        Regression: Mismatched model and provider raises ValueError.

        WHY: Ensures provider validation remains strict.
        BASELINE: Established 2025-11-03
        """
        from agents.base.agent_config import LLMConfig

        # Claude model with Anthropic provider (valid)
        LLMConfig(provider="anthropic", model="claude-sonnet-3-5")  # Should not raise

        # GPT model with Anthropic provider (invalid)
        with pytest.raises(ValueError) as exc_info:
            LLMConfig(provider="anthropic", model="gpt-4")

        assert "invalid for provider" in str(exc_info.value).lower()

        # Claude model with OpenAI provider (invalid)
        with pytest.raises(ValueError) as exc_info:
            LLMConfig(provider="openai", model="claude-opus-3")

        assert "invalid for provider" in str(exc_info.value).lower()


@pytest.mark.regression
class TestAgentAvailabilityRegression:
    """Regression tests for agent availability tracking."""

    def test_agent_starts_available(self):
        """
        Regression: Agent is available on creation.

        WHY: Ensures initial state remains consistent.
        BASELINE: Established 2025-11-03
        """
        config = AgentConfig(
            agent_id="regression_test_agent_005",
            role=AgentRole.COPYWRITER,
        )
        agent = RegressionTestAgent(config=config)

        # BASELINE: New agent is available
        assert agent.is_available is True
        assert len(agent._current_tasks) == 0

    @pytest.mark.asyncio
    async def test_agent_unavailable_after_stop(self):
        """
        Regression: Agent is unavailable after stop().

        WHY: Ensures shutdown behavior remains consistent.
        BASELINE: Established 2025-11-03
        """
        config = AgentConfig(
            agent_id="regression_test_agent_006",
            role=AgentRole.COPYWRITER,
        )
        agent = RegressionTestAgent(config=config)

        assert agent.is_available is True

        await agent.stop()

        # BASELINE: Stopped agent is unavailable
        assert agent.is_available is False

    @pytest.mark.asyncio
    async def test_agent_available_increases_with_max_concurrent_tasks(self):
        """
        Regression: Agent handles multiple concurrent tasks correctly.

        WHY: Ensures concurrency limits work as expected.
        BASELINE: Established 2025-11-03
        """
        config = AgentConfig(
            agent_id="regression_test_agent_007",
            role=AgentRole.COPYWRITER,
            max_concurrent_tasks=3,
        )
        agent = RegressionTestAgent(config=config)

        assert agent.is_available is True

        # Add tasks
        agent._current_tasks.add("task_1")
        assert agent.is_available is True  # 1/3

        agent._current_tasks.add("task_2")
        assert agent.is_available is True  # 2/3

        agent._current_tasks.add("task_3")
        assert agent.is_available is False  # 3/3 (full)

        # Remove task
        agent._current_tasks.remove("task_1")
        assert agent.is_available is True  # 2/3


@pytest.mark.regression
def test_protocol_interface_signature():
    """
    Regression: AgentProtocol has expected method signatures.

    WHY: Ensures protocol interface remains stable.
    BASELINE: Established 2025-11-03
    """
    import inspect

    from agents.base.agent_protocol import AgentProtocol

    # Get all methods defined in Protocol
    protocol_methods = [
        name
        for name, _ in inspect.getmembers(AgentProtocol, predicate=inspect.isfunction)
    ]

    # BASELINE: Expected protocol methods
    expected_methods = [
        "execute",
        "validate_task",
        "send_message",
        "receive_messages",
        "stop",
    ]

    for method in expected_methods:
        assert method in protocol_methods, f"Protocol missing method: {method}"
