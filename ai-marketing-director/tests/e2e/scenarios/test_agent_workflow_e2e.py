"""
End-to-End Tests - Complete Agent Workflows.

WHY: Tests complete user-facing workflows from start to finish.
     Validates entire system behavior with realistic scenarios.

HOW: Simulates real usage patterns with multiple agents and components.
     Uses realistic data and timing.

IMPORTANT: These are the slowest tests. Run separately in CI.

Test Scenarios:
- Agent creation and initialization
- Complete task lifecycle (assignment → execution → completion)
- Multi-agent collaboration
- Error handling and recovery
- System monitoring and metrics
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
from agents.base.agent_config import (
    create_executive_config,
    create_management_config,
    create_specialist_config,
)


# E2E test agent implementations
class E2ECopywriterAgent(BaseAgent):
    """Copywriter agent for E2E testing."""

    async def _execute_task(self, task: Task) -> dict[str, Any]:
        """Execute copywriting task."""
        if task.task_type == "create_blog":
            # Simulate blog creation
            await asyncio.sleep(0.05)  # Simulate LLM call
            return {
                "content_type": "blog",
                "title": f"Blog about {task.parameters.get('topic')}",
                "word_count": task.parameters.get("word_count", 1500),
                "content": f"This is a blog post about {task.parameters.get('topic')}...",
                "status": "draft",
            }
        elif task.task_type == "create_social_post":
            await asyncio.sleep(0.02)
            return {
                "content_type": "social_post",
                "platform": task.parameters.get("platform", "linkedin"),
                "text": f"Check out our latest insights on {task.parameters.get('topic')}!",
                "status": "draft",
            }
        else:
            raise ValueError(f"Unknown task type: {task.task_type}")


class E2EContentManagerAgent(BaseAgent):
    """Content manager agent for E2E testing."""

    async def _execute_task(self, task: Task) -> dict[str, Any]:
        """Execute content management task."""
        if task.task_type == "review_content":
            await asyncio.sleep(0.03)
            return {
                "review_status": "approved",
                "feedback": "Looks good, ready to publish",
                "quality_score": 0.95,
            }
        elif task.task_type == "assign_content_task":
            return {
                "assigned_to": task.parameters.get("assign_to"),
                "task_id": task.parameters.get("subtask_id"),
                "status": "assigned",
            }
        else:
            raise ValueError(f"Unknown task type: {task.task_type}")


@pytest.mark.e2e
@pytest.mark.slow
class TestSingleAgentWorkflow:
    """E2E tests for single agent complete workflows."""

    @pytest.mark.asyncio
    async def test_complete_blog_creation_workflow(self):
        """
        E2E: Complete blog creation workflow from task to result.

        Workflow:
        1. Create agent
        2. Assign blog creation task
        3. Agent executes task
        4. Return completed blog

        WHY: Validates end-to-end blog creation process.
        """
        # Step 1: Create copywriter agent
        config = create_specialist_config(
            agent_id="e2e_copywriter_001", role=AgentRole.COPYWRITER
        )
        copywriter = E2ECopywriterAgent(config=config)

        assert copywriter.is_available is True

        # Step 2: Create blog task
        task = Task(
            task_id="e2e_blog_task_001",
            task_type="create_blog",
            priority=TaskPriority.NORMAL,
            parameters={
                "topic": "AI Marketing Automation",
                "word_count": 2000,
                "target_audience": "Marketing Directors",
            },
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        # Step 3: Execute task
        result = await copywriter.execute(task)

        # Step 4: Verify result
        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert result.result["content_type"] == "blog"
        assert result.result["word_count"] == 2000
        assert "AI Marketing Automation" in result.result["title"]
        assert result.metadata["agent_id"] == "e2e_copywriter_001"
        assert result.metadata["execution_time"] > 0

        # Agent should be available again
        assert copywriter.is_available is True

    @pytest.mark.asyncio
    async def test_multiple_sequential_tasks_workflow(self):
        """
        E2E: Agent handles multiple tasks sequentially.

        Workflow:
        1. Create agent
        2. Execute task 1 (blog)
        3. Execute task 2 (social post)
        4. Execute task 3 (blog)

        WHY: Validates agent can handle sustained workload.
        """
        config = create_specialist_config(
            agent_id="e2e_copywriter_002", role=AgentRole.COPYWRITER
        )
        copywriter = E2ECopywriterAgent(config=config)

        tasks = [
            Task(
                task_id=f"e2e_sequential_task_{i}",
                task_type="create_blog" if i % 2 == 0 else "create_social_post",
                priority=TaskPriority.NORMAL,
                parameters={
                    "topic": f"Topic {i}",
                    "word_count": 1500 if i % 2 == 0 else None,
                    "platform": "linkedin" if i % 2 != 0 else None,
                },
                assigned_to=AgentRole.COPYWRITER,
                assigned_by=AgentRole.CONTENT_MANAGER,
                created_at=datetime.now(),
            )
            for i in range(3)
        ]

        results = []
        for task in tasks:
            result = await copywriter.execute(task)
            results.append(result)

        # All tasks completed
        assert len(results) == 3
        assert all(r.status == TaskStatus.COMPLETED for r in results)

        # Agent still available
        assert copywriter.is_available is True


@pytest.mark.e2e
@pytest.mark.slow
class TestMultiAgentWorkflow:
    """E2E tests for multi-agent collaboration workflows."""

    @pytest.mark.asyncio
    async def test_content_creation_and_review_workflow(self):
        """
        E2E: Complete content creation and review workflow.

        Workflow:
        1. Content Manager assigns task to Copywriter
        2. Copywriter creates blog
        3. Content Manager reviews blog
        4. Content approved for publication

        WHY: Validates multi-agent collaboration.
        """
        # Create agents
        manager_config = create_management_config(
            agent_id="e2e_content_manager_001", role=AgentRole.CONTENT_MANAGER
        )
        copywriter_config = create_specialist_config(
            agent_id="e2e_copywriter_003", role=AgentRole.COPYWRITER
        )

        manager = E2EContentManagerAgent(config=manager_config)
        copywriter = E2ECopywriterAgent(config=copywriter_config)

        # Step 1: Manager assigns task
        assignment_task = Task(
            task_id="e2e_assignment_001",
            task_type="assign_content_task",
            priority=TaskPriority.NORMAL,
            parameters={
                "assign_to": "copywriter",
                "subtask_id": "e2e_blog_creation_001",
            },
            assigned_to=AgentRole.CONTENT_MANAGER,
            assigned_by=AgentRole.CMO,
            created_at=datetime.now(),
        )

        assignment_result = await manager.execute(assignment_task)
        assert assignment_result.result["status"] == "assigned"

        # Step 2: Copywriter creates content
        creation_task = Task(
            task_id="e2e_blog_creation_001",
            task_type="create_blog",
            priority=TaskPriority.NORMAL,
            parameters={
                "topic": "AI-Powered Marketing Analytics",
                "word_count": 2500,
            },
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        creation_result = await copywriter.execute(creation_task)
        assert creation_result.result["status"] == "draft"
        blog_content = creation_result.result

        # Step 3: Manager reviews content
        review_task = Task(
            task_id="e2e_review_001",
            task_type="review_content",
            priority=TaskPriority.HIGH,
            parameters={
                "content_id": "e2e_blog_creation_001",
                "content": blog_content,
            },
            assigned_to=AgentRole.CONTENT_MANAGER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        review_result = await manager.execute(review_task)

        # Step 4: Verify complete workflow
        assert review_result.result["review_status"] == "approved"
        assert review_result.result["quality_score"] > 0.9

        # Both agents available
        assert manager.is_available is True
        assert copywriter.is_available is True

    @pytest.mark.asyncio
    async def test_concurrent_agents_handling_tasks(self):
        """
        E2E: Multiple agents working concurrently.

        Workflow:
        1. Create 3 copywriter agents
        2. Assign 9 tasks total (3 per agent)
        3. Execute all tasks concurrently
        4. Verify all complete successfully

        WHY: Validates system can scale with multiple agents.
        """
        # Create multiple copywriter agents
        agents = [
            E2ECopywriterAgent(
                config=create_specialist_config(
                    agent_id=f"e2e_copywriter_{i:03d}", role=AgentRole.COPYWRITER
                )
            )
            for i in range(3)
        ]

        # Create tasks for each agent
        all_tasks = []
        for agent_idx, agent in enumerate(agents):
            for task_idx in range(3):
                task = Task(
                    task_id=f"e2e_concurrent_task_a{agent_idx}_t{task_idx}",
                    task_type="create_blog",
                    priority=TaskPriority.NORMAL,
                    parameters={
                        "topic": f"Topic A{agent_idx}T{task_idx}",
                        "word_count": 1500,
                    },
                    assigned_to=AgentRole.COPYWRITER,
                    assigned_by=AgentRole.CONTENT_MANAGER,
                    created_at=datetime.now(),
                )
                all_tasks.append((agent, task))

        # Execute all tasks concurrently
        results = await asyncio.gather(
            *[agent.execute(task) for agent, task in all_tasks]
        )

        # Verify all completed
        assert len(results) == 9
        assert all(r.status == TaskStatus.COMPLETED for r in results)

        # All agents available
        assert all(agent.is_available for agent in agents)


@pytest.mark.e2e
@pytest.mark.slow
class TestErrorHandlingWorkflow:
    """E2E tests for error handling in complete workflows."""

    @pytest.mark.asyncio
    async def test_task_failure_recovery_workflow(self):
        """
        E2E: Agent recovers from task failure and continues working.

        Workflow:
        1. Assign task that fails
        2. Agent handles error
        3. Assign new valid task
        4. Agent completes successfully

        WHY: Validates system resilience and error recovery.
        """
        config = create_specialist_config(
            agent_id="e2e_copywriter_004", role=AgentRole.COPYWRITER
        )
        agent = E2ECopywriterAgent(config=config)

        # Task 1: Invalid task (will fail)
        invalid_task = Task(
            task_id="e2e_invalid_task_001",
            task_type="unknown_task_type",  # Invalid
            priority=TaskPriority.NORMAL,
            parameters={},
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        # Should fail gracefully
        from core.exceptions import AgentExecutionError

        with pytest.raises(AgentExecutionError):
            await agent.execute(invalid_task)

        # Agent should still be functional
        assert agent.is_available is True

        # Task 2: Valid task
        valid_task = Task(
            task_id="e2e_valid_task_001",
            task_type="create_blog",
            priority=TaskPriority.NORMAL,
            parameters={"topic": "Recovery Test", "word_count": 1500},
            assigned_to=AgentRole.COPYWRITER,
            assigned_by=AgentRole.CONTENT_MANAGER,
            created_at=datetime.now(),
        )

        # Should succeed
        result = await agent.execute(valid_task)
        assert result.status == TaskStatus.COMPLETED


@pytest.mark.e2e
@pytest.mark.slow
class TestAgentLifecycleWorkflow:
    """E2E tests for complete agent lifecycle."""

    @pytest.mark.asyncio
    async def test_complete_agent_lifecycle(self):
        """
        E2E: Complete agent lifecycle from creation to shutdown.

        Workflow:
        1. Create agent
        2. Execute multiple tasks
        3. Gracefully shutdown
        4. Verify cleanup

        WHY: Validates complete agent lifecycle management.
        """
        # Create agent
        config = create_specialist_config(
            agent_id="e2e_lifecycle_agent_001", role=AgentRole.COPYWRITER
        )
        agent = E2ECopywriterAgent(config=config)

        # Execute tasks
        tasks = [
            Task(
                task_id=f"e2e_lifecycle_task_{i}",
                task_type="create_blog",
                priority=TaskPriority.NORMAL,
                parameters={"topic": f"Topic {i}", "word_count": 1500},
                assigned_to=AgentRole.COPYWRITER,
                assigned_by=AgentRole.CONTENT_MANAGER,
                created_at=datetime.now(),
            )
            for i in range(5)
        ]

        for task in tasks:
            result = await agent.execute(task)
            assert result.status == TaskStatus.COMPLETED

        # Shutdown
        await agent.stop()

        # Verify shutdown
        assert agent.is_available is False


@pytest.mark.e2e
@pytest.mark.slow
def test_system_ready_for_production():
    """
    E2E: Meta-test verifying system is production-ready.

    WHY: Final checkpoint before deployment.
    """
    # This is a meta-test - actual validation is in other E2E tests
    # Here we just verify critical components are available

    # Can import all required modules
    from agents.base import AgentConfig, AgentProtocol, BaseAgent
    from agents.base.agent_config import (
        create_executive_config,
        create_management_config,
        create_specialist_config,
    )
    from core.exceptions import (
        AgentCommunicationError,
        AgentExecutionError,
        AgentValidationError,
    )

    # Can create configurations
    exec_config = create_executive_config("cmo_test", AgentRole.CMO)
    mgmt_config = create_management_config("manager_test", AgentRole.CONTENT_MANAGER)
    spec_config = create_specialist_config("specialist_test", AgentRole.COPYWRITER)

    assert exec_config is not None
    assert mgmt_config is not None
    assert spec_config is not None

    # System ready
    pass
