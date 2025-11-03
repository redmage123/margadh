"""
Message Bus module - Redis-based agent communication.

WHY: Exports MessageBus for agent-to-agent messaging.

Usage:
    from infrastructure.message_bus import MessageBus
"""

from infrastructure.message_bus.message_bus import MessageBus

__all__ = ["MessageBus"]
