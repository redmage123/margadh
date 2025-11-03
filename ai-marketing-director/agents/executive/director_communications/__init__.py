"""
Director of Communications Agent - Executive-layer brand governance.

WHY: Provides executive-level brand voice authority, messaging strategy,
     crisis communications, and PR oversight across all marketing channels.

HOW: Exports DirectorOfCommunicationsAgent for use by orchestration layer.
"""

from agents.executive.director_communications.director_communications_agent import (
    DirectorOfCommunicationsAgent,
)

__all__ = ["DirectorOfCommunicationsAgent"]
