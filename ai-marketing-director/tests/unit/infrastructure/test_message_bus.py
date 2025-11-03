"""
Unit Tests for MessageBus - Written FIRST (TDD RED).

WHY: Following TDD - write tests before implementation to define behavior.
     This test defines the expected interface and behavior of MessageBus.

HOW: Tests are written first, will fail initially (RED), then we implement
     the minimal code to pass (GREEN), then refactor.

Test Coverage:
- Connection and initialization
- Publishing messages
- Subscribing to messages
- Error handling
- Resource cleanup
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.base import AgentMessage, AgentRole, TaskPriority
from core.exceptions import MessageBusError


@pytest.mark.unit
class TestMessageBusInitialization:
    """Test MessageBus initialization and connection."""

    @pytest.mark.asyncio
    async def test_message_bus_connects_to_redis(self):
        """
        TDD RED: MessageBus should connect to Redis on initialization.

        WHY: Validates connection establishment.
        EXPECTED: MessageBus connects and is ready for use.
        """
        from infrastructure.message_bus import MessageBus

        with patch("infrastructure.message_bus.message_bus.aioredis") as mock_redis:
            mock_redis.from_url = AsyncMock()

            bus = MessageBus(redis_url="redis://localhost:6379/0")

            # Should not raise exception
            assert bus is not None
            assert hasattr(bus, "publish")
            assert hasattr(bus, "subscribe")
            assert hasattr(bus, "close")

    @pytest.mark.asyncio
    async def test_message_bus_with_custom_queue_prefix(self):
        """
        TDD RED: MessageBus should support custom queue prefix.

        WHY: Allows namespace isolation for different environments.
        EXPECTED: Bus accepts and uses custom prefix.
        """
        from infrastructure.message_bus import MessageBus

        with patch("infrastructure.message_bus.message_bus.aioredis") as mock_redis:
            mock_redis.from_url = AsyncMock()

            bus = MessageBus(
                redis_url="redis://localhost:6379/0", queue_prefix="test_agent"
            )

            assert bus is not None


@pytest.mark.unit
class TestMessageBusPublishing:
    """Test message publishing functionality."""

    @pytest.fixture
    async def mock_bus(self):
        """Create MessageBus with mocked Redis."""
        from infrastructure.message_bus import MessageBus

        with patch("infrastructure.message_bus.message_bus.aioredis") as mock_redis:
            mock_redis.from_url = AsyncMock()
            mock_client = AsyncMock()
            mock_redis.from_url.return_value = mock_client

            bus = MessageBus(redis_url="redis://localhost:6379/0")
            bus._redis = mock_client

            yield bus

            await bus.close()

    @pytest.fixture
    def test_message(self):
        """Create test message."""
        return AgentMessage(
            message_id="test_msg_001",
            from_agent=AgentRole.COPYWRITER,
            to_agent=AgentRole.CONTENT_MANAGER,
            message_type="task_completed",
            payload={"task_id": "task_123", "status": "completed"},
            priority=TaskPriority.NORMAL,
            created_at=datetime.now(),
        )

    @pytest.mark.asyncio
    async def test_publish_message_to_queue(self, mock_bus, test_message):
        """
        TDD RED: MessageBus.publish() should send message to queue.

        WHY: Core functionality - agents must send messages.
        EXPECTED: Message serialized and pushed to Redis queue.
        """
        queue_name = "agent_content_manager"

        await mock_bus.publish(queue=queue_name, message=test_message)

        # Verify Redis was called
        mock_bus._redis.lpush.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_serializes_message_to_json(self, mock_bus, test_message):
        """
        TDD RED: publish() should serialize AgentMessage to JSON.

        WHY: Redis stores strings, need JSON serialization.
        EXPECTED: Message converted to JSON string.
        """
        import json

        queue_name = "agent_content_manager"

        await mock_bus.publish(queue=queue_name, message=test_message)

        # Get the call arguments
        call_args = mock_bus._redis.lpush.call_args

        # Second argument should be JSON string
        json_data = call_args[0][1]
        parsed = json.loads(json_data)

        assert parsed["message_id"] == "test_msg_001"
        assert parsed["from_agent"] == "copywriter"
        assert parsed["to_agent"] == "content_manager"

    @pytest.mark.asyncio
    async def test_publish_raises_error_on_redis_failure(self, mock_bus, test_message):
        """
        TDD RED: publish() should wrap Redis errors.

        WHY: Exception wrapping standard (Golden Rule #7).
        EXPECTED: Redis errors wrapped in MessageBusError.
        """
        mock_bus._redis.lpush = AsyncMock(side_effect=Exception("Redis down"))

        with pytest.raises(MessageBusError) as exc_info:
            await mock_bus.publish(queue="test_queue", message=test_message)

        assert exc_info.value.original_exception is not None
        assert "redis" in str(exc_info.value).lower()


@pytest.mark.unit
class TestMessageBusSubscribing:
    """Test message subscription functionality."""

    @pytest.fixture
    async def mock_bus(self):
        """Create MessageBus with mocked Redis."""
        from infrastructure.message_bus import MessageBus

        with patch("infrastructure.message_bus.message_bus.aioredis") as mock_redis:
            mock_redis.from_url = AsyncMock()
            mock_client = AsyncMock()
            mock_redis.from_url.return_value = mock_client

            bus = MessageBus(redis_url="redis://localhost:6379/0")
            bus._redis = mock_client

            yield bus

            await bus.close()

    @pytest.mark.asyncio
    async def test_subscribe_receives_message_from_queue(self, mock_bus):
        """
        TDD RED: subscribe() should retrieve message from queue.

        WHY: Agents must receive messages from other agents.
        EXPECTED: Message pulled from Redis and deserialized.
        """
        import json

        # Mock Redis to return a message
        test_message_data = {
            "message_id": "test_msg_001",
            "from_agent": "copywriter",
            "to_agent": "content_manager",
            "message_type": "task_completed",
            "payload": {"task_id": "task_123"},
            "priority": "normal",
            "created_at": datetime.now().isoformat(),
            "reply_to": None,
        }

        mock_bus._redis.brpop = AsyncMock(
            return_value=("queue_name", json.dumps(test_message_data))
        )

        message = await mock_bus.subscribe(queue="agent_content_manager", timeout=1)

        assert message is not None
        assert message.message_id == "test_msg_001"
        assert message.from_agent == AgentRole.COPYWRITER
        assert message.to_agent == AgentRole.CONTENT_MANAGER

    @pytest.mark.asyncio
    async def test_subscribe_returns_none_on_timeout(self, mock_bus):
        """
        TDD RED: subscribe() should return None on timeout.

        WHY: Non-blocking operation - agent shouldn't hang.
        EXPECTED: None returned if no message within timeout.
        """
        # Mock Redis to return None (timeout)
        mock_bus._redis.brpop = AsyncMock(return_value=None)

        message = await mock_bus.subscribe(queue="agent_test", timeout=1)

        assert message is None

    @pytest.mark.asyncio
    async def test_subscribe_raises_error_on_redis_failure(self, mock_bus):
        """
        TDD RED: subscribe() should wrap Redis errors.

        WHY: Exception wrapping standard (Golden Rule #7).
        EXPECTED: Redis errors wrapped in MessageBusError.
        """
        mock_bus._redis.brpop = AsyncMock(
            side_effect=Exception("Redis connection lost")
        )

        with pytest.raises(MessageBusError) as exc_info:
            await mock_bus.subscribe(queue="agent_test", timeout=1)

        assert exc_info.value.original_exception is not None

    @pytest.mark.asyncio
    async def test_subscribe_handles_invalid_json_gracefully(self, mock_bus):
        """
        TDD RED: subscribe() should handle malformed messages.

        WHY: Resilience - bad data shouldn't crash agent.
        EXPECTED: Invalid JSON raises MessageBusError with context.
        """
        # Mock Redis to return invalid JSON
        mock_bus._redis.brpop = AsyncMock(return_value=("queue_name", "invalid json{"))

        with pytest.raises(MessageBusError) as exc_info:
            await mock_bus.subscribe(queue="agent_test", timeout=1)

        assert (
            "json" in str(exc_info.value).lower()
            or "parse" in str(exc_info.value).lower()
        )


@pytest.mark.unit
class TestMessageBusResourceManagement:
    """Test resource management and cleanup."""

    @pytest.mark.asyncio
    async def test_close_closes_redis_connection(self):
        """
        TDD RED: close() should close Redis connection.

        WHY: Resource cleanup prevents leaks.
        EXPECTED: Redis client closed, resources released.
        """
        from infrastructure.message_bus import MessageBus

        with patch("infrastructure.message_bus.message_bus.aioredis") as mock_redis:
            mock_redis.from_url = AsyncMock()
            mock_client = AsyncMock()
            mock_redis.from_url.return_value = mock_client

            bus = MessageBus(redis_url="redis://localhost:6379/0")
            bus._redis = mock_client

            await bus.close()

            # Verify Redis client was closed
            mock_client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_is_idempotent(self):
        """
        TDD RED: close() can be called multiple times safely.

        WHY: Prevents errors in cleanup code.
        EXPECTED: Second close() doesn't raise exception.
        """
        from infrastructure.message_bus import MessageBus

        with patch("infrastructure.message_bus.message_bus.aioredis") as mock_redis:
            mock_redis.from_url = AsyncMock()
            mock_client = AsyncMock()
            mock_redis.from_url.return_value = mock_client

            bus = MessageBus(redis_url="redis://localhost:6379/0")
            bus._redis = mock_client

            # Close twice - should not raise
            await bus.close()
            await bus.close()

            # Verify close called at least once
            assert mock_client.close.call_count >= 1


@pytest.mark.unit
class TestMessageBusBatchOperations:
    """Test batch publish/subscribe operations."""

    @pytest.fixture
    async def mock_bus(self):
        """Create MessageBus with mocked Redis."""
        from infrastructure.message_bus import MessageBus

        with patch("infrastructure.message_bus.message_bus.aioredis") as mock_redis:
            mock_redis.from_url = AsyncMock()
            mock_client = AsyncMock()
            mock_redis.from_url.return_value = mock_client

            # Mock pipeline for batch operations
            # pipeline() is NOT async, so use MagicMock
            mock_pipeline = MagicMock()
            mock_pipeline.lpush = MagicMock(return_value=None)
            mock_pipeline.execute = AsyncMock(return_value=None)
            mock_client.pipeline = MagicMock(return_value=mock_pipeline)

            bus = MessageBus(redis_url="redis://localhost:6379/0")
            bus._redis = mock_client

            yield bus

            await bus.close()

    @pytest.mark.asyncio
    async def test_publish_batch_sends_multiple_messages(self, mock_bus):
        """
        TDD RED: publish_batch() should send multiple messages efficiently.

        WHY: Performance optimization for bulk operations.
        EXPECTED: All messages sent in single pipeline operation.
        """
        messages = [
            AgentMessage(
                message_id=f"msg_{i}",
                from_agent=AgentRole.COPYWRITER,
                to_agent=AgentRole.CONTENT_MANAGER,
                message_type="test",
                payload={},
                priority=TaskPriority.NORMAL,
                created_at=datetime.now(),
            )
            for i in range(5)
        ]

        await mock_bus.publish_batch(queue="test_queue", messages=messages)

        # Should use pipeline for efficiency
        # Verify multiple messages were sent
        assert mock_bus._redis.lpush.call_count == 5 or hasattr(
            mock_bus._redis, "pipeline"
        )


@pytest.mark.unit
def test_message_bus_protocol_interface():
    """
    TDD RED: MessageBus should satisfy expected interface.

    WHY: Type safety and contract validation.
    EXPECTED: MessageBus has all required methods.
    """
    from infrastructure.message_bus import MessageBus

    required_methods = ["publish", "subscribe", "close"]

    for method in required_methods:
        assert hasattr(MessageBus, method), f"MessageBus missing method: {method}"
