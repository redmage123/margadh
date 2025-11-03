"""
MessageBus - Redis-based message bus for agent communication.

WHY: Enables async agent-to-agent communication via pub/sub pattern.
     Implements the message passing architecture for the multiagent system.

HOW: Uses Redis as message broker with JSON serialization.
     Agents publish to queues, subscribe with blocking reads.

Implementation follows TDD - tests written first (RED), implementation (GREEN),
then refactored (REFACTOR).

Usage:
    from infrastructure.message_bus import MessageBus

    # Manual resource management
    bus = MessageBus(redis_url="redis://localhost:6379/0")
    await bus.publish(queue="agent_copywriter", message=agent_message)
    message = await bus.subscribe(queue="agent_copywriter", timeout=30)
    await bus.close()

    # Or use async context manager (recommended)
    async with MessageBus(redis_url="redis://localhost:6379/0") as bus:
        await bus.publish(queue="agent_copywriter", message=agent_message)
        message = await bus.subscribe(queue="agent_copywriter", timeout=30)
"""

import json
from datetime import datetime
from typing import Any

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None  # type: ignore

from agents.base import AgentMessage, AgentRole, TaskPriority
from core.exceptions import MessageBusError, wrap_exception


class MessageBus:
    """
    Redis-based message bus for agent communication.

    WHY: Provides reliable async message passing between agents.
    HOW: Redis lists used as queues (LPUSH/BRPOP pattern).

    Attributes:
        _redis_url: Redis connection URL
        _queue_prefix: Prefix for queue names
        _redis: Redis client instance (lazy initialized)
    """

    def __init__(self, redis_url: str, queue_prefix: str = "agent"):
        """
        Initialize MessageBus.

        WHY: Sets up connection parameters for Redis.
        HOW: Stores config, actual connection deferred to first use.

        Args:
            redis_url: Redis connection URL (e.g., "redis://localhost:6379/0")
            queue_prefix: Prefix for queue names (default: "agent")

        Raises:
            ImportError: If redis library not installed
        """
        if aioredis is None:
            raise ImportError(
                "redis library not installed. Install with: pip install redis"
            )

        self._redis_url = redis_url
        self._queue_prefix = queue_prefix
        self._redis: Any = None
        self._closed = False

    async def _ensure_connection(self) -> None:
        """
        Ensure Redis connection is established.

        WHY: Lazy initialization - connect only when needed.
        HOW: Creates Redis client on first use.
        """
        if self._redis is None and not self._closed:
            try:
                self._redis = await aioredis.from_url(
                    self._redis_url, encoding="utf-8", decode_responses=True
                )
            except Exception as e:
                raise wrap_exception(
                    exc=e,
                    wrapper_class=MessageBusError,
                    message=f"Failed to connect to Redis at {self._redis_url}",
                    context={"redis_url": self._redis_url},
                ) from e

    async def publish(self, queue: str, message: AgentMessage) -> None:
        """
        Publish message to queue.

        WHY: Agents send messages to other agents via queues.
        HOW: Serializes AgentMessage to JSON, pushes to Redis list (LPUSH).

        Args:
            queue: Queue name (e.g., "agent_copywriter")
            message: AgentMessage to send

        Raises:
            MessageBusError: If publishing fails
        """
        await self._ensure_connection()

        try:
            # Serialize message to JSON
            message_data = self._serialize_message(message)

            # Push to Redis list (LPUSH = left push, BRPOP = right pop for FIFO)
            await self._redis.lpush(queue, message_data)

        except Exception as e:
            raise wrap_exception(
                exc=e,
                wrapper_class=MessageBusError,
                message=f"Failed to publish message {message.message_id} to queue {queue}",
                context={
                    "queue": queue,
                    "message_id": message.message_id,
                    "from_agent": message.from_agent.value,
                    "to_agent": message.to_agent.value,
                },
            ) from e

    async def subscribe(self, queue: str, timeout: int = 30) -> AgentMessage | None:
        """
        Subscribe to queue and wait for message.

        WHY: Agents receive messages from their inbox queue.
        HOW: Blocking read from Redis list (BRPOP) with timeout.

        Args:
            queue: Queue name to subscribe to
            timeout: Timeout in seconds (0 = wait forever)

        Returns:
            AgentMessage if received, None if timeout

        Raises:
            MessageBusError: If subscription fails or message invalid
        """
        await self._ensure_connection()

        try:
            # Blocking right pop with timeout
            result = await self._redis.brpop(queue, timeout=timeout)

            if result is None:
                # Timeout - no message available
                return None

            # result is tuple: (queue_name, message_data)
            _, message_data = result

            # Deserialize JSON to AgentMessage
            return self._deserialize_message(message_data)

        except json.JSONDecodeError as e:
            raise wrap_exception(
                exc=e,
                wrapper_class=MessageBusError,
                message=f"Failed to parse message from queue {queue} - invalid JSON",
                context={"queue": queue, "raw_data": str(message_data)[:100]},
            ) from e

        except Exception as e:
            raise wrap_exception(
                exc=e,
                wrapper_class=MessageBusError,
                message=f"Failed to subscribe to queue {queue}",
                context={"queue": queue, "timeout": timeout},
            ) from e

    async def publish_batch(self, queue: str, messages: list[AgentMessage]) -> None:
        """
        Publish multiple messages efficiently using pipeline.

        WHY: Performance optimization for bulk operations.
        HOW: Uses Redis pipeline to send all messages in one round-trip.

        Args:
            queue: Queue name
            messages: List of AgentMessage to send

        Raises:
            MessageBusError: If batch publish fails
        """
        await self._ensure_connection()

        try:
            # Use pipeline for efficiency
            pipe = self._redis.pipeline()

            for message in messages:
                message_data = self._serialize_message(message)
                pipe.lpush(queue, message_data)

            # Execute all commands at once
            await pipe.execute()

        except Exception as e:
            raise wrap_exception(
                exc=e,
                wrapper_class=MessageBusError,
                message=f"Failed to publish batch of {len(messages)} messages to queue {queue}",
                context={"queue": queue, "message_count": len(messages)},
            ) from e

    async def close(self) -> None:
        """
        Close Redis connection and release resources.

        WHY: Graceful cleanup prevents resource leaks.
        HOW: Closes Redis client, marks as closed for idempotency.
        """
        if self._redis is not None and not self._closed:
            try:
                await self._redis.close()
            except Exception:
                # Ignore errors during close
                pass
            finally:
                self._closed = True
                self._redis = None

    # ========================================================================
    # Async Context Manager Support
    # ========================================================================

    async def __aenter__(self) -> "MessageBus":
        """
        Enter async context manager.

        WHY: Enables 'async with MessageBus(...) as bus:' pattern.
        HOW: Returns self after ensuring connection.

        Returns:
            MessageBus instance
        """
        await self._ensure_connection()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit async context manager.

        WHY: Automatically closes connection on context exit.
        HOW: Calls close() to release resources.

        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)
        """
        await self.close()

    # ========================================================================
    # Private Helper Methods
    # ========================================================================

    def _serialize_message(self, message: AgentMessage) -> str:
        """
        Serialize AgentMessage to JSON string.

        WHY: Redis stores strings, need JSON serialization.
        HOW: Converts message to dict, then to JSON.

        Args:
            message: AgentMessage to serialize

        Returns:
            JSON string representation
        """
        message_dict = {
            "message_id": message.message_id,
            "from_agent": message.from_agent.value,
            "to_agent": message.to_agent.value,
            "message_type": message.message_type,
            "payload": message.payload,
            "priority": message.priority.value,
            "created_at": message.created_at.isoformat(),
            "reply_to": message.reply_to,
        }

        return json.dumps(message_dict)

    def _deserialize_message(self, message_data: str) -> AgentMessage:
        """
        Deserialize JSON string to AgentMessage.

        WHY: Convert Redis string back to AgentMessage object.
        HOW: Parses JSON, reconstructs AgentMessage with proper types.

        Args:
            message_data: JSON string from Redis

        Returns:
            AgentMessage instance

        Raises:
            json.JSONDecodeError: If JSON invalid
            KeyError: If required fields missing
        """
        message_dict = json.loads(message_data)

        # Reconstruct AgentMessage
        return AgentMessage(
            message_id=message_dict["message_id"],
            from_agent=AgentRole(message_dict["from_agent"]),
            to_agent=AgentRole(message_dict["to_agent"]),
            message_type=message_dict["message_type"],
            payload=message_dict["payload"],
            priority=TaskPriority(message_dict["priority"]),
            created_at=datetime.fromisoformat(message_dict["created_at"]),
            reply_to=message_dict.get("reply_to"),
        )
