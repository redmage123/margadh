"""
LLM module - Abstraction layer for LLM API calls.

WHY: Exports LLMProvider for unified LLM interactions.

Usage:
    from infrastructure.llm import LLMProvider
"""

from infrastructure.llm.llm_provider import LLMProvider

__all__ = ["LLMProvider"]
