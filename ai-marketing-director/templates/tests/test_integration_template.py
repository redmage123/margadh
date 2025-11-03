"""
Integration Test Template.

HOW TO USE:
1. Copy this file to your tests/integration/ directory
2. Replace [FEATURE] with the feature you're testing
3. Use REAL services (test database, test message bus, etc.)
4. Mark with @pytest.mark.integration decorator

WHY: Integration tests verify that components work together correctly with real dependencies.
"""

import pytest
import asyncio
from typing import List, Dict, Any
from datetime import datetime, timedelta

# Import real implementations (not mocks)
# from agents.[module] import [Class]
# from infrastructure.message_bus import MessageBus
# from infrastructure.database import Database


@pytest.mark.integration
class TestIntegration[FEATURE]:
    """
    Integration tests for [FEATURE].

    WHY: Verify real interactions between components.
    HOW: Uses test database, test message bus, and other real services.

    IMPORTANT:
    - Tests run against TEST environment (not production)
    - Database is cleaned after each test
    - Network calls are to test/staging endpoints
    """

    @pytest.fixture(scope="function")
    async def test_database(self):
        """
        Provide test database connection.

        WHY: Integration tests need real database, but isolated per test.
        HOW: Creates fresh test database, yields for test, then cleans up.
        """
        # Initialize test database
        from infrastructure.database import Database
        db = Database(connection_string="postgresql://localhost:5432/test_db")
        await db.connect()

        # Create schema
        await db.execute("CREATE TABLE IF NOT EXISTS test_table (...)")

        yield db

        # Cleanup: Drop test data
        await db.execute("TRUNCATE TABLE test_table CASCADE")
        await db.disconnect()

    @pytest.fixture(scope="function")
    async def test_message_bus(self):
        """
        Provide test message bus.

        WHY: Integration tests need real message passing, but isolated.
        HOW: Uses test Redis instance, clears queues after each test.
        """
        from infrastructure.message_bus import MessageBus
        message_bus = MessageBus(redis_url="redis://localhost:6379/15")  # Test DB
        await message_bus.connect()

        yield message_bus

        # Cleanup: Clear all test queues
        await message_bus.clear_all_queues()
        await message_bus.disconnect()

    @pytest.fixture
    def test_llm(self):
        """
        Provide LLM for testing.

        WHY: Can use real LLM (with test API key) or fast mock for speed.
        HOW: Configure to use cheaper/faster model or mock.
        """
        # Option 1: Use real LLM (costs money but realistic)
        from infrastructure.llm_provider import ClaudeLLM
        return ClaudeLLM(model="claude-haiku", api_key="test_key")

        # Option 2: Use deterministic mock for faster tests
        # from tests.mocks import DeterministicLLM
        # return DeterministicLLM()

    async def test_agent_collaboration_full_workflow(
        self,
        test_database,
        test_message_bus
    ):
        """
        Test complete agent collaboration workflow.

        GIVEN: Multiple agents on the same message bus
        WHEN: CMO delegates task to Content Manager
        THEN: Content Manager delegates to Copywriter, work completes successfully
        """
        # GIVEN: Initialize agents with real dependencies
        from agents.cmo_agent import CMOAgent
        from agents.content_manager import ContentManager
        from agents.copywriter import Copywriter

        cmo = CMOAgent(
            message_bus=test_message_bus,
            database=test_database
        )
        content_manager = ContentManager(
            message_bus=test_message_bus,
            database=test_database
        )
        copywriter = Copywriter(
            message_bus=test_message_bus,
            database=test_database
        )

        # Start agents listening
        await asyncio.gather(
            content_manager.start(),
            copywriter.start()
        )

        # WHEN: CMO creates task
        task_id = await cmo.create_content_task(
            task_type="blog_post",
            topic="AI Marketing ROI",
            deadline=datetime.now() + timedelta(days=7)
        )

        # Wait for workflow to complete
        await asyncio.sleep(2)  # Give agents time to process

        # THEN: Verify workflow completed
        task = await test_database.get_task(task_id)
        assert task["status"] == "completed"
        assert task["assigned_to"] == "copywriter"

        # Verify content was created
        content = await test_database.get_content(task["content_id"])
        assert content is not None
        assert content["title"] is not None
        assert len(content["body"]) > 100

        # Verify messages were exchanged
        messages = await test_message_bus.get_message_history(task_id)
        assert len(messages) >= 3  # CMO -> Manager -> Copywriter

    async def test_database_persistence_across_operations(self, test_database):
        """
        Test that data persists correctly across operations.

        GIVEN: Agent saves data to database
        WHEN: Another agent retrieves the data
        THEN: Data is correct and complete
        """
        # GIVEN: Save content
        from agents.copywriter import Copywriter
        copywriter = Copywriter(database=test_database)

        content_id = await copywriter.save_draft(
            title="Test Blog Post",
            body="Content body here...",
            metadata={"author": "copywriter", "status": "draft"}
        )

        # WHEN: Retrieve content (simulating different agent/session)
        from agents.content_manager import ContentManager
        content_manager = ContentManager(database=test_database)

        retrieved_content = await content_manager.get_content(content_id)

        # THEN: Data matches
        assert retrieved_content["title"] == "Test Blog Post"
        assert retrieved_content["body"] == "Content body here..."
        assert retrieved_content["metadata"]["author"] == "copywriter"

    async def test_message_bus_delivery_guarantees(self, test_message_bus):
        """
        Test message bus delivers messages reliably.

        GIVEN: Agent publishes message to queue
        WHEN: Another agent subscribes to the queue
        THEN: Message is delivered exactly once
        """
        # GIVEN: Publisher sends message
        message_sent = {
            "from": "content_manager",
            "to": "copywriter",
            "type": "task_assignment",
            "task_id": "12345",
            "payload": {"topic": "AI ROI"}
        }

        await test_message_bus.publish(
            queue="copywriter_tasks",
            message=message_sent
        )

        # WHEN: Subscriber receives message
        message_received = await test_message_bus.subscribe(
            queue="copywriter_tasks",
            timeout=5
        )

        # THEN: Message matches and is received exactly once
        assert message_received == message_sent

        # Verify no duplicate
        next_message = await test_message_bus.subscribe(
            queue="copywriter_tasks",
            timeout=1
        )
        assert next_message is None  # Queue should be empty

    async def test_concurrent_agent_operations(
        self,
        test_database,
        test_message_bus
    ):
        """
        Test multiple agents working concurrently.

        GIVEN: Multiple agents processing different tasks simultaneously
        WHEN: All agents are active
        THEN: No race conditions, all tasks complete successfully
        """
        from agents.copywriter import Copywriter
        from agents.designer import Designer
        from agents.seo_specialist import SEOSpecialist

        # GIVEN: Create multiple tasks
        tasks = [
            {"type": "blog_post", "topic": "AI ROI"},
            {"type": "social_post", "platform": "linkedin"},
            {"type": "infographic", "theme": "marketing stats"}
        ]

        # WHEN: Process tasks concurrently
        copywriter = Copywriter(database=test_database, message_bus=test_message_bus)
        designer = Designer(database=test_database, message_bus=test_message_bus)
        seo = SEOSpecialist(database=test_database, message_bus=test_message_bus)

        results = await asyncio.gather(
            copywriter.create_content(tasks[0]),
            copywriter.create_content(tasks[1]),
            designer.create_content(tasks[2])
        )

        # THEN: All tasks completed without errors
        assert len(results) == 3
        assert all(r["status"] == "completed" for r in results)

        # Verify no data corruption
        for result in results:
            content = await test_database.get_content(result["content_id"])
            assert content is not None
            assert content["created_at"] is not None

    async def test_error_recovery_and_retry(self, test_message_bus):
        """
        Test system recovers from failures.

        GIVEN: Agent fails on first attempt
        WHEN: Retry logic executes
        THEN: Task eventually succeeds
        """
        # GIVEN: Simulate failing agent
        from agents.copywriter import Copywriter
        copywriter = Copywriter(message_bus=test_message_bus)

        # Configure to fail twice, then succeed
        call_count = 0
        original_generate = copywriter.generate_content

        async def failing_generate(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("LLM API temporarily unavailable")
            return await original_generate(*args, **kwargs)

        copywriter.generate_content = failing_generate

        # WHEN: Execute with retry
        result = await copywriter.create_with_retry(
            topic="Test Topic",
            max_retries=5
        )

        # THEN: Eventually succeeds
        assert result["status"] == "completed"
        assert call_count == 3  # Failed twice, succeeded third time

    async def test_external_api_integration(self):
        """
        Test integration with external APIs.

        GIVEN: Configuration for external service (LinkedIn, Twitter, etc.)
        WHEN: Agent publishes content
        THEN: Content appears on external platform

        NOTE: Use test/sandbox accounts for external services
        """
        from agents.social_media_agent import SocialMediaAgent
        from infrastructure.linkedin_client import LinkedInClient

        # GIVEN: Test LinkedIn client
        linkedin = LinkedInClient(
            access_token="test_token",
            api_url="https://api.linkedin.com/v2/test"  # Test endpoint
        )

        social_agent = SocialMediaAgent(linkedin_client=linkedin)

        # WHEN: Publish post
        post_id = await social_agent.publish_to_linkedin(
            content="Test post for integration testing",
            visibility="test_only"  # Use test visibility
        )

        # THEN: Post was created
        assert post_id is not None

        # Verify post exists on LinkedIn
        post = await linkedin.get_post(post_id)
        assert post["content"] == "Test post for integration testing"

        # Cleanup: Delete test post
        await linkedin.delete_post(post_id)

    @pytest.mark.slow
    async def test_performance_under_load(
        self,
        test_database,
        test_message_bus
    ):
        """
        Test system performance with high load.

        GIVEN: 100 concurrent tasks
        WHEN: System processes all tasks
        THEN: Completes within acceptable time (e.g., 30 seconds)
        """
        from agents.copywriter import Copywriter

        copywriter = Copywriter(
            database=test_database,
            message_bus=test_message_bus
        )

        # GIVEN: Create 100 tasks
        tasks = [
            {"topic": f"Blog post {i}", "word_count": 500}
            for i in range(100)
        ]

        # WHEN: Process concurrently
        start_time = datetime.now()

        results = await asyncio.gather(
            *[copywriter.create_content(task) for task in tasks]
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # THEN: All completed within time limit
        assert len(results) == 100
        assert all(r["status"] == "completed" for r in results)
        assert duration < 30, f"Took {duration}s (expected < 30s)"


@pytest.mark.integration
class TestIntegrationDataConsistency:
    """Test data consistency across the system."""

    async def test_transaction_rollback_on_error(self, test_database):
        """
        Test database transactions rollback correctly on error.

        GIVEN: Multi-step operation that fails midway
        WHEN: Error occurs
        THEN: All changes are rolled back (data consistent)
        """
        pass

    async def test_eventual_consistency_in_distributed_system(
        self,
        test_database,
        test_message_bus
    ):
        """
        Test eventual consistency for async operations.

        GIVEN: Agent A updates data
        WHEN: Agent B reads data shortly after
        THEN: Eventually sees the update (may take a few ms)
        """
        pass
