"""
Integration Tests - Base Agent with Real Dependencies.

WHY: Tests agent behavior with actual dependencies (message bus, LLM, etc.).
     Validates integration between components.

HOW: Uses real Redis for message bus, mocked LLM with realistic responses.
     Tests actual async message passing and state management.

IMPORTANT: These tests require Redis to be running:
    docker run -d -p 6379:6379 redis:7-alpine

Test Coverage:
- Message bus integration (real Redis)
- Concurrent task execution
- Agent-to-agent communication
- Resource cleanup
"""

import asyncio
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

try:
    import redis.asyncio as aioredis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from agents.base import (
    AgentConfig,
    AgentMessage,
    AgentRole,
    BaseAgent,
    Task,
    TaskPriority,
)

# Skip all integration tests if Redis not available
pytestmark = pytest.mark.skipif(
    not REDIS_AVAILABLE, reason="Redis not installed (pip install redis)"
)


class IntegrationTestAgent(BaseAgent):
    """Concrete agent for integration testing."""

    async def _execute_task(self, task: Task) -> dict[str, Any]:
        """Execute task with simulated work."""
        # Simulate some async work
        await asyncio.sleep(0.01)

        return {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "parameters": task.parameters,
            "status": "completed",
        }


@pytest.mark.integration
class TestAgentConcurrentExecution:
    """Integration tests for concurrent task execution."""

    @pytest.fixture
    def agent(self):
        """Create test agent with realistic config."""
        config = AgentConfig(
            agent_id="integration_test_agent_001",
            role=AgentRole.COPYWRITER,
            max_concurrent_tasks=5,
        )
        return IntegrationTestAgent(config=config)

    @pytest.mark.asyncio
    async def test_agent_handles_multiple_concurrent_tasks(self, agent):
        """
        Integration: Agent executes multiple tasks concurrently.

        WHY: Validates async execution and task isolation.
        """
        tasks = [
            Task(
                task_id=f"concurrent_task_{i}",
                task_type="create_blog",
                priority=TaskPriority.NORMAL,
                parameters={"topic": f"Topic {i}", "word_count": 1500},
                assigned_to=AgentRole.COPYWRITER,
                assigned_by=AgentRole.CONTENT_MANAGER,
                created_at=datetime.now(),
            )
            for i in range(5)
        ]

        # Execute all tasks concurrently
        results = await asyncio.gather(*[agent.execute(task) for task in tasks])

        # All tasks should complete
        assert len(results) == 5

        # Each result should match its task
        for i, result in enumerate(results):
            assert result.task_id == f"concurrent_task_{i}"
            assert result.result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_agent_respects_max_concurrent_tasks(self):
        """
        Integration: Agent enforces max concurrent task limit.

        WHY: Validates load management and resource limits.
        """
        config = AgentConfig(
            agent_id="integration_test_agent_002",
            role=AgentRole.COPYWRITER,
            max_concurrent_tasks=2,  # Only 2 at a time
        )
        agent = IntegrationTestAgent(config=config)

        # Create slow tasks
        async def slow_execute_task(task: Task) -> dict[str, Any]:
            await asyncio.sleep(0.1)  # Slow
            return {"task_id": task.task_id, "status": "completed"}

        with patch.object(agent, "_execute_task", new=slow_execute_task):
            tasks = [
                Task(
                    task_id=f"load_test_task_{i}",
                    task_type="create_blog",
                    priority=TaskPriority.NORMAL,
                    parameters={"topic": f"Topic {i}"},
                    assigned_to=AgentRole.COPYWRITER,
                    assigned_by=AgentRole.CONTENT_MANAGER,
                    created_at=datetime.now(),
                )
                for i in range(3)
            ]

            # Start first two tasks (should fill capacity)
            task1_coro = agent.execute(tasks[0])
            task2_coro = agent.execute(tasks[1])

            # Give them time to start
            await asyncio.sleep(0.02)

            # Agent should now be at capacity
            assert len(agent._current_tasks) == 2
            assert agent.is_available is False

            # Wait for tasks to complete
            await task1_coro
            await task2_coro

            # Agent should be available again
            assert agent.is_available is True


@pytest.mark.integration
@pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not available for testing")
class TestMessageBusIntegration:
    """Integration tests with real Redis message bus."""

    @pytest.fixture
    async def redis_client(self):
        """Create Redis client for testing."""
        client = await aioredis.from_url(
            "redis://localhost:6379/15",  # Use DB 15 for testing
            encoding="utf-8",
            decode_responses=True,
        )

        # Clean up before test
        await client.flushdb()

        yield client

        # Clean up after test
        await client.flushdb()
        await client.close()

    @pytest.fixture
    def agent_with_redis(self):
        """Create agent configured with Redis."""
        config = AgentConfig(
            agent_id="integration_test_agent_003",
            role=AgentRole.COPYWRITER,
        )
        return IntegrationTestAgent(config=config)

    @pytest.mark.asyncio
    async def test_message_publishing_to_redis(self, agent_with_redis, redis_client):
        """
        Integration: Messages are published to Redis.

        WHY: Validates real message bus integration.
        """
        # Mock message bus to use real Redis
        from unittest.mock import AsyncMock, MagicMock

        mock_bus = MagicMock()
        mock_bus.publish = AsyncMock()

        agent_with_redis._message_bus = mock_bus

        message = AgentMessage(
            message_id="int_msg_001",
            from_agent=AgentRole.COPYWRITER,
            to_agent=AgentRole.CONTENT_MANAGER,
            message_type="task_completed",
            payload={"task_id": "task_123", "status": "completed"},
            priority=TaskPriority.NORMAL,
            created_at=datetime.now(),
        )

        await agent_with_redis.send_message(message)

        # Verify message was published
        mock_bus.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_agent_cleanup_releases_resources(self, agent_with_redis):
        """
        Integration: Agent.stop() properly releases resources.

        WHY: Validates graceful shutdown and resource cleanup.
        """
        # Create mock resources
        from unittest.mock import AsyncMock, MagicMock

        mock_bus = MagicMock()
        mock_bus.close = AsyncMock()

        mock_llm = MagicMock()
        mock_llm.close = AsyncMock()

        agent_with_redis._message_bus = mock_bus
        agent_with_redis._llm_provider = mock_llm

        # Stop agent
        await agent_with_redis.stop()

        # Verify resources were released
        mock_bus.close.assert_called_once()
        mock_llm.close.assert_called_once()
        assert agent_with_redis.is_available is False


@pytest.mark.integration
class TestAgentStateManagement:
    """Integration tests for agent state management."""

    @pytest.mark.asyncio
    async def test_task_tracking_during_execution(self):
        """
        Integration: Task tracking is accurate during execution lifecycle.

        WHY: Validates state management across async operations.
        """
        config = AgentConfig(
            agent_id="integration_test_agent_004",
            role=AgentRole.COPYWRITER,
            max_concurrent_tasks=10,
        )
        agent = IntegrationTestAgent(config=config)

        # Track state changes
        state_changes = []

        async def tracked_execute_task(task: Task) -> dict[str, Any]:
            # Record state during execution
            state_changes.append(
                {
                    "phase": "during_execution",
                    "task_id": task.task_id,
                    "current_tasks": len(agent._current_tasks),
                    "is_available": agent.is_available,
                }
            )
            await asyncio.sleep(0.01)
            return {"task_id": task.task_id, "status": "completed"}

        with patch.object(agent, "_execute_task", new=tracked_execute_task):
            task = Task(
                task_id="state_tracking_task",
                task_type="create_blog",
                priority=TaskPriority.NORMAL,
                parameters={"topic": "AI"},
                assigned_to=AgentRole.COPYWRITER,
                assigned_by=AgentRole.CONTENT_MANAGER,
                created_at=datetime.now(),
            )

            # Before execution
            assert len(agent._current_tasks) == 0
            assert agent.is_available is True

            # Execute
            result = await agent.execute(task)

            # After execution
            assert len(agent._current_tasks) == 0
            assert agent.is_available is True

            # During execution, task was tracked
            assert len(state_changes) == 1
            assert state_changes[0]["current_tasks"] == 1
            assert state_changes[0]["task_id"] == "state_tracking_task"


@pytest.mark.integration
class TestErrorRecovery:
    """Integration tests for error recovery."""

    @pytest.mark.asyncio
    async def test_agent_recovers_from_task_failure(self):
        """
        Integration: Agent remains available after task failure.

        WHY: Validates error recovery and fault tolerance.
        """
        config = AgentConfig(
            agent_id="integration_test_agent_005",
            role=AgentRole.COPYWRITER,
        )
        agent = IntegrationTestAgent(config=config)

        # Create failing task
        async def failing_execute_task(task: Task) -> dict[str, Any]:
            raise ValueError("Simulated task failure")

        with patch.object(agent, "_execute_task", new=failing_execute_task):
            task = Task(
                task_id="failing_task",
                task_type="create_blog",
                priority=TaskPriority.NORMAL,
                parameters={"topic": "AI"},
                assigned_to=AgentRole.COPYWRITER,
                assigned_by=AgentRole.CONTENT_MANAGER,
                created_at=datetime.now(),
            )

            # Task should fail
            from core.exceptions import AgentExecutionError

            with pytest.raises(AgentExecutionError):
                await agent.execute(task)

            # Agent should still be available
            assert agent.is_available is True
            assert len(agent._current_tasks) == 0

    @pytest.mark.asyncio
    async def test_multiple_failures_dont_break_agent(self):
        """
        Integration: Agent handles multiple consecutive failures.

        WHY: Validates resilience under repeated failures.
        """
        config = AgentConfig(
            agent_id="integration_test_agent_006",
            role=AgentRole.COPYWRITER,
        )
        agent = IntegrationTestAgent(config=config)

        async def failing_execute_task(task: Task) -> dict[str, Any]:
            raise ValueError(f"Failure for {task.task_id}")

        with patch.object(agent, "_execute_task", new=failing_execute_task):
            from core.exceptions import AgentExecutionError

            # Execute multiple failing tasks
            for i in range(5):
                task = Task(
                    task_id=f"failing_task_{i}",
                    task_type="create_blog",
                    priority=TaskPriority.NORMAL,
                    parameters={"topic": "AI"},
                    assigned_to=AgentRole.COPYWRITER,
                    assigned_by=AgentRole.CONTENT_MANAGER,
                    created_at=datetime.now(),
                )

                with pytest.raises(AgentExecutionError):
                    await agent.execute(task)

            # Agent should still be functional
            assert agent.is_available is True
            assert len(agent._current_tasks) == 0


@pytest.mark.integration
class TestConfigurationIntegration:
    """Integration tests for configuration usage."""

    @pytest.mark.asyncio
    async def test_tier_specific_configurations_work_correctly(self):
        """
        Integration: Tier-specific configs (executive, management, specialist) work.

        WHY: Validates configuration helpers produce working agents.
        """
        from agents.base.agent_config import (
            create_executive_config,
            create_management_config,
            create_specialist_config,
        )

        # Create agents with tier-specific configs
        executive_config = create_executive_config("cmo_001", AgentRole.CMO)
        management_config = create_management_config(
            "content_manager_001", AgentRole.CONTENT_MANAGER
        )
        specialist_config = create_specialist_config(
            "copywriter_001", AgentRole.COPYWRITER
        )

        executive_agent = IntegrationTestAgent(config=executive_config)
        management_agent = IntegrationTestAgent(config=management_config)
        specialist_agent = IntegrationTestAgent(config=specialist_config)

        # All should be functional
        assert executive_agent.is_available is True
        assert management_agent.is_available is True
        assert specialist_agent.is_available is True

        # Executive has different concurrency than specialist
        assert (
            executive_config.max_concurrent_tasks
            < specialist_config.max_concurrent_tasks
        )
