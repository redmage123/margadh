"""
Market Research Agent module.

WHY: Provides market intelligence, competitive analysis, and research capabilities.
HOW: Exports MarketResearchAgent for use by executive and management layers.
"""

from agents.specialists.market_research.market_research_agent import (
    MarketResearchAgent,
)

__all__ = ["MarketResearchAgent"]
